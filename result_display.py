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
Created on Thu Dec 12 18:01:41 2024

@author: Adam Lérondel
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

    def display_results(self, total_water_resources, total_water_needed, required_storage, solutions_avec_cout, all_solutions, savings, resources, needs):
        result_text = """
        <div style="text-align: center;">
            <h2>Résultats</h2>
            <p><strong>Ressources en eau disponibles:</strong> {:.2e} m³</p>
            <p><strong>Besoins en eau (sont considérés les besoins légalement couvrables au vu des normes en vigueur):</strong> {:.2e} m³</p>
            <p><strong>Capacité de stockage requise:</strong> {:.2e} m³</p>
            <h3>Solutions Envisageables:</h3>
        """.format(total_water_resources * 10**(-3), total_water_needed * 10**(-3), required_storage * 10**(-3))

        for solution in all_solutions:
            result_text += f"<p><strong>{solution['name']}:</strong> {solution['description']}</p>"
            # for param, value in solution["parameters"].items():
            #     result_text += f"<li><strong>{param.replace('_', ' ').capitalize()}:</strong> {value * 10**(-3)} m³</li>"

        result_text += "<h3>Solutions Retenues (au vu des coûts):</h3>"

        for solution in solutions_avec_cout:
            result_text += f"<p><strong>{solution['name']}:</strong> {solution['description']}</p>"

        result_text += "</div>"

        self.result_label.setText(result_text)

        total_water_resources = 0 if np.isnan(total_water_resources) else total_water_resources
        total_water_needed = 0 if np.isnan(total_water_needed) else total_water_needed

        calculation.plot_results(resources, needs, required_storage, savings)

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
