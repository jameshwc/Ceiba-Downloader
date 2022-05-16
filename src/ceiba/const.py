from enum import Enum
from typing import Dict
from .i18n.en import en
from .i18n.zh_tw import zh_tw

cname_map = {
    'bulletin': '公佈欄', 'syllabus': '課程大綱', 'hw': '作業',
    'info': '課程資訊', 'personal': '教師資訊', 'grade': '學習成績',
    'board': '討論看板', 'calendar': '課程行事曆', 'share': '資源分享',
    'vote': '投票區', 'student': '修課學生'}
ename_map = {v: k for k, v in cname_map.items()}

class Role(Enum):
    Student = 0
    TA = 1
    Professor = 2
    Outside_Teacher = 3
    Outside_Student = 4

    def __str__(self):
        return self.name.lower()

    @property
    def is_admin(self) -> bool:
        return self == Role.TA or self == Role.Professor or self == Role.Outside_Teacher

class String:

    def __init__(self):
        self.lang = 'zh-tw'
        self.available_langs = ['zh-tw', 'en']

        self._data: Dict[str, Dict[str, str]] = {}

        self.load_dict('zh-tw', zh_tw)
        self.load_dict('en', en)

    def load_dict(self, lang, lang_dict):

        for role in Role:
            name = role.name
            self.init_str(f'role_{role}')
            self._data[f'role_{role}'][lang] = lang_dict['role'][name]

        for info, str_ in lang_dict['info'].items():
            self.init_str(info)
            self._data[info][lang] = str_

        for qt, str_ in lang_dict['qt'].items():
            self.init_str(f'qt_{qt}')
            self._data[f'qt_{qt}'][lang] = str_

    def init_str(self, name):
        if name not in self._data:
            self._data[name] = {}

    def set_lang(self, lang):
        if lang not in self.available_langs:
            raise
        self.lang = lang

    def role(self, role: int) -> str:
        return self._data[f'role_{role}'][self.lang]

    def course(self, course_name: str, course_num: str, class_num: str) -> str:
        if len(class_num) > 0:
            return self._data['course'][self.lang].format(course_name, course_num, class_num)
        return self._data['course_without_class'][self.lang].format(course_name, course_num)

    @property
    def name_map(self) -> Dict[str, str]:
        if self.lang == 'zh-tw':
            return cname_map
        return ename_map

    @property
    def sso_login(self) -> str:
        return self._data['sso_login'][self.lang]

    @property
    def alternative_login(self) -> str:
        return self._data['alternative_login'][self.lang]

    @property
    def cancel_on_object(self) -> str:
        return self._data['cancel_on_object'][self.lang]

    @property
    def wrong_with_object (self) -> str:
        return self._data['wrong_with_object'][self.lang]

    @property
    def wrong_with_downloading_url (self) -> str:
        return self._data['wrong_with_downloading_url'][self.lang]

    @property
    def course_download_info(self) -> str:
        return self._data['course_download_info'][self.lang]

    @property
    def course_module_download_info(self) -> str:
        return self._data['course_module_download_info'][self.lang]

    @property
    def course_finish_info(self) -> str:
        return self._data['course_finish_info'][self.lang]

    @property
    def crawler_download_info(self) -> str:
        return self._data['crawler_download_info'][self.lang]

    @property
    def crawler_download_fail(self) -> str:
        return self._data['crawler_download_fail'][self.lang]

    @property
    def object_download_info(self) -> str:
        return self._data['object_download_info'][self.lang]

    @property
    def object_finish_info(self) -> str:
        return self._data['object_finish_info'][self.lang]

    @property
    def crawler_timeout_error(self) -> str:
        return self._data['crawler_timeout_error'][self.lang]

    @property
    def skip_external_href(self) -> str:
        return self._data['skip_external_href'][self.lang]

    @property
    def error_skip_and_continue_download_modules(self) -> str:
        return self._data['error_skip_and_continue_download_modules'][self.lang]

    @property
    def error_skip_and_continue_download_courses(self) -> str:
        return self._data['error_skip_and_continue_download_courses'][self.lang]

    @property
    def error_unable_to_parse_course_sn(self) -> str:
        return self._data['error_unable_to_parse_course_sn'][self.lang]

    @property
    def try_to_login(self) -> str:
        return self._data['try_to_login'][self.lang]

    @property
    def login_successfully(self) -> str:
        return self._data['login_successfully'][self.lang]

    @property
    def try_to_get_courses(self) -> str:
        return self._data['try_to_get_courses'][self.lang]

    @property
    def get_courses_successfully(self) -> str:
        return self._data['get_courses_successfully'][self.lang]

    @property
    def start_downloading_courses(self) -> str:
        return self._data['start_downloading_courses'][self.lang]

    @property
    def download_courses_successfully(self) -> str:
        return self._data['download_courses_successfully'][self.lang]

    @property
    def start_downloading_homepage(self) -> str:
        return self._data['start_downloading_homepage'][self.lang]

    @property
    def download_homepage_successfully(self) -> str:
        return self._data['download_homepage_successfully'][self.lang]

    @property
    def send_ticket_successfully(self) -> str:
        return self._data['send_ticket_successfully'][self.lang]

    @property
    def homepage(self) -> str:
        return self._data['homepage'][self.lang]

    @property
    def admin_homepage(self) -> str:
        return self._data['admin_homepage'][self.lang]

    @property
    def urlf(self) -> str:
        return self._data['urlf'][self.lang]

    @property
    def url_duplicate(self) -> str:
        return self._data['url_duplicate'][self.lang]

    @property
    def exception_invalid_login_parameters(self) -> str:
        return self._data['exception_invalid_login_parameters'][self.lang]

    @property
    def exception_invalid_credentials(self) -> str:
        return self._data['exception_invalid_credentials'][self.lang]

    @property
    def exception_invalid_login_role(self) -> str:
        return self._data['exception_invalid_login_role'][self.lang]

    @property
    def exception_invalid_filepath(self) -> str:
        return self._data['exception_invalid_filepath'][self.lang]

    @property
    def exception_null_ticket_content(self) -> str:
        return self._data['exception_null_ticket_content'][self.lang]

    @property
    def exception_send_ticket_error(self) -> str:
        return self._data['exception_send_ticket_error'][self.lang]

    @property
    def exception_http_not_found_error(self) -> str:
        return self._data['exception_http_not_found_error'][self.lang]

    @property
    def exception_check_for_updates(self) -> str:
        return self._data['exception_check_for_updates'][self.lang]

    @property
    def exception_crawler_connection_error(self) -> str:
        return self._data['exception_crawler_connection_error'][self.lang]

    @property
    def warning_fail_to_get_course(self) -> str:
        return self._data['warning_fail_to_get_course'][self.lang]

    @property
    def warning_partial_failure_on_homepage(self) -> str:
        return self._data['warning_partial_failure_on_homepage'][self.lang]

    @property
    def warning_max_retries_exceeded(self) -> str:
        return self._data['warning_max_retries_exceeded'][self.lang]

    @property
    def retry_after_five_seconds(self) -> str:
        return self._data['retry_after_five_seconds'][self.lang]

    @property
    def try_to_pause_download(self) -> str:
        return self._data['try_to_pause_download'][self.lang]

    @property
    def pause_download(self) -> str:
        return self._data['pause_download'][self.lang]

    @property
    def resume_download(self) -> str:
        return self._data['resume_download'][self.lang]

    @property
    def wait_to_completely_download_module(self) -> str:
        return self._data['wait_to_completely_download_module'][self.lang]

    @property
    def try_to_stop_download(self) -> str:
        return self._data['try_to_stop_download'][self.lang]

    @property
    def stop_download(self) -> str:
        return self._data['stop_download'][self.lang]

    @property
    def qt_stop_button(self) -> str:
        return self._data['qt_stop_button'][self.lang]

    @property
    def qt_pause_button(self) -> str:
        return self._data['qt_pause_button'][self.lang]

    @property
    def qt_resume_button(self) -> str:
        return self._data['qt_resume_button'][self.lang]

    @property
    def qt_login_method_label(self) -> str:
        return self._data['qt_login_method_label'][self.lang]

    @property
    def qt_login_groupbox_title(self) -> str:
        return self._data['qt_login_groupbox_title'][self.lang]

    @property
    def qt_username_label(self) -> str:
        return self._data['qt_username_label'][self.lang]

    @property
    def qt_password_label(self) -> str:
        return self._data['qt_password_label'][self.lang]

    @property
    def qt_login_button(self) -> str:
        return self._data['qt_login_button'][self.lang]

    @property
    def qt_login_method_left_label(self) -> str:
        return self._data['qt_login_method_left_label'][self.lang]

    @property
    def qt_login_method_right_label(self) -> str:
        return self._data['qt_login_method_right_label'][self.lang]

    @property
    def qt_login_method_left_label_tooltip(self) -> str:
        return self._data['qt_login_method_left_label_tooltip'][self.lang]

    @property
    def qt_login_method_right_label_tooltip(self) -> str:
        return self._data['qt_login_method_right_label_tooltip'][self.lang]

    @property
    def qt_welcome(self) -> str:
        return self._data['qt_welcome'][self.lang]

    @property
    def qt_courses_group_box(self) -> str:
        return self._data['qt_courses_group_box'][self.lang]

    @property
    def qt_status_group_box(self) -> str:
        return self._data['qt_status_group_box'][self.lang]

    @property
    def qt_download_button(self) -> str:
        return self._data['qt_download_button'][self.lang]

    @property
    def qt_check_all_courses_checkbox(self) -> str:
        return self._data['qt_check_all_courses_checkbox'][self.lang]

    @property
    def qt_download_item_label(self) -> str:
        return self._data['qt_download_item_label'][self.lang]

    @property
    def qt_check_all_download_item_checkbox(self) -> str:
        return self._data['qt_check_all_download_item_checkbox'][self.lang]

    @property
    def qt_download_admin_checkbox(self) -> str:
        return self._data['qt_download_admin_checkbox'][self.lang]

    @property
    def qt_download_admin_checkbox_tooltip(self) -> str:
        return self._data['qt_download_admin_checkbox_tooltip'][self.lang]

    @property
    def qt_only_download_homepage_checkbox(self) -> str:
        return self._data['qt_only_download_homepage_checkbox'][self.lang]

    @property
    def qt_only_download_homepage_checkbox_tooltip(self) -> str:
        return self._data['qt_only_download_homepage_checkbox_tooltip'][self.lang]

    @property
    def qt_logger_debug_checkbox(self) -> str:
        return self._data['qt_logger_debug_checkbox'][self.lang]

    @property
    def qt_filepath_label(self) -> str:
        return self._data['qt_filepath_label'][self.lang]

    @property
    def qt_file_browse_button(self) -> str:
        return self._data['qt_file_browse_button'][self.lang]

    @property
    def qt_download_item_menu_button(self) -> str:
        return self._data['qt_download_item_menu_button'][self.lang]

    @property
    def qt_download_finish_msgbox(self) -> str:
        return self._data['qt_download_finish_msgbox'][self.lang]

    @property
    def qt_download_finish_msgbox_open_dir(self) -> str:
        return self._data['qt_download_finish_msgbox_open_dir'][self.lang]

    @property
    def qt_download_finish_msgbox_open_browser(self) -> str:
        return self._data['qt_download_finish_msgbox_open_browser'][self.lang]

strings = String()
