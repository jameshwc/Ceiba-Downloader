class InvalidLoginParameters(Exception):
    def __str__(self):
        return '你必須提供 cookies 或計中的帳號密碼！'


class InvalidCredentials(Exception):
    def __str__(self):
        return '登入失敗！請檢查帳號與密碼是否正確！'


class InvalidFilePath(Exception):
    def __str__(self):
        return '路徑錯誤！請檢查路徑是否空白與錯誤！'

class NullTicketContent(Exception):
    def __str__(self):
        return '內容空白！你必須提供意見內容！'

class SendTicketError(Exception):
    def __init__(self, content):
        self.content = content
    
    def __str__(self):
        return '傳送意見失敗！錯誤：{}'.format(self.content)

class NotFound(Exception):
    def __init__(self, text, url):
        super().__init__()
        self.text = text
        self.url = url

    def __str__(self):
        return '[404 not found] 下載 {} 時發生問題！（網址：{}）'.format(
            self.text, self.url)  # same as the one in strings.py
