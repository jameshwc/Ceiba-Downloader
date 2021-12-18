import logging
from functools import cached_property

from PySide6.QtCore import (Property, QEasingCurve, QObject, QPoint,
                            QPropertyAnimation, QRect, Qt, Signal)
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QCheckBox, QComboBox, QPlainTextEdit


class PyToggle(QCheckBox):
    def __init__(
        self,
        width=50,
        bg_color="#777",
        circle_color="#DDD",
        active_color="#00BCFF",
        animation_curve=QEasingCurve.OutBounce
    ):
        QCheckBox.__init__(self)
        self.setFixedSize(width, 28)
        self.setCursor(Qt.PointingHandCursor)

        # COLORS
        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color

        self._position = 3
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(500)
        self.stateChanged.connect(self.setup_animation)

    @Property(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()

    # START STOP ANIMATION
    def setup_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - 26)
        else:
            self.animation.setEndValue(4)
        self.animation.start()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setFont(QFont("Segoe UI", 9))

        # SET PEN
        p.setPen(Qt.NoPen)

        # DRAW RECT
        rect = QRect(0, 0, self.width(), self.height())

        if not self.isChecked():
            p.setBrush(QColor(self._bg_color))
            p.drawRoundedRect(0, 0, rect.width(), 28, 14, 14)
            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._position, 3, 22, 22)
        else:
            p.setBrush(QColor(self._active_color))
            p.drawRoundedRect(0, 0, rect.width(), 28, 14, 14)
            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._position, 3, 22, 22)

        p.end()

class PyGuiCustomLogFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR:   ("[%(levelname)-8s] %(message)s", QColor("red")),
        logging.DEBUG:   ("[%(levelname)-8s] [%(filename)s:%(lineno)d] %(message)s", "green"),
        logging.INFO:    ("[%(levelname)-8s] %(message)s", "#0000FF"),
        logging.WARNING: ('%(asctime)s - %(name)s - %(levelname)s - %(message)s', QColor(100, 100, 0))
    }

    def format( self, record ):
        last_fmt = self._style._fmt
        opt = PyGuiCustomLogFormatter.FORMATS.get(record.levelno)
        if opt:
            fmt, color = opt
            self._style._fmt = "<font color=\"{}\">{}</font>".format(QColor(color).name(),fmt)
        res = logging.Formatter.format( self, record )
        self._style._fmt = last_fmt
        return res
class PyQtSignal(QObject):
    log = Signal(str)


class PyLogOutput(logging.Handler):

    def __init__(self, parent=None):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.signal.log.connect(self.widget.appendPlainText)

    @cached_property
    def signal(self):
        return PyQtSignal()

    def emit(self, record: logging.LogRecord):
        print(record.msg)
        msg = self.format(record)
        if record.levelno == logging.ERROR:
            msg = '<span style="color:#ff0000;">' + msg + "</span>"
        # self.widget.appendPlainText(msg)
        self.signal.log.emit(msg)


class PyCheckableComboBox(QComboBox):
    # once there is a checkState set, it is rendered
    # here we assume default Unchecked
    def addItem(self, item):
        super(PyCheckableComboBox, self).addItem(item)
        item = self.model().item(self.count() - 1, 0)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)

    def itemChecked(self, index):
        item = self.model().item(index, 0)
        return item.checkState() == Qt.Checked

    def checkAll(self):
        for i in range(self.count()):
            item: QCheckBox = self.model().item(i, 0)
            if item.checkState() != Qt.Checked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
