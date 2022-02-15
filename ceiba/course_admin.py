from urllib.parse import urljoin
from bs4 import BeautifulSoup
from bs4.element import Tag
from pathlib import Path
from . import util
from typing import List
import re
from .crawler import Crawler

class Admin():

    def __init__(self, sess, course_sn, admin_url):
        self.sess = sess
        self.course_sn = course_sn
        self.admin_url = admin_url
        self.path = Path()
    
    def crawl(self, path: Path):
        self.path = path
        self.crawl_main_page()
        # resp = util.get(self.sess, util.admin_module_urls['ftp'])
        # soup = BeautifulSoup(resp.content, 'html.parser')
        # self.frame = self.parse_frame(soup, resp.url)
        # Path("crawl.html").write_text(str(self.frame), encoding='utf-8')
    
    def crawl_main_page(self):
        resp = util.get(self.sess, self.admin_url + self.course_sn)
        soup = BeautifulSoup(resp.content, 'html.parser')
        link_button: Tag
        for link_button in soup.find_all('input'):
            if link_button.get('value') == '進入' and link_button.get('disabled') == None:
                module = re.search(r"singleadm\('([a-z]*)'\)" ,link_button.get('onclick')).group(1)
                link_button.name = 'a'
                link_button['href'] = module + "/" + module + ".html"
                link_button.string = link_button.get('value')
        Crawler(self.sess, resp.url, self.path).download_css(soup.find_all('link'))
        self.path.joinpath('index.html').write_text(str(soup), encoding='utf-8')
    
    def parse_frame(self, soup: BeautifulSoup, url: str) -> List[str]:
        nav = soup.find('div', {"id": "majornav"})
        module_urls = []
        a: Tag
        for a in nav.find_all('a'):
            if a.get_text() in ['主功能表', '主題首頁', '']:
                continue
            module_urls.append((a.get_text(), urljoin(url, a['href'])))
            a['href'] = util.admin_ename_map[a.get_text()]
        
        for a in soup.find('ul', {"id": "nav-top"}).find_all('a'):
            a.replaceWithChildren()
        
        return soup