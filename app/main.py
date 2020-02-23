from client.s3_client import S3Client
from util.pdf_util import PDFUtil
from io import BytesIO
import argparse
from config.config import Config
from handlers.file_processor import S3FileProcessor

from client.sql_client import SQLClient

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='<config file>', type=str, required=True)
    args = parser.parse_args()
    config_file = args.config
    config = Config(config_file)
    sql_client = SQLClient(config)
    records = sql_client.fetch_connection("ikram")
    print(records)
    #records = sql_client.fetch_all_s3_connections()
    #print(records)
    s3FileProcessor = S3FileProcessor(config,
                                      records[0][2],
                                      records[0][3],
                                      records[0][4],
                                      records[0][5],
                                      records[0][1])
    s3FileProcessor.read_bucket()
    j = dict()
    j['res'] = "Processed"