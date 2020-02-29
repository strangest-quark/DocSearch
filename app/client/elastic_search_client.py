from elasticsearch import Elasticsearch
from config.config import Config
import nltk
from nltk.corpus import wordnet
from spellchecker import SpellChecker


class ES_Client:

    def __init__(self, config: Config):
        self.es = Elasticsearch([config.es_host], port=config.es_port)
        self.index = config.es_index
        self.spell = SpellChecker()

    def get_similar(self, word):
        synonyms = []
        for syn in wordnet.synsets(word):
            for l in syn.lemmas():
                synonyms.append(l.name())
        return synonyms

    def set_index(self, index):
        self.index = index

    def index_es(self, doc_id, doc):
        res = self.es.index(index=self.index, id=doc_id, body=doc)
        print(res)

    def update_es(self, doc_id, doc, index):
        return self.es.update(index=index, doc_type="_doc", id=doc_id, body=doc)

    def get_es(self, doc_id, index):
        print(self.es.get(index=index, id=doc_id))
        return self.es.get(index=index, id=doc_id)

    def get_id_from_index(self, doc_id):
        res = self.es.get(index=self.index, id=doc_id)
        return res['_source']

    def match_all(self):
        res = self.es.search(index=self.index, body={"query": {"match_all": {}}})
        print("Got %d Hits:" % res['hits']['total']['value'])
        return res['hits']['hits']

    def full_text_search(self, query):
        res = self.es.search(index=self.index, body={"query": {"query_string": {"query": query}}})
        if res['hits']['total']['value'] == 0:
            print('Retrying')
            query = self.get_alternate_query(query)
            print(query)
            res = self.es.search(index=self.index, body={"query": {"query_string": {"query": query}}})
            print("Got %d Hits:" % res['hits']['total']['value'])
            return [res['hits']['hits'], True]
        print("Got %d Hits:" % res['hits']['total']['value'])
        return [res['hits']['hits'], False]

    def get_alternate_query(self, query):
        other_queries = []
        if len(self.spell.unknown(query)) > 0:
            other_queries = other_queries + self.spell.candidates(query)
        other_queries = other_queries + self.get_similar(query)
        new_query = '(' + query + ') OR'
        for q in other_queries:
            new_query = new_query + ' (' + q + ') OR'
        return new_query[:-3]

    def text_and_tag_search(self, query, tag):
        search = '{"query": ' \
                 '{"bool": ' \
                 '{ "must": ' \
                 '[{"term": {"content": "' + query + '"}},' \
                                                     '{"bool": {"should": [' \
                                                     '{"term": {"tags": "' + tag + '"}},' \
                                                                                   '{"term": {"automated_tags": "' + tag + '"}}]}}]}}}'
        res = self.es.search(index=self.index, body=search)
        if res['hits']['total']['value'] == 0:
            query = self.get_alternate_query(query)
            res = self.es.search(index=self.index, body={"query": {"query_string": {"query": query + 'OR' + tag}}})
            print("Got %d Hits:" % res['hits']['total']['value'])
            return [res['hits']['hits'], True]
        print("Got %d Hits:" % res['hits']['total']['value'])
        return [res['hits']['hits'], False]

    def tag_search(self, tag):
        search = '{"query": {"bool": {"should": [{"term": {"tags": "' + tag + '"}},{"term": {"automated_tags": "' + tag + '"}}]}}}'
        res = self.es.search(index=self.index, body=search)
        if res['hits']['total']['value'] == 0:
            query = self.get_alternate_query(tag)
            res = self.es.search(index=self.index, body={"query": {"query_string": {"query": query}}})
            print("Got %d Hits:" % res['hits']['total']['value'])
            return [res['hits']['hits'], True]
        print("Got %d Hits:" % res['hits']['total']['value'])
        return [res['hits']['hits'], False]
