import requests
import os
import config
import re
import sys
from typing import List, Dict
from bs4 import BeautifulSoup, ResultSet

cookies = {
    'PHPSESSID':'dccfafabab5c8eca3f0e1c354d8e5e3c',
    'user': 'YjA3OTAyMDAxOuW%2BkOe2reismTpzdHVkZW50OuWQjOWtuA%3D%3D'
}

home_url = 'https://ceiba.ntu.edu.tw'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'
skip_courses_list = ['中文系大學國文網站']

class WeeklyContent():
    
    def __init__(self):
        pass
    
class Course():
    
    def __init__(self, semester, course_num, cname, ename, teacher, href):
        self.semester = semester
        self.course_num = course_num
        self.cname = cname
        self.ename = ename
        self.teacher = teacher
        self.href = href
        self.folder_name = "_".join([self.semester, self.cname, self.teacher])
        self.folder_path = os.path.join(config.download_dir, self.folder_name)
        self.course_sn = 0
    
    def __str__(self):
        return " ".join([self.cname, self.teacher, self.href])
    
    def download(self, session: requests.Session):
        current_url = session.get(self.href, cookies=cookies).url
        self.course_sn = re.search('course/[0-9a-f]+', current_url).group(0).strip('course/')
        url_getter = lambda x: module_url + "?csn=" + self.course_sn + "&default_fun=" + x + "&current_lang=chinese" # TODO:language
        self.__download_syllabus(session, url_getter('syllabus'))
    
    def __download_syllabus(self, session: requests.Session, url: str):
        soup = BeautifulSoup(session.get(url, cookies=cookies).content, 'html.parser')
        table = soup.find('table')
        trs = table.find_all('tr')
        for tr in trs[1:]: # skip table header
            cols = tr.find_all('td')
            links = [x.get('href') for x in cols[3].find_all('a')]
            cols = [ele.text.strip() for ele in cols]
            print(cols, links)
        

class Session():
    
    def __init__(self):
        self.cookies = []
        self.courses: List[Course] = []
        self.sess: requests.Session = requests.session()
        
    def get_courses_list(self):
        soup = BeautifulSoup(self.sess.get('https://ceiba.ntu.edu.tw/student/index.php?seme_op=109-2', cookies=cookies).content, 'html.parser') # TODO: all
        table = soup.find_all("table")[0] # tables[1] is the courses not set up in ceiba
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            href = cols[4].find('a').get('href')
            cols = [ele.text.strip() for ele in cols]
            name = cols[4].split('\n')
            cname = name[0].strip()
            if cname in skip_courses_list:
                continue
            ename = name[1] if len(name) > 1 else ""
            self.courses.append(Course(cols[0], cols[2], cname, ename, cols[5], href))
        
    def mkdir(self):
        for course in self.courses:
            os.mkdir(course.folder_path)

    def download_courses(self):
        for course in self.courses[:1]:
            course.download(self.sess)

session = Session()
session.get_courses_list()
# session.mkdir()
session.download_courses()