import logging
import os
from typing import List, Union
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import Signal
from pathlib import Path

from . import strings, util
from .course import Course
from .crawler import Crawler
from .exceptions import (InvalidCredentials, InvalidFilePath,
                        InvalidLoginParameters)


class Ceiba():
    def __init__(self,
                 cookie_PHPSESSID=None,
                 cookie_user=None,
                 username=None,
                 password=None):

        self.sess: requests.Session = requests.session()
        self.courses: List[Course] = []
        self.sess.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
        })
        self.student_name = ""
        self.path = ""
        self.username = ""
        self.password = ""
        self.course_dir_map = {}  # cname map to dir

        if cookie_PHPSESSID and cookie_user:
            self.sess.cookies.set("PHPSESSID", cookie_PHPSESSID)
            self.sess.cookies.set("user", cookie_user)
        elif username and password:
            self.username = username
            self.password = password
        else:
            raise InvalidLoginParameters

    def login_user(self):
        logging.info('正在嘗試登入 Ceiba...')
        resp = util.get(self.sess, util.login_url)
        payload = {'user': self.username, 'pass': self.password}
        resp = util.post(self.sess, resp.url, data=payload)  # will get resp that redirect to /ChkSessLib.php
        if '登入失敗' in resp.content.decode('utf-8'):
            raise InvalidCredentials
        resp = util.post(self.sess, resp.url, data=payload)  # idk why it needs to post twice
        logging.info('登入 Ceiba 成功！')

    def login(self, progress: Signal = None):
        if len(self.username) > 0 and len(self.password) > 0:
            self.login_user()
            if progress:
                progress.emit(1)

        # check if user credential is correct
        soup = BeautifulSoup(util.get(self.sess, util.courses_url).content, 'html.parser')
        if progress:
            progress.emit(1)
        try:
            self.student_name = soup.find("span", {"class": "user"}).text
        except AttributeError:
            raise InvalidCredentials

    def get_courses_list(self, progress: Signal = None):

        logging.info('正在取得課程...')
        soup = BeautifulSoup(
            util.get(self.sess, util.courses_url).content, 'html.parser')
        for br in soup.find_all("br"):
            br.replace_with("\n")

        # tables[1] is the courses not set up in ceiba
        table = soup.find_all("table")[0]
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            href = cols[4].find('a').get('href')
            cols = [ele.text.strip() for ele in cols]
            name = cols[4].split('\n')
            cname = name[0].strip()
            if cname in util.skip_courses_list:
                continue
            ename = name[1] if len(name) > 1 else ""
            course = Course(semester=cols[0],
                            course_num=cols[2],
                            cname=cname,
                            ename=ename,
                            teacher=cols[5],
                            href=href)
            self.courses.append(course)
            self.course_dir_map[cname] = course.folder_name
        logging.info('取得課程完畢！')
        return self.courses

    def download_courses(self,
                         path: Union[Path, str],
                         cname_filter=None,
                         modules_filter=None,
                         progress: Signal = None):

        self.path = Path(path) if type(path) == str else path
        self.courses_dir = self.path / "courses"

        try:
            if len(path) == 0:
                raise FileNotFoundError
            self.courses_dir.mkdir(parents=True, exist_ok=True)
        except FileNotFoundError:
            raise InvalidFilePath

        logging.info('開始下載課程...')
        for course in self.courses:
            if cname_filter is None or course.cname in cname_filter:
                logging.info(strings.course_download_info.format(course.cname))
                self.courses_dir.joinpath(course.folder_name).mkdir(exist_ok=True)
                course.download(self.courses_dir, self.sess, modules_filter,
                                progress)
                logging.info(strings.course_finish_info.format(course.cname))
        self.download_ceiba_homepage(self.path, cname_filter, progress=progress)
        logging.info('完成下載！')

    def download_ceiba_homepage(self,
                                path: Union[Path,str],
                                cname_filter=None,
                                progress: Signal = None):
        
        self.path = Path(path) if type(path) == str else path

        logging.info('開始下載 Ceiba 首頁！')
        if progress:
            progress.emit(0)
        resp = util.get(self.sess, util.courses_url)
        soup = BeautifulSoup(resp.content, 'html.parser')

        Crawler(self.sess, resp.url, self.path).download_css(soup.find_all('link'))

        rows = soup.find_all("table")[0].find_all('tr')
        valid_a_tag = set()
        for row in rows[1:]:
            cols = row.find_all('td')
            course = cols[4].find('a')
            if course.text in util.skip_courses_list or (
                    cname_filter is not None
                    and course.text not in cname_filter):
                course.replaceWithChildren()
                row['style'] = 'background: silver;'
                continue
            course['href'] = "courses/" + self.course_dir_map[
                course.text] + '/index.html'
            valid_a_tag.add(course)

        for a in soup.find_all('a'):
            if a not in valid_a_tag:
                a.replaceWithChildren()

        for op in soup.find_all('option'):
            op.extract()

        self.path.joinpath('index.html').write_text(str(soup), encoding='utf-8')

        logging.info('下載首頁完成！')
