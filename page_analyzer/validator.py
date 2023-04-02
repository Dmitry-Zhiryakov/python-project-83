from validators.url import url as validator_url


def validate(url):
    errors = []
    if len(url) > 255:
        errors.append('URL превышает 255 символов')
    if not validator_url(url):
        errors.append('Некорректный URL')
    if not url:
        errors.append('URL обязателен')
    return errors
