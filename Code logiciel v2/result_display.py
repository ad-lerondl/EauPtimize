from PyQt5 import QtWidgets, QtGui, QtCore
import calculation
import numpy as np


class ResultDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Prix du litre d'eau en France (pour les calculs d'économies)
        self.water_cost_per_liter = 0.002
        self.setWindowTitle("Résultats")
        self.resize(800, 600)

        # Layout principal
        main_layout = QtWidgets.QVBoxLayout(self)

        # Groupe 1 : Résultats et graphiques avec barre de scroll
        self.create_results_group(main_layout)

        # Groupe 2 : Solutions envisagées avec le tableau des économies
        self.create_solutions_group(main_layout)

        self.setLayout(main_layout)

    def create_results_group(self, main_layout):
        self.results_group = QtWidgets.QGroupBox("Résultats et Graphiques")
        self.results_layout = QtWidgets.QVBoxLayout(self.results_group)

        # Description
        self.description_label = QtWidgets.QLabel(
            "On répertorie dans cette partie la consommation annuelle en eau du projet ainsi que les ressources en eaux grises disponibles."
        )
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)
        self.results_layout.addWidget(self.description_label)

        # Tableau des résultats (Groupe 1)
        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setRowCount(2)
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Description", "Valeur (L/an)"])
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setFixedSize(550, 250)

        # Centrer le texte dans les cellules
        self.results_table.setStyleSheet("""
            QTableWidget::item {
                text-align: center;
            }
        """)

        self.results_layout.addWidget(self.results_table)

        # Graphiques
        self.water_bar_chart = QtWidgets.QLabel()
        self.water_bar_chart.setAlignment(QtCore.Qt.AlignCenter)
        self.results_layout.addWidget(self.water_bar_chart)

        self.water_pie_chart = QtWidgets.QLabel()
        self.water_pie_chart.setAlignment(QtCore.Qt.AlignCenter)
        self.results_layout.addWidget(self.water_pie_chart)

        self.gray_water_pie_chart = QtWidgets.QLabel()
        self.gray_water_pie_chart.setAlignment(QtCore.Qt.AlignCenter)
        self.results_layout.addWidget(self.gray_water_pie_chart)

        # Barre de scroll
        self.results_scroll_area = QtWidgets.QScrollArea()
        self.results_scroll_area.setWidget(self.results_group)
        self.results_scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.results_scroll_area)

    def create_solutions_group(self, main_layout):
        self.solution_group = QtWidgets.QGroupBox("Solutions envisagées")
        self.solution_layout = QtWidgets.QVBoxLayout(self.solution_group)

        # Description principale du groupe
        self.solution_description_label = QtWidgets.QLabel(
            "On répertorie dans cette partie les solutions envisagées, les coûts et les économies engendrées."
        )
        self.solution_description_label.setAlignment(QtCore.Qt.AlignCenter)
        self.solution_layout.addWidget(self.solution_description_label)

        # Texte pour le tableau des solutions
        self.solution_table_label = QtWidgets.QLabel("Tableau des solutions envisagées :")
        self.solution_table_label.setAlignment(QtCore.Qt.AlignLeft)
        self.solution_layout.addWidget(self.solution_table_label)

        # Tableau des solutions
        self.solution_table = QtWidgets.QTableWidget()
        self.solution_table.setColumnCount(5)
        self.solution_table.setRowCount(1)  # Ligne des titres ajoutée comme donnée
        self.solution_table.verticalHeader().setVisible(False)
        self.solution_table.horizontalHeader().setVisible(False)  # Masquer les en-têtes

        # Ajouter les titres comme une première ligne
        self.solution_table.setItem(0, 0, QtWidgets.QTableWidgetItem("Solution"))
        self.solution_table.setItem(0, 1, QtWidgets.QTableWidgetItem("Description"))
        self.solution_table.setItem(0, 2, QtWidgets.QTableWidgetItem("Traitement"))
        self.solution_table.setItem(0, 3, QtWidgets.QTableWidgetItem("Prix installation"))
        self.solution_table.setItem(0, 4, QtWidgets.QTableWidgetItem("Prix entretien"))

        # Centrer le texte dans les cellules du tableau des solutions
        self.solution_table.setStyleSheet("""
            QTableWidget::item {
                text-align: center;
            }
        """)

        # Ajuster les colonnes et l'affichage
        self.solution_table.setColumnWidth(0, 300)
        self.solution_table.setColumnWidth(1, 700)
        self.solution_table.setColumnWidth(2, 300)
        self.solution_table.setColumnWidth(3, 150)
        self.solution_table.setColumnWidth(4, 150)
        self.solution_table.setMinimumHeight(1000)
        self.solution_table.setMinimumWidth(1600)

        self.solution_layout.addWidget(self.solution_table)

        # Texte pour le tableau des économies d'eau
        self.water_savings_table_label = QtWidgets.QLabel("Tableau des économies d'eau :")
        self.water_savings_table_label.setAlignment(QtCore.Qt.AlignLeft)
        self.solution_layout.addWidget(self.water_savings_table_label)

        # Tableau des économies d'eau
        self.water_savings_table = QtWidgets.QTableWidget()
        self.water_savings_table.setColumnCount(3)
        self.water_savings_table.setHorizontalHeaderLabels([
            "Source", "Volume économisé (L/an)", "Coût économisé (€)"
        ])
        self.water_savings_table.verticalHeader().setVisible(False)

        # Centrer le texte dans les cellules
        self.water_savings_table.setStyleSheet("""
            QTableWidget::item {
                text-align: center;
            }
        """)

        # Ajuster les colonnes et l'affichage
        self.water_savings_table.setColumnWidth(0, 400)  # Source
        self.water_savings_table.setColumnWidth(1, 400)  # Volume économisé
        self.water_savings_table.setColumnWidth(2, 200)  # Coût économisé
        self.water_savings_table.setMinimumHeight(600)

        self.solution_layout.addWidget(self.water_savings_table)

        # Barre de scroll pour le groupe
        self.solution_scroll_area = QtWidgets.QScrollArea()
        self.solution_scroll_area.setWidget(self.solution_group)
        self.solution_scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.solution_scroll_area)

    def display_results(self, water_needed, water_resources, total_water_resources, total_water_needed, input_data):
        # Calculer les totaux
        total_water_resources = sum(water_resources)
        total_water_needed = sum(water_needed)

        # Mettre à jour le tableau des résultats (Groupe 1)
        self.results_table.setItem(0, 0, QtWidgets.QTableWidgetItem("Besoins en eau [L/an]"))
        self.results_table.setItem(0, 1, QtWidgets.QTableWidgetItem(f"{total_water_needed:.2f}"))
        self.results_table.setItem(1, 0, QtWidgets.QTableWidgetItem("Ressources en eaux grises [L/an]"))
        self.results_table.setItem(1, 1, QtWidgets.QTableWidgetItem(f"{total_water_resources:.2f}"))

        # Mettre à jour les graphiques
        calculation.plot_results(water_resources, water_needed)
        self.water_bar_chart.setPixmap(QtGui.QPixmap("Conso_eaux_grises.png"))
        self.water_pie_chart.setPixmap(QtGui.QPixmap("Conso_eau.png"))
        self.gray_water_pie_chart.setPixmap(QtGui.QPixmap("Eau_grises.png"))

        # Mettre à jour les solutions et économies d'eau
        solutions = calculation.suggest_solutions(input_data)
        self.display_solutions(solutions, input_data)

        water_save = calculation.calculate_savings(input_data)
        self.display_water_savings(water_save)

    def display_solutions(self, solutions, input_data):
        total_installation_cost = 0
        total_maintenance_cost = 0

        self.solution_table.setRowCount(len(solutions) + 1)  # +1 pour la ligne des totaux
        for row, solution in enumerate(solutions):
            num_people = input_data["num_residents"] + input_data["nb_travail"]
            installation_cost = solution.get("installation_cost", 0) * num_people
            maintenance_cost = solution.get("maintenance_cost", 0) * num_people

            self.solution_table.setItem(row, 0, QtWidgets.QTableWidgetItem(solution["name"]))
            self.solution_table.setItem(row, 1, QtWidgets.QTableWidgetItem(solution["description"]))
            self.solution_table.setItem(row, 2, QtWidgets.QTableWidgetItem(solution.get("traitement", "N/A")))
            self.solution_table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{installation_cost:.2f} €"))
            self.solution_table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{maintenance_cost:.2f} €/an"))

            total_installation_cost += installation_cost
            total_maintenance_cost += maintenance_cost

        total_row = len(solutions)
        self.solution_table.setItem(total_row, 0, QtWidgets.QTableWidgetItem("Total"))
        self.solution_table.setItem(total_row, 1, QtWidgets.QTableWidgetItem(""))
        self.solution_table.setItem(total_row, 2, QtWidgets.QTableWidgetItem(""))
        self.solution_table.setItem(total_row, 3, QtWidgets.QTableWidgetItem(f"{total_installation_cost:.2f} €"))
        self.solution_table.setItem(total_row, 4, QtWidgets.QTableWidgetItem(f"{total_maintenance_cost:.2f} €/an"))

        self.solution_table.verticalHeader().setDefaultSectionSize(200)

    def display_water_savings(self, water_save):
        # Définir les titres explicites pour chaque source d'eau
        titles_mapping = {
            "pluie": "Volume d'eau de pluie récupéré",
            "recup_hyg": "Volume d'eaux des douches",
            "recup_vet": "Volume d'eaux des machines à laver",
            "recup_vai": "Volume d'eaux des lave-vaisselles",
        }

        total_volume_saved = 0
        total_cost_saved = 0

        # Définir le nombre de lignes du tableau (données + ligne totale)
        self.water_savings_table.setRowCount(len(water_save) + 1)

        # Remplir le tableau
        for row, (key, volume) in enumerate(water_save.items()):
            cost_saved = volume * self.water_cost_per_liter
            total_volume_saved += volume
            total_cost_saved += cost_saved

            # Utiliser les titres explicites pour les clés
            title = titles_mapping.get(key, key)  # Si pas trouvé, utiliser la clé par défaut

            self.water_savings_table.setItem(row, 0, QtWidgets.QTableWidgetItem(title))
            self.water_savings_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{volume:.2f} L/an"))
            self.water_savings_table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{cost_saved:.2f} €"))

        # Ajouter la ligne des totaux
        total_row = len(water_save)
        self.water_savings_table.setItem(total_row, 0, QtWidgets.QTableWidgetItem("Total"))
        self.water_savings_table.setItem(total_row, 1, QtWidgets.QTableWidgetItem(f"{total_volume_saved:.2f} L/an"))
        self.water_savings_table.setItem(total_row, 2, QtWidgets.QTableWidgetItem(f"{total_cost_saved:.2f} €"))

        # Ajouter le texte pour la rentabilisation
        self.add_project_payback_text()

    def add_project_payback_text(self):
        """
        Ajoute un texte affichant le temps nécessaire pour rentabiliser le projet.
        """
        # Supprimer l'ancien label s'il existe pour éviter les doublons
        if hasattr(self, "payback_label"):
            self.payback_label.deleteLater()

        # Récupérer les totaux du tableau des solutions
        total_installation_cost = float(self.solution_table.item(self.solution_table.rowCount() - 1, 3).text().replace("€", "").strip())
        total_maintenance_cost_per_year = float(self.solution_table.item(self.solution_table.rowCount() - 1, 4).text().replace("€/an", "").strip())

        # Récupérer les économies totales du tableau des économies d'eau
        total_cost_saved = float(self.water_savings_table.item(self.water_savings_table.rowCount() - 1, 2).text().replace("€", "").strip())

        # Calcul du temps de rentabilisation
        if total_cost_saved > total_maintenance_cost_per_year:
            years_to_payback = total_installation_cost / (total_cost_saved - total_maintenance_cost_per_year)
        else:
            years_to_payback = float('inf')  # Cas où les économies ne couvrent pas l'entretien

        # Créer le texte pour la rentabilité
        self.payback_label = QtWidgets.QLabel()
        if years_to_payback == float('inf'):
            self.payback_label.setText("Le projet ne sera pas rentabilisé avec les conditions actuelles.")
        else:
            self.payback_label.setText(f"Le projet sera rentabilisé en environ {years_to_payback:.1f} années.")

        self.payback_label.setAlignment(QtCore.Qt.AlignCenter)
        self.solution_layout.addWidget(self.payback_label)


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
        self.resize(1600, 1200)

