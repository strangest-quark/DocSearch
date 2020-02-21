import csv

from config.config import Config
import mysql.connector


class SQLClient:

    def __init__(self, config: Config):
        self.select_rows_query = "SELECT * FROM bbc"
        db_config = {
            'user': config.mysql_username,
            'password': config.mysql_password,
            'host': config.mysql_host,
            'port': config.mysql_port,
            'database': config.mysql_db_name
        }
        self.mydb = mysql.connector.connect(**db_config)
        self.csv_filename = config.mysql_csv_filename
        cursor = self.mydb.cursor()
        self.mydb.commit()
        cursor.close()

    def fetch_all(self):
        cursor = self.mydb.cursor()
        cursor.execute(self.select_rows_query)
        records = cursor.fetchall()
        cursor.close()
        return records

    def insert_csv_to_db(self, table_name):
            cursor = self.mydb.cursor()
            with open(self.csv_filename, newline='') as csvfile:
                csv_data = csv.reader(csvfile, delimiter=",")
                next(csv_data)
                for row in csv_data:
                    print("row: "+ str(row))
                    try:
                        cursor.execute('INSERT INTO ' + table_name + '(id, content, tags) VALUES("%s", "%s", "%s")', (int(row[0]), row[1], str(row[2])))
                    except:
                        print("Insert for id: "+str(row[0])+" failed")
            self.mydb.commit()
            cursor.close()
            print("Csv to mysql db data insertion done")

    def fetch_some_rows(self, rowCount):
        cursor = self.mydb.cursor()
        cursor.execute(self.select_rows_query)
        records = cursor.fetchmany(size=rowCount)
        for row in records:
            print("Id: ", row[0])
            print("Content: ", row[1])
            print("Tags: ", row[2])
            print("\n")
        return records
