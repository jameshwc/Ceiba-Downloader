# This Python file uses the following encoding: utf-8
from os import error
import sys
from typing import Dict

from PySide6 import QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from exceptions import InvalidCredentials
from pytoggle import PyToggle
from ceiba import Ceiba
class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.create_login_group_box()
        self.create_courses_group_box()
        
        main_layout = QGridLayout()
        main_layout.addWidget(self.login_group_box, 0, 0)
        main_layout.addWidget(self.courses_group_box, 1, 0)
        main_layout.setRowStretch(1, 1)
        # main_layout.setRowStretch(2, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        self.setLayout(main_layout)

    def create_login_group_box(self):
        self.login_group_box = QGroupBox("使用者")
        
        username_label = QLabel('帳號 (學號):')
        self.username_edit = QLineEdit('')
        
        password_label = QLabel('密碼 :')
        self.password_edit = QLineEdit('')
        self.password_edit.setEchoMode(QLineEdit.Password)
		
        login_button = QPushButton('Login')
        login_button.clicked.connect(self.login)
        
        self.method_toggle = PyToggle(width=80)
        
        def switch_method():
            if self.method_toggle.isChecked():
                username_label.setText('Cookie [user]:')
                password_label.setText('Cookie [PHPSESSID]:')
            else:
                username_label.setText('帳號 (學號):')
                password_label.setText('密碼 :')
                
        self.method_toggle.clicked.connect(switch_method)
        
        method_left_label = QLabel('登入方式：帳號 / 密碼（不安全）')
        method_right_label = QLabel('cookies （安全）')
        
        self.login_layout = QGridLayout()
        
        self.login_layout.addWidget(method_left_label, 0, 0, 1, 1)
        self.login_layout.addWidget(self.method_toggle, 0, 1, 1, 1)
        self.login_layout.addWidget(method_right_label, 0, 2, 1, 1)
        
        self.login_layout.addWidget(username_label, 1, 0)
        self.login_layout.addWidget(self.username_edit, 1, 1, 1, 2)
        self.login_layout.addWidget(password_label, 2, 0)
        self.login_layout.addWidget(self.password_edit, 2, 1, 1, 2)
        self.login_layout.addWidget(login_button, 3, 1, 1, 2)
        self.login_layout.setColumnStretch(0, 0)
        self.login_layout.setColumnStretch(1, 1)
        self.login_group_box.setLayout(self.login_layout)

    def create_courses_group_box(self):
        self.courses_group_box = QGroupBox("課程")
    
    def login(self):
        login_error_msg_box = QMessageBox()
        login_error_msg_box.setWindowTitle('登入失敗！')
        login_error_msg_box.setIcon(QMessageBox.Critical)
        login_error_msg_box.setStandardButtons(QMessageBox.Retry)
        
        if self.method_toggle.isChecked():
            ceiba = Ceiba(cookie_user=self.username_edit.text(), cookie_PHPSESSID=self.password_edit.text())
        else:
            try:
                ceiba = Ceiba(username=self.username_edit.text(), password=self.password_edit.text())
            except InvalidCredentials:
                login_error_msg_box.setText('登入失敗！請檢查帳號（學號）與密碼輸入是否正確！')
                login_error_msg_box.exec()
                return
        try:
            courses = ceiba.get_courses_list()
        except InvalidCredentials:
            login_error_msg_box.setText('登入失敗！請檢查 Cookies 有沒有輸入正確！')
            login_error_msg_box.exec()
            return
        
        for i in reversed(range(self.login_layout.count())): 
            self.login_layout.itemAt(i).widget().setParent(None)
        
        welcome_label = QLabel(ceiba.student_name + "，歡迎你！")    
        welcome_label.setFont(QFont('', 32))
        self.login_layout.addWidget(welcome_label, 0, 0)
        self.login_group_box.setLayout(self.login_layout)
        
        courses_main_layout = QGridLayout()
        courses_by_semester_layouts: Dict[str, QLayout] = {}
        
        for course in courses:
            if course.semester not in courses_by_semester_layouts:
                layout = QGridLayout()
                courses_by_semester_layouts[course.semester] = layout
            checkbox = QCheckBox("&"+ course.cname)
            checkbox.setChecked(True)
            courses_by_semester_layouts[course.semester].addWidget(checkbox)
        
        tabWidget = QTabWidget()
        for semester in courses_by_semester_layouts:
            semester_widget = QWidget()
            semester_widget.setLayout(courses_by_semester_layouts[semester])
            tabWidget.addTab(semester_widget, "&"+semester)
        
        options_and_download_groupbox = QGroupBox()
        options_and_download_layout = QVBoxLayout()
        download_button = QPushButton('下載')
        check_all_courses_button = QCheckBox('勾選全部')
        options_and_download_layout.addWidget(check_all_courses_button)
        options_and_download_layout.addWidget(download_button)
        options_and_download_groupbox.setLayout(options_and_download_layout)
        courses_main_layout.addWidget(tabWidget, 0, 0)
        courses_main_layout.addWidget(options_and_download_groupbox, 1, 0)
        self.courses_group_box.setLayout(courses_main_layout)
        self.courses_group_box.setCheckable(True)
            
if __name__ == "__main__":
    app = QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())