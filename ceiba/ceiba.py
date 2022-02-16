from datetime import datetime
import json
import logging
import uuid
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet

from . import util
from .course import Course
from .crawler import Crawler
from .exceptions import (CheckForUpdatesError, InvalidCredentials,
                         InvalidFilePath, InvalidLoginParameters,
                         NullTicketContent, SendTicketError)
from .const import strings, Role

class Ceiba():
    def __init__(self):

        self.sess: requests.Session = requests.session()
        self.courses: List[Course] = []
        self.sess.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
        })
        self.student_name: str = ""
        self.email: str = "Not Login"
        self.course_dir_map: Dict[str, str] = {}  # cname map to dir
        self.is_login: bool = False
        self.is_alternative: bool = False
        # alternative users including ta, outside instructors & students, etc.
        try:
            with open('version.txt', 'r', encoding='utf-8') as f:
                self.version: str = f.read()
        except FileNotFoundError:
            self.version: str = "1.0"

    def login_user(self, username, password):
        logging.info(strings.try_to_login)
        resp = util.get(self.sess, util.login_url)
        payload = {'user': username, 'pass': password}
        resp = util.post(self.sess, resp.url, data=payload)  # will get resp that redirect to /ChkSessLib.php
        if any(x in resp.content.decode('utf-8') for x in ['登入失敗', '更改密碼']):
            raise InvalidCredentials
        resp = util.post(self.sess, resp.url, data=payload)  # idk why it needs to post twice

    def login_alternative_user(self, username: str, password: str):
        payload = {'loginid': username, 'password': password, 'op': 'login'}
        resp = util.post(self.sess, util.login_alternative_url, data=payload)  # will get resp that redirect to /ChkSessLib.php
        if '登出' not in resp.content.decode('utf-8'):
            raise InvalidCredentials
        
    def login(self, role: Role = Role.NTUer,
              cookie_PHPSESSID: Optional[str] = None, 
              username: Optional[str] = None,
              password: Optional[str] = None,
              progress = None):
        '''
        :param role: Integer. 0: NTUer, 1: TA, 2: Professor, 3: Outside NTU
        '''
        self.role = role
        
        if cookie_PHPSESSID:
            self.sess.cookies.set("PHPSESSID", cookie_PHPSESSID)
        elif username and password:
            if self.role == Role.NTUer:
                self.login_user(username, password)
            elif self.role == Role.TA or \
                 self.role == Role.Outside_Teacher or \
                 self.role == Role.Outside_Student:
                self.login_alternative_user(username, password)
            if progress:
                progress.emit(1)
        else:
            raise InvalidLoginParameters
        # check if user credential is correct
        
        info_url = util.info_url(self.role)

        soup = BeautifulSoup(util.get(self.sess, info_url).content, 'html.parser')
        if progress:
            progress.emit(1)
        try:
            trs = soup.find_all("tr")
            self.student_name = trs[0].find('td').text
            self.email = trs[5].find('td').text
            if self.role == Role.TA:  # ta
                self.email = trs[4].find('td').text
            self.id: str = self.email.split('@')[0]
            self.is_login = True
        except (AttributeError, IndexError) as e:
            raise InvalidCredentials from e
        logging.info(strings.login_successfully)

    def __get_courses_rows_from_homepage_table(self, soup) -> ResultSet:
        table: Tag = soup.find_all("table")[0]
        rows = table.find_all('tr')[1:]
        
        try:
            second_table: Tag = soup.find_all("table")[1] 
            # tables[1] may be audit courses or not-set-up-in-ceiba courses
            if '旁聽' in second_table.find_previous_sibling('h2').get_text():
                rows.extend(second_table.find_all('tr')[1:])
        except IndexError:
            pass
        
        return rows
            
    def get_courses_list(self):

        logging.info(strings.try_to_get_courses)
        courses_url = util.courses_url(self.role)
        
        soup = BeautifulSoup(
            util.get(self.sess, courses_url).content, 'html.parser')

        rows = self.__get_courses_rows_from_homepage_table(soup)
        
        count: int = 0
        row: Tag
        for row in rows:
            count += 1
            try:
                cols = row.find_all('td')
                href = cols[4].find('a').get('href')
                name = cols[4].get_text(strip=True, separator='\n').splitlines()
                
                admin_url = None
                if util.is_admin(self.role):
                    onclick_val = cols[len(cols)-1].find('input').get('onclick')
                    m = re.search(r"\'([0-9a-f]*)\'", onclick_val)
                    if m:
                        course_sn = m.group(1)
                    if self.role == Role.TA:
                        admin_url = util.ta_admin_url + course_sn
                    else:
                        admin_url = util.admin_url + course_sn

                cols = [ele.text.strip() for ele in cols]
                cname = name[0]
                if cname in util.skip_courses_list:
                    continue
                ename = name[1] if len(name) > 1 else cname
                if ename.startswith('http'):  # some courses have no ename but show their url (in ta's page)
                    ename = cname  # use cname instead

                course = Course(semester=cols[0],
                                course_num=cols[2],
                                cname=cname,
                                ename=ename,
                                teacher=cols[5],
                                href=href,
                                admin_url=admin_url)
                self.courses.append(course)
                self.course_dir_map[course.id] = course.folder_name
            except (IndexError, AttributeError) as e:
                logging.error(e, exc_info=True)
                logging.warning(strings.warning_fail_to_get_course.format(count))
        logging.info(strings.get_courses_successfully)
        return self.courses

    def download_courses(self,
                         path: Union[Path, str],
                         course_id_filter=None,
                         modules_filter=None,
                         progress = None):

        self.path = Path(path) / "-".join(["ceiba", self.id, datetime.today().strftime('%Y%m%d')])
        self.courses_dir = self.path / "courses"
        
        try:
            if type(path) == str and len(path) == 0:
                raise FileNotFoundError
            self.courses_dir.mkdir(parents=True, exist_ok=True)
        except FileNotFoundError:
            raise InvalidFilePath

        self.download_ceiba_homepage(path, course_id_filter)
        
        logging.info(strings.start_downloading_courses)
        for course in self.courses:
            course_name = course.cname if strings.lang == 'zh-tw' else course.ename
            if course_id_filter is None or course.id in course_id_filter:
                logging.info(strings.course_download_info.format(course_name))
                self.courses_dir.joinpath(course.folder_name).mkdir(exist_ok=True)
                try:
                    if self.role == Role.Professor or \
                        self.role == Role.Outside_Teacher or \
                        self.role == Role.TA:
                        course.download_admin(self.courses_dir, self.sess, progress)
                    else:
                        course.download(self.courses_dir, self.sess, modules_filter, progress)
                except Exception as e:
                    logging.error(e, exc_info=True)
                    logging.warning(strings.error_skip_and_continue_download_courses.format(course_name))
                    continue
                logging.info(strings.course_finish_info.format(course_name))
        logging.info(strings.download_courses_successfully)

    def download_ceiba_homepage(self,
                                path: Union[Path,str],
                                course_id_filter=None):
        
        self.path = Path(path) / "-".join(["ceiba", self.id, datetime.today().strftime('%Y%m%d')])
        
        try:
            if type(path) == str and len(path) == 0:
                raise FileNotFoundError
            self.path.mkdir(parents=True, exist_ok=True)
        except FileNotFoundError:
            raise InvalidFilePath
        
        logging.info(strings.start_downloading_homepage)
        
        courses_url = util.courses_url(self.role)

        resp = util.get(self.sess, courses_url)
        soup = BeautifulSoup(resp.content, 'html.parser')

        Crawler(self.sess, resp.url, self.path).download_css(soup.find_all('link'))

        rows = self.__get_courses_rows_from_homepage_table(soup)
        
        valid_a_tag = set()
        row: Tag
        for row in rows:
            try:
                cols = row.find_all('td')
                course = cols[4].find('a')
                cols = [ele.text.strip() for ele in cols]
                course_id = cols[0] + cols[2]
                if course.text in util.skip_courses_list or (
                        course_id_filter is not None
                        and course_id not in course_id_filter):
                    course.replaceWithChildren()
                    row['style'] = 'background: silver;'
                    continue
                course['href'] = "courses/" + self.course_dir_map[course_id] + '/index.html'
                if util.is_admin(self.role):
                    op = row.find('input', {'value': '管理'})
                    op.name = 'a'
                    op.string = '管理'
                    op['href'] = "courses/" + self.course_dir_map[course_id] + "/admin/index.html"
                    for attr in ['class', 'name', 'onclick', 'type', 'value']:
                        del op[attr]
                    valid_a_tag.add(op)
                valid_a_tag.add(course)
            except (IndexError, AttributeError) as e:
                logging.error(e, exc_info=True)
                logging.warning(strings.warning_partial_failure_on_homepage)

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
        timestamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        mac_addr = hex(uuid.getnode())
        id = timestamp + "-" + mac_addr
        payload = {'id': id, 'type': ticket_type, 'content': content, 'timestamp': timestamp, 
                   'mac_addr': mac_addr, 'version': self.version}
        if not anonymous:
            payload['email'] = self.email
        resp = self.sess.post(util.ticket_url, json.dumps(payload))
        if resp.status_code == 200 and resp.content == b'"Success"':
            logging.info(strings.send_ticket_successfully)
            return
        raise SendTicketError(resp.content)
    
    def check_for_updates(self) -> bool:
        try:
            resp = self.sess.get('https://raw.githubusercontent.com/jameshwc/Ceiba-Downloader/master/version.txt')
            version = str(resp.content, 'utf-8')
        except Exception as e:
            logging.error(e, exc_info=True)
            raise CheckForUpdatesError
        if version > self.version:
            return True
        return False
    
    def set_lang(self, lang: str):
        strings.set_lang(lang)
        