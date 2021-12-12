
import config
from ceiba import Ceiba

if __name__ == "__main__":
    ceiba = Ceiba(username=config.username, password=config.password)
    ceiba.get_courses_list()
    ceiba.download_courses()