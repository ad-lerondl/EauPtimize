# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 21:08:25 2025

@author: adaml
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import os
import json


class WelcomePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Charger le fichier CSS externe
        style_path = os.path.join(os.path.dirname(__file__), "styles.css")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(20)

        # --- En-tête horizontal : logo - titre/slogan - logo ---
        header_layout = QtWidgets.QHBoxLayout()

        logo_left = QtWidgets.QLabel()
        logo_left.setPixmap(QtGui.QPixmap("logo_outil.png").scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        header_layout.addWidget(logo_left, alignment=QtCore.Qt.AlignLeft)

        title_container = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("EauPtimize")
        title.setObjectName("TitleLabel")
        slogan = QtWidgets.QLabel("L'eau d'aujourd'hui, l'écologie de demain !")
        slogan.setObjectName("SloganLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        slogan.setAlignment(QtCore.Qt.AlignCenter)
        title_container.addWidget(title)
        title_container.addWidget(slogan)

        header_layout.addLayout(title_container)

        logo_right = QtWidgets.QLabel()
        logo_right.setPixmap(QtGui.QPixmap("logo_urbanwater.png").scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        header_layout.addWidget(logo_right, alignment=QtCore.Qt.AlignRight)

        main_layout.addLayout(header_layout)

        # --- Instruction texte ---
        instruction_label = QtWidgets.QLabel("Veuillez sélectionner le type de bâtiment pour lequel vous souhaitez effectuer une simulation :")
        instruction_label.setAlignment(QtCore.Qt.AlignCenter)
        instruction_label.setWordWrap(True)
        main_layout.addWidget(instruction_label)

        # --- Boutons ---
        with open('building_types.json', 'r', encoding='utf-8') as file:
            building_types = json.load(file)
        buttons_name = {cle: valeur['name'] for (cle, valeur) in building_types.items()}

        self.buttons = {}
        button_layout = QtWidgets.QVBoxLayout()
        for label, text in buttons_name.items():
            self.buttons[label] = QtWidgets.QPushButton(text)
            self.buttons[label].setFixedHeight(45)  # ✅ corrigé : plus de place pour le texte
            button_layout.addWidget(self.buttons[label])

        main_layout.addLayout(button_layout)

        # --- Pied de page ---
        footer_label = QtWidgets.QLabel("Un projet commandité par UrbanWater et réalisé par des élèves ingénieurs de Centrale Lyon")
        footer_label.setAlignment(QtCore.Qt.AlignCenter)
        footer_label.setObjectName("FooterLabel")
        main_layout.addWidget(footer_label)

        # --- Logo Centrale Lyon au centre ---
        centrale_logo = QtWidgets.QLabel()
        centrale_logo.setPixmap(QtGui.QPixmap("logo_centrale.png").scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        centrale_logo.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(centrale_logo)

        self.setLayout(main_layout)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    welcome_page = WelcomePage()
    welcome_page.setWindowTitle("EauPtimize - Accueil")
    welcome_page.resize(700, 700)
    welcome_page.show()
    sys.exit(app.exec_())
