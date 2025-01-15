# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 18:01:19 2024

@author: adaml
"""

from PyQt5 import QtWidgets, QtCore, QtSql


class InputForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):

        # Lier la feuille de style CSS
        self.setStyleSheet(open("styles.css").read())

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)

        # Thème: Paramètres habitation
        self.habitat_section = QtWidgets.QGroupBox("Paramètres habitation")
        self.habitat_layout = QtWidgets.QVBoxLayout()
        self.habitat_layout.setSpacing(5)

        self.nb_habitants = QtWidgets.QSpinBox()
        self.nb_habitants.setRange(0, 2147483647)
        self.nb_habitants.setValue(0)
        self.habitat_layout.addWidget(QtWidgets.QLabel("Nombre d'habitant :"))
        self.habitat_layout.addWidget(self.nb_habitants)

        

        self.conso_hab = QtWidgets.QSpinBox()
        self.conso_hab.setRange(0, 2147483647)
        self.conso_hab.setValue(120)
        self.habitat_layout.addWidget(QtWidgets.QLabel("Consommation en eau potable par habitant (L/jour) :"))
        self.habitat_layout.addWidget(self.conso_hab)

        self.habitat_section.setLayout(self.habitat_layout)
        scroll_layout.addWidget(self.habitat_section)
        scroll_layout.addSpacing(20)

        # Thème: Répartition consommation
        self.conso_section = QtWidgets.QGroupBox("Répartition de la consommation en eau des habitants")
        self.conso_layout = QtWidgets.QVBoxLayout()
        self.conso_layout.setSpacing(5)

        self.conso_hyg = QtWidgets.QSpinBox()
        self.conso_hyg.setRange(0, 2147483647)
        self.conso_hyg.setValue(40)
        self.conso_layout.addWidget(QtWidgets.QLabel("Hygiène (%) :"))
        self.conso_layout.addWidget(self.conso_hyg)

        self.conso_vet = QtWidgets.QSpinBox()
        self.conso_vet.setRange(0, 2147483647)
        self.conso_vet.setValue(15)
        self.conso_layout.addWidget(QtWidgets.QLabel("Lavage de vêtements (%) :"))
        self.conso_layout.addWidget(self.conso_vet)

        self.conso_exc = QtWidgets.QSpinBox()
        self.conso_exc.setRange(0, 2147483647)
        self.conso_exc.setValue(20)
        self.conso_layout.addWidget(QtWidgets.QLabel("Évacuation des excrétats (%) :"))
        self.conso_layout.addWidget(self.conso_exc)

        self.conso_alim = QtWidgets.QSpinBox()
        self.conso_alim.setRange(0, 2147483647)
        self.conso_alim.setValue(10)
        self.conso_layout.addWidget(QtWidgets.QLabel("Alimentation (%) :"))
        self.conso_layout.addWidget(self.conso_alim)

        self.conso_vai = QtWidgets.QSpinBox()
        self.conso_vai.setRange(0, 2147483647)
        self.conso_vai.setValue(5)
        self.conso_layout.addWidget(QtWidgets.QLabel("Lavage de la vaisselle (%) :"))
        self.conso_layout.addWidget(self.conso_vai)

        self.conso_net = QtWidgets.QSpinBox()
        self.conso_net.setRange(0, 2147483647)
        self.conso_net.setValue(10)
        self.conso_layout.addWidget(QtWidgets.QLabel("Nettoyage et autres usages (%) :"))
        self.conso_layout.addWidget(self.conso_net)

        self.conso_section.setLayout(self.conso_layout)
        scroll_layout.addWidget(self.conso_section)
        scroll_layout.addSpacing(20)

        # Thème: Paramètres travail
        self.travail_section = QtWidgets.QGroupBox("Paramètres travail")
        self.travail_layout = QtWidgets.QVBoxLayout()
        self.travail_layout.setSpacing(5)

        self.nb_travail = QtWidgets.QSpinBox()
        self.nb_travail.setRange(0, 2147483647)
        self.nb_travail.setValue(0)
        self.travail_layout.addWidget(QtWidgets.QLabel("Nombre de travailleurs :"))
        self.travail_layout.addWidget(self.nb_travail)

        self.conso_travail = QtWidgets.QSpinBox()
        self.conso_travail.setRange(0, 2147483647)
        self.conso_travail.setValue(47)
        self.travail_layout.addWidget(QtWidgets.QLabel("Consommation en eau potable par travailleur (L/jour) :"))
        self.travail_layout.addWidget(self.conso_travail)

        self.travail_section.setLayout(self.travail_layout)
        scroll_layout.addWidget(self.travail_section)
        scroll_layout.addSpacing(20)

        # Thème: Répartition consommation
        self.conso_section = QtWidgets.QGroupBox("Répartition de la consommation en eau des travailleurs :")
        self.conso_layout = QtWidgets.QVBoxLayout()
        self.conso_layout.setSpacing(5)

        self.conso_hyg_travail = QtWidgets.QSpinBox()
        self.conso_hyg_travail.setRange(0, 2147483647)
        self.conso_hyg_travail.setValue(30)
        self.conso_layout.addWidget(QtWidgets.QLabel("Hygiène (%) :"))
        self.conso_layout.addWidget(self.conso_hyg_travail)

        self.conso_exc_travail = QtWidgets.QSpinBox()
        self.conso_exc_travail.setRange(0, 2147483647)
        self.conso_exc_travail.setValue(30)
        self.conso_layout.addWidget(QtWidgets.QLabel("Évacuation des excrétats (%) :"))
        self.conso_layout.addWidget(self.conso_exc_travail)

        self.conso_alim_travail = QtWidgets.QSpinBox()
        self.conso_alim_travail.setRange(0, 2147483647)
        self.conso_alim_travail.setValue(10)
        self.conso_layout.addWidget(QtWidgets.QLabel("Consommation directe (%) :"))
        self.conso_layout.addWidget(self.conso_alim_travail)

        self.conso_net_travail = QtWidgets.QSpinBox()
        self.conso_net_travail.setRange(0, 2147483647)
        self.conso_net_travail.setValue(30)
        self.conso_layout.addWidget(QtWidgets.QLabel("Nettoyage des locaux, des équipements et autres usages (%) :"))
        self.conso_layout.addWidget(self.conso_net_travail)

        self.conso_section.setLayout(self.conso_layout)
        scroll_layout.addWidget(self.conso_section)
        scroll_layout.addSpacing(20)

        # Utilisations voulues
        self.ut_section = QtWidgets.QGroupBox("Utilisations voulues")
        self.ut_layout = QtWidgets.QVBoxLayout()
        self.ut_layout.setSpacing(5)

        self.surf_net = QtWidgets.QSpinBox()
        self.surf_net.setRange(0, 2147483647)
        self.surf_net.setValue(0)
        self.ut_layout.addWidget(QtWidgets.QLabel("Surface à nettoyer (m²) :"))
        self.ut_layout.addWidget(self.surf_net)

        self.surf_veg = QtWidgets.QSpinBox()
        self.surf_veg.setRange(0, 2147483647)
        self.surf_veg.setValue(0)
        self.ut_layout.addWidget(QtWidgets.QLabel("Surface végétalisée à arroser (m²) :"))
        self.ut_layout.addWidget(self.surf_veg)

        self.exc = QtWidgets.QCheckBox("Évacuation des excrétats :")
        self.ut_layout.addSpacing(10)
        self.ut_layout.addWidget(self.exc)

        self.font = QtWidgets.QCheckBox("Alimentation des fontaines :")
        self.ut_layout.addSpacing(10)
        self.ut_layout.addWidget(self.font)

        self.pisc = QtWidgets.QSpinBox()
        self.pisc.setRange(0, 2147483647)
        self.pisc.setValue(0)
        self.ut_layout.addWidget(QtWidgets.QLabel("Volume total des piscines (L) :"))
        self.ut_layout.addWidget(self.pisc)

        self.ut_section.setLayout(self.ut_layout)
        scroll_layout.addWidget(self.ut_section)

        # Thème: Paramètres pluie
        self.pluie_section = QtWidgets.QGroupBox("Paramètres pluie")
        self.pluie_layout = QtWidgets.QVBoxLayout()
        self.pluie_layout.setSpacing(5)

        self.location = QtWidgets.QComboBox()
        self.pluie_layout.addWidget(QtWidgets.QLabel("Implantation géographique:"))
        self.pluie_layout.addWidget(self.location)
        self.fill_city_dropdown()

        self.precip = QtWidgets.QSpinBox()
        self.precip.setRange(0, 2147483647)
        self.precip.setValue(700)
        self.pluie_layout.addWidget(QtWidgets.QLabel("Précipitations (mm/an) :"))
        self.pluie_layout.addWidget(self.precip)

        self.surfpl = QtWidgets.QSpinBox()
        self.surfpl.setRange(0, 2147483647)
        self.surfpl.setValue(0)
        self.pluie_layout.addWidget(QtWidgets.QLabel("Surface de récupération de l'eau de pluie (m²) :"))
        self.pluie_layout.addWidget(self.surfpl)

        self.pluie_section.setLayout(self.pluie_layout)
        scroll_layout.addWidget(self.pluie_section)
        scroll_layout.addSpacing(20)

        self.calculate_button = QtWidgets.QPushButton("Calculer")
        scroll_layout.addWidget(self.calculate_button)
        scroll_area.setWidget(scroll_content)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def fill_city_dropdown(self):
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('pluviometrie.db')
        if db.open():
            query = QtSql.QSqlQuery("SELECT Ville FROM Prec_Anuelles")
            while query.next():
                self.location.addItem(query.value(0))
        else:
            print("Erreur lors de la connexion à la base de données.")
            db.close()

    def get_input_data(self):
        return {
            "num_toilets": self.nb_toilettes.value(),
            "location": self.location.currentText(),
            "roof_area": self.surf_toit.value(),
            "nb_habitants": self.nb_habitants.value(),
            "conso_hab": self.conso_hab.value(),
            "conso_hyg": self.conso_hyg.value(),
            "conso_vet": self.conso_vet.value(),
            "conso_exc": self.conso_exc.value(),
            "conso_alim": self.conso_alim.value(),
            "conso_vai": self.conso_vai.value(),
            "conso_net": self.conso_net.value(),
            "nb_travail": self.nb_travail.value(),
            "conso_travail": self.conso_travail.value(),
            "conso_hyg_travail": self.conso_hyg_travail.value(),
            "conso_exc_travail": self.conso_exc_travail.value(),
            "conso_alim_travail": self.conso_alim_travail.value(),
            "conso_net_travail": self.conso_net_travail.value(),
            "surf_net": self.surf_net.value(),
            "surf_veg": self.surf_veg.value(),
            "exc": self.exc.isChecked(),
            "font": self.font.isChecked(),
        }
