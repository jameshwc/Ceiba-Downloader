
from ceiba import Ceiba
from getpass import getpass
import logging
import sys

if __name__ == "__main__":
    ceiba = Ceiba(username=input('Please input username: '),
                  password=getpass('Please input password: '))
    # ceiba.path = input('Please input desired backup path: ')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger().setLevel(logging.INFO)
    ceiba.login()
    ceiba.get_courses_list()
    ceiba.download_courses('D:\\備份\\ceiba',
                           cname_filter_list=['文化人類學丙'],
                        #    modules_filter=['bulletin', 'info', 'teacher']
                           )
    import strings
    strings.cancel_on_object = strings.cancel_on_object_tw
