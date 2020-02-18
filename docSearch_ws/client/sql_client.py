import csv
import pymysql

from docSearch_ws.config.config import Config


class SQLClient:

    def __init__(self, config: Config):
        self.create_table_query = "CREATE TABLE bbc(id INT(6) UNSIGNED PRIMARY KEY, content TEXT NOT NULL, tags TEXT NOT NULL)"

        self.select_rows_query = "SELECT * FROM bbc"
        self.mydb = pymysql.connect(host=config.mysql_host,
                                    user=config.mysql_username,
                                    passwd=config.mysql_password,
                                    db=config.mysql_db_name,
                                    port=config.mysql_port)
        self.csv_filename = config.mysql_csv_filename
        cursor = self.mydb.cursor()
        #cursor.execute(self.create_table_query)
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
                cursor.execute('INSERT INTO ' + table_name + '(id, content, tags) VALUES("%s", "%s", "%s")', (int(row[0]), row[1], str(row[2])))
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
        cursor.close()
        return records
