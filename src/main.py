
import logging
import sys
from getpass import getpass

from ceiba.ceiba import Ceiba

'''

This is an example of how to use the API in cli mode.
If you know python well, you can easily customize the code :)

'''

if __name__ == "__main__":
    ceiba = Ceiba()
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger().setLevel(logging.INFO)
    ceiba.login(username=input('Please input username: '),
                  password=getpass('Please input password: '))
    ceiba.get_courses_list()
    course_id_filter = []
    for course in ceiba.courses:
        print(course.semester, course.cname, course.ename, course.teacher)
        opt = input('您是否要下載這個課程？[y/n/z]').lower()
        if opt == 'y':
            course_id_filter.append(course.id)
        elif opt == 'z':
            break
    ceiba.download_courses('D:\\備份\\ceiba',
                           course_id_filter=course_id_filter,  # or None to download all courses
                           modules_filter=['board', 'bulletin', 'info', 'teacher']
                           )
