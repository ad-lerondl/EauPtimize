# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 12:55:42 2024

@author: adaml
"""

from PyQt5 import QtWidgets
import calculation
from welcome_page import WelcomePage
from input_form import BuildingInputForm
from result_display import ResultDisplay
import json


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('EauPtimize')
        self.setStyleSheet(open('styles.css').read())

        # Utiliser QStackedWidget pour gérer les pages
        self.stacked_widget = QtWidgets.QStackedWidget()

        # Créer les pages
        self.welcome_page = WelcomePage()
        self.input_form = BuildingInputForm(building_type=None)
        self.result_display = ResultDisplay()

        # Ajouter les pages au QStackedWidget
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.input_form)
        self.stacked_widget.addWidget(self.result_display)

        # Connexion des boutons de la page de bienvenue
        for building_type, button in self.welcome_page.buttons.items():
            button.clicked.connect(lambda checked, bt=building_type: self.show_input_form(bt))

        # Connexion du bouton de calcul
        self.input_form.calculate_button.clicked.connect(self.calculate_savings)
        self.input_form.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.welcome_page))

        self.result_display.home_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.welcome_page))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        # Afficher la page de bienvenue au démarrage
        self.stacked_widget.setCurrentWidget(self.welcome_page)

    def show_input_form(self, building_type):
        # Mettre à jour le formulaire d'entrée avec le type de bâtiment sélectionné
        self.input_form = BuildingInputForm(building_type=building_type)
        self.input_form.calculate_button.clicked.connect(self.calculate_savings)
        self.input_form.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.welcome_page))
        self.stacked_widget.removeWidget(self.stacked_widget.widget(1))
        self.stacked_widget.insertWidget(1, self.input_form)
        self.stacked_widget.setCurrentWidget(self.input_form)

    def calculate_savings(self):
        input_data = self.input_form.get_input_data()
        resources = calculation.calculate_resources(input_data, self.input_form.building_type)
        print(resources)
        needs = calculation.calculate_needs(input_data, self.input_form.building_type)
        print(needs)

        total_water_resources = sum(list(resources.values()))
        total_water_needed = sum(list(needs.values()))
        required_storage = total_water_resources - total_water_needed if total_water_resources > total_water_needed else 0

        solutions = calculation.suggest_solutions(total_water_resources, total_water_needed, resources, needs, self.input_form.building_type)
        savings = calculation.calculate_savings(input_data, solutions, total_water_resources, total_water_needed, required_storage)

        self.result_display.display_results(total_water_resources, total_water_needed, required_storage, solutions, savings)

        # Afficher la page des résultats
        self.stacked_widget.setCurrentWidget(self.result_display)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
