import requests
import config
url = 'https://ceiba.ntu.edu.tw/modules/hw/hw_download.php?csn=519670&hw_sn=273991&ch=0'

cookies = {
    'PHPSESSID': config.PHPSESSID,
    'user': config.USER
}

from pathlib import Path

path = Path("hello.txt") # TODO: check if filename exists
resp = requests.get(url, cookies=cookies)
path.write_bytes(resp.content)