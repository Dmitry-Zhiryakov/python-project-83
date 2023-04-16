from validators.url import url as validator_url
from urllib.parse import urlparse


URL_LENGTH = 255


def validate_url(url):
    errors = []
    if len(url) > URL_LENGTH:
        errors.append(('danger', f"URL превышает {URL_LENGTH} символов"))
    if not validator_url(url):
        errors.append(('danger', 'Некорректный URL'))
    if not url:
        errors.append(('danger', 'URL обязателен'))
    return errors


def normalize_url(url):
    components = urlparse(url)
    return f"{components.scheme}://{components.netloc}"
