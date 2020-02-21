from typing import List, Dict
from flask import Flask
from flask import request
from flask import jsonify
import mysql.connector
from client.elastic_search_client import ES_Client
from client.sql_client import SQLClient
from config.config import Config
from config.setup import Setup
import json
import argparse

app = Flask(__name__)

config = None
es_client = None
sql_client = None


@app.route('/')
def hello_world():
    return 'DocSearch is running!'


# /search_tag?search=history
@app.route('/search_tag', methods=['GET', 'POST'])
def tag_search():
    tag = request.args.get('search')
    j = dict()
    j['res'] = es_client.tag_search(tag)
    return jsonify(j)

# /search_full_text?search=history
@app.route('/search_full_text', methods=['GET', 'POST'])
def search_full_text():
    full_text = request.args.get('search')
    j = dict()
    j['res'] = es_client.full_text_search(full_text)
    return jsonify(j)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='<config file>', type=str, required=True)
    args = parser.parse_args()
    config_file = args.config
    config = Config(config_file)
    es_client = ES_Client(config)
    setup = Setup(config)
    sql_client = SQLClient(config)
    sql_client.insert_csv_to_db("bbc")
    sql_client.fetch_some_rows(5)
    setup.populate_index_from_mysql()
    app.run(host='0.0.0.0', port=80)
