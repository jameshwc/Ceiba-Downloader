import logging
import datetime
import json
from typing import List, Union, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import SignalInstance
from pathlib import Path
import uuid

from . import util
from .strings import strings
from .course import Course
from .crawler import Crawler
from .exceptions import (InvalidCredentials, InvalidFilePath,
                        InvalidLoginParameters, NullTicketContent, SendTicketError)


class Ceiba():
    def __init__(self):

        self.sess: requests.Session = requests.session()
        self.courses: List[Course] = []
        self.sess.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
        })
        self.student_name = ""
        self.email = "Not Login"
        self.username = ""
        self.password = ""
        self.course_dir_map = {}  # cname map to dir
        self.is_login = False

    def login_user(self, username, password):
        logging.info(strings.try_to_login)
        resp = util.get(self.sess, util.login_url)
        payload = {'user': username, 'pass': password}
        resp = util.post(self.sess, resp.url, data=payload)  # will get resp that redirect to /ChkSessLib.php
        if '登入失敗' in resp.content.decode('utf-8'):
            raise InvalidCredentials
        resp = util.post(self.sess, resp.url, data=payload)  # idk why it needs to post twice
        logging.info(strings.login_successfully)

    def login(self, 
              cookie_PHPSESSID: Optional[str] = None, 
              username: Optional[str] = None,
              password: Optional[str] = None,
              progress: Optional[SignalInstance] = None):
        
        if cookie_PHPSESSID:
            self.sess.cookies.set("PHPSESSID", cookie_PHPSESSID)
            # self.sess.cookies.set("user", cookie_user)
        elif username and password:
            self.login_user(username, password)
            if progress:
                progress.emit(1)
        else:
            raise InvalidLoginParameters
        
        # check if user credential is correct
        soup = BeautifulSoup(util.get(self.sess, util.info_url).content, 'html.parser')
        if progress:
            progress.emit(1)
        try:
            trs = soup.find_all("tr")
            self.student_name = trs[0].find('td').text
            self.email = trs[5].find('td').text
            self.is_login = True
        except AttributeError as e:
            raise InvalidCredentials from e

    def get_courses_list(self, progress: Optional[SignalInstance] = None):

        logging.info(strings.try_to_get_courses)
        soup = BeautifulSoup(
            util.get(self.sess, util.courses_url).content, 'html.parser')

        # tables[1] is the courses not set up in ceiba
        table = soup.find_all("table")[0]
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            href = cols[4].find('a').get('href')
            cols = [ele.text.strip() for ele in cols]
            name = cols[4].split('\xa0')
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
        logging.info(strings.get_courses_successfully)
        return self.courses

    def download_courses(self,
                         path: Union[Path, str],
                         cname_filter=None,
                         modules_filter=None,
                         progress: Optional[SignalInstance] = None):

        self.path = Path(path)
        self.courses_dir = self.path / "courses"
        
        try:
            if type(path) == str and len(path) == 0:
                raise FileNotFoundError
            self.courses_dir.mkdir(parents=True, exist_ok=True)
        except FileNotFoundError:
            raise InvalidFilePath

        logging.info(strings.start_downloading_courses)
        for course in self.courses:
            if cname_filter is None or course.cname in cname_filter:
                logging.info(strings.course_download_info.format(course.cname))
                self.courses_dir.joinpath(course.folder_name).mkdir(exist_ok=True)
                course.download(self.courses_dir, self.sess, modules_filter,
                                progress)
                logging.info(strings.course_finish_info.format(course.cname))
        self.download_ceiba_homepage(self.path, cname_filter, progress=progress)
        logging.info(strings.download_courses_successfully)

    def download_ceiba_homepage(self,
                                path: Union[Path,str],
                                cname_filter=None,
                                progress: Optional[SignalInstance] = None):
        
        self.path = Path(path)

        logging.info(strings.start_downloading_homepage)
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

        logging.info(strings.download_homepage_successfully)

    def send_ticket(self, ticket_type: str, content: str, anonymous=False):
        if len(content.strip()) == 0:
            raise NullTicketContent
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        mac_addr = hex(uuid.getnode())
        id = timestamp + "-" + mac_addr
        payload = {'id': id, 'type': ticket_type, 'content': content, 'timestamp': timestamp, 'mac_addr': mac_addr}
        if not anonymous:
            payload['email'] = self.email
        resp = self.sess.post(util.ticket_url, json.dumps(payload))
        if resp.status_code == 200 and resp.content == b'"Success"':
            return
        else:
            raise SendTicketError(resp.content)
    
    def set_lang(self, lang: str):
        strings.set_lang(lang)