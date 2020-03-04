import csv

from config.config import Config
import mysql.connector


class SQLClient:

    def __init__(self, config: Config):
        self.select_s3_rows_query = "SELECT * FROM s3_connections"
        self.select_bbc_rows_query = "SELECT * FROM bbc"
        self.select_s3_connection_row = "SELECT * FROM s3_connections WHERE name=%s"
        self.user = config.mysql_username
        self.password = config.mysql_password
        self.port = config.mysql_port
        self.host = config.mysql_host
        self.database  = config.mysql_db_name
        self.csv_filename = config.mysql_csv_filename
        self.mydb = None

    def setup(self):
        db_config = {
            'user': self.user,
            'password': self.password,
            'host': self.host,
            'port': self.port,
            'database': self.db_name
        }
        self.mydb = mysql.connector.connect(**db_config)
        cursor = self.mydb.cursor()
        self.mydb.commit()
        cursor.close()

    def fetch_all_s3_connections(self):
        if self.mydb is None:
            self.setup()
        cursor = self.mydb.cursor()
        cursor.execute(self.select_s3_rows_query)
        records = cursor.fetchall()
        cursor.close()
        return records

    def fetch_all_bbc(self):
        if self.mydb is None:
            self.setup()
        cursor = self.mydb.cursor()
        cursor.execute(self.select_bbc_rows_query)
        records = cursor.fetchall()
        cursor.close()
        return records

    def fetch_connection(self, name):
        if self.mydb is None:
            self.setup()
        cursor = self.mydb.cursor()
        print('SELECT * FROM s3_connections WHERE name="'+name+'"')
        cursor.execute('SELECT * FROM s3_connections WHERE name="'+name+'"')
        records = cursor.fetchall()
        cursor.close()
        return records

    def insert_into_s3_connections(self, name, access_key_id, access_key, bucket, region):
        if self.mydb is None:
            self.setup()
        cursor = self.mydb.cursor()
        try:
            query = 'INSERT INTO s3_connections(name, access_key_id, access_key, bucket, region) VALUES("'+name+'", "'+access_key_id+'", "'+access_key+'", "'+bucket+'", "'+region+'")'
            print(query)
            cursor.execute(query)
        except:
            return "Storing this connection failed"
        return 200

    def insert_csv_to_db(self, table_name):
        if self.mydb is None:
            self.setup()
        cursor = self.mydb.cursor()
        with open(self.csv_filename, newline='') as csvfile:
            csv_data = csv.reader(csvfile, delimiter=",")
            next(csv_data)
            for row in csv_data:
                try:
                    cursor.execute('INSERT INTO ' + table_name + '(id, content, tags) VALUES("%s", "%s", "%s")',
                                   (int(row[0]), row[1], str(row[2])))
                    print("row " + str(row[0]) + " inserted")
                except:
                    print("Insert for id: " + str(row[0]) + " failed")
        self.mydb.commit()
        cursor.close()
        print("Csv to mysql db data insertion done")

    def fetch_some_rows(self, rowCount):
        if self.mydb is None:
            self.setup()s
        cursor = self.mydb.cursor()
        cursor.execute(self.select_rows_query)
        records = cursor.fetchmany(size=rowCount)
        for row in records:
            print("Id: ", row[0])
            print("Content: ", row[1])
            print("Tags: ", row[2])
            print("\n")
        return records
