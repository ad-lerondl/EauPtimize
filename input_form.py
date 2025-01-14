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

        # Thème: Caractéristiques du bâtiment
        self.building_section = QtWidgets.QGroupBox("Caractéristiques du bâtiment")
        self.building_layout = QtWidgets.QVBoxLayout()
        self.building_layout.setSpacing(5)
        self.building_type = QtWidgets.QLineEdit()
        self.building_layout.addWidget(QtWidgets.QLabel("Type de bâtiment:"))
        self.building_layout.addWidget(self.building_type)
        self.roof_area = QtWidgets.QSpinBox()
        self.roof_area.setRange(0, 10000)
        self.building_layout.addWidget(QtWidgets.QLabel("Surface de toit (m²):"))
        self.building_layout.addWidget(self.roof_area)
        self.location = QtWidgets.QComboBox()
        self.building_layout.addWidget(QtWidgets.QLabel("Implantation géographique:"))
        self.building_layout.addWidget(self.location)
        self.fill_city_dropdown()
        self.building_layout.addSpacing(15)
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.building_layout.addWidget(line)
        self.building_layout.addSpacing(15)
        self.num_toilets = QtWidgets.QSpinBox()
        self.num_toilets.setRange(1, 20)
        self.building_layout.addWidget(QtWidgets.QLabel("Nombre de toilettes:"))
        self.building_layout.addWidget(self.num_toilets)
        self.garden = QtWidgets.QCheckBox("Présence d'un jardin")
        self.building_layout.addSpacing(10)
        self.building_layout.addWidget(self.garden)
        self.building_section.setLayout(self.building_layout)
        scroll_layout.addWidget(self.building_section)
        scroll_layout.addSpacing(20)

        # Thème: Caractéristiques des habitants
        self.resident_section = QtWidgets.QGroupBox("Caractéristiques des habitants")
        self.resident_layout = QtWidgets.QVBoxLayout()
        self.resident_layout.setSpacing(5)
        self.num_residents = QtWidgets.QSpinBox()
        self.num_residents.setRange(1, 100)
        self.resident_layout.addWidget(QtWidgets.QLabel("Nombre d'habitants:"))
        self.resident_layout.addWidget(self.num_residents)
        self.daily_shower = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.daily_shower.setRange(0, 500)
        self.resident_layout.addWidget(QtWidgets.QLabel("Utilisation quotidienne de la douche (litres):"))
        self.resident_layout.addWidget(self.daily_shower)
        self.daily_toilet = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.daily_toilet.setRange(0, 20)
        self.resident_layout.addWidget(QtWidgets.QLabel("Utilisation quotidienne des toilettes (litres):"))
        self.resident_layout.addWidget(self.daily_toilet)
        self.weekly_washing_machine = QtWidgets.QSpinBox()
        self.weekly_washing_machine.setRange(0, 10)
        self.resident_layout.addWidget(QtWidgets.QLabel("Nombre de machines à laver par semaine :"))
        self.resident_layout.addWidget(self.weekly_washing_machine)
        self.daily_garden = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.daily_garden.setRange(0, 100)
        self.resident_layout.addWidget(QtWidgets.QLabel("Arrosage quotidien du jardin (litres):"))
        self.resident_layout.addWidget(self.daily_garden)
        self.resident_section.setLayout(self.resident_layout)
        scroll_layout.addWidget(self.resident_section)
        scroll_layout.addSpacing(20)

        # Thème: Budgets maximums
        self.budget_section = QtWidgets.QGroupBox("Budgets maximums")
        self.budget_layout = QtWidgets.QVBoxLayout()
        self.budget_layout.setSpacing(5)
        self.budget_max_defined = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.budget_max_defined.setRange(0, 1000)
        self.budget_layout.addWidget(QtWidgets.QLabel("Budget maximal envisagé (en k€) :"))
        self.budget_layout.addWidget(self.budget_max_defined)
        self.budget_section.setLayout(self.budget_layout)
        scroll_layout.addWidget(self.budget_section)
        scroll_layout.addSpacing(20)

        # Questions supplémentaires
        self.extra_questions_section = QtWidgets.QGroupBox("Questions supplémentaires")
        self.extra_questions_layout = QtWidgets.QVBoxLayout()
        self.extra_questions_layout.setSpacing(5)

        self.heating_system = QtWidgets.QComboBox()
        self.heating_system.addItems(["Ballon d'eau chaude", "Autre"])
        self.extra_questions_layout.addWidget(QtWidgets.QLabel("Système de chauffage:"))
        self.extra_questions_layout.addWidget(self.heating_system)
        self.main_pipe = QtWidgets.QCheckBox("Présence d'une seule arrivée de canalisation")
        self.extra_questions_layout.addSpacing(10)
        self.extra_questions_layout.addWidget(self.main_pipe)
        self.renovation_plan = QtWidgets.QComboBox()
        self.renovation_plan.addItems(["Gros travaux", "Aménagements"])
        self.extra_questions_layout.addWidget(QtWidgets.QLabel("Travaux envisageables :"))
        self.extra_questions_layout.addWidget(self.renovation_plan)
        self.extra_questions_section.setLayout(self.extra_questions_layout)
        scroll_layout.addWidget(self.extra_questions_section)

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
            "building_type": self.building_type.text(),
            "num_residents": self.num_residents.value(),
            "num_toilets": self.num_toilets.value(),
            "garden": self.garden.isChecked(),
            "roof_area": self.roof_area.value(),
            "location": self.location.currentText(),
            "daily_shower_usage": self.daily_shower.value(),
            "daily_toilet_usage": self.daily_toilet.value(),
            "daily_garden_watering": self.daily_garden.value()
        }
