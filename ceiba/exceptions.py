from .const import strings

class InvalidLoginParameters(Exception):
    def __str__(self):
        return strings.exception_invalid_login_parameters


class InvalidCredentials(Exception):
    def __str__(self):
        return strings.exception_invalid_credentials


class InvalidFilePath(Exception):
    def __str__(self):
        return strings.exception_invalid_filepath

class NullTicketContent(Exception):
    def __str__(self):
        return strings.exception_null_ticket_content

class SendTicketError(Exception):
    def __init__(self, content):
        self.content = content
    
    def __str__(self):
        return strings.exception_send_ticket_error.format(self.content)

class CheckForUpdatesError(Exception):
    def __str__(self):
        return strings.exception_check_for_updates
    
class NotFound(Exception):
    def __init__(self, text, url):
        super().__init__()
        self.text = text
        self.url = url

    def __str__(self):
        return strings.exception_http_not_found_error.format(self.text, self.url) 

class CrawlerConnectionError(Exception):
    def __init__(self, url):
        self.url = url
        
    def __str__(self):
        return strings.exception_crawler_connection_error.format(self.url)