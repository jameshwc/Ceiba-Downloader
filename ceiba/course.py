import logging
import re
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from . import util
from .crawler import Crawler
from .const import strings
from .crawler_admin import Admin


class Course():

    def __init__(self, semester, course_num, cname, ename, teacher, href, admin_url: str):
        self.semester: str = semester
        self.course_num: str = course_num
        self.cname: str = cname
        self.ename: str = ename
        self.teacher: str = teacher
        self.href: str = href
        self.admin_url = admin_url
        self.folder_name: str = util.get_valid_filename("_".join([self.semester, self.cname, self.ename, self.teacher]))
        self.id: str = self.semester + self.course_num
        self.course_sn: str = ""
        self.path: Path = None

    def __str__(self):
        return " ".join([self.cname, self.ename, self.teacher, self.href])

    def download(self,
                 path: Path,
                 session: requests.Session,
                 modules_filter_list: Optional[List[str]] = None,
                 progress = None):
        
        self.path = path / self.folder_name
        self.path.mkdir(exist_ok=True)
        
        course_name = self.cname if strings.lang == 'zh-tw' else self.ename
        
        course_url = util.get(session, self.href).url
        m = re.search(r'course/([0-9a-f]*)+', course_url)
        if m and m.group(0).startswith('course/'):
            self.course_sn = m.group(0)[7:]
        else:
            logging.error(strings.error_unable_to_parse_course_sn.format(course_name, course_name))
            logging.debug(strings.urlf.format(course_url))
            return
        
        modules = self.download_homepage(session, strings.homepage, modules_filter_list)
        
        if progress and modules_filter_list:
            modules_not_in_this_module_num = len(modules_filter_list) - len(modules)
            if modules_not_in_this_module_num > 0:
                progress.emit(modules_not_in_this_module_num)
        
        for module in modules:
            module_name = util.cname_map[module] if strings.lang == 'zh-tw' else module
            try:
                self.download_module(session, module_name, module)
            except Exception as e:
                logging.error(e, exc_info=True)
                logging.warning(strings.error_skip_and_continue_download_modules.format(course_name, module_name))
            if progress:
                progress.emit(1)

    @util.progress_decorator()
    def download_module(self, session: requests.Session, obj_name: str, module: str):
        url = util.module_url + "?csn=" + self.course_sn + "&default_fun=" + module + "&current_lang=chinese"  # TODO:language

        module_dir = self.path / module
        module_dir.mkdir(exist_ok=True)

        Crawler(session, url, module_dir, module=module, filename=module).crawl()

    @util.progress_decorator()
    def download_homepage(self,
                          session: requests.Session,
                          name: str = strings.homepage,
                          modules_filter_list: List[str] = None):
        param = "?csn=" + self.course_sn + "&default_fun=info&current_lang=chinese"  # TODO:language
        button_url = util.button_url + param
        banner_url = util.banner_url + param
        homepage_url = util.homepage_url + param
        Crawler(session, banner_url, self.path, filename="banner").crawl()
        self.__download_homepage_frame(session, homepage_url)
        return self.__download_button(session, button_url, 'button.html',
                                      modules_filter_list)

    def __download_homepage_frame(self,
                            session: requests.Session,
                            url: str,
                            filename: str = 'index.html'):
        resp = util.get(session, url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        soup.find("frame", {"name": "topFrame"})['src'] = "banner.html"
        soup.find("frame", {"name": "leftFrame"})['src'] = "button.html"
        soup.find("frame", {"name": "mainFrame"})['src'] = "info/info.html"
        # TODO: footer.php
        self.path.joinpath(filename).write_text(str(soup), encoding='utf-8')

    def __download_button(self,
                          session: requests.Session,
                          url: str,
                          filename: str,
                          modules_filter_list: List[str] = None) -> List[str]:
        resp = util.get(session, url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        Crawler(session, url, self.path).download_css(soup.find_all('link'))

        nav_co = soup.find("div", {"id": "nav_co"})
        items = []
        for a in nav_co.find_all('a'):
            m = re.search(r"onclick\('(.*?)'.*\)", a['onclick'])
            if m:
                item = m.group(1)
            else:
                logging.debug('Abnormal onclick value: ' + a['onclick'])  
                # Only found out such case in '108-1 Machine Learning Foundations'
                item = a.next_element['id']
            if item in ['logout', 'calendar'] or \
                    (modules_filter_list is not None and item not in modules_filter_list):
                # I assume the calendar is a feature nobody uses.
                a.extract()  # remove the element
                continue
            a['onclick'] = "parent.parent.mainFrame.location='" + item + "/" + item + ".html'"
            items.append(item)
        self.path.joinpath(filename).write_text(str(soup), encoding='utf-8')
        return items

    def download_admin(self,
                       path: Path,
                       session: requests.Session,
                       progress = None):
        
        self.path = path / self.folder_name
        self.admin_path = self.path / "admin"
        self.admin_path.mkdir(exist_ok=True, parents=True)

        # course_name = self.cname if strings.lang == 'zh-tw' else self.ename
        admin_modules = self.download_admin_main_page(session)
        for mod in admin_modules:
            if mod in util.admin_skip_mod:
                continue
            url = util.admin_module_urlgen(mod)
            path = self.admin_path / mod
            path.mkdir(exist_ok=True)
            Admin(session, url, path, mod, mod).crawl()
        # self.admin.crawl(self.admin_path)
        
    
    def download_admin_main_page(self, session: requests.Session):
        resp = util.get(session, self.admin_url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        modules = []
        link_button: Tag
        for link_button in soup.find_all('input'):
            if link_button.get('type') == 'hidden':
                continue
            if link_button.get('value') == '進入' and link_button.get('disabled') == None:
                link_button.string = link_button.get('value')
                link_button.name = 'a'
                m = re.search(r"singleadm\('([a-z]*)'\)" ,link_button.get('onclick'))
                if not m:
                    continue
                module = m.group(1)
                link_button['href'] = module + "/" + module + ".html"
                modules.append(module)
            else:
                link_button.replaceWithChildren()
        Crawler(session, resp.url, self.admin_path).download_css(soup.find_all('link'))
        self.admin_path.joinpath('index.html').write_text(str(soup), encoding='utf-8')
        return modules 
