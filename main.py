
from ceiba import Ceiba

if __name__ == "__main__":
    ceiba = Ceiba(username=input('Please input username: '), password=input('Please input password: '))
    ceiba.get_courses_list()
    ceiba.download_courses()
