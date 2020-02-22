from client.s3_client import S3Client
from client.sql_client import SQLClient
from config.config import Config


class ConnectionHandler:

    def __init__(self, config: Config):
        self.sql_client = SQLClient(config)

    def add_s3_connection_to_db(self,aws_access_key_id, aws_secret_access_key, bucket, region, name):
        self.sql_client.insert_into_s3_connections(name, aws_access_key_id, aws_secret_access_key, bucket, region)

    def add_s3_connection(self, aws_access_key_id, aws_secret_access_key, bucket, region, name):
        try:
            s3_client = S3Client(aws_access_key_id, aws_secret_access_key, bucket, region)
            keys = s3_client.get_s3_keys(bucket)
            if not isinstance(keys, str) :
                self.add_s3_connection_to_db(aws_access_key_id, aws_secret_access_key, bucket, region, name)
                if len(keys) > 0:
                    return keys
                else:
                    return "No files in bucket"
            else:
                return keys
        except:
            return "Connection failed"

    def view_all_s3_connections(self):
        j = dict()
        j['res'] = dict()
        records = self.sql_client.fetch_all_s3_connections()
        for record in records:
            sub = dict()
            sub['name'] = record[1]
            sub['acess_key_id'] = record[2]
            sub["access_key"] = record[3]
            sub["bucket"] = record[4]
            sub["region"] = record[5]
            j['res'][record[0]] = sub
        return j

