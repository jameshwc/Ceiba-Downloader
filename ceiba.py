from PySide6.QtWidgets import QProgressBar
import requests
import logging
import os
import util
import strings
from course import Course
from typing import List
from exceptions import InvalidLoginParameters, InvalidCredentials
from qt_custom_widget import PyLogOutput

class Ceiba():
    
    def __init__(
            self,
            cookie_PHPSESSID=None,
            cookie_user=None,
            username=None,
            password=None):

        self.sess: requests.Session = requests.session()
        self.courses: List[Course] = []
        self.sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'})
        self.student_name = ""
        self.path = ""
        self.username = ""
        self.password = ""

        if cookie_PHPSESSID and cookie_user:
            self.sess.cookies.set("PHPSESSID", cookie_PHPSESSID)
            self.sess.cookies.set("user", cookie_user)
        elif username and password:
            self.username = username
            self.password = password
        else:
            raise InvalidLoginParameters

    def login_user(self):
        resp = self.sess.get(util.login_url)
        logging.info('正在嘗試登入 Ceiba...')
        payload = {'user': self.username, 'pass': self.password}
        # will get resp that redirect to /ChkSessLib.php
        resp = self.sess.post(resp.url, data=payload)
        # idk why it needs to post twice
        resp = self.sess.post(resp.url, data=payload)
        if '登入失敗' in resp.content.decode('utf-8'):
            raise InvalidCredentials
        logging.info('登入 Ceiba 成功！')

    def login(self):
        if len(self.username) > 0 and len(self.password) > 0:
            self.login_user()
        
        # check if user credential is correct
        soup = util.beautify_soup(self.sess.get(util.courses_url).content)
        self.student_name = soup.find("span", {"class": "user"}).text
        if self.student_name == "":
            raise InvalidCredentials

    def get_courses_list(self):
        
        logging.info('正在取得課程...')
        soup = util.beautify_soup(self.sess.get(util.courses_url).content)
        
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
            self.courses.append(
                Course(
                    semester=cols[0],
                    course_num=cols[2],
                    cname=cname,
                    ename=ename,
                    teacher=cols[5],
                    href=href
                ))
        return self.courses

    def download_courses(self, path: str, cname_filter_list=None, modules_filter=None, progress_bar: QProgressBar = None):
        for course in self.courses:
            if cname_filter_list is None or course.cname in cname_filter_list:
                logging.info(strings.course_download_info.format(course.cname))
                
                os.makedirs(path, exist_ok=True)
                progress_val = progress_bar.value()
                course.download(path, self.sess, modules_filter, progress_bar)
                progress_bar.setValue(progress_val + len(modules_filter))
                
                logging.info(strings.course_finish_info.format(course.cname))
            