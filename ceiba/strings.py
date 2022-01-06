class String:

    def __init__(self):
        self.lang = "zh-tw"

        self._cancel_on_object = {}
        self._wrong_with_object = {}
        self._wrong_with_downloading_url = {}
        self._wrong_with_alert = {}
        self._course_download_info = {}
        self._course_module_download_info = {}
        self._course_finish_info = {}
        self._crawler_download_info = {}
        self._crawler_download_fail = {}
        self._object_download_info = {}
        self._object_finish_info = {}
        self._crawler_timeour_error = {}
        self._skip_external_href = {}
        self._error_skip_and_continue_download = {}
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
        self._exception_invalid_login_parameters = {}
        self._exception_invalid_credentials = {}
        self._exception_invalid_filepath = {}
        self._exception_null_ticket_content = {}
        self._exception_send_ticket_error = {}
        self._exception_http_not_found_error = {}

        self.set_zh_tw()
        self.set_en()

    def set_lang(self, lang):
        if lang not in ['zh-tw', 'en']:
            raise
        self.lang = lang
    
    def set_zh_tw(self):
        self._cancel_on_object['zh-tw'] = '{} 的 {} 功能並未開啟！取消下載 {} 檔案。'
        self._wrong_with_object['zh-tw'] = '下載 {} 時遇到問題！取消下載 {} 的 {} 檔案'
        self._wrong_with_downloading_url['zh-tw'] = '下載 {} 時遇到問題！網址為 {}'
        self._wrong_with_alert['zh-tw'] = '你可以按任意鍵以繼續下載其他檔案，或是 Ctrl+C 中斷程式運行'
        self._course_download_info['zh-tw'] = '現在正在下載 {} ...'
        self._course_module_download_info['zh-tw'] = '現在正在下載 {} 的 {} ...'
        self._course_finish_info['zh-tw'] = '{} 下載完畢！'
        self._crawler_download_info['zh-tw'] = '下載 {}...'
        self._crawler_download_fail['zh-tw'] = '下載 {} 時發生問題！（網址：<a>{}</a>）'
        self._object_download_info['zh-tw'] = '現在正在下載 {} 的 {} ...'
        self._object_finish_info['zh-tw'] = '{} 的 {} 下載完畢！'
        self._crawler_timeour_error['zh-tw'] = '下載遭到 Ceiba 伺服器阻止，沉睡 5 秒鐘後重試...'
        self._skip_external_href['zh-tw'] = '外部連結 {}，取消下載'
        self._error_skip_and_continue_download['zh-tw'] = '下載 {} 的 {} 時發生問題！繼續下載其他部分...'
        self._error_unable_to_parse_course_sn['zh-tw'] = '無法取得《{}》的 SN 碼！取消下載 {}...'
        self._try_to_login['zh-tw'] = '正在嘗試登入 Ceiba...'
        self._login_successfully['zh-tw'] = '登入 Ceiba 成功！'
        self._try_to_get_courses['zh-tw'] = '正在取得課程...'
        self._get_courses_successfully['zh-tw'] = '取得課程完畢！'
        self._start_downloading_courses['zh-tw'] = '開始下載課程...'
        self._download_courses_successfully['zh-tw'] = '下載課程完畢！'
        self._start_downloading_homepage['zh-tw'] = '開始下載 Ceiba 首頁！'
        self._download_homepage_successfully['zh-tw'] = '下載首頁完成！'
        self._homepage['zh-tw'] = '首頁'
        self._urlf['zh-tw'] = '網址：{}'
        self._url_duplicate['zh-tw'] = 'url 重複，跳過下載：{}'
        self._exception_invalid_login_parameters['zh-tw'] = '你必須提供 cookies 或計中的帳號密碼！'
        self._exception_invalid_credentials['zh-tw'] = '登入失敗！請檢查帳號與密碼是否正確！'
        self._exception_invalid_filepath['zh-tw'] = '路徑錯誤！請檢查路徑是否空白與錯誤！'
        self._exception_null_ticket_content['zh-tw'] = '內容空白！你必須提供意見內容！'
        self._exception_send_ticket_error['zh-tw'] = '傳送意見失敗！錯誤：{}'
        self._exception_http_not_found_error['zh-tw'] = '[404 not found] 下載 {} 時發生問題！（網址：<a>{}</a>）'
    
    def set_en(self):
        # TODO: translate
        self._cancel_on_object['en'] = '{} 的 {} 功能並未開啟！取消下載 {} 檔案。'
        self._wrong_with_object['en'] = '下載 {} 時遇到問題！取消下載 {} 的 {} 檔案'
        self._wrong_with_downloading_url['en'] = '下載 {} 時遇到問題！網址為 {}'
        self._wrong_with_alert['en'] = '你可以按任意鍵以繼續下載其他檔案，或是 Ctrl+C 中斷程式運行'
        self._course_download_info['en'] = 'Downloading {} ...'
        self._course_module_download_info['en'] = '現在正在下載 {} 的 {} ...'
        self._course_finish_info['en'] = '{} 下載完畢！'
        self._crawler_download_info['en'] = 'Downloading {} ...'
        self._crawler_download_fail['en'] = '下載 {} 時發生問題！（網址：<a>{}</a>）'
        self._object_download_info['en'] = '現在正在下載 {} 的 {} ...'
        self._object_finish_info['en'] = '{} 的 {} 下載完畢！'
        self._crawler_timeour_error['en'] = '下載遭到 Ceiba 伺服器阻止，沉睡 5 秒鐘後重試...'
        self._skip_external_href['en'] = '外部連結 {}，取消下載'
        self._error_skip_and_continue_download['en'] = '下載 {} 的 {} 時發生問題！繼續下載其他部分...'
        self._error_unable_to_parse_course_sn['en'] = '無法取得《{}》的 SN 碼！取消下載 {}...'
        self._try_to_login['en'] = '正在嘗試登入 Ceiba...'
        self._login_successfully['en'] = '登入 Ceiba 成功！'
        self._try_to_get_courses['en'] = '正在取得課程...'
        self._get_courses_successfully['en'] = '取得課程完畢！'
        self._start_downloading_courses['en'] = '開始下載課程...'
        self._download_courses_successfully['en'] = '下載課程完畢！'
        self._start_downloading_homepage['en'] = '開始下載 Ceiba 首頁！'
        self._download_homepage_successfully['en'] = '下載首頁完成！'
        self._homepage['en'] = '首頁'
        self._urlf['en'] = '網址：{}'
        self._url_duplicate['en'] = 'url 重複，跳過下載：{}'
        self._exception_invalid_login_parameters['en'] = '你必須提供 cookies 或計中的帳號密碼！'
        self._exception_invalid_credentials['en'] = '登入失敗！請檢查帳號與密碼是否正確！'
        self._exception_invalid_filepath['en'] = '路徑錯誤！請檢查路徑是否空白與錯誤！'
        self._exception_null_ticket_content['en'] = '內容空白！你必須提供意見內容！'
        self._exception_send_ticket_error['en'] = '傳送意見失敗！錯誤：{}'
        self._exception_http_not_found_error['en'] = '[404 not found] 下載 {} 時發生問題！（網址：<a>{}</a>）'
    
    @property
    def cancel_on_object(self):
        return self._cancel_on_object[self.lang]

    @property
    def wrong_with_object (self):
        return self._wrong_with_alert[self.lang]
    
    @property
    def wrong_with_downloading_url (self):
        return self._wrong_with_downloading_url[self.lang]
    
    @property
    def wrong_with_alert(self):
        return self._wrong_with_alert[self.lang]
    
    @property
    def course_download_info(self):
        return self._wrong_with_alert[self.lang]
    
    @property
    def course_module_download_info(self):
        return self._course_module_download_info[self.lang]
    
    @property
    def course_finish_info(self):
        return self._course_finish_info[self.lang]
    
    @property
    def crawler_download_info(self):
        return self.crawler_download_info[self.lang]
    
    @property
    def crawler_download_fail(self):
        return self._crawler_download_fail[self.lang]
    
    @property
    def object_download_info(self):
        return self._object_download_info[self.lang]
    
    @property
    def object_finish_info(self):
        return self._object_finish_info[self.lang]
    
    @property
    def crawler_timeour_error(self):
        return self._crawler_timeour_error[self.lang]
    
    @property
    def skip_external_href(self):
        return self._skip_external_href[self.lang]
    
    @property
    def error_skip_and_continue_download(self):
        return self._error_skip_and_continue_download[self.lang]
    
    @property
    def error_unable_to_parse_course_sn(self):
        return self._error_unable_to_parse_course_sn[self.lang]
    
    @property
    def try_to_login(self):
        return self._try_to_login[self.lang]
    
    @property
    def login_successfully(self):
        return self._login_successfully[self.lang]
    
    @property
    def try_to_get_courses(self):
        return self._try_to_get_courses[self.lang]
    
    @property
    def get_courses_successfully(self):
        return self._get_courses_successfully[self.lang]
    
    @property
    def start_downloading_courses(self):
        return self._start_downloading_courses[self.lang]
    
    @property
    def download_courses_successfully(self):
        return self._download_courses_successfully[self.lang]
    
    @property
    def start_downloading_homepage(self):
        return self._start_downloading_homepage[self.lang]
    
    @property
    def download_homepage_successfully(self):
        return self._download_homepage_successfully[self.lang]
    
    @property
    def homepage(self):
        return self._homepage[self.lang]
    
    @property
    def urlf(self):
        return self._urlf[self.lang]
    
    @property
    def url_duplicate(self):
        return self._url_duplicate[self.lang]
    
    @property
    def exception_invalid_login_parameters(self):
        return self._exception_invalid_login_parameters[self.lang]
    
    @property
    def exception_invalid_credentials(self):
        return self._exception_invalid_credentials[self.lang]
    
    @property
    def exception_invalid_filepath(self):
        return self._exception_invalid_filepath[self.lang]
    
    @property
    def exception_null_ticket_content(self):
        return self._exception_null_ticket_content[self.lang]
    
    @property
    def exception_send_ticket_error(self):
        return self._exception_send_ticket_error[self.lang]
    
    @property
    def exception_http_not_found_error(self):
        return self._exception_http_not_found_error[self.lang]

strings = String()