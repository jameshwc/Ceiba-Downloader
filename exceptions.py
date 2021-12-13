class InvalidLoginParameters(Exception):
    def __str__(self):
        return '你必須提供 cookies 或計中的帳號密碼！'

class InvalidCredentials(Exception):
    def __str__(self):
        return '登入失敗！請檢查帳號與密碼是否正確！'
    
