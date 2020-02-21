from client.elastic_search_client import ES_Client
from client.sql_client import SQLClient
from config.config import Config


class Setup:
    def __init__(self, config: Config):
        self.sql_client = SQLClient(config)
        self.es_client = ES_Client(config)

    def populate_index_from_mysql(self):
        rows = self.sql_client.fetch_all()
        for row in rows:
            body = {
                'tags': row[2],
                'content': row[1]
            }
            self.es_client.index_es(row[0], body)