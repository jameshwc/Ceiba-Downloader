import requests
from bs4 import BeautifulSoup
from getpass import getpass

base_url = 'https://cool.ntu.edu.tw/api/v1/'
export_url = 'https://cool.ntu.edu.tw/api/v1/courses/215/content_exports'

sess = requests.session()

def login():
    page = sess.get('https://cool.ntu.edu.tw/login/saml').text
    soup = BeautifulSoup( page[page.find('<form'):page.find('</form>')+7], 'html.parser' )
    payload = {}
    for data in soup.find_all('input'):
        if 'UsernameTextBox' in data.get('name'):
            payload[data.get('name')] = input('Username: ').strip()
        elif 'PasswordTextBox' in data.get('name'):
            payload[data.get('name')] = getpass('Password: ')
        else:
            payload[data.get('name')] = data.get('value')

    url = 'https://adfs.ntu.edu.tw' + soup.form.get('action')
    soup = BeautifulSoup( sess.post(url, data=payload).text, 'html.parser' )
    payload = {'SAMLResponse': soup.input.get('value')}
    url = 'https://cool.ntu.edu.tw/login/saml'
    sess.post(url, data=payload)

login()
print(sess.post(export_url, data={"export_type": "zip"}).content.decode('utf-8'))