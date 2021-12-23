# This Python file uses the following encoding: utf-8
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QPalette, QColor
from PySide6.QtWidgets import (QApplication, QCheckBox, QFileDialog,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLayout, QLineEdit, QMainWindow, QMessageBox,
                               QProgressBar, QPushButton, QScrollArea, QSizePolicy, QTabWidget, QVBoxLayout, QWidget)

from ceiba.ceiba import Ceiba
from ceiba import util
from ceiba.course import Course
from ceiba.exceptions import InvalidCredentials, InvalidLoginParameters
from qt_custom_widget import PyCheckableComboBox, PyLogOutput, PyToggle
from qt_material import apply_stylesheet

def exception_handler(type, value, tb):
    logging.getLogger().error("{}: {}\n{}".format(type.__name__, str(value), tb.tb_frame.f_code.co_filename))


class CeibaSignals(QObject):
    finished = Signal()
    success = Signal()
    failed = Signal()
    progress = Signal(int)
    result = Signal(object)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = CeibaSignals()
        self.kwargs["progress"] = self.signals.progress

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            logging.error(e)
            logging.debug(e, exc_info=True)
            self.signals.failed.emit()
        else:
            self.signals.result.emit(result)
            self.signals.success.emit()
        finally:
            self.signals.finished.emit()


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ceiba Downloader by Jameshwc")
        icon_path = Path('resources/ceiba.ico')
        if hasattr(sys, '_MEIPASS'):
            icon_path = sys._MEIPASS / icon_path
        self.setWindowIcon(QIcon(str(icon_path)))

        self.create_login_group_box()
        self.create_courses_group_box()
        self.create_options_and_download_groupbox()
        self.create_status_group_box()
        
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

    def create_login_group_box(self):
        self.login_group_box = QGroupBox("使用者")

        username_label = QLabel('帳號 (學號):')
        username_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.username_edit = QLineEdit('')

        password_label = QLabel('密碼 :')
        password_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.password_edit = QLineEdit('')
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('登入')
        self.login_button.clicked.connect(self.login)

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
        self.login_layout.addWidget(self.login_button, 3, 1, 1, 2)
        self.login_layout.setColumnStretch(0, 0)
        self.login_layout.setColumnStretch(1, 1)
        self.login_group_box.setLayout(self.login_layout)

    def create_courses_group_box(self):
        self.courses_group_box = QGroupBox("課程")
        self.courses_group_box.setDisabled(True)

    def create_status_group_box(self):
        self.status_group_box = QGroupBox("狀態")
        self.status_layout = QGridLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        self.log_output = PyLogOutput(self.status_group_box)
        self.log_output.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                              '%Y-%m-%d %H:%M:%S'))
        logging.getLogger().addHandler(self.log_output)
        logging.getLogger("urllib3").propagate = False
        logging.getLogger().setLevel(logging.INFO)
        # logging.getLogger().setLevel(logging.DEBUG)
        sys.excepthook = exception_handler

        self.status_layout.addWidget(self.log_output.widget)
        self.status_layout.addWidget(self.progress_bar)
        self.status_group_box.setLayout(self.status_layout)

    def login(self):

        try:
            if self.method_toggle.isChecked():
                self.ceiba = Ceiba(cookie_user=self.username_edit.text(),
                                cookie_PHPSESSID=self.password_edit.text())
                self.progress_bar.setMaximum(1)
            else:
                self.ceiba = Ceiba(username=self.username_edit.text(),
                                password=self.password_edit.text())
                self.progress_bar.setMaximum(2)
        except InvalidLoginParameters as e:
            logging.error(e)
            return

        def fail_handler():
            if self.method_toggle.isChecked():
                QMessageBox.critical(self, '登入失敗！',
                                     '登入失敗！請檢查 Cookies 有沒有輸入正確！',
                                     QMessageBox.Retry)
            else:
                QMessageBox.critical(self, '登入失敗！', '登入失敗！請檢查帳號（學號）與密碼輸入是否正確！',
                                     QMessageBox.Retry)
            self.login_button.setEnabled(True)
            self.password_edit.clear()

        worker = Worker(self.ceiba.login)
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

        welcome_label = QLabel(self.ceiba.student_name + "，歡迎你！")
        welcome_label.setFont(QFont('', 24))
        self.login_layout.addWidget(welcome_label, 0, 0)
        self.login_group_box.setLayout(self.login_layout)

        worker = Worker(self.ceiba.get_courses_list)
        worker.signals.result.connect(self.fill_course_group_box)
        worker.signals.progress.connect(self.update_progressbar)
        self.thread_pool.start(worker)
        self.progress_bar.setMaximum(1)

    def fill_course_group_box(self, courses: List[Course]):
        self.courses_group_box.setDisabled(False)

        courses_main_layout = QVBoxLayout()
        courses_by_semester_layouts: Dict[str, QLayout] = {}
        self.courses_checkboxes: List[QCheckBox] = []

        for course in courses:
            if course.semester not in courses_by_semester_layouts:
                layout = QVBoxLayout()
                courses_by_semester_layouts[course.semester] = layout
            checkbox = QCheckBox("&" + course.cname)
            self.courses_checkboxes.append(checkbox)
            courses_by_semester_layouts[course.semester].addWidget(checkbox)
        
        courses_main_layout = QGridLayout()
        courses_by_semester_layouts: Dict[str, QLayout] = {}
        self.courses_checkboxes: List[QCheckBox] = []

        for course in courses:
            if course.semester not in courses_by_semester_layouts:
                layout = QGridLayout()
                courses_by_semester_layouts[course.semester] = layout
            checkbox = QCheckBox("&" + course.cname)
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

        check_all_courses_checkbox = QCheckBox('勾選全部課程')
        check_all_courses_checkbox.stateChanged.connect(
            click_all_courses_checkbox)
        
        courses_main_layout.addWidget(tabWidget, 0, 0)
        courses_main_layout.addWidget(check_all_courses_checkbox, 1, 0)
        self.courses_group_box.setLayout(courses_main_layout)
        self.options_and_download_groupbox.setHidden(False)

    def create_options_and_download_groupbox(self):
        self.options_and_download_groupbox = QGroupBox()
        options_and_download_layout = QGridLayout()
        self.download_button = QPushButton('下載')
        self.download_button.clicked.connect(self.download)

        self.download_item_combo_box = PyCheckableComboBox()
        self.download_item_combo_box.setPlaceholderText('<---點我展開--->')
        for item_name in util.cname_map.values():
            if item_name == '課程資訊':
                self.download_item_combo_box.addItem(item_name,
                                                     state=Qt.Checked,
                                                     enabled=False)
            else:
                self.download_item_combo_box.addItem(item_name)
        self.download_item_combo_box.setCurrentIndex(-1)
        download_item_label = QLabel('下載項目：')
        download_item_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        check_all_download_item_checkbox = QCheckBox('勾選全部下載項目')
        check_all_download_item_checkbox.stateChanged.connect(
            self.download_item_combo_box.checkAll)
        download_item_layout = QHBoxLayout()
        download_item_layout.addWidget(download_item_label)
        download_item_layout.addWidget(self.download_item_combo_box)
        download_item_layout.addWidget(check_all_download_item_checkbox)
        download_item_layout.setContentsMargins(0, 0, 0, 0)
        download_item_layout.setSpacing(0)
        download_item_group_box = QGroupBox()
        download_item_group_box.setLayout(download_item_layout)

        filepath_label = QLabel('存放路徑：')
        self.filepath_line_edit = QLineEdit()
        self.filepath_line_edit.setReadOnly(True)
        file_browse_button = QPushButton('瀏覽')
        file_browse_button.clicked.connect(self.get_save_directory)
        
        file_groupbox_layout = QHBoxLayout()
        file_groupbox_layout.addWidget(filepath_label)
        file_groupbox_layout.addWidget(self.filepath_line_edit)
        file_groupbox_layout.addWidget(file_browse_button)
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
        for i in range(self.download_item_combo_box.count()):
            if self.download_item_combo_box.itemChecked(i):
                module_cname = self.download_item_combo_box.model().item(
                    i, 0).text()
                for ename, cname in util.cname_map.items():
                    if cname == module_cname:
                        items.append(ename)
                        break

        cname_list = [
            x.text()[1:] for x in self.courses_checkboxes if x.isChecked()
        ]

        self.progress_bar.setMaximum(len(cname_list) * len(items))
        worker = Worker(self.ceiba.download_courses,
                        path=self.filepath_line_edit.text(),
                        cname_filter=cname_list,
                        modules_filter=items)
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
            if sys.platform == 'win32':
                os.startfile(path)
            else:
                # TODO: Not test on Linux/Mac yet.
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                import subprocess
                subprocess.call([opener, path])

        download_finish_msgbox = QMessageBox(self)
        download_finish_msgbox.setWindowTitle('下載完成！')
        download_finish_msgbox.setText('下載完成！')
        download_finish_msgbox.addButton('打開檔案目錄',
                                         download_finish_msgbox.YesRole)
        download_finish_msgbox.addButton('打開 Ceiba 網頁',
                                         download_finish_msgbox.ActionRole)
        # download_finish_msgbox.addButton(QMessageBox.Ok)
        download_finish_msgbox.exec()
        role = download_finish_msgbox.buttonRole(
            download_finish_msgbox.clickedButton())
        if role == download_finish_msgbox.ActionRole:  # open index.html
            open_path(Path(self.filepath_line_edit.text(), 'index.html'))
        elif role == download_finish_msgbox.YesRole:  # open dir
            open_path(Path(self.filepath_line_edit.text()))

    def update_progressbar(self, add_value: int):
        if add_value < 0:
            self.progress_bar.setMaximum(self.progress_bar.maximum() +
                                         (add_value * -1))
        elif add_value == 0:  # magic number
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(0)
            self.progress_bar.setMinimum(0)
        elif add_value == 999:  # magic number
            self.progress_bar.setMaximum(self.progress_bar.maximum())
        else:
            self.progress_bar.setValue(self.progress_bar.value() + add_value)


if __name__ == "__main__":

    app = QApplication([])

    window = MyApp()
    custom_qss_path = Path('resources/custom.qss')
    font_path = Path('resources/GenSenRounded-M.ttc')
    
    # for pyinstaller single-file executables. 
    # src: https://helloworldbookblog.com/distributing-python-programs-part-2-the-harder-stuff/
    if hasattr(sys, '_MEIPASS'):
        custom_qss_path = sys._MEIPASS / custom_qss_path
        font_path = sys._MEIPASS / font_path

    font_id = QFontDatabase.addApplicationFont(str(font_path))
    font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
    extra = {'font_family': font_name}
    apply_stylesheet(window,
                     theme='dark_lightgreen.xml',
                     extra=extra)
    stylesheet = window.styleSheet()
    window.setStyleSheet(stylesheet + custom_qss_path.read_text().format(**os.environ))
    window.showMaximized()
    window.show()

    sys.exit(app.exec())
