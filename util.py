import re
import strings
from bs4 import BeautifulSoup

def get_valid_filename(name: str):
    s = str(name).strip().replace(' ', '_')
    s = re.sub(r'(?u)[^-\w.]', '_', s)
    return s

def beautify_soup(content: bytes):
    soup = BeautifulSoup(content, 'html.parser')
    for br in soup.find_all("br"):
        br.replace_with("\n")
    return soup

def progress_decorator():
    def decorator(func):
        def wrap(self, *args):
            print(strings.object_download_info.format(self.cname, args[3]))
            func(self, *args)
            print(strings.object_finish_info.format(self.cname, args[3]))
        return wrap
    return decorator