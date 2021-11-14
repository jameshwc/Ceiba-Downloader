import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from pathlib import Path
from util import get_valid_filename


class Crawler():

    def __init__(self, session: requests.Session, url: str, path: str, filename: str):
        self.session = session
        self.url = url
        self.path = path
        self.filename = get_valid_filename(filename)

    def crawl(self, is_table=False, urls=None):
        response = self.session.get(self.url)
        if response.headers['content-type'] != 'text/html':
            path = Path(os.path.join(self.path, self.filename))  # TODO: check if filename exists
            path.write_bytes(response.content)
            return
        soup = BeautifulSoup(response.content, 'html.parser')
        for css in soup.find_all('link'):
            url = urljoin(self.url, css.get('href'))
            css['href'] = url.split('/')[-1]
            c = Crawler(self.session, url, self.path, css['href'])
            c.crawl()

        for a in soup.find_all('a'):
            if len(a.text) > 0:
                if not a['href'].startswith('http'):
                    url = urljoin(self.url, a.get('href'))
                    a['href'] = get_valid_filename(url.split('/')[-1])
                    c = Crawler(self.session, url, self.path, a['href'])
                    c.crawl()
        with open(os.path.join(self.path, self.filename), 'w', encoding='utf-8') as html:
            html.write(str(soup))
