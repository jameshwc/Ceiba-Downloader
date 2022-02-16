import logging
import re
from pathlib import Path
from typing import Dict, Set, List
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from . import util
from .exceptions import NotFound
from .const import strings


class Crawler():

    crawled_files_path: Set[Path] = set()
    crawled_urls: Dict[str, Path] = {}

    # Dicuss: should we move css/img to root folder instead of download them every time in each course?

    def __init__(self,
                 session: requests.Session,
                 url: str,
                 path: Path,
                 module: str = "",
                 filename: str = "",
                 text: str = ""):
        self.session = session
        self.url = url
        self.path = path
        self.module = module
        self.filename = util.get_valid_filename(filename)
        self.text = text
        self._board_dir: Dict[str, Path] = {}
        self._is_board = False

    def crawl(self) -> Path:
        if self.url in Crawler.crawled_urls:
            # See issue #11 [https://github.com/jameshwc/Ceiba-Downloader/issues/11]
            if util.is_relative_to(Crawler.crawled_urls[self.url], self.path):
                logging.debug(strings.url_duplicate.format(self.url))
                return Crawler.crawled_urls[self.url]
        
        response = util.get(self.session, self.url)
        if response.status_code == 404 or response.content.startswith(
                bytes('<html><head><title>Request Rejected</title>', encoding='utf-8')):
            raise NotFound(self.text, response.url)

        if self.module != "grade" and len(self.text.strip()) > 0:  # grade module has many 'show' and 'hide' pages to download
            logging.info(strings.crawler_download_info.format(self.text))

        if 'text/html' not in response.headers['content-type']:  # files (e.g. pdf, docs)
            return self._save_files(response.content)

        self.filename += ".html"
        filepath = self._get_uniq_filepath(self.path.joinpath(self.filename))
        Crawler.crawled_files_path.add(filepath)
        Crawler.crawled_urls[self.url] = filepath

        soup = BeautifulSoup(response.content, 'html.parser')
        self.download_css(soup.find_all('link'))
        self.download_imgs(soup.find_all('img'))
        

        if self.module == 'board':
            self.__handle_board(soup.find_all('caption'))  # special case for board
        elif self.module == 'bulletin':
            soup = self.__handle_bulletin(soup, response.url)
        
        soup = self.crawl_hrefs(soup, response.url)

        for op in soup.find_all('option'):
            op.extract()  # TODO: we should use <a> to replace <option>
        
        filepath.write_text(str(soup), encoding='utf-8')
        return filepath

    def crawl_css_and_resources(self):
        response = util.get(self.session, self.url)
        path = self.path / self.filename
        if path.exists():
            return
        new_content = response.content
        resources: List[str] = re.findall(r'url\((.*?)\)', str(response.content))
        if len(resources) > 0:
            resources_path = self.path / "resources"
            resources_path.mkdir(exist_ok=True)
            for res in resources:
                resp = util.get(self.session, urljoin(self.url, res))
                res_filename = res.split('/')[-1]
                resources_path.joinpath(res_filename).write_bytes(resp.content)
                new_content = new_content.replace(
                    bytes('url(' + res, encoding='utf-8'),
                    bytes('url(resources/' + res_filename, encoding='utf-8'))
        path.write_bytes(new_content)

    def crawl_hrefs(self, soup: BeautifulSoup, resp_url: str) -> BeautifulSoup:

        skip_href_texts = util.default_skip_href_texts
        if self.module == 'board':
            skip_href_texts = util.board_skip_href_texts
        elif self.module == 'student':
            skip_href_texts = util.student_skip_href_texts
        
        hrefs = soup.find_all('a')
        a: Tag
        for a in hrefs:
            if a.text in skip_href_texts:
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
            
            if self.module == 'vote' and a.get('href') == "#" and a.get('onclick'):
                m = re.search(r"window\.open\(\'(.*?)\'.*", a.get('onclick'))
                if m:
                    url = urljoin(resp_url, m.group(1))
                    del a['onclick']
                filename = a.parent.parent.find_all('td')[1].text.strip()
                text = filename
            
            crawler_path = self.path
            if self._is_board and a.text in self._board_dir:
                crawler_path = self._board_dir[a.text]
            try:
                filename = Crawler(self.session, url, crawler_path, self.module, filename, text).crawl()
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

    def __handle_board(self, captions: List[Tag]):
        for caption in captions:
            caption_text: str = caption.get_text()
            if caption_text.startswith('看板列表'):
                rows = caption.parent.find('tbody').find_all('tr')
                for row in rows:
                    a_tag: Tag = row.find("p", {"class": "fname"}).find('a')
                    dir_name = util.get_valid_filename(a_tag.text)
                    self._board_dir[a_tag.text] = self.path / dir_name
                    self._board_dir[a_tag.text].mkdir(exist_ok=True)
                self._is_board = True
                break
    
    def __handle_bulletin(self, soup: BeautifulSoup, resp_url: str):
        op: Tag
        for op in soup.find_all('option'):
            url = urljoin(resp_url, op['value'])
            op.name = 'a'
            op['href'] = url
            del op['value']
            del op['selected']
        select = soup.find('select')
        if select:
            select.replaceWithChildren()
        return soup

    def download_imgs(self, imgs: ResultSet):
        img: Tag
        for img in imgs:
            url = urljoin(self.url, img.get('src'))
            if urlparse(url).netloc != 'ceiba.ntu.edu.tw':
                continue  # skip downloading external images
            img['src'] = url.split('/')[-1]
            path = self.path / img['src']
            if path.exists():
                continue
            img_response = util.get(self.session, url)
            path.write_bytes(img_response.content)

    def download_css(self, links: ResultSet):
        css: Tag
        for css in links:
            url = urljoin(self.url, css.get('href'))
            if urlparse(url).netloc != 'ceiba.ntu.edu.tw':
                continue  # skip downloading external css
            filename = url.split('/')[-1]
            css['href'] = 'static/' + filename
            static_dir = self.path / 'static'
            static_dir.mkdir(exist_ok=True)
            Crawler(self.session, url, static_dir, self.module, filename,
                    css['href']).crawl_css_and_resources()

    def _save_files(self, content: bytes) -> Path:
        files_dir = self.path / "files"
        files_dir.mkdir(exist_ok=True)
        filepath = self._get_uniq_filepath(files_dir.joinpath(self.filename))
        filepath.write_bytes(content)
        self.__class__.crawled_files_path.add(filepath)
        self.__class__.crawled_urls[self.url] = filepath
        return filepath
        
    def _get_uniq_filepath(self, path: Path):
        if path not in Crawler.crawled_files_path:
            return path

        name = path.stem
        ext = path.suffix
        i = 0
        while path in Crawler.crawled_files_path:
            i += 1
            path = path.parent / (name + "_{}".format(i) + ext)
        return path
