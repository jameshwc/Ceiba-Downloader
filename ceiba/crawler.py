import logging
import re
from pathlib import Path
from typing import Dict, Set, List, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from . import util
from .exceptions import NotFound, StopDownload
from .const import strings

class Crawler():

    crawled_files_path: Set[Path] = set()
    crawled_urls: Dict[str, Path] = {}

    # Dicuss: should we move css/img to root folder instead of download them every time in each course?

    @classmethod
    def reset(cls):
        cls.crawled_files_path.clear()
        cls.crawled_urls = {}

    def __init__(self,
                 session: requests.Session,
                 url: str,
                 path: Path,
                 is_admin=False,
                 course_name: str = "",
                 module: str = "",
                 filename: str = "",
                 text: str = ""):
        self.session = session
        self.url = url
        self.path = path
        self.is_admin = is_admin
        self.course_name = course_name
        self.module = module
        self.filename = util.get_valid_filename(filename)
        self.text = text
        self._board_dir: Dict[str, Path] = {}
        self._is_board = False

    def crawl(self) -> Path:
        if self.url in Crawler.crawled_urls:
            # See issue #11 [https://github.com/jameshwc/Ceiba-Downloader/issues/11]
            if util.is_relative_to(Crawler.crawled_urls[self.url], self.path):
                return Crawler.crawled_urls[self.url]

        response = util.get(self.session, self.url)
        if response.status_code == 404 or response.content.startswith(
                bytes('<html><head><title>Request Rejected</title>', encoding='utf-8')):
            raise NotFound(self.text, response.url)

        if self.module != "grade" and len(self.text.strip()) > 0:  # grade module has many 'show' and 'hide' pages to download
            module_name = util.full_cname_map[self.module] if strings.lang == 'zh-tw' else self.module
            logging.info(strings.crawler_download_info.format(self.course_name, module_name, self.text))


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
        elif self.module == 'hw':
            soup = self.__handle_hw(soup, response.url)
        elif self.module == 'share':
            soup = self.__handle_share(soup)

        if self.is_admin:
            soup = self.remove_nav_and_footer(soup)
            soup = self.parse_frame(soup)
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

        skip_href_texts = util.skip_href_texts(self.module, self.is_admin)

        if self.is_admin:
            hrefs = soup.find('div', {'id': 'section'}).find_all('a')
        else:
            hrefs = soup.find_all('a')

        a: Tag
        for a in hrefs:
            util.check_pause_and_stop()
            if a.text in skip_href_texts or \
                (self.module == 'ftp' and a.text.endswith('.htm')):
                a.replaceWithChildren()
                continue
            url = urljoin(resp_url, a.get('href'))
            if not url.startswith('http') or \
               urlparse(url).netloc != 'ceiba.ntu.edu.tw' or \
               urlparse(url).path == '' or \
               (len(a.text) == 0 and (self.module != 'vote' or a.get('href') != '#')):
                continue
            filename = a.text
            text = a.text
            is_admin = self.is_admin

            if self.module == 'vote' and a.get('href') == "#" and a.get('onclick'):
                m = re.search(r"window\.open\(\'(.*?)\'.*", a.get('onclick'))
                if m:
                    url = urljoin(resp_url, m.group(1))
                    del a['onclick']
                if self.is_admin:
                    filename = a.parent.parent.parent.find_all('td')[0].text.strip() + "_result"
                else:
                    filename = a.parent.parent.find_all('td')[1].text.strip()
                text = filename
                is_admin = False

            crawler_path = self.path
            if self._is_board and a.text in self._board_dir:
                crawler_path = self._board_dir[a.text]
            try:
                filename = Crawler(self.session, url, crawler_path, is_admin, self.course_name, self.module, filename, text).crawl()
            except StopDownload as e:
                raise e
            except NotFound as e:
                logging.warning(e)
                a.string = a.text + " [404 not found]"
                a['href'] = url
                # a.replaceWithChildren()  # discuss: when 404 happens, should it link to original url?
            except Exception as e:
                logging.error(strings.crawler_download_fail.format(text, url), exc_info=True)
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

    def __handle_hw(self, soup: BeautifulSoup, resp_url: str) -> BeautifulSoup:
        great_hw_buttons: List[Tag] = soup.find_all('input', {'class': 'btn'})
        for great_hw_button in great_hw_buttons:
            onclick_val = great_hw_button.get('onclick')
            if onclick_val is None:
                continue
            m = re.search(r"hw_view\('(.*)','(.*)\'\)", onclick_val)
            if m and m.group(1) and m.group(2):
                lang, hw_sn = m.group(1), m.group(2)
                great_hw_button['href'] = urljoin(resp_url, f'hw_view.php?current_lang={lang}+"&hw_sn={hw_sn}')
                great_hw_button.name = 'a'
                great_hw_button.string = great_hw_button['value']
                for attr in ['type', 'value', 'onclick', 'class']:
                    del great_hw_button[attr]
            else:
                continue
        return soup

    def __handle_share(self, soup: BeautifulSoup) -> BeautifulSoup:
        # handle some encoding error (Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.)
        for a in soup.find_all('a'):
            a['href'] = a['href'].replace('¤t_', '&')
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
            Crawler(self.session, url, static_dir, self.is_admin, filename=filename, text=css['href']).crawl_css_and_resources()


    def parse_frame(self, soup: BeautifulSoup) -> BeautifulSoup:
        nav = soup.find('div', {"id": "majornav"})
        try:
            a: Tag
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
        except AttributeError as e:
            logging.error(e, exc_info=True)
        return soup

    def remove_nav_and_footer(self, soup: BeautifulSoup) -> BeautifulSoup:
        for a in soup.find('ul', {"id": "nav-top"}).find_all('a'):
            a.extract()

        for a in soup.find('div', {'id': 'footer'}).find_all('a'):
            a.extract()

        courses_list_a_tag = soup.find('li', {'id': 'clist'}).find('a')
        href_path = Path(courses_list_a_tag['href']).parent / '../../index.html'
        courses_list_a_tag['href'] = href_path.as_posix()
        soup.find('li', {'id': 'uinfo'}).extract()  # TODO: keep info page
        return soup

    def _save_files(self, content: bytes) -> Path:
        files_dir = self.path / "files"
        files_dir.mkdir(exist_ok=True)
        filepath = self._get_uniq_filepath(files_dir.joinpath(self.filename))
        filepath.write_bytes(content)
        Crawler.crawled_files_path.add(filepath)
        Crawler.crawled_urls[self.url] = filepath
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
