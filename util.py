import re
import strings
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import os
from collections import namedtuple

home_url = 'https://ceiba.ntu.edu.tw'
login_url = 'https://ceiba.ntu.edu.tw/ChkSessLib.php'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'
courses_url = 'https://ceiba.ntu.edu.tw/student/index.php?seme_op=107-2'
button_url = 'https://ceiba.ntu.edu.tw/modules/button.php'
skip_courses_list = ['中文系大學國文網站']
Link = namedtuple('Link', ['name', 'url'])


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
            print(strings.object_download_info.format(self.cname, args[3]))
            func(self, *args)
            print(strings.object_finish_info.format(self.cname, args[3]))
        return wrap
    return decorator
