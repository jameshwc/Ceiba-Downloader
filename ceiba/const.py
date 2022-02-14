from enum import Enum

class Role(Enum):
    NTUer = 0
    TA = 1
    Professor = 2
    Outside_Teacher = 3
    Outside_Student = 4

    def __str__(self):
        return self.name.replace("_", " ")

class String:

    def __init__(self):
        self.lang = "zh-tw"
        
        self._role = {}
        for role in Role:
            self._role[role] = {}
        
        self._cancel_on_object = {}
        self._wrong_with_object = {}
        self._wrong_with_downloading_url = {}
        self._course_download_info = {}
        self._course_module_download_info = {}
        self._course_finish_info = {}
        self._crawler_download_info = {}
        self._crawler_download_fail = {}
        self._object_download_info = {}
        self._object_finish_info = {}
        self._crawler_timeout_error = {}
        self._skip_external_href = {}
        self._error_skip_and_continue_download_modules = {}
        self._error_skip_and_continue_download_courses = {}
        self._error_unable_to_parse_course_sn = {}
        self._try_to_login = {}
        self._login_successfully = {}
        self._try_to_get_courses = {}
        self._get_courses_successfully = {}
        self._start_downloading_courses = {}
        self._download_courses_successfully = {}
        self._start_downloading_homepage = {}
        self._download_homepage_successfully = {}
        self._homepage = {}
        self._urlf = {}
        self._url_duplicate = {}
        self._send_ticket_successfully = {}
        self._retry_after_five_seconds = {}
        self._exception_invalid_login_parameters = {}
        self._exception_invalid_credentials = {}
        self._exception_invalid_filepath = {}
        self._exception_null_ticket_content = {}
        self._exception_send_ticket_error = {}
        self._exception_check_for_updates = {}
        self._exception_http_not_found_error = {}
        self._exception_crawler_connection_error = {}
        self._warning_fail_to_get_course = {}
        self._warning_partial_failure_on_homepage = {}
        self._warning_max_retries_exceeded = {}
        
        self._qt_feedback = {}
        self._qt_submit = {}
        self._qt_anonymous = {}
        self._qt_submit_ticket_successfully = {}
        self._qt_user = {}
        self._qt_username = {}
        self._qt_password = {}
        self._qt_login = {}
        self._qt_login_method_unsafe = {}
        self._qt_login_method_safe = {}
        self._qt_course = {}
        self._qt_status = {}
        self._qt_send_ticket_button = {}

        self.set_zh_tw()
        self.set_en()

    def set_lang(self, lang):
        if lang not in ['zh-tw', 'en']:
            raise
        self.lang = lang
    
    def set_zh_tw(self):
        self._role[Role.NTUer]['zh-tw'] = '台大學生'
        self._role[Role.TA]['zh-tw'] = '助教'
        self._role[Role.Professor]['zh-tw'] = '教授'
        self._role[Role.Outside_Teacher]['zh-tw'] = '校外老師'
        self._role[Role.Outside_Student]['zh-tw'] = '校外學生'

        self._cancel_on_object['zh-tw'] = '{} 的 {} 功能並未開啟！取消下載 {} 檔案。'
        self._wrong_with_object['zh-tw'] = '下載 {} 時遇到問題！取消下載 {} 的 {} 檔案'
        self._wrong_with_downloading_url['zh-tw'] = '下載 {} 時遇到問題！網址為 {}'
        self._course_download_info['zh-tw'] = '現在正在下載 {} ...'
        self._course_module_download_info['zh-tw'] = '現在正在下載 {} 的 {} ...'
        self._course_finish_info['zh-tw'] = '{} 下載完畢！'
        self._crawler_download_info['zh-tw'] = '下載 {}...'
        self._crawler_download_fail['zh-tw'] = '下載 {} 時發生問題！（網址：{}）'
        self._object_download_info['zh-tw'] = '現在正在下載 {} 的 {} ...'
        self._object_finish_info['zh-tw'] = '{} 的 {} 下載完畢！'
        self._crawler_timeout_error['zh-tw'] = '下載遭到 Ceiba 伺服器阻止，沉睡 5 秒鐘後重試...'
        self._skip_external_href['zh-tw'] = '外部連結 {}，取消下載'
        self._error_skip_and_continue_download_modules['zh-tw'] = '下載 {} 的 {} 時發生問題！繼續下載其他部分...'
        self._error_skip_and_continue_download_courses['zh-tw'] = '下載課程 {} 時發生問題！跳過並下載其他課程...'
        self._error_unable_to_parse_course_sn['zh-tw'] = '無法取得《{}》的 SN 碼！取消下載 {}...'
        self._try_to_login['zh-tw'] = '正在嘗試登入 Ceiba...'
        self._login_successfully['zh-tw'] = '登入 Ceiba 成功！'
        self._try_to_get_courses['zh-tw'] = '正在取得課程...'
        self._get_courses_successfully['zh-tw'] = '取得課程完畢！'
        self._start_downloading_courses['zh-tw'] = '開始下載課程...'
        self._download_courses_successfully['zh-tw'] = '下載課程完畢！'
        self._start_downloading_homepage['zh-tw'] = '開始下載 Ceiba 首頁！'
        self._download_homepage_successfully['zh-tw'] = '下載首頁完成！'
        self._send_ticket_successfully['zh-tw'] = '傳送意見完成！'
        self._homepage['zh-tw'] = '首頁'
        self._urlf['zh-tw'] = '網址：{}'
        self._url_duplicate['zh-tw'] = 'url 重複，跳過下載：{}'
        self._exception_invalid_login_parameters['zh-tw'] = '你必須提供 cookies 或計中的帳號密碼！'
        self._exception_invalid_credentials['zh-tw'] = '登入失敗！請檢查帳號與密碼是否正確！'
        self._exception_invalid_filepath['zh-tw'] = '路徑錯誤！請檢查路徑是否空白與錯誤！'
        self._exception_null_ticket_content['zh-tw'] = '內容空白！你必須提供意見內容！'
        self._exception_send_ticket_error['zh-tw'] = '傳送意見失敗！錯誤：{}'
        self._exception_http_not_found_error['zh-tw'] = '[404 not found] 下載 {} 時發生問題！（網址：{}）'
        self._exception_check_for_updates['zh-tw'] = '檢查更新時發生錯誤！'
        self._exception_crawler_connection_error['zh-tw'] = '連線時發生問題！發生錯誤的網址：{}'
        self._warning_fail_to_get_course['zh-tw'] = '取得第 {} 堂課程資訊錯誤！跳過並取得其他堂課程...'
        self._warning_partial_failure_on_homepage['zh-tw'] = '下載首頁時發生部分錯誤！首頁有可能無法正常顯示...'
        self._warning_max_retries_exceeded['zh-tw'] = '超過最大重試連線次數！停止嘗試連線！'
        self._retry_after_five_seconds['zh-tw'] = '五秒後重新連線...'
    
    def set_en(self):
        self._role[Role.NTUer]['en'] = 'NTU Students'
        self._role[Role.TA]['en'] = 'TA'
        self._role[Role.Professor]['en'] = 'Professor'
        self._role[Role.Outside_Teacher]['en'] = 'Outside Teacher'
        self._role[Role.Outside_Student]['en'] = 'Outside Student'

        self._cancel_on_object['en'] = 'There is no {1} module in course {0}! Cancel the download of {}.'
        self._wrong_with_object['en'] = 'Error when downloading {0}! Cancel the download of {2} in {1}.'
        self._wrong_with_downloading_url['en'] = 'Error when downloading {} ! Url: {}'
        self._course_download_info['en'] = 'Downloading {} ...'
        self._course_module_download_info['en'] = 'Downloading {1} of course "{0}" ...'
        self._course_finish_info['en'] = '{} has been completely downloaded!'
        self._crawler_download_info['en'] = 'Downloading {} ...'
        self._crawler_download_fail['en'] = 'Error when downloading {}! (url: {})'
        self._object_download_info['en'] = 'Downloading {1} of {0} ...'
        self._object_finish_info['en'] = 'Finish downloading {1} of {0}!'
        self._crawler_timeout_error['en'] = 'The Ceiba server has blocked the connection, sleep 5 seconds to continue the download...'
        self._skip_external_href['en'] = 'Cancel the download of external link {} !'
        self._error_skip_and_continue_download_modules['en'] = 'Error when downloading {1} of {0}! Skip it and continue downloading...'
        self._error_skip_and_continue_download_courses['en'] = 'Error when downloading the course {}! Skip it and continue downloading...'
        self._error_unable_to_parse_course_sn['en'] = 'Can\'t parse the course code of {} ! Cancel the download of {}...'
        self._try_to_login['en'] = 'Trying to log in Ceiba...'
        self._login_successfully['en'] = 'Successfully log in to Ceiba!'
        self._try_to_get_courses['en'] = 'Trying to get the courses...'
        self._get_courses_successfully['en'] = 'Successfully got the courses!'
        self._start_downloading_courses['en'] = 'Downloading the courses...'
        self._download_courses_successfully['en'] = 'The courses has been downloaded successfully!'
        self._start_downloading_homepage['en'] = 'Start to download Ceiba homepage!'
        self._download_homepage_successfully['en'] = 'Ceiba homepage has been downloaded successfully!'
        self._send_ticket_successfully['en'] = 'Successfully sent the ticket!'
        self._homepage['en'] = 'homepage'
        self._urlf['en'] = 'url: {}'
        self._url_duplicate['en'] = 'duplicate url: skipping download - {}'
        self._exception_invalid_login_parameters['en'] = 'You must fill in the username/password or cookies!'
        self._exception_invalid_credentials['en'] = 'Fail to log in! Please check if you fill in correct username and password!'
        self._exception_invalid_filepath['en'] = 'The file path is incorrect! Please check if the path is empty or wrong!'
        self._exception_null_ticket_content['en'] = 'The content is empty! You must type something to submit issues!'
        self._exception_send_ticket_error['en'] = 'Fail to report issue! Error: {}'
        self._exception_http_not_found_error['en'] = '[404 not found] Error when downloading {} ! (url: {})'
        self._exception_check_for_updates['en'] = 'Error when checking for updates!'
        self._exception_crawler_connection_error['en'] = 'Connection error! The url that caused the error is {}'
        self._warning_fail_to_get_course['en'] = 'Error when getting no.{} course! Skip it to get the other courses...'
        self._warning_max_retries_exceeded['en'] = 'Max retries exceeded! Stop retrying the connection!'
        self._warning_partial_failure_on_homepage['en'] = 'Partially fail to download homepage! It may not show correctly...'
        self._retry_after_five_seconds['en'] = 'Retry connection after 5 seconds...'
    
    def role(self, role: int) -> str:
        return self._role[role][self.lang]

    @property
    def cancel_on_object(self) -> str:
        return self._cancel_on_object[self.lang]

    @property
    def wrong_with_object (self) -> str:
        return self._wrong_with_object[self.lang]
    
    @property
    def wrong_with_downloading_url (self) -> str:
        return self._wrong_with_downloading_url[self.lang]
    
    @property
    def course_download_info(self) -> str:
        return self._course_download_info[self.lang]
    
    @property
    def course_module_download_info(self) -> str:
        return self._course_module_download_info[self.lang]
    
    @property
    def course_finish_info(self) -> str:
        return self._course_finish_info[self.lang]
    
    @property
    def crawler_download_info(self) -> str:
        return self._crawler_download_info[self.lang]
    
    @property
    def crawler_download_fail(self) -> str:
        return self._crawler_download_fail[self.lang]
    
    @property
    def object_download_info(self) -> str:
        return self._object_download_info[self.lang]
    
    @property
    def object_finish_info(self) -> str:
        return self._object_finish_info[self.lang]
    
    @property
    def crawler_timeout_error(self) -> str:
        return self._crawler_timeout_error[self.lang]
    
    @property
    def skip_external_href(self) -> str:
        return self._skip_external_href[self.lang]
    
    @property
    def error_skip_and_continue_download_modules(self) -> str:
        return self._error_skip_and_continue_download_modules[self.lang]
    
    @property
    def error_skip_and_continue_download_courses(self) -> str:
        return self._error_skip_and_continue_download_courses[self.lang]
        
    @property
    def error_unable_to_parse_course_sn(self) -> str:
        return self._error_unable_to_parse_course_sn[self.lang]
    
    @property
    def try_to_login(self) -> str:
        return self._try_to_login[self.lang]
    
    @property
    def login_successfully(self) -> str:
        return self._login_successfully[self.lang]
    
    @property
    def try_to_get_courses(self) -> str:
        return self._try_to_get_courses[self.lang]
    
    @property
    def get_courses_successfully(self) -> str:
        return self._get_courses_successfully[self.lang]
    
    @property
    def start_downloading_courses(self) -> str:
        return self._start_downloading_courses[self.lang]
    
    @property
    def download_courses_successfully(self) -> str:
        return self._download_courses_successfully[self.lang]
    
    @property
    def start_downloading_homepage(self) -> str:
        return self._start_downloading_homepage[self.lang]
    
    @property
    def download_homepage_successfully(self) -> str:
        return self._download_homepage_successfully[self.lang]
    
    @property
    def send_ticket_successfully(self) -> str:
        return self._send_ticket_successfully[self.lang]
    
    @property
    def homepage(self) -> str:
        return self._homepage[self.lang]
    
    @property
    def urlf(self) -> str:
        return self._urlf[self.lang]
    
    @property
    def url_duplicate(self) -> str:
        return self._url_duplicate[self.lang]
    
    @property
    def exception_invalid_login_parameters(self) -> str:
        return self._exception_invalid_login_parameters[self.lang]
    
    @property
    def exception_invalid_credentials(self) -> str:
        return self._exception_invalid_credentials[self.lang]
    
    @property
    def exception_invalid_filepath(self) -> str:
        return self._exception_invalid_filepath[self.lang]
    
    @property
    def exception_null_ticket_content(self) -> str:
        return self._exception_null_ticket_content[self.lang]
    
    @property
    def exception_send_ticket_error(self) -> str:
        return self._exception_send_ticket_error[self.lang]
    
    @property
    def exception_http_not_found_error(self) -> str:
        return self._exception_http_not_found_error[self.lang]

    @property
    def exception_check_for_updates(self) -> str:
        return self._exception_check_for_updates[self.lang]

    @property
    def exception_crawler_connection_error(self) -> str:
        return self._exception_crawler_connection_error[self.lang]
    
    @property
    def warning_fail_to_get_course(self) -> str:
        return self._warning_fail_to_get_course[self.lang]
    
    @property
    def warning_partial_failure_on_homepage(self) -> str:
        return self._warning_partial_failure_on_homepage[self.lang]
    
    @property
    def warning_max_retries_exceeded(self) -> str:
        return self._warning_max_retries_exceeded[self.lang]
    
    @property
    def retry_after_five_seconds(self) -> str:
        return self._retry_after_five_seconds[self.lang]

strings = String()
