import os
import psycopg2
from psycopg2.extras import NamedTupleCursor
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from datetime import date
from page_analyzer.validator import validate


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template(
        'index.html'
    )


@app.get('/urls')
def urls_get():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT id, name FROM urls ORDER BY created_at DESC;')
        urls = curs.fetchall()
        return render_template('urls.html',
                               urls=urls
                               )


@app.post('/urls')
def add_url():
    url = request.form['url']

    errors = validate(url)
    if errors:
        return render_template(
            'index.html',
            errors=errors,
            url=url
        )

    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;',
                     (url, date.today()))
        data = curs.fetchone()
        conn.commit()
    conn.close()
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=data.id, ))


@app.route('/urls/<int:id>', methods=['GET'])
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT * FROM urls WHERE id = %s;', (id,))
        url = curs.fetchone()
        return render_template('url.html',
                               url=url,
                               messages=messages
                               )
