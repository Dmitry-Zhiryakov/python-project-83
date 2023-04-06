import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor
from datetime import date


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class UrlsRepo(Database):
    def get_by_id(self, id):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE id = %s', (id,))
            return curs.fetchone()

    def find_all(self):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''SELECT * FROM urls
            LEFT JOIN (SELECT id AS check_id, url_id, created_at
            AS last_check FROM url_checks
            WHERE id IN (SELECT MAX(id) FROM url_checks GROUP BY url_id))
            AS last_checks ON urls.id = last_checks.url_id
            ORDER BY id DESC;''')
            return curs.fetchall()


class UrlChecksRepo(Database):
    def add_check(self, url_id):
        with self.conn.cursor() as curs:
            curs.execute('''INSERT INTO url_checks (url_id, created_at)
                         VALUES (%s, %s);''', (url_id, date.today(),))
            self.commit()

    def get_checks(self, id):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''SELECT * FROM url_checks WHERE url_id = %s
                         ORDER BY id DESC;''', (id,))
            return curs.fetchall()
