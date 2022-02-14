# This Python file uses the following encoding: utf-8
import logging
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Dict, List

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QAction, QActionGroup, QFontDatabase, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox,
                               QFileDialog, QGridLayout, QGroupBox,
                               QHBoxLayout, QLabel, QLayout, QLineEdit,
                               QMainWindow, QMessageBox, QProgressBar,
                               QPushButton, QRadioButton, QScrollArea,
                               QSizePolicy, QTabWidget, QTextEdit, QVBoxLayout,
                               QWidget, QMenu, QWidgetAction, QComboBox)
from qt_material import apply_stylesheet

from ceiba import util
from ceiba.ceiba import Ceiba
from ceiba.course import Course
from ceiba.const import Role, strings
from qt_custom_widget import PyLogOutput, PyToggle

dirname = os.path.dirname(__file__) or '.'

def exception_handler(type, value, tb: TracebackType):
    logging.getLogger().error(
        "{}: {}\n{}, line {}".format(type.__name__, str(value), tb.tb_frame.f_code.co_filename, tb.tb_lineno)
    )


class CeibaSignals(QObject):
    finished = Signal()
    success = Signal()
    failed = Signal()
    progress = Signal(int)
    result = Signal(object)


class Worker(QRunnable):
    def __init__(self, fn, progress=False, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = CeibaSignals()
        if progress:
            self.kwargs["progress"] = self.signals.progress

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            logging.error(e)
            self.signals.failed.emit()
        else:
            self.signals.result.emit(result)
            self.signals.success.emit()
        finally:
            self.signals.finished.emit()

class TicketSubmit(QMainWindow):
    def __init__(self, ceiba: Ceiba, thread_pool: QThreadPool, parent=None):
        super().__init__(parent)
        self.ceiba = ceiba
        self.thread_pool = thread_pool
        self.setCentralWidget(QWidget(self))
        main_layout = QVBoxLayout(self.centralWidget())
        self.setWindowTitle('意見回饋 / Report Issue')
        type_group_box = QGroupBox()
        self.type_button_group = QButtonGroup()
        type_layout = QHBoxLayout()
        
        self.issue_radio_button = QRadioButton('Issue', type_group_box)
        self.feedback_radio_button = QRadioButton('Feedback', type_group_box)
        self.others_radio_button = QRadioButton('Others', type_group_box)
        self.issue_radio_button.setChecked(True)
        for button in [self.issue_radio_button, self.feedback_radio_button, self.others_radio_button]:
            type_layout.addWidget(button)
            self.type_button_group.addButton(button)
        
        type_group_box.setLayout(type_layout)
        type_group_box.setProperty("class", "no-padding")

        self.content_edit = QTextEdit()
        self.submit_button = QPushButton('傳送 / Submit')
        self.submit_button.clicked.connect(self.submit_ticket)
        self.anonymous_checkbox = QCheckBox("匿名傳送 / Anonymous")
        if not self.ceiba.is_login:
            self.anonymous_checkbox.setChecked(True)
            self.anonymous_checkbox.setDisabled(True)
        main_layout.addWidget(type_group_box, 1)
        main_layout.addWidget(self.content_edit, 8)
        main_layout.addWidget(self.anonymous_checkbox, 1)
        main_layout.addWidget(self.submit_button, 1)
    
    def submit_ticket(self):
        worker = Worker(self.ceiba.send_ticket, progress=False, ticket_type=self.type_button_group.checkedButton().text(),
                        content=self.content_edit.toPlainText(), anonymous=self.anonymous_checkbox.isChecked())
        worker.signals.failed.connect(self.close)
        worker.signals.success.connect(self.close)
        self.thread_pool.start(worker)
        self.submit_button.setDisabled(True)

class About(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCentralWidget(QWidget(self))
        main_layout = QGridLayout(self.centralWidget())
        self.setWindowTitle('關於 / About')
        
        about_icon = QLabel()
        about_icon.setProperty("class", "no-padding")
        icon = QPixmap(dirname / Path('resources/ceiba.ico'))
        icon = icon.scaled(36, 36, Qt.KeepAspectRatioByExpanding)
        about_icon.setPixmap(icon)
        about_icon.show()
        about_text = QLabel('Ceiba Downloader VERSION')
        about_layout = QHBoxLayout()
        about_layout.addWidget(about_icon)
        about_layout.addWidget(about_text, 1)
        about_group_box = QGroupBox(self)
        about_group_box.setLayout(about_layout)
        github_button = QPushButton('Source Code')
        github_button.clicked.connect(self.open_github)
        author_button = QPushButton('Author: Jameshwc')
        author_button.clicked.connect(self.open_author)

        main_layout.addWidget(about_group_box, 0, 0, 1, 2)
        main_layout.addWidget(author_button, 1, 0)
        main_layout.addWidget(github_button, 1, 1)
    
    def open_author(self):
        webbrowser.open('https://jameshsu.csie.org')
    
    def open_github(self):
        webbrowser.open('https://github.com/jameshwc/Ceiba-Downloader')
    

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ceiba Downloader by Jameshwc")
        icon_path = dirname / Path("resources/ceiba.ico")
        self.setWindowIcon(QIcon(str(icon_path)))
        self.ceiba = Ceiba()
        self.language = 'zh-tw'
        
        self.create_menu_bar()
        self.create_login_group_box()
        self.create_courses_group_box()
        self.create_options_and_download_groupbox()
        self.create_status_group_box()
        self.set_zh_tw()
        
        self.login_group_box.move
        self.courses_group_box.setHidden(True)
        self.options_and_download_groupbox.setHidden(True)
        self.setCentralWidget(QWidget(self))
        self.thread_pool = QThreadPool()

        self.main_layout = QGridLayout(self.centralWidget())
        self.user_layout = QGridLayout()
        self.user_layout.addWidget(self.login_group_box, 0, 0)
        self.user_layout.addWidget(self.courses_group_box, 1, 0)
        self.user_layout.addWidget(self.options_and_download_groupbox, 2, 0)
        self.user_layout.setRowStretch(0, 1)
        self.user_layout.setRowStretch(1, 4)
        self.user_layout.setRowStretch(2, 1)
        self.user_groupbox = QGroupBox()
        self.user_groupbox.setLayout(self.user_layout)
        self.main_layout.addWidget(self.user_groupbox, 0, 0)
        self.main_layout.addWidget(self.status_group_box, 0, 1)
        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 1)
        self.check_for_updates()
        self.username_edit.setFocus()

    def create_menu_bar(self):
        self.menu_bar = self.menuBar()
        self.menu_language = self.menu_bar.addMenu("&語言 / Language")
        self.menu_language_group = QActionGroup(self)
        
        self.menu_chinese = QAction("&中文", self, checkable=True)
        self.menu_chinese.setChecked(True)
        self.menu_english = QAction("&English", self, checkable=True)

        self.menu_chinese.triggered.connect(self.set_zh_tw)
        self.menu_english.triggered.connect(self.set_en)

        self.menu_language_group.addAction(self.menu_english)
        self.menu_language_group.addAction(self.menu_chinese)
        
        self.menu_language.addAction(self.menu_chinese)
        self.menu_language.addAction(self.menu_english)

        menu = self.menu_bar
        if sys.platform == 'darwin':  # mac can't have one action menu
            self.menu_help = self.menu_bar.addMenu("&幫助 / Help")
            menu = self.menu_help
        
        self.menu_report = menu.addAction("&意見回饋 / Report Issue")
        self.menu_report.triggered.connect(self.open_ticket_window)
        
        self.menu_check_update = menu.addAction("&檢查更新 / Check for Updates")
        self.menu_check_update.triggered.connect(self.check_for_updates)
        self.has_checked_onstart = False  # check updates when onstart
        
        self.menu_about = menu.addAction("&關於 / About ")  # extra space for fixing strange mac behavior
        self.menu_about.triggered.connect(self.open_about_window)

    def create_login_group_box(self):
        self.login_group_box = QGroupBox(self)

        self.username_label = QLabel()
        self.username_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.username_edit = QLineEdit("")
        self.password_label = QLabel()
        self.password_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.password_edit = QLineEdit("")
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.login_user_menu = QComboBox(self)
        for role in Role:
            self.login_user_menu.addItem(strings.role(role))

        self.login_button = QPushButton()
        self.login_button.clicked.connect(self.login)

        self.username_edit.returnPressed.connect(self.login_button.click)
        self.password_edit.returnPressed.connect(self.login_button.click)
        
        self.method_toggle = PyToggle(width=80)

        def switch_method():
            if self.method_toggle.isChecked():
                self.username_label.setHidden(True)
                self.username_edit.setHidden(True)
                self.password_label.setText("Cookie [PHPSESSID]:")
            else:
                self.username_label.setHidden(False)
                self.username_edit.setHidden(False)
                self.password_label.setText(self.password_label_text)

        self.method_toggle.clicked.connect(switch_method)

        self.login_method_left_label = QLabel()
        self.login_method_right_label = QLabel()
        self.login_method_left_label.setProperty('class', 'hover')
        self.login_method_right_label.setProperty('class', 'hover')
        
        self.welcome_label = QLabel()
        self.welcome_label.setProperty('class', 'welcome')
        
        self.login_layout = QGridLayout()

        self.login_layout.addWidget(self.login_method_left_label, 0, 0, 1, 1)
        self.login_layout.addWidget(self.method_toggle, 0, 1, 1, 1)
        self.login_layout.addWidget(self.login_method_right_label, 0, 2, 1, 1)

        self.login_layout.addWidget(self.username_label, 1, 0)
        self.login_layout.addWidget(self.username_edit, 1, 1, 1, 2)
        self.login_layout.addWidget(self.password_label, 2, 0)
        self.login_layout.addWidget(self.password_edit, 2, 1, 1, 2)
        self.login_layout.addWidget(self.login_user_menu, 3, 0, 1, 1)
        self.login_layout.addWidget(self.login_button, 3, 1, 1, 2)
        self.login_layout.setColumnStretch(0, 0)
        self.login_layout.setColumnStretch(1, 1)
        self.login_group_box.setLayout(self.login_layout)

    def create_courses_group_box(self):
        self.courses_group_box = QGroupBox()
        self.courses_group_box.setDisabled(True)
        self.courses_checkboxes: List[QCheckBox] = []
        self.courses = []
        self.check_all_courses_checkbox = QCheckBox()

    def create_status_group_box(self):
        self.status_group_box = QGroupBox()
        self.status_layout = QGridLayout()

        self.log_output = PyLogOutput(self.status_group_box)
        self.log_output.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
            )
        )
        logging.getLogger().addHandler(self.log_output)
        logging.getLogger("urllib3").propagate = False
        logging.getLogger().setLevel(logging.INFO)
        # logging.getLogger().setLevel(logging.DEBUG)
        # sys.excepthook = exception_handler
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        self.status_layout.addWidget(self.log_output.widget)
        self.status_layout.addWidget(self.progress_bar)
        self.status_group_box.setLayout(self.status_layout)

    def login(self):
        if self.method_toggle.isChecked():
            worker = Worker(self.ceiba.login, progress=True,
                    cookie_PHPSESSID=self.password_edit.text(),
                    role=Role(self.login_user_menu.currentIndex())
                )
            self.progress_bar.setMaximum(1)
        else:
            worker = Worker(self.ceiba.login, progress=True,
                            username=self.username_edit.text(),
                            password=self.password_edit.text(),
                            role=Role(self.login_user_menu.currentIndex())
                        )
            self.progress_bar.setMaximum(2)

        def fail_handler():
            self.login_button.setEnabled(True)
            self.password_edit.clear()

        worker.signals.failed.connect(fail_handler)
        worker.signals.success.connect(self.after_login_successfully)
        worker.signals.progress.connect(self.update_progressbar)
        self.thread_pool.start(worker)
        self.login_button.setDisabled(True)

    def after_login_successfully(self):

        self.courses_group_box.setHidden(False)
        self.update_progressbar(0)  # busy indicator
        for i in reversed(range(self.login_layout.count())):
            self.login_layout.itemAt(i).widget().setParent(None)
                
        self.welcome_label.setText(self.welcome_text.format(self.ceiba.student_name, self.ceiba.email))
        self.login_layout.addWidget(self.welcome_label, 0, 0)
        self.login_group_box.setLayout(self.login_layout)
        worker = Worker(self.ceiba.get_courses_list)
        worker.signals.result.connect(self.fill_course_group_box)
        self.thread_pool.start(worker)
        self.progress_bar.setMaximum(1)

    def fill_course_group_box(self, courses: List[Course]):
        self.courses = courses
        self.courses_group_box.setDisabled(False)

        courses_main_layout = QGridLayout()
        courses_by_semester_layouts: Dict[str, QLayout] = {}

        for course in self.courses:
            
            if course.semester not in courses_by_semester_layouts:
                layout = QGridLayout()
                courses_by_semester_layouts[course.semester] = layout
            
            if self.language == 'zh-tw':
                checkbox = QCheckBox("&" + course.cname)
            elif self.language == 'en':
                checkbox = QCheckBox('&' + course.ename)
            
            self.courses_checkboxes.append(checkbox)
            courses_by_semester_layouts[course.semester].addWidget(checkbox)

        tabWidget = QTabWidget()
        for semester in courses_by_semester_layouts:
            semester_widget = QScrollArea()
            semester_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            semester_widget.setWidgetResizable(True)
            temp_widget = QWidget()
            semester_widget.setWidget(temp_widget)
            temp_widget.setLayout(courses_by_semester_layouts[semester])
            tabWidget.addTab(semester_widget, "&" + semester)

        def click_all_courses_checkbox(state):
            for checkbox in self.courses_checkboxes:
                if state == Qt.Checked:
                    checkbox.setCheckState(Qt.Checked)
                elif state == Qt.Unchecked:
                    checkbox.setCheckState(Qt.Unchecked)

        self.check_all_courses_checkbox.stateChanged.connect(click_all_courses_checkbox)

        courses_main_layout.addWidget(tabWidget, 0, 0)
        courses_main_layout.addWidget(self.check_all_courses_checkbox, 1, 0)
        self.courses_group_box.setLayout(courses_main_layout)
        self.options_and_download_groupbox.setHidden(False)

    def create_options_and_download_groupbox(self):
        self.options_and_download_groupbox = QGroupBox()
        options_and_download_layout = QGridLayout()
        self.download_button = QPushButton()
        self.download_button.clicked.connect(self.download)

        self.download_item_menu = QMenu(self)
        for item_name in util.cname_map.values():
            checkbox = QCheckBox("&" + item_name)
            checkable_action = QWidgetAction(self.download_item_menu)
            checkable_action.setDefaultWidget(checkbox)
            self.download_item_menu.addAction(checkable_action)
            if item_name == "課程資訊":
                checkbox.setChecked(True)
                checkbox.setDisabled(True)
            elif item_name == "課程行事曆":
                checkbox.setDisabled(True)
        self.download_item_menu_button = QPushButton(self)
        self.download_item_menu_button.setMenu(self.download_item_menu)
        self.download_item_label = QLabel()
        self.download_item_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        
        self.check_all_download_item_checkbox = QCheckBox()
        def download_item_menu_check_all():
            for action in self.download_item_menu.actions():
                # act: QWidgetAction = None
                if not action.defaultWidget().isEnabled():
                    continue
                if self.check_all_download_item_checkbox.isChecked():
                    action.defaultWidget().setChecked(True)
                else:
                    action.defaultWidget().setChecked(False)
        self.check_all_download_item_checkbox.stateChanged.connect(download_item_menu_check_all)

        self.only_download_homepage_checkbox = QCheckBox()
        self.only_download_homepage_checkbox.setProperty('class', 'hover')
        
        def disable_download_item_menu_button():
            if self.only_download_homepage_checkbox.isChecked():
                self.download_item_menu_button.setDisabled(True)
                self.check_all_download_item_checkbox.setDisabled(True)
                self.download_item_label.setDisabled(True)
            else:
                self.download_item_menu_button.setEnabled(True)
                self.check_all_download_item_checkbox.setEnabled(True)
                self.download_item_label.setEnabled(True)
        
        self.only_download_homepage_checkbox.clicked.connect(disable_download_item_menu_button)
        download_item_layout = QHBoxLayout()
        download_item_layout.addWidget(self.download_item_label)
        download_item_layout.addWidget(self.download_item_menu_button)
        download_item_layout.addWidget(self.check_all_download_item_checkbox)
        download_item_layout.addWidget(self.only_download_homepage_checkbox)
        download_item_group_box = QGroupBox()
        download_item_group_box.setLayout(download_item_layout)

        self.filepath_label = QLabel()
        self.filepath_line_edit = QLineEdit()
        self.filepath_line_edit.setReadOnly(True)
        self.file_browse_button = QPushButton()
        self.file_browse_button.clicked.connect(self.get_save_directory)

        file_groupbox_layout = QHBoxLayout()
        file_groupbox_layout.addWidget(self.filepath_label)
        file_groupbox_layout.addWidget(self.filepath_line_edit)
        file_groupbox_layout.addWidget(self.file_browse_button)
        file_groupbox = QGroupBox()
        file_groupbox.setLayout(file_groupbox_layout)

        download_item_group_box.setProperty("class", "no-padding")
        options_and_download_layout.addWidget(download_item_group_box, 0, 0)
        file_groupbox.setProperty("class", "no-padding")
        options_and_download_layout.addWidget(file_groupbox, 1, 0)
        options_and_download_layout.addWidget(self.download_button, 2, 0)

        self.options_and_download_groupbox.setProperty("class", "no-padding")
        self.options_and_download_groupbox.setLayout(options_and_download_layout)

    def download(self):
        items = []
        for action in self.download_item_menu.actions():
            action: QWidgetAction = action
            checkbox: QCheckBox = action.defaultWidget()
            if checkbox.isChecked():
                module_name = checkbox.text()[1:]  # remove '&'
                for ename, cname in util.cname_map.items():
                    if module_name in [cname, ename]:
                        items.append(ename)
                        break
        
        course_id_list = []
        for i in range(len(self.courses_checkboxes)):
            if self.courses_checkboxes[i].isChecked():
                course_id_list.append(self.courses[i].id)
        
        
        self.progress_bar.setMaximum(len(course_id_list) * len(items))
        if self.only_download_homepage_checkbox.isChecked():
            worker = Worker(
                self.ceiba.download_ceiba_homepage,
                path=self.filepath_line_edit.text(),
                course_id_filter=course_id_list,
            )
        else:
            worker = Worker(
                self.ceiba.download_courses,
                progress=True,
                path=self.filepath_line_edit.text(),
                course_id_filter=course_id_list,
                modules_filter=items,
            )
            worker.signals.progress.connect(self.update_progressbar)
        worker.signals.success.connect(self.after_download_successfully)
        worker.signals.finished.connect(self.after_download)
        self.thread_pool.start(worker)
        self.download_button.setDisabled(True)

    def get_save_directory(self):
        filepath = QFileDialog.getExistingDirectory(self)
        self.filepath_line_edit.setText(filepath)

    def after_download(self):
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.download_button.setEnabled(True)
        self.progress_bar.setMaximum(1)
        self.progress_bar.reset()

    def after_download_successfully(self):
        def open_path(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                # TODO: Not test on Linux/Mac yet.
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                import subprocess

                subprocess.call([opener, path])
        
        self.download_finish_msgbox = QMessageBox(self)
        self.download_finish_msgbox.setWindowTitle("Ceiba Downloader by Jameshwc")
        self.download_finish_msgbox.setText(self.download_finish_msgbox_text)
        self.download_finish_msgbox.addButton(self.download_finish_msgbox_open_dir_text, self.download_finish_msgbox.YesRole)
        self.download_finish_msgbox.addButton(self.download_finish_msgbox_open_browser_text, self.download_finish_msgbox.ActionRole)
        self.download_finish_msgbox.exec()
        role = self.download_finish_msgbox.buttonRole(self.download_finish_msgbox.clickedButton())
        if role == self.download_finish_msgbox.ActionRole:  # open index.html
            open_path(Path(self.ceiba.path, "index.html"))
        elif role == self.download_finish_msgbox.YesRole:  # open dir
            open_path(Path(self.ceiba.path))

    def update_progressbar(self, add_value: int):
        if add_value < 0:
            self.progress_bar.setMaximum(self.progress_bar.maximum() + (add_value * -1))
        elif add_value == 0:  # magic number
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(0)
            self.progress_bar.setMinimum(0)
        elif add_value == 999:  # magic number
            self.progress_bar.setMaximum(self.progress_bar.maximum())
        else:
            self.progress_bar.setValue(self.progress_bar.value() + add_value)

    def open_ticket_window(self):
        self.ticket_window = TicketSubmit(self.ceiba, self.thread_pool, self)
        self.ticket_window.move(self.log_output.geometry().center())
        self.ticket_window.show()
    
    def open_about_window(self):
        about_window = About(self)
        about_window.show()
    
    def check_for_updates(self):
        worker = Worker(self.ceiba.check_for_updates)
        worker.signals.result.connect(self.open_check_for_updates_msgbox)
        self.thread_pool.start(worker)

    def open_check_for_updates_msgbox(self, has_new_version: bool):
        if has_new_version:
            update_msgbox = QMessageBox(self)
            update_msgbox.setIcon(QMessageBox.Information)
            update_msgbox.setWindowTitle('Ceiba Downloader By Jameshwc')
            update_msgbox.setText('There are available updates!')
            update_msgbox.addButton('Download the latest version', QMessageBox.ActionRole)
            update_msgbox.addButton('Cancel', QMessageBox.RejectRole)
            update_msgbox.exec()
            if update_msgbox.buttonRole(update_msgbox.clickedButton()) == QMessageBox.ActionRole:
                webbrowser.open('https://github.com/jameshwc/Ceiba-Downloader/releases/latest')
        elif self.has_checked_onstart:
            QMessageBox.information(self, 'Ceiba Downloader by Jameshwc', 'There are currently no updates available.', QMessageBox.Close)
        else:
            self.has_checked_onstart = True

    def set_en(self):
        self.ceiba.set_lang('en')
        self.language = 'en'
        self.login_group_box.setTitle('User')
        self.username_label.setText('Username (Student ID): ')
        if not self.method_toggle.isChecked():
            self.password_label.setText('Password: ')
        self.password_label_text = 'Password: '
            
        self.login_button.setText('Log in')
        self.login_method_left_label.setText('Username/Password [?]')
        self.login_method_right_label.setText('Cookies [?]')
        self.login_method_left_label.setToolTip('It\'s unsafe to log in via a third-party program! You should use cookies as your credential instead.')
        self.login_method_right_label.setToolTip('Log in Ceiba manually and you can view cookies using F12 in your browser. Please copy the content of PHPSESSID in your cookies.')
        for role in Role:
            self.login_user_menu.setItemText(role.value, strings.role(role))
        
        self.courses_group_box.setTitle('Courses')
        self.status_group_box.setTitle('Status')
        self.welcome_text = "Welcome, {} ({})!"
        self.welcome_label.setText(self.welcome_text.format(self.ceiba.student_name, self.ceiba.email))

        for i in range(len(self.courses_checkboxes)):
            self.courses_checkboxes[i].setText("&" + self.courses[i].ename)
        
        self.download_button.setText('Download')
        self.check_all_courses_checkbox.setText('Check All Courses')
        self.download_item_label.setText('Download Items: ')
        self.check_all_download_item_checkbox.setText('Check All Items ')
        self.only_download_homepage_checkbox.setText('Only Homepage [?]')
        self.only_download_homepage_checkbox.setToolTip(
        '''Download Ceiba homepage only.
        You should use this option when you had downloaded a few courses before
        and don\'t want to repetively download those courses.''')
        self.filepath_label.setText('Path: ')
        self.file_browse_button.setText('Browse')
        self.download_item_menu_button.setText("<-- Click to expand -->")
        for action in self.download_item_menu.actions():
            checkbox = action.defaultWidget()
            if checkbox.text()[1:] in util.ename_map:
                checkbox.setText("&" + util.ename_map[checkbox.text()[1:]])
            
        self.download_finish_msgbox_text = 'The download has completed!'
        self.download_finish_msgbox_open_dir_text = 'Open Ceiba directory'
        self.download_finish_msgbox_open_browser_text = 'Open Ceiba homepage'

    
    def set_zh_tw(self):
        self.ceiba.set_lang('zh-tw')
        self.language = 'zh-tw'
        self.login_group_box.setTitle('使用者')
        self.username_label.setText('帳號 (學號) :')
        if not self.method_toggle.isChecked():
            self.password_label.setText('密碼 :')
        self.password_label_text = '密碼 :'
        
        self.login_button.setText('登入')
        self.login_method_left_label.setText('登入方式：帳號 / 密碼 [?]')
        self.login_method_right_label.setText('cookies [?]')
        self.login_method_left_label.setToolTip('除非你信任本程式作者，否則不應該在計中網站以外的地方輸入自己的帳密！')
        self.login_method_right_label.setToolTip('透過手動登入 Ceiba 可以從瀏覽器的 F12 視窗看到 Cookies，請複製 PHPSESSID 的內容')
        for role in Role:
            self.login_user_menu.setItemText(role.value, strings.role(role))
        
        self.courses_group_box.setTitle('課程')
        self.status_group_box.setTitle('狀態')
        self.welcome_text = "{} ({})，歡迎你！"
        self.welcome_label.setText(self.welcome_text.format(self.ceiba.student_name, self.ceiba.email))
        
        for i in range(len(self.courses_checkboxes)):
            self.courses_checkboxes[i].setText("&" + self.courses[i].cname)

        self.download_button.setText('下載')
        self.check_all_courses_checkbox.setText('勾選所有課程')
        self.download_item_label.setText(' 下載項目： ')
        self.check_all_download_item_checkbox.setText(' 勾選全部下載項目 ')
        self.only_download_homepage_checkbox.setText(' 只下載首頁[?] ')
        self.only_download_homepage_checkbox.setToolTip(
            '只下載 Ceiba 首頁。當你已經下載了部分課程，且不希望重複下載那些課程時，可以勾選這個選項。')
        self.filepath_label.setText(' 存放路徑： ')
        self.file_browse_button.setText('瀏覽')
        self.download_item_menu_button.setText("<-- 點我展開 -->")
        for action in self.download_item_menu.actions():
            checkbox: QCheckBox = action.defaultWidget()
            if checkbox.text()[1:] in util.cname_map:
                checkbox.setText("&" + util.cname_map[checkbox.text()[1:]])
        
        self.download_finish_msgbox_text = '下載完成！'
        self.download_finish_msgbox_open_dir_text = '打開檔案目錄'
        self.download_finish_msgbox_open_browser_text = '打開 Ceiba 網頁'


if __name__ == "__main__":
    app = QApplication([])

    window = MyApp()
    custom_qss_path = dirname / Path("resources/custom.qss")
    font_path = dirname / Path("resources/GenSenRounded-M.ttc")

    font_id = QFontDatabase.addApplicationFont(str(font_path))
    font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
    extra = {"font_family": font_name}
    apply_stylesheet(window, theme="dark_lightgreen.xml", extra=extra)
    stylesheet = window.styleSheet()
    window.setStyleSheet(stylesheet + custom_qss_path.read_text().format(**os.environ))
    window.showMaximized()
    window.show()

    sys.exit(app.exec())
