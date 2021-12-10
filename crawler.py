import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from pathlib import Path
from util import get_valid_filename
from tqdm import tqdm
import re


class Crawler():

    crawled_urls = {}
    crawled_static_files = {}  # css/img: use path to avoid repetitive downloads.
    # TODO: we should move css/img to root folder instead of download them every time in each course

    def __init__(self, session: requests.Session, url: str, path: str, filename: str, text: str = ""):
        self.session = session
        self.url = url
        self.path = path
        self.filename = get_valid_filename(filename)
        self.text = text

    def crawl(self, is_table=False, static=False) -> bool:
        '''
        Return True if the url is file, and return False if the url is html.
        '''
        response = self.session.get(self.url)
        
        if response.url in Crawler.crawled_urls:
            return Crawler.crawled_urls[response.url]
        if (self.path, response.url) in Crawler.crawled_static_files:
            return True
        
        print(response.url, self.text)
        
        if 'text/html' not in response.headers['content-type']:
            self.__download_files(response, static)
            Crawler.crawled_static_files[(self.path, response.url)] = True
            return True
        
        soup = BeautifulSoup(response.content, 'html.parser')
        Crawler.crawled_urls[response.url] = False
        
        if is_table:
            os.makedirs(os.path.join(self.path, "files"), exist_ok=True)
        
        for css in soup.find_all('link'):
            url = urljoin(self.url, css.get('href'))
            css['href'] = url.split('/')[-1]
            c = Crawler(self.session, url, self.path, css['href'], 0)
            c.crawl(static=True)

        for img in soup.find_all('img'):
            url = urljoin(self.url, img.get('src'))
            img['src'] = url.split('/')[-1]
            c = Crawler(self.session, url, self.path, img['src'], 0)
            c.crawl(static=True)
        
        for op in soup.find_all('option'):
            op.extract()
        hrefs = tqdm(soup.find_all('a')) if is_table else soup.find_all('a')
        # hrefs = soup.find_all('a')
        skip_href_texts = ['作業列表', '友善列印']
        skip_href_texts.extend(['看板列表', '最新張貼', '排行榜', '推薦文章', '搜尋文章', '發表紀錄', ' 新增主題', '引用', ' 回覆', '分頁顯示', '上個主題', '下個主題', '全部顯示'])
        skip_href_texts.extend(['上頁', '下頁'])
        for a in hrefs:
            if a.text in skip_href_texts:
                a.replaceWithChildren()
                continue
            if len(a.text) > 0 and not a['href'].startswith('mailto'):
                if not a['href'].startswith('http') or a['href'].startswith('https://ceiba.ntu.edu.tw'):
                    url = urljoin(response.url, a.get('href'))

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
    
    def __download_files(self, response: requests.Response, static: bool):
        if self.filename.endswith('.html'):
            self.filename = self.filename.removesuffix('.html')
        if static:  # css/img
            filepath = os.path.join(self.path, self.filename)
            path = Path(filepath)  # TODO: check if filename exists
            if path.exists():
                print('')
            if response.headers['content-type'] == 'text/css':
                new_content = response.content
                resources = re.findall(r'url\((.*?)\)', str(response.content))
                if len(resources) > 0:
                    resources_path = os.path.join(self.path, "resources")
                    os.makedirs(resources_path, exist_ok=True)
                    for res in resources:
                        resp = self.session.get(urljoin(self.url, res))
                        res_filename = res.split('/')[-1]
                        with open(os.path.join(resources_path, res_filename), 'wb') as resource_file:
                            resource_file.write(resp.content)
                        new_content = new_content.replace(bytes('url(' + res, encoding='utf-8'), bytes('url(resources/' + res_filename, encoding='utf-8'))
                path.write_bytes(new_content)
            else:
                path.write_bytes(response.content)
        
        else:  # files (e.g. .pdf, .docx, .pptx)
            path = Path(os.path.join(os.path.join(self.path, "files"), self.filename))
            path.write_bytes(response.content)
