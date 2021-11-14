import requests
import os
import config
import util
import strings
from course import Course
from typing import List
from exceptions import InvalidLoginParameters, InvalidCredentials


class Ceiba():

    def __init__(
            self,
            cookie_PHPSESSID=None,
            cookie_user=None,
            username=None,
            password=None):

        self.sess: requests.Session = requests.session()
        self.courses: List[Course] = []

        if cookie_PHPSESSID and cookie_user:
            self.sess.cookies.set("PHPSESSID", config.PHPSESSID)
            self.sess.cookies.set("user", config.USER)
        elif username and password:
            self.login_user(self.sess, username, password)
        else:
            raise InvalidLoginParameters

    def login_user(self, session: requests.Session, username, password):
        resp = session.get(util.login_url)
        payload = {'user': username, 'pass': password}
        # will get resp that redirect to /ChkSessLib.php
        resp = session.post(resp.url, data=payload)
        # idk why it needs to post twice
        resp = session.post(resp.url, data=payload)
        if '登入失敗' in resp.content.decode('utf-8'):
            raise InvalidCredentials

    def get_courses_list(self):
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
                    href=href))
        print(len(self.courses))

    def download_courses(self):
        for course in self.courses:
            print(strings.course_download_info.format(course.cname))
            os.makedirs(course.path, exist_ok=True)
            course.download(self.sess)
            print(strings.course_finish_info.format(course.cname))


if __name__ == "__main__":
    ceiba = Ceiba(username=config.username, password=config.password)
    ceiba.get_courses_list()
    ceiba.download_courses()
