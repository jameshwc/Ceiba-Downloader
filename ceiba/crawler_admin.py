import logging
import re
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse
from xml.dom.minidom import Attr

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from . import util
from .const import strings
from .crawler import Crawler
from .exceptions import NotFound


class Admin(Crawler):

    crawled_files_path: Set[Path] = set()
    crawled_urls: Dict[str, Path] = {}
    
    def __init__(self, sess: requests.Session, url: str, path: Path, module: str, filename: str = "", text: str = ""):
        super().__init__(sess, url, path, module, filename, text)
    
    def crawl(self) -> Path:
        
        if self.url in Admin.crawled_urls:
            if util.is_relative_to(Admin.crawled_urls[self.url], self.path):
                return Admin.crawled_urls[self.url]
        
        resp = util.get(self.session, self.url)
        if resp.status_code == 404 or resp.content.startswith(
                bytes('<html><head><title>Request Rejected</title>', encoding='utf-8')):
            raise NotFound(self.text, resp.url)
        
        if len(self.text.strip()) > 0:
            logging.info(strings.crawler_download_info.format(self.text))
        
        if 'text/html' not in resp.headers['content-type']:
            return self._save_files(resp.content)

        self.filename += ".html"
        filepath = self._get_uniq_filepath(self.path.joinpath(self.filename))
        Admin.crawled_files_path.add(filepath)
        Admin.crawled_urls[self.url] = filepath

        soup = BeautifulSoup(resp.content, 'html.parser')
        self.download_css(soup.find_all('link'))
        self.download_imgs(soup.find_all('img'))

        try:
            soup = self.parse_frame(soup, resp.url)
            soup = self.crawl_hrefs(soup, resp.url)
        except Exception as e:
            logging.error(e, exc_info=True)

        filepath.write_text(str(soup), encoding='utf-8')
        return filepath

    def parse_frame(self, soup: BeautifulSoup, url: str) -> BeautifulSoup:
        nav = soup.find('div', {"id": "majornav"})
        a: Tag
        try:
            for a in nav.find_all('a'):
                if a.get_text() == '主功能表':
                    a['href'] = "../index.html"
                else:
                    module = util.admin_ename_map[a.get_text()]
                    if module in util.admin_skip_mod:
                        a.parent.parent.extract()
                        # a.extract()
                    else:
                        a['href'] = "../" + module + "/" + module + ".html"
            
            for a in soup.find('ul', {"id": "nav-top"}).find_all('a'):
                a.extract()
            
            for a in soup.find('div', {'id': 'footer'}).find_all('a'):
                a.extract()
        except AttributeError as e:
            logging.error(e, exc_info=True)
            while True:
                try:
                    eval(input())
                except KeyboardInterrupt:
                    break
                except:
                    continue
        return soup

    def crawl_hrefs(self, soup: BeautifulSoup, resp_url: str) -> BeautifulSoup:
        skip_href_texts = util.admin_skip_href_texts(self.module)
        try:
            hrefs = soup.find('div', {'id': 'section'}).find_all('a')
        except AttributeError:
            logging.warning()
        a: Tag
        for a in hrefs:
            if a.text in skip_href_texts:
                a.replaceWithChildren()
                continue
            if a.text.endswith('.htm') and self.module == 'ftp':
                a.replaceWithChildren()
                continue
            url = urljoin(resp_url, a.get('href'))
            if not url.startswith('http') or \
               urlparse(url).netloc != 'ceiba.ntu.edu.tw' or \
               urlparse(url).path == '' or \
               len(a.text) == 0:
                continue
            filename = a.text
            text = a.text
            crawler_path = self.path
            if self._is_board and a.text in self._board_dir:
                crawler_path = self._board_dir[a.text]
            try:
                filename = Admin(self.session, url, crawler_path, self.module, filename, text).crawl()
            except NotFound as e:
                logging.warning(e)
                a.string = a.text + " [404 not found]"
                a['href'] = url
                # a.replaceWithChildren()  # discuss: when 404 happens, should it link to original url?
            except Exception as e:
                logging.warning(strings.crawler_download_fail.format(text, url), exc_info=True)
                a.string = a.text + " [ERROR]"
            else:
                a['href'] = util.relative_path(self.path, filename)
        return soup 
    def __crawl_section(self, soup: BeautifulSoup):
        ...
