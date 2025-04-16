# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 22:18:38 2025

@author: adaml
"""

from PyQt5 import QtWidgets, QtCore, QtGui, Qt


class MenuWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI(parent)

    def initUI(self, parent):
        self.setFixedWidth(0)
        self.setStyleSheet("background-color: #2c3e50;")

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.back_button = QtWidgets.QPushButton("Retour")
        self.edit_constants_button = QtWidgets.QPushButton("Modifier les constantes")

        self.back_button.clicked.connect(parent.back_signal.emit)

        layout.addWidget(self.back_button)
        layout.addWidget(self.edit_constants_button)

        self.setLayout(layout)

        # Initialiser le menu comme fermé
        # self.hide()

    def toggle_menu(self):
        width = self.width()
        new_width = 200 if width == 0 else 0

        self.animation = QtCore.QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(width)
        self.animation.setEndValue(new_width)
        self.animation.start()

    def animate(self, start, end):
        self.anim = QtCore.QPropertyAnimation(self, b"maximumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(QtCore.QPoint(start, self.y()))
        self.anim.setEndValue(QtCore.QPoint(end, self.y()))
        self.anim.start()
