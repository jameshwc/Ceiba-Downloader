import requests
import os
import config
import util
import strings
import re
import csv
from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from namedlist import namedlist
from crawler import Crawler


class Course():

    def __init__(self, semester, course_num, cname, ename, teacher, href):
        self.semester = semester
        self.course_num = course_num
        self.cname = cname
        self.ename = ename
        self.teacher = teacher
        self.href = href
        self.folder_name = util.get_valid_filename("_".join([self.semester, self.cname, self.teacher]))
        self.path = os.path.join(config.download_dir, self.folder_name)
        self.course_sn = 0

    def __str__(self):
        return " ".join([self.cname, self.teacher, self.href])

    def download(self, session: requests.Session):
        current_url = session.get(self.href).url
        self.course_sn = re.search('course/[0-9a-f]+', current_url).group(0).strip('course/')
        # self.__html_download(session, 'bulletin', 'bulletin', '公佈欄')
        # self.__html_download(session, 'syllabus', 'syllabus', '課程大綱')
        # self.__html_download(session, 'homeworks', 'hw', '作業')


    @util.progress_decorator()
    def __html_download(self, session: requests.Session, obj: str, module: str, obj_cname: str):
        url = util.module_url + "?csn=" + self.course_sn + "&default_fun=" + module + "&current_lang=chinese" # TODO:language
        resp = session.get(url)
        if any(x in resp.content.decode('utf-8') for x in ['此功能並未開啟', '目前無指派作業']):
            print(strings.cancel_on_object.format(self.cname, obj_cname, obj_cname))
            return

        dir = os.path.join(self.path, obj)
        os.makedirs(dir, exist_ok=True)

        c = Crawler(session, url, dir, obj + '.html')
        c.crawl(is_table=True, obj=module + '/')
    
    @util.progress_decorator()
    def __homepage_download(self, session: requests.Session):
        button_url = util.button_url + "?csn=" + self.course_sn + "&default_fun=board&current_lang=chinese" # TODO:language
