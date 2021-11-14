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
        url_getter = lambda x: util.module_url + "?csn=" + self.course_sn + "&default_fun=" + x + "&current_lang=chinese" # TODO:language
        # self.__download(session, url_getter('syllabus'), 'syllabus', '課程大綱')
        # self.__download(session, url_getter('hw'), 'homeworks', '作業')
        self.__html_download(session, url_getter('bulletin'), 'bulletin', '公佈欄')

    def __html_download(self, session: requests.Session, url: str, obj: str, obj_cname: str):
        resp = session.get(url)
        if any(x in resp.content.decode('utf-8') for x in ['此功能並未開啟', '目前無指派作業']):
            print(strings.cancel_on_object.format(self.cname, obj_cname, obj_cname))
            return
        soup = util.beautify_soup(resp.content)
        try:
            trs = soup.find('table').find_all('tr')
        except AttributeError:
            print(strings.wrong_with_object.format(obj_cname, self.cname, obj_cname))
            input(strings.wrong_with_alert)
            return

        contents = []
        dir = os.path.join(self.path, obj)
        os.makedirs(dir, exist_ok=True)
        handler = self.__handler_factory(obj, html=True)

        # for tr in tqdm(trs[1:]):
        for tr in trs[1:]:
            content = handler(session, tr, url, dir)
            contents.append(content)
        
        c = Crawler(session, url, dir, 'bulletin.html')
        c.crawl(is_table=True, )

    @util.progress_decorator()
    def __download(self, session: requests.Session, url: str, obj: str, obj_cname: str):
        resp = session.get(url)
        if any(x in resp.content.decode('utf-8') for x in ['此功能並未開啟', '目前無指派作業']):
            print(strings.cancel_on_object.format(self.cname, obj_cname, obj_cname))
            return
        soup = util.beautify_soup(resp.content)
        try:
            trs = soup.find('table').find_all('tr')
        except AttributeError:
            print(strings.wrong_with_object.format(obj_cname, self.cname, obj_cname))
            input(strings.wrong_with_alert)
            return

        contents = []
        dir = os.path.join(self.path, obj)
        os.makedirs(dir, exist_ok=True)
        handler = self.__handler_factory(obj)

        # for tr in tqdm(trs[1:]):
        for tr in trs[1:]:
            content = handler(session, tr, url, dir)
            contents.append(content)

        headers = [x.text.strip() for x in trs[0].find_all('th')]
        with open(os.path.join(dir, obj + ".csv"), "w", newline='', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(contents)

    def __handler_factory(self, obj: str, html=False):
        if html:
            if obj == "bulletin":
                return self.__handler_html_bulletins
        if obj == "syllabus":
            return self.__handler_syllabus
        elif obj == "homeworks":
            return self.__handler_homeworks
        elif obj == "bulletin":
            return self.__handler_bulletins

    def __handler_html_bulletins(self, session, tr, url, dir):
        pass

    def __handler_bulletins(self, session, tr, url, dir):
        cols = tr.find_all('td')
        link = urljoin(urljoin(url, 'bulletin/'), cols[2].find('a').get('href'))
        Bulletin = namedlist('Bulletin', ('no', 'date', 'title', 'deadline'))
        cols = Bulletin(*[ele.text.strip() for ele in cols])
        folder_name = util.get_valid_filename("_".join([cols.no.zfill(3), cols.date, cols.title]))
        folder_path = os.path.join(dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        self.__download_bulletin(session, cols[0], link, folder_path)
        return cols[:]

    def __handler_syllabus(self, session, tr: BeautifulSoup, url, dir):
        columns = ('week', 'date', 'title', 'files')
        Syllabus = namedlist('Syllabus', columns, default=(None, ) * len(columns))
        cols = Syllabus(*tr.find_all('td'))
        links = [(x.text.strip(), urljoin(url, x.get('href'))) for x in cols.files.find_all('a')]
        cols = Syllabus(*[ele.text.strip() for ele in cols[:3]])
        if len(links) > 0:
            cols.files = "\n".join([x[0] for x in links])
        content = cols[:]
        cols.title = cols.title.split('\n')[0][:15]
        folder_name = "_".join([util.get_valid_filename(x) for x in [cols.week, cols.date, cols.title]])
        folder_path = os.path.join(dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        for doc in links:
            self.__download_document(session, doc[0], doc[1], folder_path)
        return content

    def __handler_homeworks(self, session, tr, url, dir):
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
        folder_path = os.path.join(dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        # self.__download(session, link, "homework", "作業")
        self.__download_homework(session, cols[0], link, folder_path)
        return cols[:]

    def __handler_homework(self, session, tr, url, dir):
        head_text = tr.find('th').text.strip()
        if head_text == "檔案上傳":
            return
        td = tr.find('td')
        content = td.text.replace(u'\xa0', ' ').strip()
        links = [(x.text.strip(), urljoin(url, x.get('href'))) for x in td.find_all('a')]
        if len(links) > 0:
            for link in links:
                if len(link[0]) > 0:  # skip downloading no-text link since it may be empty file.
                    self.__download_document(session, link[0], link[1], dir)
        return content

    def __download_bulletin(self, session, name, url, path):
        content = session.get(url).content
        soup = util.beautify_soup(content)
        trs = soup.find('table').find_all('tr')
        header = []
        content = []
        for tr in trs[1:]:
            head_text = tr.find('th').text.strip()
            header.append(head_text)
            td = tr.find('td')
            content.append(td.text.replace(u'\xa0', ' ').strip())
            if head_text == "相關附檔":
                if len(td.text.strip()) > 0:
                    links = [util.Link(x.text.strip(), urljoin(url, x.get('href'))) for x in td.find_all('a')]
                    for link in links:
                        self.__download_document(session, link.name, link.url, path)
        with open(os.path.join(path, name + ".csv"), 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerow(content)

    def __download_homework(self, session, name, url, path):
        soup = util.beautify_soup(session.get(url).content)
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
            links = [util.Link(x.text.strip(), urljoin(url, x.get('href'))) for x in td.find_all('a')]
            if len(links) > 0:
                for link in links:
                    if len(link.name) > 0:  # skip downloading no-text link since it may be empty file.
                        if link.name == "檔案":  # don't use such text as filename; use info from url instead.
                            self.__download_document(session, link.url.split('/')[-1], link.url, path)
                        else:
                            self.__download_document(session, link.name, link.url, path)
        with open(os.path.join(path, name + ".csv"), "w", newline='', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerow(content)

    def __download_homework_eval(self, session: requests.Session, url):
        soup = util.beautify_soup(session.get(url).content)
        table = soup.find('table')
        tr = table.find_all('tr')[1]
        cols = [x.text.strip() for x in tr.find_all('td')]
        return "成績：{}\n作業評語：{}".format(cols[1], cols[2])

    def __download_document(self, session: requests.Session, name, url, path):
        path = Path(os.path.join(path, util.get_valid_filename(name)))  # TODO: check if filename exists
        try:
            resp = session.get(url)
        except Exception:
            print(strings.wrong_with_downloading_url.format(name, url))
            input(strings.wrong_with_alert)
            return
        path.write_bytes(resp.content)
