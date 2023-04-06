import os
import psycopg2
from psycopg2.extras import NamedTupleCursor
from dotenv import load_dotenv
from datetime import date
from page_analyzer.validator import validate, normalize
from page_analyzer.urls_repo import UrlsRepo, UrlChecksRepo
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)


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
def get_urls():
    urls_repo = UrlsRepo()
    urls = urls_repo.find_all()
    urls_repo.close()
    return render_template('urls.html',
                           urls=urls)


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

    normalized_url = normalize(url)
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT id, name FROM urls WHERE name = %s',
                     (normalized_url,)
                     )
        found_url = curs.fetchone()
        if found_url:
            id = found_url.id
            flash('Страница уже существует', 'info')
        else:
            curs.execute(
                '''INSERT INTO urls (name, created_at)
                VALUES (%s, %s) RETURNING id;''',
                (normalized_url, date.today())
            )
            data = curs.fetchone()
            conn.commit()
            id = data.id
            flash('Страница успешно добавлена', 'success')
    conn.close()
    return redirect(url_for('show_url', id=id, ))


@app.route('/urls/<int:id>', methods=['GET'])
def show_url(id):
    messages = get_flashed_messages(with_categories=True)

    urls_repo = UrlsRepo()
    url = urls_repo.get_by_id(id)
    urls_repo.close()

    url_checks_repo = UrlChecksRepo()
    checks = url_checks_repo.get_checks(id)
    url_checks_repo.close()

    return render_template('url.html',
                           messages=messages,
                           url=url,
                           checks=checks
                           )


@app.route('/urls/<id>/checks', methods=['POST'])
def add_check(id):
    url_checks_repo = UrlChecksRepo()
    url_checks_repo.add_check(id)
    url_checks_repo.close()
    return redirect(url_for('show_url', id=id))
