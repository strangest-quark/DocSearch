from docSearch_ws.client.elastic_search_client import ES_Client
from docSearch_ws.client.sql_client import SQLClient
from docSearch_ws.config.config import Config
import argparse

from docSearch_ws.config.setup import Setup

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='<config file>', type=str, required=True)

    args = parser.parse_args()

    config_file = args.config
    config = Config(config_file)

    es_client = ES_Client(config)
    sql_client = SQLClient(config)
    setup = Setup(config)

    sql_client.insert_csv_to_db("bbc")
    sql_client.fetch_some_rows(5)
    setup.populate_index_from_mysql()
    es_client.tag_search("sports")
    es_client.match_all()


