import requests
import os
import config
import util
import strings
import re
import csv
from tqdm import tqdm
from typing import List, Dict
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from urllib.request import urlretrieve

cookies = {
    'PHPSESSID': config.PHPSESSID,
    'user': config.USER
}

home_url = 'https://ceiba.ntu.edu.tw'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'
courses_url = 'https://ceiba.ntu.edu.tw/student/index.php?seme_op=all'
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
        self.folder_name = util.get_valid_filename("_".join([self.semester, self.cname, self.teacher]))
        self.path = os.path.join(config.download_dir, self.folder_name)
        self.course_sn = 0
    
    def __str__(self):
        return " ".join([self.cname, self.teacher, self.href])
    
    def download(self, session: requests.Session):
        current_url = session.get(self.href, cookies=cookies).url
        self.course_sn = re.search('course/[0-9a-f]+', current_url).group(0).strip('course/')
        url_getter = lambda x: module_url + "?csn=" + self.course_sn + "&default_fun=" + x + "&current_lang=chinese" # TODO:language
        self.__download_syllabus(session, url_getter('syllabus'))
        self.__download_homeworks(session, url_getter('hw'))
    
    @util.progress_decorator("課程大綱")
    def __download_syllabus(self, session: requests.Session, url: str):
        resp = session.get(url, cookies=cookies)
        soup = util.beautify_soup(resp.content)
        table = soup.find('table')
        trs = table.find_all('tr')
        content = []
        syllabus_dir = os.path.join(self.path, 'syllabus')
        os.makedirs(syllabus_dir, exist_ok=True)
        for tr in tqdm(trs[1:]): # skip table header
            cols = tr.find_all('td')
            links = [(x.text.strip(), urljoin(url, x.get('href'))) for x in cols[3].find_all('a')]
            cols = [ele.text.strip() for ele in cols[:3]]
            if len(links) > 0:
                cols.append("\n".join([x[0] for x in links]))
            content.append(cols[:])
            cols[2] = cols[2].split('\n')[0][:15]
            folder_name = "_".join([util.get_valid_filename(x) for x in cols[:3]])
            folder_path = os.path.join(syllabus_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            for doc in links:
                self.__download_document(session, doc[0], doc[1], folder_path)
        
        headers = [x.text.strip() for x in trs[0].find_all('th')]
        with open(os.path.join(syllabus_dir, 'syllabus.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(content)

    @util.progress_decorator("作業")
    def __download_homeworks(self, session: requests.Session, url: str):
        resp = session.get(url, cookies=cookies)
        if '此功能並未開啟' in resp.content.decode('utf-8'):
            print(strings.cancel_on_homework.format(self.cname))
            return
        soup = util.beautify_soup(session.get(url, cookies=cookies).content)
        table = soup.find('table')
        trs = table.find_all('tr')
        content = []
        hw_dir = os.path.join(self.path, 'homework')
        os.makedirs(hw_dir, exist_ok=True)
        for tr in tqdm(trs[1:]):
            cols = tr.find_all('td')
            link = urljoin(urljoin(url, 'hw/'), cols[0].find('a').get('href'))
            eval_content = None
            if cols[7].find('a'):
                eval_link = urljoin(urljoin(url, 'hw/'), cols[7].find('a').get('href'))
                eval_content = self.__download_homework_eval(session, eval_link)
            cols = [ele.text.strip() for ele in cols[:7]]
            if eval_content:
                cols.append(eval_content)
            else:
                cols.append("")
            date = cols[4].split(' ')[0]
            folder_name = "_".join([date, cols[0]])
            folder_path = os.path.join(hw_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            self.__download_homework(session, cols[0], link, folder_path)
            content.append(cols[:])
        
        headers = [x.text.strip() for x in trs[0].find_all('th')]
        with open(os.path.join(hw_dir, "homework.csv"), "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(content)

    def __download_homework(self, session, name, url, path):
        soup = util.beautify_soup(session.get(url, cookies=cookies).content)
        table = soup.find('table')
        trs = table.find_all('tr')
        header = []
        content = []
        for tr in trs[1:]:
            head_text = tr.find('th').text.strip()
            if head_text == "檔案上傳":
                continue
            header.append(head_text)
            td = tr.find('td')
            content.append(td.text.replace(u'\xa0', ' ').strip())
            links = [(x.text.strip(), urljoin(url, x.get('href'))) for x in td.find_all('a')]
            if len(links) > 0:
                for link in links:
                    if len(link[0]) > 0: # skip downloading no-text link since it may be empty file.
                        self.__download_document(session, link[0], link[1], path)
        with open(os.path.join(path, name + ".csv"), "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerow(content)
    
    def __download_homework_eval(self, session: requests.Session, url):
        soup = util.beautify_soup(session.get(url, cookies=cookies).content)
        table = soup.find('table')
        tr = table.find_all('tr')[1]
        cols = [x.text.strip() for x in tr.find_all('td')]
        return "成績：{}\n作業評語：{}".format(cols[1], cols[2])

    def __download_document(self, session: requests.Session, name, url, path):
        path = Path(os.path.join(path, util.get_valid_filename(name))) # TODO: check if filename exists
        try:
            resp = session.get(url, cookies=cookies)
        except:
            print(strings.wrong_with_downloading_url.format(name, url))
            input(strings.wrong_with_alert)
            return
        path.write_bytes(resp.content)

    
class Ceiba():
    
    def __init__(self):
        self.cookies = []
        self.courses: List[Course] = []
        self.sess: requests.Session = requests.session()
        
    def get_courses_list(self):
        soup = util.beautify_soup(self.sess.get(courses_url, cookies=cookies).content)
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
        
    def download_courses(self):
        for course in self.courses:
            print(strings.course_download_info.format(course.cname))
            os.makedirs(course.path, exist_ok=True)
            course.download(self.sess)
            print(strings.course_finish_info.format(course.cname))

if __name__ == "__main__":
    ceiba = Ceiba()
    ceiba.get_courses_list()
    ceiba.download_courses()