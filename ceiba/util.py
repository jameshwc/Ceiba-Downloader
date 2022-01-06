import logging
import re
import time

from requests import Session
# import appdirs
from bs4 import BeautifulSoup

from .strings import strings

# from pathlib import Path

home_url = 'https://ceiba.ntu.edu.tw'
login_url = 'https://ceiba.ntu.edu.tw/ChkSessLib.php'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'
courses_url = 'https://ceiba.ntu.edu.tw/student/index.php?seme_op=all'
info_url = 'https://ceiba.ntu.edu.tw/student/?op=personal'
button_url = 'https://ceiba.ntu.edu.tw/modules/button.php'
banner_url = 'https://ceiba.ntu.edu.tw/modules/banner.php'
homepage_url = 'https://ceiba.ntu.edu.tw/modules/index.php'
skip_courses_list = ['中文系大學國文網站']
cname_map = {
    'bulletin': '公佈欄',
    'syllabus': '課程大綱',
    'hw': '作業',
    'info': '課程資訊',
    'personal': '教師資訊',
    'grade': '學習成績',
    'board': '討論看板',
    'calendar': '課程行事曆',
    'share': '資源分享',
    'vote': '投票區',
    'student': '修課學生'
}

ticket_url = 'https://xk4axzhtgc.execute-api.us-east-2.amazonaws.com/Practicing/message'

def get_valid_filename(name: str):
    s = str(name).strip().replace(' ', '_').replace('/', '-')
    s = re.sub(r'(?u)[^-\w.]', '_', s)
    return s


def progress_decorator():
    def decorator(func):
        def wrap(self, *args):
            logging.info(
                strings.object_download_info.format(self.cname, args[1]))
            ret = func(self, *args)
            logging.info(strings.object_finish_info.format(
                self.cname, args[1]))
            return ret

        return wrap

    return decorator


def get(session: Session, url: str):
    return loop_connect(session.get, url)

def post(session: Session, url: str, data=None):
    return loop_connect(session.post, url, data=data)

def loop_connect(http_method_func, url, **kwargs):
    while True:
        try:
            response = http_method_func(url, **kwargs)
        # except (TimeoutError, ConnectionResetError):
        except Exception as e:
            if type(e) == TimeoutError or type(e) == ConnectionResetError:
                logging.error(strings.crawler_timeour_error)
            else:
                logging.error(e)
                logging.debug("發生錯誤的網址：{}".format(url))
                logging.info('五秒後重新連線...')
            time.sleep(5)
            continue
        return response