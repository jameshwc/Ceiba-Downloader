
import logging
import sys
from getpass import getpass

from ceiba import Ceiba

if __name__ == "__main__":
    ceiba = Ceiba(username=input('Please input username: '),
                  password=getpass('Please input password: '))
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger().setLevel(logging.INFO)
    ceiba.login()
    ceiba.get_courses_list()
    ceiba.download_courses('D:\\備份\\ceiba',
                           cname_filter_list=['宗教、博物館與數位轉譯'],
                           modules_filter=['board', 'bulletin', 'info', 'teacher']
                           )
