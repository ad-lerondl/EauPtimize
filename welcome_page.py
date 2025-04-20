# -*- coding: utf-8 -*-
#
# Copyright (c) [2025] [Adam Lérondel]
#
# Licensed under the Fair Source License, Version 0.9.6 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.fair.io/license
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Created on Tue Apr  8 21:08:25 2025

@author: Adam Lérondel
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import os
import json
import sqlite3


class WelcomePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.city_user = None
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
            self.buttons[label].setFixedHeight(45)
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

        # --- Bouton discret pour base de données ---
        # --- Barre de recherche de ville avec auto-complétion ---
        search_layout = QtWidgets.QVBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une ville...")
        self.search_input.textChanged.connect(self.update_city_suggestions)
        self.search_results = QtWidgets.QListWidget()
        self.search_results.hide()
        self.search_results.setMaximumHeight(100)
        self.search_results.itemClicked.connect(self.city_selected)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_results)
        main_layout.addLayout(search_layout)

        self.setLayout(main_layout)

    def update_city_suggestions(self, text):
        self.city_user = None
        if len(text) < 3:
            self.search_results.hide()
            return

        try:
            conn = sqlite3.connect("pluviometrie_france.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Villes FROM pluviometrie_villes_France WHERE Villes LIKE ? LIMIT 10", (text + '%',))
            rows = cursor.fetchall()
            conn.close()

            self.search_results.clear()
            for row in rows:
                self.search_results.addItem(row[0])

            if rows:
                self.search_results.show()
                if len(rows) == 1:
                    self.city_user = rows[0][0]
            else:
                self.search_results.hide()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erreur BDD", f"Erreur lors de la recherche :\n{e}")

    def city_selected(self, item):
        self.search_input.setText(item.text())
        self.search_results.hide()
        self.city_user = self.search_input.text()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    welcome_page = WelcomePage()
    welcome_page.setWindowTitle("EauPtimize - Accueil")
    welcome_page.resize(700, 700)
    welcome_page.show()
    sys.exit(app.exec_())
