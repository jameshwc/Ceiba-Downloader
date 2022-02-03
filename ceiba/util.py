from http.client import RemoteDisconnected
import logging
import re
import time

from requests import Session, Response
# import appdirs

from .strings import strings
from .exceptions import CrawlerConnectionError
from pathlib import Path
from abc import abstractclassmethod

# from pathlib import Path

CONNECT_RETRY_MAX = 10
REQUESTS_TIMEOUT = 300

home_url = 'https://ceiba.ntu.edu.tw'
login_url = 'https://ceiba.ntu.edu.tw/ChkSessLib.php'
login_alternative_url = 'https://ceiba.ntu.edu.tw/index.php?error_check=OK'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'
courses_url = 'https://ceiba.ntu.edu.tw/student/index.php?seme_op=all'
alternative_courses_url = 'https://ceiba.ntu.edu.tw/ta/index.php?seme_op=all'
alternative_info_url = 'https://ceiba.ntu.edu.tw/ta/?op=personal'
info_url = 'https://ceiba.ntu.edu.tw/student/?op=personal'
button_url = 'https://ceiba.ntu.edu.tw/modules/button.php'
banner_url = 'https://ceiba.ntu.edu.tw/modules/banner.php'
homepage_url = 'https://ceiba.ntu.edu.tw/modules/index.php'
skip_courses_list = ['中文系大學國文網站']

cname_map = {
    'bulletin': '公佈欄', 'syllabus': '課程大綱', 'hw': '作業',
    'info': '課程資訊', 'personal': '教師資訊', 'grade': '學習成績',
    'board': '討論看板', 'calendar': '課程行事曆', 'share': '資源分享',
    'vote': '投票區', 'student': '修課學生'}
ename_map = {v: k for k, v in cname_map.items()}

default_skip_href_texts = ['友善列印', '分頁顯示']
board_skip_href_texts = default_skip_href_texts + [
                '看板列表', '最新張貼', '排行榜', '推薦文章', '搜尋文章', '發表紀錄',
                ' 新增主題', '引用', ' 回覆', '分頁顯示', '上個主題', '下個主題',
                '修改', '上一頁', '下一頁', ' 我要評分', ' 我要推薦']
student_skip_href_texts = default_skip_href_texts + ['上頁', '下頁']

ticket_url = 'https://xk4axzhtgc.execute-api.us-east-2.amazonaws.com/Practicing/message'

def get_valid_filename(name: str) -> str:
    s = str(name).strip().replace(' ', '_').replace('/', '-')
    s = re.sub(r'(?u)[^-\w.]', '_', s)
    return s

def progress_decorator():
    def decorator(func):
        def wrap(self, *args):
            name = self.cname if strings.lang == 'zh-tw' else self.ename
            logging.info(
                strings.object_download_info.format(name, args[1]))
            ret = func(self, *args)
            logging.info(strings.object_finish_info.format(
                name, args[1]))
            return ret

        return wrap

    return decorator

# alternative function for python3.10 pathlib.Path.is_relative_to
def is_relative_to(self: Path, other: Path) -> bool:
    try:
        self.relative_to(other)
        return True
    except ValueError:
        return False

def get(session: Session, url: str) -> Response:
    return loop_connect(session.get, url)

def post(session: Session, url: str, data=None) -> Response:
    return loop_connect(session.post, url, data=data)

def loop_connect(http_method_func, url, **kwargs) -> Response:
    count = 0
    while count < CONNECT_RETRY_MAX:
        try:
            return http_method_func(url, timeout=REQUESTS_TIMEOUT, **kwargs)
        except Exception as e:
            if type(e) in [TimeoutError, ConnectionResetError, RemoteDisconnected]:
                logging.error(strings.crawler_timeout_error)
            else:
                logging.error(e, exc_info=True)
                logging.debug(strings.urlf.format(url))
                logging.warning(strings.retry_after_five_seconds)
            count += 1
            time.sleep(5)
    
    logging.warning(strings.warning_max_retries_exceeded)
    raise CrawlerConnectionError(url)