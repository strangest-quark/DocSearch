from client.s3_client import S3Client
from client.sql_client import SQLClient
from config.config import Config


class ConnectionHandler:

    def __init__(self, config: Config):
        self.sql_client = SQLClient(config)

    def add_s3_connection_to_db(self,aws_access_key_id, aws_secret_access_key, bucket, region, name):
        return self.sql_client.insert_into_s3_connections(name, aws_access_key_id, aws_secret_access_key, bucket, region)

    def add_s3_connection(self, aws_access_key_id, aws_secret_access_key, bucket, region, name):
        try:
            s3_client = S3Client(aws_access_key_id, aws_secret_access_key, bucket, region)
            keys = s3_client.get_s3_keys(bucket)
            if not isinstance(keys, str) :
                code = self.add_s3_connection_to_db(aws_access_key_id, aws_secret_access_key, bucket, region, name)
                if code != 200:
                    return "Aborting connection add"
                if len(keys) > 0:
                    return keys
                else:
                    return "No files in bucket"
            else:
                return keys
        except:
            return "Connection failed"

    def view_s3_connection(self, aws_access_key_id, aws_secret_access_key, bucket, region):
        try:
            s3_client = S3Client(aws_access_key_id, aws_secret_access_key, bucket, region)
            keys = s3_client.get_s3_keys(bucket)
            if not isinstance(keys, str) :
                if len(keys) > 0:
                    return keys
                else:
                    return "No files in bucket"
            else:
                return keys
        except:
            return "Connection failed"

    def view_all_s3_connections(self):
        j = []
        records = self.sql_client.fetch_all_s3_connections()
        for record in records:
            sub = dict()
            sub['name'] = record[0].replace("'","")
            sub['acess_key_id'] = record[1].replace("'","")
            sub["access_key"] = record[2].replace("'","")
            sub["bucket"] = record[3].replace("'","")
            sub["region"] = record[4].replace("'","")
            j.append(sub)
        return j

    def get_s3_connection(self, name):
        return self.sql_client.fetch_connection(name)

