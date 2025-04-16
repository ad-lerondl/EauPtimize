# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 18:01:41 2024

@author: adaml
"""


from PyQt5 import QtWidgets, QtGui, QtCore
import calculation
import numpy as np
from menu_widget import MenuWidget


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
            QPushButton {
                background-color: #00796b;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
        """)

        main_layout = QtWidgets.QVBoxLayout()

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

        """self.back_button = QtWidgets.QPushButton("Back")
        self.back_button.setObjectName("BackButton")
        self.back_button.setFixedHeight(52)
        main_layout.addWidget(self.back_button, alignment=QtCore.Qt.AlignCenter)"""

        self.home_button = QtWidgets.QPushButton("Home")
        self.home_button.setObjectName("BackButton")
        self.home_button.setFixedHeight(52)
        main_layout.addWidget(self.home_button, alignment=QtCore.Qt.AlignCenter)

        """self.pdf_button = QtWidgets.QPushButton("Générer un pdf")
        self.pdf_button.setObjectName("MainButton")
        self.pdf_button.setFixedHeight(52)
        main_layout.addWidget(self.pdf_button, alignment=QtCore.Qt.AlignCenter)"""

        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

    def display_results(self, total_water_resources, total_water_needed, required_storage, solutions, savings):
        result_text = f"<h2>Résultats</h2>"
        result_text += f"<p><strong>Ressources en eau disponibles:</strong> {total_water_resources} litres</p>"
        result_text += f"<p><strong>Besoins en eau:</strong> {total_water_needed} litres</p>"
        result_text += f"<p><strong>Capacité de stockage requise:</strong> {required_storage} litres</p>"
        result_text += "<h3>Solutions Envisageables:</h3>"

        for solution in solutions:
            result_text += f"<p><strong>{solution['name']}:</strong> {solution['description']}</p>"
            result_text += "<ul>"
            for param, value in solution["parameters"].items():
                result_text += f"<li><strong>{param.replace('_', ' ').capitalize()}:</strong> {value} litres</li>"
            result_text += "</ul>"

        self.result_label.setText(result_text)

        total_water_resources = 0 if np.isnan(total_water_resources) else total_water_resources
        total_water_needed = 0 if np.isnan(total_water_needed) else total_water_needed

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
