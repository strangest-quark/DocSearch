from client.s3_client import S3Client
from client.elastic_search_client import ES_Client
from util.pdf_util import PDFUtil
from config.config import Config
import textract
from io import BytesIO
from docx import Document


class S3FileProcessor:

    def __init__(self, config: Config, aws_access_key_id, aws_secret_access_key, bucket, region, index):
        self.pdfUtil = PDFUtil()
        self.esClient = ES_Client(config)
        self.s3Client = S3Client(aws_access_key_id, aws_secret_access_key, bucket, region)
        self.bucket = bucket
        self.esClient.set_index(index.replace(' ','').lower())

    def process_pdf(self, body, key):
        text = self.pdfUtil.pdf_to_text(body)
        metadata = self.pdfUtil.get_metadata(body)
        print(text)
        if text is not None:
            es_body = {
                'content': text
            }
            for obj in metadata[0]:
                es_body[obj] = (metadata[0][obj]).decode("utf-8")
        self.esClient.index_es(key, es_body)

    def process_doc(self, url, key):
        text = ' '.join(textract.process(url).decode('utf-8').splitlines())
        if text is not None:
            es_body = {
                'content': text
            }
        document = Document(url)
        core_properties = document.core_properties
        metadata = [attr for attr in dir(core_properties) if not callable(getattr(core_properties, attr)) and not attr.startswith("__") and not attr.startswith("_")]
        for meta in metadata:
            if getattr(core_properties, meta):
                es_body[meta] = str(getattr(core_properties, meta))
        self.esClient.index_es(key, es_body)

    def process_text(self, body, key):
        text = ' '.join(body.decode('utf-8').splitlines())
        if text is not None:
            es_body = {
                'content': text
            }
        self.esClient.index_es(key, es_body)

    def read_bucket(self):
        keys = self.s3Client.get_s3_keys(self.bucket)
        for key in keys:
            if key.endswith(".pdf"):
                body = self.s3Client.get_s3_file_body(key)
                self.process_pdf(body, key)
            if key.endswith(".docx"):
                self.s3Client.download_file(self.bucket, key)
                self.process_doc(key, key)
            if key.endswith(".txt"):
                body = self.s3Client.get_s3_file_body(key)
                self.process_text(body, key)


