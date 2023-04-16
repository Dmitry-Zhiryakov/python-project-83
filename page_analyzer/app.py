import os
import requests
from page_analyzer import urls_repo
from page_analyzer.validator import validate_url, normalize_url
from bs4 import BeautifulSoup
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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def get_urls():
    urls = urls_repo.get_all_urls()
    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form['url']

    errors = validate_url(url)
    if errors:
        return render_template(
            'index.html',
            messages=errors,
            url=url
        ), 422

    normalized_url = normalize_url(url)
    found_url = urls_repo.get_url_by_name(normalized_url)

    if found_url:
        id = found_url.id
        flash('Страница уже существует', 'info')
    else:
        id = urls_repo.add_url(normalized_url)
        flash('Страница успешно добавлена', 'success')

    return redirect(url_for('show_url', id=id,))


@app.route('/urls/<int:id>', methods=['GET'])
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = urls_repo.get_url_by_id(id)
    checks = urls_repo.get_checks_by_id(id)
    return render_template(
        'url.html',
        messages=messages,
        url=url,
        checks=checks
    )


def get_page_content(page):
    soup = BeautifulSoup(page, 'html.parser')

    h1 = soup.find('h1').get_text() if soup.find('h1') else ''
    title = soup.find('title').get_text() if soup.find('title') else ''
    find_description = soup.find('meta', attrs={'name': 'description'})
    if find_description:
        description = find_description.get('content', '')
    else:
        description = ''

    return {
        'h1': h1[:255],
        'title': title[:255],
        'description': description[:255]
    }


@app.route('/urls/<id>/checks', methods=['POST'])
def add_check_url(id):
    url = urls_repo.get_url_by_id(id)

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
    urls_repo.add_url_check(check_result)
    flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url', id=id))
