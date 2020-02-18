from docSearch_ws.client.elastic_search_client import ES_Client
from docSearch_ws.client.sql_client import SQLClient
from docSearch_ws.config.config import Config


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