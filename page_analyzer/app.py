import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request
from datetime import datetime

from page_analyzer.validator import validate


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template(
        'show.html'
    )


@app.route('/urls', methods=['GET', 'POST'])
def add_url():
    url = request.form['url']

    errors = validate(url)
    if errors:
        return render_template(
            'show.html',
            errors=errors,
            url=url
        )

    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as curs:
        curs.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                     (url, datetime.today().replace(microsecond=0)))
    conn.commit()
    conn.close()
    return render_template('show.html')
