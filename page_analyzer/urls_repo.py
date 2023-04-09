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
    def add_url(self, name):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                '''INSERT INTO urls (name, created_at)
                VALUES (%s, %s) RETURNING id;''', (name, date.today())
            )
            id = curs.fetchone().id
            self.commit()
            return id

    def get_by_id(self, id):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE id = %s', (id,))
            return curs.fetchone()

    def get_by_name(self, name):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE name = %s', (name,))
            return curs.fetchone()

    def find_all(self):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                '''SELECT * FROM urls LEFT JOIN
                (SELECT id AS check_id, url_id, status_code, created_at
                AS last_check FROM url_checks
                WHERE id IN (SELECT MAX(id) FROM url_checks GROUP BY url_id))
                AS last_checks ON urls.id = last_checks.url_id
                ORDER BY id DESC;'''
            )
            return curs.fetchall()


class UrlChecksRepo(Database):
    def add_check(self, check_result):
        with self.conn.cursor() as curs:
            curs.execute(
                '''INSERT INTO url_checks
                (url_id, status_code, h1,title, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s);''',
                (check_result['url_id'], check_result['status_code'],
                 check_result['h1'], check_result['title'],
                 check_result['description'], date.today(),)
            )
            self.commit()

    def get_checks(self, id):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                '''SELECT * FROM url_checks WHERE url_id = %s
                ORDER BY id DESC;''', (id,))
            return curs.fetchall()
