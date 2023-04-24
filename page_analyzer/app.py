import os
from dotenv import load_dotenv
import psycopg2
import requests
from page_analyzer import urls_repo
from page_analyzer.validator import validate_url, normalize_url
from page_analyzer.parse_page import get_page_content
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


def open_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def get_urls():
    conn = open_connection()
    urls = urls_repo.get_all_urls(conn)
    conn.close()
    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def add_url():
    conn = open_connection()
    url = request.form['url']

    errors = validate_url(url)
    if errors:
        return render_template(
            'index.html',
            messages=errors,
            url=url
        ), 422

    normalized_url = normalize_url(url)
    found_url = urls_repo.get_url_by_name(conn, normalized_url)

    if found_url:
        id = found_url.id
        flash('Страница уже существует', 'info')
    else:
        id = urls_repo.add_url(conn, normalized_url)
        conn.commit()
        flash('Страница успешно добавлена', 'success')

    conn.close()
    return redirect(url_for('show_url', id=id,))


@app.route('/urls/<int:id>', methods=['GET'])
def show_url(id):
    conn = open_connection()
    messages = get_flashed_messages(with_categories=True)
    url = urls_repo.get_url_by_id(conn, id)
    checks = urls_repo.get_checks_by_id(conn, id)
    conn.close()
    return render_template(
        'url.html',
        messages=messages,
        url=url,
        checks=checks
    )


@app.route('/urls/<id>/checks', methods=['POST'])
def add_check_url(id):
    conn = open_connection()
    url = urls_repo.get_url_by_id(conn, id)

    try:
        response = requests.get(url.name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))

    page = response.text
    check_result = {
        'url_id': id,
        'status_code': response.status_code,
        **get_page_content(page)
    }
    urls_repo.add_url_check(conn, check_result)
    conn.commit()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id))
