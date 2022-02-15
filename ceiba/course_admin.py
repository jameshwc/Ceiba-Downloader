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
        modules = self.crawl_main_page()
        for mod in modules:
            resp = util.get(self.sess, util.admin_module_urlgen(mod))
            soup = BeautifulSoup(resp.content, 'html.parser')
            soup = self.parse_frame(soup, resp.url)
            mod_path = self.path.joinpath(mod)
            mod_path.mkdir(exist_ok=True)
            Crawler(self.sess, resp.url, mod_path).download_css(soup.find_all('link'))
            mod_path.joinpath(mod+".html").write_text(str(soup), encoding='utf-8')
    
    def crawl_main_page(self) -> List[str]:
        resp = util.get(self.sess, self.admin_url + self.course_sn)
        soup = BeautifulSoup(resp.content, 'html.parser')
        modules = []
        link_button: Tag
        for link_button in soup.find_all('input'):
            if link_button.get('type') == 'hidden':
                continue
            if link_button.get('value') == '進入' and link_button.get('disabled') == None:
                link_button.string = link_button.get('value')
                link_button.name = 'a'
                module = re.search(r"singleadm\('([a-z]*)'\)" ,link_button.get('onclick')).group(1)
                link_button['href'] = module + "/" + module + ".html"
                modules.append(module)
            else:
                link_button.replaceWithChildren()
        Crawler(self.sess, resp.url, self.path).download_css(soup.find_all('link'))
        self.path.joinpath('index.html').write_text(str(soup), encoding='utf-8')
        return modules
    
    def parse_frame(self, soup: BeautifulSoup, url: str) -> BeautifulSoup:
        nav = soup.find('div', {"id": "majornav"})
        module_urls = []
        a: Tag
        for a in nav.find_all('a'):
            module_urls.append((a.get_text(), urljoin(url, a['href'])))
            if a.get_text() == '主功能表':
                a['href'] = "../index.html"
            else:
                module = util.admin_ename_map[a.get_text()]
                a['href'] = "../" + module + "/" + module + ".html"
        
        for a in soup.find('ul', {"id": "nav-top"}).find_all('a'):
            a.replaceWithChildren()
        
        return soup