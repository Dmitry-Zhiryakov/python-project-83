import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor
from datetime import date


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class UrlsRepo:
    @staticmethod
    def add_url(name):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(
                    '''INSERT INTO urls (name, created_at)
                    VALUES (%s, %s) RETURNING id;''', (name, date.today())
                )
                id = curs.fetchone().id
                conn.commit()
                return id

    @staticmethod
    def get_by_id(id):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute('SELECT * FROM urls WHERE id = %s', (id,))
                return curs.fetchone()

    @staticmethod
    def get_by_name(name):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute('SELECT * FROM urls WHERE name = %s', (name,))
                return curs.fetchone()

    @staticmethod
    def find_all():
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(
                    '''SELECT * FROM urls LEFT JOIN
                    (SELECT id AS check_id, url_id, status_code, created_at
                    AS last_check FROM url_checks WHERE id IN
                    (SELECT MAX(id) FROM url_checks GROUP BY url_id))
                    AS last_checks ON urls.id = last_checks.url_id
                    ORDER BY id DESC;'''
                )
                return curs.fetchall()


class UrlChecksRepo:
    @staticmethod
    def add_url_check(check_result):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    '''INSERT INTO url_checks
                    (url_id, status_code, h1,title, description, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s);''',
                    (check_result['url_id'], check_result['status_code'],
                     check_result['h1'], check_result['title'],
                     check_result['description'], date.today(),)
                )
                conn.commit()

    @staticmethod
    def get_checks_by_id(id):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(
                    '''SELECT * FROM url_checks WHERE url_id = %s
                    ORDER BY id DESC;''', (id,))
                return curs.fetchall()
