import logging
import os
import re
from pathlib import Path
from urllib.parse import urljoin
from typing import Dict, Union, Set

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from . import util
from .strings import strings
from .exceptions import NotFound


class Crawler():

    crawled_files_path: Set[Path] = set()
    crawled_urls: Dict[str, Path] = {}

    # TODO: we should move css/img to root folder instead of download them every time in each course

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

    def crawl(self) -> Path:
        if self.url in Crawler.crawled_urls:
            # See issue #11 [https://github.com/jameshwc/Ceiba-Downloader/issues/11]
            if Crawler.crawled_urls[self.url].is_relative_to(self.path):
                logging.debug(strings.url_duplicate.format(self.url))
                return Crawler.crawled_urls[self.url]
        
        response = util.get(self.session, self.url)
        if response.status_code == 404 or response.content.startswith(
                bytes('<html><head><title>Request Rejected</title>', encoding='utf-8')):
            raise NotFound(self.text, response.url)

        if self.module != "grade" and len(self.text.strip()) > 0:  # grade module has many 'show' and 'hide' pages to download
            logging.info(strings.crawler_download_info.format(self.text))

        if 'text/html' not in response.headers['content-type']:  # files (e.g. pdf, docs)
            files_dir = self.path / "files"
            files_dir.mkdir(exist_ok=True)
            filepath = self.__get_uniq_filepath(files_dir.joinpath(self.filename))
            filepath.write_bytes(response.content)
            Crawler.crawled_files_path.add(filepath)
            Crawler.crawled_urls[self.url] = filepath
            return filepath

        self.filename += ".html"
        filepath = self.__get_uniq_filepath(self.path.joinpath(self.filename))
        Crawler.crawled_files_path.add(filepath)
        Crawler.crawled_urls[self.url] = filepath

        soup = BeautifulSoup(response.content, 'html.parser')
        self.download_css(soup.find_all('link'))
        self.download_imgs(soup.find_all('img'))
        
        for op in soup.find_all('option'):
            op.extract()

        self.is_board = False
        if self.module == 'board':
            self.__handle_board(soup.find_all('caption'))  # special case for board
        
        soup = self.crawl_hrefs(soup, response.url)

        filepath.write_text(str(soup), encoding='utf-8')
        return filepath

    def crawl_css_and_resources(self):
        response = util.get(self.session, self.url)
        path = self.path / self.filename
        if path.exists():
            return
        new_content = response.content
        resources = re.findall(r'url\((.*?)\)', str(response.content))
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

        skip_href_texts = ['友善列印', '分頁顯示']
        if self.module == 'board':
            skip_href_texts.extend([
                '看板列表', '最新張貼', '排行榜', '推薦文章', '搜尋文章', '發表紀錄', ' 新增主題', '引用',
                ' 回覆', '分頁顯示', '上個主題', '下個主題', '修改'])
            # '修改' may be an indicator to only download the owner's article?
            skip_href_texts.extend(['上一頁', '下一頁', ' 我要評分', ' 我要推薦'])
        elif self.module == 'student':
            skip_href_texts.extend(['上頁', '下頁'])
        hrefs = soup.find_all('a')
        for a in hrefs:
            if a.text in skip_href_texts:
                a.replaceWithChildren()
                continue
            if a['href'].startswith('mailto') or a['href'].startswith('javascript') or (a['href'].startswith('http') and 'ceiba.ntu.edu.tw' not in a['href']) or len(a.text) == 0:
                continue
            url = urljoin(resp_url, a.get('href'))
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
            if self.is_board and a.text in self.board_dir:
                crawler_path = self.board_dir[a.text]
            try:
                filename = Crawler(self.session, url, crawler_path, self.module, filename, text).crawl()
            except NotFound as e:
                logging.warning(e)
                a.string = a.text + " [404 not found]"
                a['href'] = url
                # a.replaceWithChildren()  # discuss: when 404 happens, should it link to original url?
                continue
            a['href'] = crawler_path.relative_to(self.path) / filename
        return soup

    def __handle_board(self, captions):
        self.board_dir: Dict[str, Path] = {}
        for caption in captions:
            caption_text: str = caption.get_text()
            if caption_text.startswith('看板列表'):
                rows = caption.parent.find('tbody').find_all('tr')
                for row in rows:
                    a_tag = row.find("p", {"class": "fname"}).find('a')
                    dir_name = util.get_valid_filename(a_tag.text)
                    self.board_dir[a_tag.text] = self.path / dir_name
                    self.board_dir[a_tag.text].mkdir(exist_ok=True)
                self.is_board = True
                break

    def download_imgs(self, imgs):
        for img in imgs:
            url = urljoin(self.url, img.get('src'))
            img['src'] = url.split('/')[-1]
            path = self.path / img['src']
            if path.exists():
                continue
            img_response = util.get(self.session, url)
            path.write_bytes(img_response.content)

    def download_css(self, links: ResultSet):
        for css in links:
            url = urljoin(self.url, css.get('href'))
            if url.startswith('http') and 'ceiba' not in url:
                continue  # skip downloading external css
            filename = url.split('/')[-1]
            css['href'] = 'static/' + filename
            static_dir = self.path / 'static'
            static_dir.mkdir(exist_ok=True)
            Crawler(self.session, url, static_dir, self.module, filename,
                    css['href']).crawl_css_and_resources()

    def __get_uniq_filepath(self, path: Path):
        if path not in Crawler.crawled_files_path:
            return path

        name = path.stem
        ext = path.suffix
        i = 0
        while path in Crawler.crawled_files_path:
            i += 1
            path = path.parent / (name + "_{}".format(i) + ext)
        return path
