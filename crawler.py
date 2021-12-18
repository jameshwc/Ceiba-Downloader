import logging
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

import strings
from util import get_valid_filename


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

    def get(self, url: str):
        while True:
            try:
                response = self.session.get(url)
            except (TimeoutError, ConnectionError, ConnectionResetError):
                logging.error(strings.crawler_timeour_error)
                time.sleep(5)
                continue
            return response

    def crawl(self, is_table=False, static=False) -> bool:
        '''
        Return True if the url is file, and return False if the url is html.
        '''
        response = self.get(self.url)

        if not static and not response.url.startswith('https://ceiba.ntu.edu.tw'):
            logging.warn(strings.skip_external_href.format(response.url))
            return  # TODO: download (optionally) external documents (.pdf, .docx, etc.) (may limit the domain names)
        
        if self.url in Crawler.crawled_urls:
            return Crawler.crawled_urls[self.url]
        if (self.path, self.url) in Crawler.crawled_static_files:
            return True
        
        if str.encode('The requested URL was rejected. Please consult with your administrator.') in response.content:
            logging.error(strings.crawler_download_fail.format(self.text, response.url))
            return False
        
        if len(self.text) > 0 and not static:
            logging.info(strings.crawler_download_info.format(self.text))
        
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
            c = Crawler(self.session, url, self.path, css['href'], css['href'])
            c.crawl(static=True)

        for img in soup.find_all('img'):
            url = urljoin(self.url, img.get('src'))
            img['src'] = url.split('/')[-1]
            c = Crawler(self.session, url, self.path, img['src'], css['href'])
            c.crawl(static=True)
        
        for op in soup.find_all('option'):
            op.extract()
            
        hrefs = soup.find_all('a')

        skip_href_texts = ['作業列表', '友善列印']
        skip_href_texts.extend(['看板列表', '最新張貼', '排行榜', '推薦文章', '搜尋文章', '發表紀錄', ' 新增主題', '引用', ' 回覆', '分頁顯示', '上個主題', '下個主題', '修改'])
        # '修改' may be an indicator to download the owner's article?
        skip_href_texts.extend(['上頁', '下頁', '上一頁', '下一頁', ' 我要評分'])

        # special case for board
        is_board = False
        board_dir = {}
        for caption in soup.find_all('caption'):
            caption_text: str = caption.get_text()
            if caption_text.startswith('看板列表'):
                rows = caption.parent.find('tbody').find_all('tr')
                for row in rows:
                    a_tag = row.find("p", {"class": "fname"}).find('a')
                    dir_name = get_valid_filename(a_tag.text)
                    board_dir[a_tag.text] = os.path.join(self.path, dir_name)
                    os.makedirs(board_dir[a_tag.text], exist_ok=True)
                is_board = True
                break

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
                    if is_board and a.text in board_dir:
                        a['href'] = os.path.join(board_dir[a.text], filename)
                        is_file = Crawler(self.session, url, board_dir[a.text], a['href'], a.text).crawl(is_table=True)
                    else:
                        a['href'] = filename
                        is_file = Crawler(self.session, url, self.path, a['href'], a.text).crawl()
                    if is_file:  # TODO: avoid duplicate filenames?
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
                pass  # TODO
            if response.headers['content-type'] == 'text/css':
                new_content = response.content
                resources = re.findall(r'url\((.*?)\)', str(response.content))
                if len(resources) > 0:
                    resources_path = os.path.join(self.path, "resources")
                    os.makedirs(resources_path, exist_ok=True)
                    for res in resources:
                        resp = self.get(urljoin(self.url, res))
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
