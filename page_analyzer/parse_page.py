from bs4 import BeautifulSoup


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
