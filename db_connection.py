import pymysql

from config import Config


class Database:
    def __init__(self, user, password, host, port):
        """ Initialize the connection and create the cursor object """
        self._conn = pymysql.connect(user=user, password=password, host=host, port=port)
        self._cursor = self._conn.cursor()

    @property
    def cursor(self):
        """ Return the cursor object """
        return self._cursor

    def execute_query(self, query):
        """ Execute the query """
        self.cursor.execute(query)
        self._conn.commit()

    def fetchall(self, query):
        """ Execute the query and fetch all data """
        self.execute_query(query=query)
        return self.cursor.fetchall()


db = Database(user=Config.DATABASE_USER, password=Config.DATABASE_PASS, host=Config.DATABASE_READ_HOST,
              port=Config.DATABASE_PORT)
