import re
import strings
from bs4 import BeautifulSoup
import appdirs
import os
import json
from pathlib import Path
home_url = 'https://ceiba.ntu.edu.tw'
login_url = 'https://ceiba.ntu.edu.tw/ChkSessLib.php'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'
courses_url = 'https://ceiba.ntu.edu.tw/student/index.php?seme_op=107-2'
button_url = 'https://ceiba.ntu.edu.tw/modules/button.php'
banner_url = 'https://ceiba.ntu.edu.tw/modules/banner.php'
homepage_url = 'https://ceiba.ntu.edu.tw/modules/index.php'
skip_courses_list = ['中文系大學國文網站']
data_dir = Path(appdirs.user_data_dir('ceiba-downloader', 'jameshwc'))
data_dir.mkdir(parents=True, exist_ok=True)

crawled_courses = json.load(os.path.join(data_dir, 'courses.json'))


def get_valid_filename(name: str):
    s = str(name).strip().replace(' ', '_').replace('/', '-')
    s = re.sub(r'(?u)[^-\w.]', '_', s)
    return s


def beautify_soup(content: bytes):
    soup = BeautifulSoup(content, 'html.parser')
    for br in soup.find_all("br"):
        br.replace_with("\n")
    return soup


def progress_decorator():
    def decorator(func):
        def wrap(self, *args):
            print(strings.object_download_info.format(self.cname, args[1]))
            ret = func(self, *args)
            print(strings.object_finish_info.format(self.cname, args[1]))
            return ret
        return wrap
    return decorator
