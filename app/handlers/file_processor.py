import os

from client.s3_client import S3Client
from client.elastic_search_client import ES_Client
from util.pdf_util import PDFUtil
from util.automated_tags import AutomatedTags
from config.config import Config
from client.sql_client import SQLClient
import textract
from io import BytesIO
from docx import Document
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import re


class S3FileProcessor:

    def __init__(self, config: Config, aws_access_key_id, aws_secret_access_key, bucket, region, index):
        self.pdfUtil = PDFUtil()
        self.esClient = ES_Client(config)
        self.sqlClient = SQLClient(config)
        self.automatedTags = AutomatedTags()
        self.s3Client = S3Client(aws_access_key_id, aws_secret_access_key, bucket, region)
        self.bucket = bucket
        self.index = index
        self.esClient.set_index(index.replace(' ', '').lower())

    def get_tag_string(self, text):
        tags = self.automatedTags.get_tags(text)
        tag_array=[]
        tag_string = ''
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:°"’”.]')
        if tags is not None:
            for tag in tags:
                if regex.search(tag) is None:
                    tag_array.append(tag)
        tags = list(dict.fromkeys(tag_array))
        for tag in tags:
            tag_string = tag_string+','+tag
        if tag_string is not None:
            tag_string = tag_string[1:]
        return tag_string

    def remove_tag_duplicates(self, tag_string):
        tags = tag_string.split(',')
        tags = list(dict.fromkeys(tags))
        tag_str = ''
        for tag in tags:
            tag_str = tag_str+','+tag
        if tag_str is not None:
            tag_str = tag_str[1:]
        return tag_str


    def process_pdf(self, body, key):
        text = self.pdfUtil.pdf_to_text(body)
        metadata = self.pdfUtil.get_metadata(body)
        print(text)
        es_body=''
        tag_string=''
        if text is not None:
            tag_string = self.get_tag_string(text)
            es_body = {
                'content': text,
                'automated_tags': tag_string,
                'tags': '',
                'summary': self.get_summary(text)
            }
            for obj in metadata[0]:
                try:
                    es_body[obj] = (metadata[0][obj]).decode("utf-8")
                except:
                    continue
        self.esClient.index_es(key, es_body)
        return tag_string

    def process_doc(self, url, key):
        text = ' '.join(textract.process(url).decode('utf-8').splitlines())
        es_body = ''
        tag_string = ''
        if text is not None:
            tag_string = self.get_tag_string(text)
            es_body = {
                'content': text,
                'automated_tags': tag_string,
                'tags': '',
                'summary': self.get_summary(text)
            }
        document = Document(url)
        core_properties = document.core_properties
        metadata = [attr for attr in dir(core_properties) if
                    not callable(getattr(core_properties, attr)) and not attr.startswith("__") and not attr.startswith(
                        "_")]
        for meta in metadata:
            try:
                if getattr(core_properties, meta):
                    es_body[meta] = str(getattr(core_properties, meta))
            except:
                continue
        print(self.esClient.index_es(key, es_body))
        return tag_string

    def process_text(self, body, key):
        text = ' '.join(body.decode('utf-8').splitlines())
        es_body = ''
        tag_string = ''
        if text is not None:
            tag_string = self.get_tag_string(text)
            es_body = {
                'content': text,
                'automated_tags': tag_string,
                'tags': '',
                'summary': self.get_summary(text)
            }
        print(self.esClient.index_es(key, es_body))
        return tag_string

    def add_to_unique_tag_list(self, tag_string):
        tag_string = tag_string.replace(',', ' ')
        self.sqlClient.insert_into_tags(self.index, tag_string)

    def read_bucket(self):
        keys = self.s3Client.get_s3_keys(self.bucket)
        tag_string = ""
        for key in keys:
            try:
                if key.endswith(".pdf"):
                    body = self.s3Client.get_s3_file_body(key)
                    tag_string = tag_string + "," + self.process_pdf(body, key)
                if key.endswith(".docx"):
                    self.s3Client.download_file(self.bucket, key)
                    tag_string = tag_string + "," + self.process_doc('/tmp/' + key, key)
                if key.endswith(".txt"):
                    body = self.s3Client.get_s3_file_body(key)
                    tag_string = tag_string + "," + self.process_text(body, key)
            except:
                print("Skipping processing for this file")
        try:
            tag_string = self.remove_tag_duplicates(tag_string)
            self.add_to_unique_tag_list(tag_string)
        except:
            print("Error in adding tags to db")

    def get_summary(self, text):
        LANGUAGE = "english"
        SENTENCES_COUNT = 3
        parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        summary = ""

        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            summary += str(sentence)
        return summary
