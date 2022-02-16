from http.client import RemoteDisconnected
import logging
import re
import time

from requests import Session, Response
from typing import Callable
from .const import strings, Role
from .exceptions import CrawlerConnectionError
from pathlib import Path
from os.path import relpath

CONNECT_RETRY_MAX = 10
REQUESTS_TIMEOUT = 300

home_url = 'https://ceiba.ntu.edu.tw'
login_url = 'https://ceiba.ntu.edu.tw/ChkSessLib.php'
login_alternative_url = 'https://ceiba.ntu.edu.tw/index.php?error_check=OK'
module_url = 'https://ceiba.ntu.edu.tw/modules/main.php'

role_short = {Role.NTUer: 'student', Role.TA: 'ta', 
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

cname_map = {
    'bulletin': '公佈欄', 'syllabus': '課程大綱', 'hw': '作業',
    'info': '課程資訊', 'personal': '教師資訊', 'grade': '學習成績',
    'board': '討論看板', 'calendar': '課程行事曆', 'share': '資源分享',
    'vote': '投票區', 'student': '修課學生'}
ename_map = {v: k for k, v in cname_map.items()}

admin_cname_map = {
    'ftp': '檔案上傳', 'user': '使用者', 'theme': '主題首頁',
    'info': '課程資訊', 'syllabus': '大綱內容', 'bulletin': '公佈欄',
    'calendar': '行事曆', 'board': '討論區', 'hw': '作業', 
    'share': '資源分享', 'vote': '投票', 'grade': '成績'
}
admin_ename_map = {v: k for k, v in admin_cname_map.items()}
admin_ename_map['討論看板'] = 'board'

default_skip_href_texts = ['友善列印', '分頁顯示']
board_skip_href_texts = default_skip_href_texts + [
                '看板列表', '最新張貼', '排行榜', '推薦文章', '搜尋文章', '發表紀錄',
                ' 新增主題', '引用', ' 回覆', '分頁顯示', '上個主題', '下個主題',
                '修改', '上一頁', '下一頁', ' 我要評分', ' 我要推薦']
student_skip_href_texts = default_skip_href_texts + ['上頁', '下頁']

admin_skip_mod = ['calendar', 'user', 'theme', 'grade']
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
        return ['匯出', '指派作業']
    elif mod == 'vote':
        return ['張貼投票']
    else:
        return []

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

def is_admin(role: Role) -> bool:
    return role == Role.TA or role == Role.Professor or role == Role.Outside_Teacher

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

def debug():
    while True:
        try:
            eval(input())
        except KeyboardInterrupt:
            break