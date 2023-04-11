import os
import requests
from page_analyzer.urls_repo import UrlsRepo, UrlChecksRepo
from page_analyzer.validator import validate, normalize
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
    urls_repo = UrlsRepo()
    urls = urls_repo.find_all()
    urls_repo.close()
    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form['url']

    errors = validate(url)
    if errors:
        return render_template(
            'index.html',
            errors=errors,
            url=url
        ), 422

    normalized_url = normalize(url)
    urls_repo = UrlsRepo()
    found_url = urls_repo.get_by_name(normalized_url)

    if found_url:
        id = found_url.id
        flash('Страница уже существует', 'info')
    else:
        id = urls_repo.add_url(normalized_url)
        flash('Страница успешно добавлена', 'success')

    urls_repo.close()
    return redirect(url_for('show_url', id=id,))


@app.route('/urls/<int:id>', methods=['GET'])
def show_url(id):
    messages = get_flashed_messages(with_categories=True)

    urls_repo = UrlsRepo()
    url = urls_repo.get_by_id(id)
    urls_repo.close()

    url_checks_repo = UrlChecksRepo()
    checks = url_checks_repo.get_checks(id)
    url_checks_repo.close()

    return render_template(
        'url.html',
        messages=messages,
        url=url,
        checks=checks
    )


def get_check_result(page):
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
def add_check(id):
    urls_repo = UrlsRepo()
    url = urls_repo.get_by_id(id)
    urls_repo.close()

    try:
        response = requests.get(url.name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))

    url_checks_repo = UrlChecksRepo()
    page = response.text
    check_result = {
        'url_id': id,
        'status_code': response.status_code,
        **get_check_result(page)
    }
    url_checks_repo.add_check(check_result)
    url_checks_repo.close()
    flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url', id=id))
