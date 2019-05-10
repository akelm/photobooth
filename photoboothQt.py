#!/usr/bin/python3
import os
import sys

import yaml
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QWidget, QLineEdit

import photobooth
from photologging import Logging

log = Logging()


class FotoThread(QThread):
    # signal for getting email from QLineEdit
    signal = pyqtSignal()

    def __init__(self, config=None):
        QThread.__init__(self)
        self.exiting = False
        self.photo = photobooth.Photo(config=config)
        log.append("photothread init")

    def run(self):
        log.append("PhotoThread run")
        while not self.exiting:
            log.append("photobooth loop")
            # takes photo, sets camera transparency and waits for button press
            # button is pressed after user enters email
            self.photo.prep_and_photo()
            # button pressed
            self.signal.emit()
            # email is beeing collected now
            # displays "thank you" etc
            self.photo.finishing()

    def stop(self):
        self.exiting = True
        self.photo.close()
        self.exiting = True
        self.wait()

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        with open("photoconfig.yaml", 'r') as stream:
            self.config = yaml.full_load(stream)
        realpath = os.path.dirname(os.path.realpath(__file__))
        for (key, val) in self.config['paths'].items():
            self.config['paths'][key] = os.path.join(realpath, val)
        self.make_gui()
        self.foto_thread = FotoThread(config=self.config)
        # connects the pyqtSignal with get_email method
        self.foto_thread.signal.connect(self.get_email)
        self.foto_thread.start()

    def get_email(self):
        log.append("getting email")
        # get email from QEntry
        email = self.line.text().strip()
        self.line.setText("")
        if email:
            # use email it as filename with images paths
            if os.path.exists(self.config['paths']['piclist']):
                newaddr = os.path.join(self.config['paths']['addr'], email)
                os.rename(self.config['paths']['piclist'], newaddr)
        log.append(email)

    def on_button_press(self):
        sender = self.sender()
        if sender.text() == "<":
            self.line.setText(self.line.text()[0:-1])
        else:
            self.line.setText(self.line.text() + sender.text())

    def make_gui(self):
        self.name = None
        self.setStyleSheet("color:white; background-color: black; border-style: none")
        self.showFullScreen()
        self.setCursor(Qt.BlankCursor)

        stretchval = 10

        self.line = QLineEdit()
        self.line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.line.setAlignment(Qt.AlignCenter)
        self.line.adjustSize()
        self.line.setStyleSheet("font: bold; font-size: 46px; font-family: Arial")
        self.line.setCursor(Qt.BlankCursor)
        self.line.setMinimumWidth(self.config['camera']['screen_wh'][0])

        hbox = QHBoxLayout()
        hbox.addWidget(self.line, stretchval, Qt.AlignCenter)
        hbox.setAlignment(Qt.AlignCenter)
        hbox.setContentsMargins(0, self.config['camera']['screen_wh'][1] / 12, 0,
                                self.config['camera']['screen_wh'][1] / 12)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox, stretchval)
        vbox.setContentsMargins(0, 0, 0, 0)

        keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '<'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '+'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '_', '-'],
            ['@', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '.', ''],
        ]

        for row in keys:
            rowlayout = QHBoxLayout()
            rowlayout.setContentsMargins(0, 0, 0, 0)
            for letter in row:
                klwidget = QPushButton(letter)
                klwidget.clicked.connect(self.on_button_press)
                klwidget.setStyleSheet("QPushButton {padding: 0;}")
                klwidget.setStyleSheet("font: bold; font-size: 44px")
                klwidget.setMinimumWidth(self.config['camera']['screen_wh'][1] / 12)
                klwidget.setMinimumHeight(self.config['camera']['screen_wh'][1] / 6)
                klwidget.adjustSize()
                rowlayout.addWidget(klwidget, stretchval, Qt.AlignBottom)
            vbox.addLayout(rowlayout, stretchval)

        self.setLayout(vbox)


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        log.append("keyboard interrupt")
    except Exception as exception:
        log.append("unexpected error: " + str(exception))
