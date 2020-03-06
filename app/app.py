from typing import List, Dict
from flask import Flask
from flask import request
from flask import jsonify
import mysql.connector
from client.elastic_search_client import ES_Client
from client.s3_client import S3Client
from client.sql_client import SQLClient
from config.config import Config
from config.setup import Setup
from handlers.connections_handler import ConnectionHandler
from handlers.graph_handler import GraphHandler
import json
import argparse
from flask_cors import CORS, cross_origin
from flask_api import status
import time
from handlers.file_processor import S3FileProcessor

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

config = None
setup = None
es_client = None
sql_client = None
connectionHandler = None
graph_handler = None


@app.route('/')
@cross_origin()
def hello_world():
    return 'DocSearch is running!'

@app.route('/search_zero', methods=['POST'])
@cross_origin()
def search_zero():
    setup()
    req_body = request.get_json()
    conn = req_body["connection"].replace(" ", "").lower()
    es_client.set_index(conn)
    j = dict()
    res = es_client.match_all()
    j['res'] = res
    return jsonify(j)

# /search_tag
@app.route('/search_tag', methods=['POST'])
@cross_origin()
def tag_search():
    setup()
    req_body = request.get_json()
    tag = req_body["tag"]
    conn = req_body["connection"].replace(" ", "").lower()
    es_client.set_index(conn)
    j = dict()
    res = es_client.tag_search(tag)
    j['res'] = res[0]
    j['semantic_res'] = res[1]
    return jsonify(j)


# /search_full_text
@app.route('/search_full_text', methods=['POST'])
@cross_origin()
def search_full_text():
    setup()
    req_body = request.get_json()
    full_text = req_body["txt"]
    conn = req_body["connection"].replace(" ", "").lower()
    es_client.set_index(conn)
    j = dict()
    res = es_client.full_text_search(full_text)
    j['res'] = res[0]
    j['semantic_res'] = res[1]
    return jsonify(j)


# /search_content_and_tag
@app.route('/search_content_and_tag', methods=['POST'])
@cross_origin()
def search_content_and_tag():
    setup()
    req_body = request.get_json()
    full_text = req_body["txt"]
    tag = req_body["tag"]
    conn = req_body["connection"].replace(" ", "").lower()
    es_client.set_index(conn)
    j = dict()
    res = es_client.text_and_tag_search(full_text, tag)
    j['res'] = res[0]
    j['semantic_res'] = res[1]
    return jsonify(j)


@app.route('/add_connection', methods=['POST'])
@cross_origin()
def add_connection():
    setup()
    req_body = request.get_json()
    j = dict()
    try:
        if req_body['connection_type'] == "s3":
            try:
                keys = connectionHandler.add_s3_connection(req_body["access_key_id"], req_body["access_key"],
                                                           req_body["bucket"], req_body["region"], req_body["name"])
                res = keys
                j["res"] = keys
                if isinstance(res, list):
                    try:
                       p=_process_files(req_body["name"])
                    except:
                       p="processing failed"
                    j["processed"] = p
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
        j['res'] = "Error in adding connection"
        return jsonify(j), status.HTTP_400_BAD_REQUEST


@app.route('/view_connection', methods=['GET'])
@cross_origin()
def view_connection():
    setup()
    j = dict()
    j['res'] = connectionHandler.view_all_s3_connections()
    return jsonify(j)

def _process_files(connection_name):
    setup()
    records = connectionHandler.get_s3_connection(connection_name)
    s3FileProcessor = S3FileProcessor(config,
                                      records[0][1],
                                      records[0][2],
                                      records[0][3],
                                      records[0][4],
                                      records[0][0])
    s3FileProcessor.read_bucket()
    return "processed"


@app.route('/process_files', methods=['POST'])
@cross_origin()
def process_files():
    setup()
    req_body = request.get_json()
    connection_name = req_body["name"]
    records = connectionHandler.get_s3_connection(connection_name)
    s3FileProcessor = S3FileProcessor(config,
                                      records[0][1],
                                      records[0][2],
                                      records[0][3],
                                      records[0][4],
                                      records[0][0])
    s3FileProcessor.read_bucket()
    j = dict()
    j['res'] = "Processed"
    return jsonify(j)


@app.route('/view_file', methods=['POST'])
@cross_origin()
def view_file():
    setup()
    req_body = request.get_json()
    connection_name = req_body["name"]
    file_name = req_body["file_name"]
    records = connectionHandler.get_s3_connection(connection_name)
    s3Client = S3Client(records[0][1],
                        records[0][2],
                        records[0][3],
                        records[0][4])
    j = dict()
    res = s3Client.get_presigned_url(file_name)
    if res != 404:
        j["res"] = res
        return jsonify(j)
    else:
        j['res'] = "File not found"
        return jsonify(j)


@app.route('/view_files', methods=['POST'])
@cross_origin()
def view_files():
    setup()
    req_body = request.get_json()
    connection_name = req_body["name"]
    records = connectionHandler.get_s3_connection(connection_name)
    j = dict()
    res = connectionHandler.view_s3_connection(records[0][1], records[0][2], records[0][3], records[0][4])
    if isinstance(res, list):
        j['res'] = res
        return jsonify(j)
    else:
        return jsonify(j), status.HTTP_400_BAD_REQUEST


@app.route('/add_tag', methods=['POST'])
@cross_origin()
def add_tag():
    setup()
    j = dict()
    req_body = request.get_json()
    file_key = req_body["file"]
    tag = req_body["tag"]
    connection_name = req_body["conn_name"]
    try:
        res = es_client.get_es(file_key, connection_name)
        print(res)
    except:
        j["res"] = "Error in file get"
        return jsonify(j), status.HTTP_400_BAD_REQUEST
    existing_tags = res["_source"]["tags"]
    if existing_tags != "":
        tag = ',' + tag
    body = {
        'doc': {
            'tags': existing_tags + tag
        }
    }
    try:
        es_client.update_es(file_key, body, connection_name)
        j["res"] = "Tag added"
        return jsonify(j)
    except:
        j["res"] = "Tag not added"
        return jsonify(j), status.HTTP_400_BAD_REQUEST


@app.route('/delete_tag', methods=['POST'])
@cross_origin()
def delete_tag():
    setup()
    j = dict()
    req_body = request.get_json()
    file_key = req_body["file"]
    tag = req_body["tag"]
    connection_name = req_body["conn_name"]
    try:
        res = es_client.get_es(file_key, connection_name)
        print(res)
    except:
        j["res"] = "Error in file get"
        return jsonify(j), status.HTTP_400_BAD_REQUEST
    existing_tags = res["_source"]["tags"]
    if existing_tags == "":
        j["res"] = "No tags to delete"
        return jsonify(j)
    if ',' + tag in existing_tags:
        existing_tags = existing_tags.replace(',' + tag, '')
    elif tag in existing_tags:
        existing_tags = existing_tags.replace(tag, '')
    else:
        j["res"] = "Tag not found"
        return jsonify(j), status.HTTP_400_BAD_REQUEST
    body = {
        'doc': {
            'tags': existing_tags
        }
    }
    try:
        es_client.update_es(file_key, body, connection_name)
        j["res"] = "Tag deleted"
        return jsonify(j)
    except:
        j["res"] = "Tag not deleted"
        return jsonify(j), status.HTTP_400_BAD_REQUEST


@app.route('/fetch_tags', methods=['POST'])
@cross_origin()
def fetch_tags():
    setup()
    req_body = request.get_json()
    j = dict()
    res = sql_client.fetch_tags(req_body['name'])
    tag_string = res[0][1]
    j['res'] = tag_string.split()
    return jsonify(j)


@app.route('/delete_automated_tag', methods=['POST'])
@cross_origin()
def delete_automated_tag():
    setup()
    j = dict()
    req_body = request.get_json()
    file_key = req_body["file"]
    tag = req_body["tag"]
    connection_name = req_body["conn_name"]
    try:
        res = es_client.get_es(file_key, connection_name)
        print(res)
    except:
        j["res"] = "Error in file get"
        return jsonify(j), status.HTTP_400_BAD_REQUEST
    existing_tags = res["_source"]["automated_tags"]
    if existing_tags == "":
        j["res"] = "No tags to delete"
        return jsonify(j)
    if ',' + tag in existing_tags:
        existing_tags = existing_tags.replace(',' + tag, '')
    elif tag in existing_tags:
        existing_tags = existing_tags.replace(tag, '')
    else:
        j["res"] = "Automated Tag not found"
        return jsonify(j), status.HTTP_400_BAD_REQUEST
    body = {
        'doc': {
            'automated_tags': existing_tags
        }
    }
    try:
        es_client.update_es(file_key, body, connection_name)
        j["res"] = "Tag deleted"
        return jsonify(j)
    except:
        j["res"] = "Tag not deleted"
        return jsonify(j), status.HTTP_400_BAD_REQUEST


@app.route('/get_graph', methods=['POST'])
@cross_origin()
def get_graph():
    setup()
    j = dict()
    req_body = request.get_json()
    connection_name = req_body["conn_name"]
    return jsonify(graph_handler.entry(connection_name))


def setup():
    global connectionHandler
    global es_client
    global sql_client
    global graph_handler
    global config
    config = Config('./config/local.yaml')
    connectionHandler = ConnectionHandler(config)
    es_client = ES_Client(config)
    sql_client = SQLClient(config)
    graph_handler = GraphHandler(config)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
