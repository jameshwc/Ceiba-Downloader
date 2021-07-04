import requests
from selenium import webdriver
import config
import os
import re

home_url = 'https://ceiba.ntu.edu.tw'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'
skip_courses_list = ['中文系大學國文網站']

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
        return self.cname + self.teacher + self.href
    
    def download(self, driver):
        driver.get(self.href)
        self.course_sn = re.search('course/[0-9a-f]+', driver.current_url).group(0).strip('course/')
        print(self.course_sn)
        url_getter = lambda x: module_url + "?csn=" + self.course_sn + "&default_fun=" + x + "&current_lang=chinese" # TODO:language
        self.__download_syllabus(driver, url_getter('syllabus'))
    
    def __download_syllabus(self, driver, url):
        driver.get(url)
        table = driver.find_element_by_tag_name('table')
        trs = table.find_elements_by_tag_name('tr')
        for tr in trs[1:]: # skip table header
            
        

class Session():
    
    def __init__(self):
        self.cookies = []
        self.courses = []
        self.driver = webdriver.Chrome()
        self.login()
        
    def login(self):
        self.driver.get(home_url)
        login_buttons = self.driver.find_elements_by_class_name('btn')
        assert len(login_buttons) >= 3
        login_buttons[2].click()
        
        self.driver.find_element_by_name("user").send_keys(config.username)
        self.driver.find_element_by_name("pass").send_keys(config.password)
        self.driver.find_element_by_name("Submit").click()
    
    def get_courses_list(self):
        self.driver.get('https://ceiba.ntu.edu.tw/student/index.php?seme_op=109-2') # TODO: all
        table = self.driver.find_elements_by_tag_name("table")[0] # tables[1] is the courses not set up in ceiba
        trs = table.find_elements_by_tag_name("tr")
        for tr in trs[1:]: # skip table's head
            tds = tr.find_elements_by_tag_name("td")
            name = tds[4].text.split('\n')
            cname = name[0].strip()
            if cname in skip_courses_list:
                continue
            ename = name[1] if len(name) > 1 else ""
            href = tds[4].find_element_by_tag_name("a").get_attribute('href')
            self.courses.append(Course(tds[0].text, tds[2].text, cname, ename, tds[5].text, href))
    
    def mkdir(self):
        for course in self.courses:
            os.mkdir(course.folder_path)

    def download_courses(self):
        for course in self.courses[:1]:
            course.download(self.driver)

session = Session()
session.get_courses_list()
# session.mkdir()
session.download_courses()