import boto3
from botocore.client import Config


class S3Client:

    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket, region):
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.s3_client = self.session.client('s3', region_name=region,
                                             config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4'))
        self.s3_resource = self.session.resource('s3')
        self.bucket = self.s3_resource.Bucket(bucket)

    def get_s3_keys(self, bucket):
        """Get a list of keys in an S3 bucket."""
        self.bucket = self.s3_resource.Bucket(bucket)
        keys = []
        try:
            for key in self.bucket.objects.all():
                keys.append(key.key)
        except Exception as e:
            return str(e)
        return keys

    def get_presigned_url(self, key):
        return self.s3_client.generate_presigned_url('get_object', Params={'Bucket': self.bucket, 'Key': key})

    def get_s3_file_body(self, bucket, key):
        return bucket.Object(key).get()['Body'].read()
