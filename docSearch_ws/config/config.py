import os
import yaml


class Config:

    def __init__(self, environment_file=None):
        if environment_file:
            with open(environment_file) as env_file:
                self.env_list = yaml.load(env_file)
        self.__configure_elasticsearch()
        self.__configure_mysql()

    def __configure_elasticsearch(self):
        self.es_host = os.getenv('HOST', self.env_list['ES']['HOST'])
        self.es_port = os.getenv('PORT', self.env_list['ES']['PORT'])
        self.es_index = os.getenv('INDEX', self.env_list['ES']['INDEX'])

    def __configure_mysql(self):
        self.mysql_username = os.getenv('USERNAME', self.env_list['MYSQL']['USERNAME'])
        self.mysql_password = os.getenv('PASSWORD', self.env_list['MYSQL']['PASSWORD'])
        self.mysql_db_name = os.getenv('DB_NAME', self.env_list['MYSQL']['DB_NAME'])
        self.mysql_host = os.getenv('HOST', self.env_list['MYSQL']['HOST'])
        self.mysql_port = os.getenv('PORT', self.env_list['MYSQL']['PORT'])
        self.mysql_csv_filename = os.getenv('HOST', self.env_list['MYSQL']['CSV_FILENAME'])

