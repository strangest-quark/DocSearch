from typing import List, Dict
from flask import Flask
from flask import request
from flask import jsonify
import mysql.connector
from client.elastic_search_client import ES_Client
from client.sql_client import SQLClient
from config.config import Config
from config.setup import Setup
from handlers.connections_handler import ConnectionHandler
import json
import argparse
from flask_cors import CORS, cross_origin
from flask_api import status


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


config = None
es_client = None
sql_client = None
connectionHandler = None


@app.route('/')
@cross_origin()
def hello_world():
    return 'DocSearch is running!'


# /search_tag?search=history
@app.route('/search_tag', methods=['GET'])
@cross_origin()
def tag_search():
    tag = request.args.get('search')
    j = dict()
    j['res'] = es_client.tag_search(tag)
    return jsonify(j)

# /search_full_text?search=history
@app.route('/search_full_text', methods=['GET'])
@cross_origin()
def search_full_text():
    full_text = request.args.get('search')
    j = dict()
    j['res'] = es_client.full_text_search(full_text)
    return jsonify(j)

@app.route('/add_connection', methods=['POST'])
@cross_origin()
def add_connection():
    req_body = request.get_json()
    j=dict()
    try:
        if req_body['connection_type'] == "s3":
            try:
                keys = connectionHandler.add_s3_connection(req_body["access_key_id"], req_body["access_key"], req_body["bucket"], req_body["region"], req_body["name"])
                res = keys
                j["res"] = keys
                if isinstance(res, list):
                    return jsonify(j)
                else:
                    return jsonify(j), status.HTTP_400_BAD_REQUEST
            except:
                j['res'] = "Error adding connection"
                return jsonify(j), status.HTTP_400_BAD_REQUEST
        else:
            j['res'] = "Only s3 connections supported"
            return jsonify(j), status.HTTP_400_BAD_REQUEST
    except:
        j['res'] = "Error adding connection"
        return jsonify(j), status.HTTP_400_BAD_REQUEST

@app.route('/view_connection', methods=['GET'])
@cross_origin()
def view_connection():
    j = dict()
    j['res'] = connectionHandler.view_all_s3_connections()
    return jsonify(j)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='<config file>', type=str, required=True)
    args = parser.parse_args()
    config_file = args.config
    config = Config(config_file)
    connectionHandler = ConnectionHandler(config)
    es_client = ES_Client(config)
    setup = Setup(config)
    sql_client = SQLClient(config)
    sql_client.insert_csv_to_db("bbc")
    #sql_client.fetch_some_rows(5)
    setup.populate_index_from_mysql()
    app.run(host='0.0.0.0', port=80)
