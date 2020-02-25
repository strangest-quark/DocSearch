from elasticsearch import Elasticsearch
from config.config import Config


class ES_Client:

    def __init__(self, config: Config):
        self.es = Elasticsearch([config.es_host], port=config.es_port)
        self.index = config.es_index

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
        for hit in res['hits']['hits']:
            print("_source: " + hit["_source"]["content"])

    def full_text_search(self, query):
        res = self.es.search(index=self.index, body={"query": {"query_string": {"query": query}}})
        print("Got %d Hits:" % res['hits']['total']['value'])
        return res['hits']['hits']

    def text_and_tag_search(self, query, tag):
        res = self.es.search(index=self.index, body={"query": {
            "bool": {
                "must": [
                    {"term": {"tags": tag}},
                    {"term": {"content": query}}
                ]
            }}})
        print("Got %d Hits:" % res['hits']['total']['value'])
        return res['hits']['hits']

    def tag_search(self, tag):
        res = self.es.search(index=self.index, body={"query": {"bool": {"must": [{"term": {"tags": tag}}]}}})
        print("Got %d Hits:" % res['hits']['total']['value'])
        return res['hits']['hits']
