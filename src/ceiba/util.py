from http.client import RemoteDisconnected
import logging
from operator import truediv
import re
import time
import os
from requests import Session, Response
from typing import Callable
from pathlib import Path
from os.path import relpath

from .const import strings, Role, cname_map
from .exceptions import CrawlerConnectionError, StopDownload

CONNECT_RETRY_MAX = 10
REQUESTS_TIMEOUT = 300
PAUSE = False
STOP = False

home_url = 'https://ceiba.ntu.edu.tw'
login_url = 'https://ceiba.ntu.edu.tw/ChkSessLib.php'
login_alternative_url = 'https://ceiba.ntu.edu.tw/index.php?error_check=OK'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'

role_short = {Role.Student: 'student', Role.TA: 'ta', Role.Professor: 'teacher',
              Role.Outside_Student: 'student', Role.Outside_Teacher: 'outside_teacher'}
courses_url: Callable[[Role], str] = lambda role: 'https://ceiba.ntu.edu.tw/{}/index.php?seme_op=all'.format(role_short[role])
info_url: Callable[[Role], str] = lambda role: 'https://ceiba.ntu.edu.tw/{}/?op=personal'.format(role_short[role])

admin_module_urlgen = lambda module: 'https://ceiba.ntu.edu.tw/course_admin/{}/?fsw={}'.format(module, module)

button_url = 'https://ceiba.ntu.edu.tw/modules/button.php'
banner_url = 'https://ceiba.ntu.edu.tw/modules/banner.php'
homepage_url = 'https://ceiba.ntu.edu.tw/modules/index.php'

ta_admin_url = 'https://ceiba.ntu.edu.tw/course_ta_adm/?csno='
admin_url = 'https://ceiba.ntu.edu.tw/course_admin/?csno='
skip_courses_list = ['中文系大學國文網站']



admin_cname_map = {
    'ftp': '檔案上傳', 'user': '使用者', 'theme': '主題首頁',
    'info': '課程資訊', 'syllabus': '大綱內容', 'bulletin': '公佈欄',
    'calendar': '行事曆', 'board': '討論區', 'hw': '作業',
    'share': '資源分享', 'vote': '投票', 'grade': '成績', 'mail': '寄信'
}

full_cname_map = {**admin_cname_map, **cname_map}
admin_ename_map = {v: k for k, v in admin_cname_map.items()}
admin_ename_map['討論看板'] = 'board'

default_skip_href_texts = ['友善列印', '分頁顯示']
default_skip_href_texts_en = ['Printer Friendly', 'Show by Page']
board_skip_href_texts = default_skip_href_texts + [
                '看板列表', '最新張貼', '排行榜', '推薦文章', '搜尋文章', '發表紀錄',
                ' 新增主題', '引用', ' 回覆', '上個主題', '下個主題',
                '修改', ' 我要評分', ' 我要推薦']
board_skip_href_texts_en = default_skip_href_texts_en + [
    'Forum Index', 'New Posts', 'Ranking', 'Great Picks', 'Search', 'Records',
    ' New Topic', 'Quote', ' Reply', 'Previous Topic', 'Next Topic',
    'Modify', ' Rate it'
]
student_skip_href_texts = default_skip_href_texts + ['上頁', '下頁']
student_skip_href_texts_en = default_skip_href_texts_en + ['Previously Page', 'Next Page']

admin_skip_mod = ['calendar', 'user', 'theme', 'grade', 'mail']
admin_mod_num = len(admin_cname_map) - len(admin_skip_mod)

ticket_url = 'https://xk4axzhtgc.execute-api.us-east-2.amazonaws.com/Practicing/message'

def homepage_url_to_role(url: str, sso=False) -> Role:
    m = re.match('https:\/\/ceiba\.ntu\.edu\.tw\/([A-Za-z].*)\/', url)
    if m and m.group(1):
        if m.group(1) == 'student':
            if sso:
                return Role.Student
            return Role.Outside_Student
        elif m.group(1) == 'teacher':
            return Role.Professor
        elif m.group(1) == 'ta':
            return Role.TA
        elif m.group(1) == 'outside_teacher':
            return Role.Outside_Teacher
    return None

def skip_href_texts(mod: str, lang: str, admin: bool):
    if admin:
        return admin_skip_href_texts(mod)
    if lang == 'chinese':
        if mod == 'board':
            return board_skip_href_texts
        elif mod == 'student':
            return student_skip_href_texts
        return default_skip_href_texts
    elif lang == 'english':
        if mod == 'board':
            return board_skip_href_texts_en
        elif mod == 'student':
            return student_skip_href_texts_en
        return default_skip_href_texts_en

def admin_skip_href_texts(mod: str):
    if mod == 'syllabus':
        return ['新增一週']
    elif mod == 'bulletin':
        return ['張貼公告']
    elif mod == 'info':
        return ['友善列印']
    elif mod == 'board':
        return board_skip_href_texts + ['新增看板', '修改', '刪除']
    elif mod == 'hw':
        return ['匯出', '指派作業', '依個人', '批改作業']
    elif mod == 'vote':
        return ['張貼投票']
    else:
        return []


def get_valid_filename(name: str) -> str:
    s = str(name).strip().replace(' ', '_').replace('/', '-')
    s = re.sub(r'(?u)[^-\w.]', '_', s)
    return s

def progress_decorator():
    def decorator(func):
        def wrap(self, *args, **kwargs):
            name = self.cname if strings.lang == 'zh-tw' else self.ename
            logging.info(
                strings.object_download_info.format(name, args[1]))
            ret = func(self, *args, **kwargs)
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

def relative_path(self: Path, other: Path) -> str:
    return Path(relpath(other.resolve(), self.resolve())).as_posix()

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
                logging.error(strings.urlf.format(url))
                logging.warning(strings.retry_after_five_seconds)
            count += 1
            time.sleep(5)

    logging.warning(strings.warning_max_retries_exceeded)
    raise CrawlerConnectionError(url)

def pause() -> bool:
    global PAUSE
    if PAUSE:
        logging.warning(strings.resume_download)
    else:
        logging.warning(strings.try_to_pause_download)
        logging.warning(strings.wait_to_completely_download_module)
    PAUSE = not PAUSE
    return PAUSE

def stop():
    global STOP
    STOP = True
    logging.warning(strings.try_to_stop_download)

def check_pause_and_stop():
    global STOP
    global PAUSE
    if PAUSE:
        logging.warning(strings.pause_download)
    while PAUSE or STOP:
        if STOP:
            STOP = False
            PAUSE = False
            raise StopDownload
        time.sleep(1)
