# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 18:01:41 2024

@author: adaml
"""

from PyQt5 import QtWidgets, QtGui, QtCore
import calculation
import numpy as np


class ResultDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #e0f7fa;
            }
            QLabel {
                font-size: 16px;
                color: #00796b;
                text-align: center;
            }
        """)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)

        self.result_label = QtWidgets.QLabel("Entrez les données pour voir les résultats")
        self.result_label.setAlignment(QtCore.Qt.AlignCenter)
        self.scroll_layout.addWidget(self.result_label)

        self.water_pie_chart = QtWidgets.QLabel()
        self.water_pie_chart.setAlignment(QtCore.Qt.AlignCenter)
        self.water_pie_chart.mousePressEvent = self.show_water_pie_chart
        self.scroll_layout.addWidget(self.water_pie_chart)

        self.cost_bar_chart = QtWidgets.QLabel()
        self.cost_bar_chart.setAlignment(QtCore.Qt.AlignCenter)
        self.cost_bar_chart.mousePressEvent = self.show_cost_bar_chart
        self.scroll_layout.addWidget(self.cost_bar_chart)

        self.scroll_area.setWidget(self.scroll_content)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def display_results(self, total_water_resources, total_water_needed, required_storage, solutions, savings):
        result_text = f"Ressources en eau disponibles: {total_water_resources} litres\n"
        result_text += f"Besoins en eau: {total_water_needed} litres\n"
        result_text += f"Capacité de stockage requise: {required_storage} litres\n\n"
        result_text += "Solutions Envisageables:\n"

        for solution in solutions:
            result_text += f"\n- {solution['name']}: {solution['description']}"
            for param, value in solution["parameters"].items():
                result_text += f"\n   - {param.replace('_', ' ').capitalize()}: {value} litres"

        self.result_label.setText(result_text)

        # Vérifier et remplacer les NaN par zéro
        total_water_resources = 0 if np.isnan(total_water_resources) else total_water_resources
        total_water_needed = 0 if np.isnan(total_water_needed) else total_water_needed

        # Mettre à jour et afficher les graphiques
        calculation.plot_results(total_water_resources, total_water_needed, required_storage, savings)

        self.water_pie_chart.setPixmap(QtGui.QPixmap('water_resources_vs_needs.png'))
        self.cost_bar_chart.setPixmap(QtGui.QPixmap('cost_savings_vs_implementation_cost.png'))

    def show_water_pie_chart(self, event):
        self.chart_window = ChartWindow('water_resources_vs_needs.png')
        self.chart_window.show()

    def show_cost_bar_chart(self, event):
        self.chart_window = ChartWindow('cost_savings_vs_implementation_cost.png')
        self.chart_window.show()


class ChartWindow(QtWidgets.QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.initUI(image_path)

    def initUI(self, image_path):
        layout = QtWidgets.QVBoxLayout()

        image_label = QtWidgets.QLabel()
        image_label.setPixmap(QtGui.QPixmap(image_path))
        layout.addWidget(image_label)

        self.setLayout(layout)
        self.setWindowTitle("Graphique")
        self.resize(800, 600)
