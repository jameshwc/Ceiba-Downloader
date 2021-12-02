import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from pathlib import Path
from util import get_valid_filename
from tqdm import tqdm


class Crawler():

    def __init__(self, session: requests.Session, url: str, path: str, filename: str, text: str = ""):
        self.session = session
        self.url = url
        self.path = path
        self.filename = get_valid_filename(filename)
        self.text = text

    def crawl(self, is_table=False, obj=None, urls=None, static=False) -> bool:
        '''
        Return True if the url is file, and return False if the url is html.
        '''
        response = self.session.get(self.url)
        if response.headers['content-type'] != 'text/html':
            if self.filename.endswith('.html'):
                self.filename = self.filename.removesuffix('.html')
            if static:
                path = Path(os.path.join(self.path, self.filename))  # TODO: check if filename exists
            else:
                path = Path(os.path.join(os.path.join(self.path, "files"), self.filename))
            path.write_bytes(response.content)
            return True
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if is_table:
            os.makedirs(os.path.join(self.path, "files"), exist_ok=True)
        
        for css in soup.find_all('link'):
            url = urljoin(self.url, css.get('href'))
            css['href'] = url.split('/')[-1]
            
            c = Crawler(self.session, url, self.path, css['href'])
            c.crawl(static=True)

        for img in soup.find_all('img'):
            url = urljoin(self.url, img.get('src'))
            img['src'] = url.split('/')[-1]
            c = Crawler(self.session, url, self.path, img['src'])
            c.crawl(static=True)
        
        hrefs = tqdm(soup.find_all('a')) if is_table else soup.find_all('a')
        for a in hrefs:
            if len(a.text) > 0 and a.text not in ['作業列表']:
                if not a['href'].startswith('http') or a['href'].startswith('https://ceiba.ntu.edu.tw'):
                    url = urljoin(urljoin(self.url, obj), a.get('href'))
                    filename = get_valid_filename(a.text)
                    if not filename.endswith('.html') or not filename.endswith('.htm'):
                        filename += ".html"
                    a['href'] = filename
                    c = Crawler(self.session, url, self.path, a['href'], a.text)
                    is_file = c.crawl()
                    if is_file:
                        a['href'] = os.path.join("files", filename.removesuffix('.htm').removesuffix('.html'))

        with open(os.path.join(self.path, self.filename), 'w', encoding='utf-8') as html:
            html.write(str(soup))
        return False
