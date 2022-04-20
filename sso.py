'''
https://hasinthaindrajee.medium.com/browser-sso-for-cli-applications-b0be743fa656
'''

from ceiba.ceiba import Ceiba
from flask import Flask, request
from werkzeug.serving import make_server
from PySide6.QtCore import QRunnable, QObject, Signal

SSO_SERVER_PORT = 8688
SSO_SERVER_ADDR = 'localhost'
SSO_SERVER_URL = 'http://' + SSO_SERVER_ADDR + ':' + str(SSO_SERVER_PORT)
REDIRECT_LOGIN_URL = "https://web2.cc.ntu.edu.tw/p/s/login2/p1.php"  # TODO change it to correct one

redirect_html = '<script>location.href = "{}";</script>'.format(REDIRECT_LOGIN_URL)
success_login_html = '''
<p>登入成功！請跳轉回 Ceiba Downloader...</p>
<p>Login successfully! Please redirect to Ceiba Downloader!</p>
'''

class SSOServerSignal(QObject):
    finished = Signal()

class SSOServer(QRunnable):

    def __init__(self, ceiba: Ceiba, host=SSO_SERVER_ADDR, port=SSO_SERVER_PORT):
        super().__init__()
        self.app = Flask("ceiba-downloader")
        self.ceiba = ceiba
        self.signals = SSOServerSignal()
        self.server = make_server(host, port, self.app)

        @self.app.route('/')
        def __home(): return self.home()
        @self.app.route('/login')
        def __login(): return self.login()

    def home(self):
        return redirect_html

    def login(self):
        session = request.args.get('session')
        role_code = request.args.get('role')
        if session == "" or role_code == "":
            return "你必須提供 Session 值以及登入身分！"
        try:
            self.ceiba.login_localhost_sso(session, role_code)
        except Exception as e:
            return e.__str__()
        self.signals.finished.emit()
        return success_login_html

    def run(self):
        print("start http server")
        self.server.serve_forever()

    def shutdown(self):
        print("server shutting down")
        self.server.shutdown()