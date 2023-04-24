from psycopg2.extras import NamedTupleCursor
from datetime import date


def add_url(conn, name):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            '''INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id;''', (name, date.today())
        )
        id = curs.fetchone().id
        return id


def get_url_by_id(conn, id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT * FROM urls WHERE id = %s', (id,))
        return curs.fetchone()


def get_url_by_name(conn, name):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT * FROM urls WHERE name = %s', (name,))
        return curs.fetchone()


def get_all_urls(conn):
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


def add_url_check(conn, check_result):
    with conn.cursor() as curs:
        curs.execute(
            '''INSERT INTO url_checks
            (url_id, status_code, h1,title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);''',
            (check_result['url_id'], check_result['status_code'],
             check_result['h1'], check_result['title'],
             check_result['description'], date.today(),)
        )


def get_checks_by_id(conn, id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            '''SELECT * FROM url_checks WHERE url_id = %s
            ORDER BY id DESC;''', (id,))
        return curs.fetchall()
