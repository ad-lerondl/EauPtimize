# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 18:01:19 2024

@author: adaml
"""


from PyQt5 import QtWidgets, QtCore
import json
import os


class BuildingInputForm(QtWidgets.QWidget):
    def __init__(self, building_type, parent=None):
        super().__init__(parent)
        self.building_type = building_type
        self.dynamic_lists = {}  # Pour stocker les listes dynamiques (par exemple "foyers")
        self.memory_layout = []
        self.initUI()

    def initUI(self):
        style_path = os.path.join(os.path.dirname(__file__), "styles.css")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

        self.setWindowTitle("Paramètres")

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(30, 20, 30, 20)
        scroll_layout.setSpacing(15)

        title_label = QtWidgets.QLabel("Configuration du bâtiment")
        title_label.setObjectName("PageTitle")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        scroll_layout.addWidget(title_label)

        with open('building_types.json', 'r', encoding='utf-8') as file:
            building_types = json.load(file)

        if self.building_type in building_types:
            building_info = building_types[self.building_type]
            self.create_fields(scroll_layout, building_info['fields'])

        # Boutons en bas
        self.back_button = QtWidgets.QPushButton("Back")
        self.back_button.setObjectName("BackButton")
        self.back_button.setFixedHeight(52)
        scroll_layout.addWidget(self.back_button, alignment=QtCore.Qt.AlignCenter)

        self.calculate_button = QtWidgets.QPushButton("Calculer")
        self.calculate_button.setObjectName("MainButton")
        self.calculate_button.setFixedHeight(52)
        scroll_layout.addWidget(self.calculate_button, alignment=QtCore.Qt.AlignCenter)

        scroll_area.setWidget(scroll_content)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def create_fields(self, layout, fields):
        """
        Crée récursivement des widgets à partir de la liste de champs.
        """
        for field in fields:
            field_type = field.get('type')
            if field_type == 'spinbox':
                self.add_spinbox(layout, field)
            elif field_type == 'checkbox':
                checkbox = QtWidgets.QCheckBox(field['label'])
                checkbox.setObjectName("FormCheckBox")
                checkbox.setChecked(field.get('default', False))
                layout.addWidget(checkbox)
                setattr(self, field['name'], checkbox)
            elif field_type == 'lineedit':
                container = QtWidgets.QWidget()
                form_layout = QtWidgets.QHBoxLayout(container)
                form_layout.setContentsMargins(0, 0, 0, 0)
                label = QtWidgets.QLabel(field['label'])
                label.setObjectName("FormLabel")
                text_entry = QtWidgets.QLineEdit()
                text_entry.setFixedHeight(36)
                text_entry.setObjectName("TextBox")
                form_layout.addWidget(label)
                form_layout.addStretch()
                form_layout.addWidget(text_entry)
                layout.addWidget(container)
                setattr(self, field['name'], text_entry)
            elif field_type == 'combobox':
                container = QtWidgets.QWidget()
                form_layout = QtWidgets.QHBoxLayout(container)
                form_layout.setContentsMargins(0, 0, 0, 0)
                label = QtWidgets.QLabel(field['label'])
                label.setObjectName("FormLabel")
                combo = QtWidgets.QComboBox()
                combo.addItems(field.get('options', []))
                if 'default' in field and field['default'] in field['options']:
                    combo.setCurrentText(field['default'])
                combo.setFixedHeight(36)
                combo.setObjectName("ComboBox")
                form_layout.addWidget(label)
                form_layout.addStretch()
                form_layout.addWidget(combo)
                layout.addWidget(container)
                setattr(self, field['name'], combo)
            elif field_type == 'list':
                # Crée une groupbox pour le champ de type liste
                group_box = QtWidgets.QGroupBox(field['label'])
                group_box.setObjectName("ListGroupBox")
                group_layout = QtWidgets.QVBoxLayout(group_box)
                group_layout.setContentsMargins(10, 10, 10, 10)
                group_layout.setSpacing(10)

                if field.get('optional', False) is True:
                    sub_widget = QtWidgets.QWidget()
                    sub_layout = QtWidgets.QFormLayout(sub_widget)
                    add_button = QtWidgets.QPushButton(field.get('text_button', "Ajouter"))
                    add_button.setFixedHeight(36)
                    add_button.setObjectName("SecondaryButton")
                    subfields = field['subfields']
                    self.memory_layout.append(sub_layout)
                    add_button.clicked.connect(lambda: self.create_fields(self.memory_layout[-1], subfields))

                    group_layout.addWidget(sub_widget)
                    group_layout.addWidget(add_button, alignment=(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop))

                    """# Pour "foyers", on souhaite une liste dynamique
                    container = QtWidgets.QWidget()
                    container_layout = QtWidgets.QVBoxLayout(container)
                    container_layout.setContentsMargins(0, 0, 0, 0)
                    container_layout.setSpacing(5)
                    group_layout.addWidget(container)
                    # Capture locale de la clé pour éviter les problèmes de fermeture
                    field_name = field['name']
                    self.dynamic_lists[field_name] = []

                    def add_item():
                        item_widget = QtWidgets.QWidget()
                        item_layout = QtWidgets.QHBoxLayout(item_widget)
                        item_layout.setContentsMargins(0, 0, 0, 0)
                        # Container pour les sous-champs : on utilise un FormLayout pour la cohérence
                        form_container = QtWidgets.QWidget()
                        form_layout = QtWidgets.QFormLayout(form_container)
                        self.create_fields(form_layout, field.get('subfields', []))
                        item_layout.addWidget(form_container)
                        remove_btn = QtWidgets.QPushButton("Supprimer")
                        remove_btn.setFixedSize(90, 30)
                        item_layout.addWidget(remove_btn)

                        def remove_item():
                            container_layout.removeWidget(item_widget)
                            item_widget.deleteLater()
                            self.dynamic_lists[field_name].remove(item_widget)

                        remove_btn.clicked.connect(remove_item)
                        container_layout.addWidget(item_widget)
                        self.dynamic_lists[field_name].append(item_widget)

                    add_button = QtWidgets.QPushButton("Ajouter un foyer")
                    add_button.setFixedHeight(36)
                    add_button.setObjectName("SecondaryButton")
                    add_button.clicked.connect(add_item)
                    group_layout.addWidget(add_button, alignment=QtCore.Qt.AlignRight)"""
                else:
                    # Pour les autres listes, on affiche une instance fixe des sous-champs.
                    sub_widget = QtWidgets.QWidget()
                    sub_layout = QtWidgets.QFormLayout(sub_widget)
                    self.create_fields(sub_layout, field.get('subfields', []))
                    group_layout.addWidget(sub_widget)
                # On ajoute la groupbox dans le layout principal
                # Selon le layout utilisé, ici j'utilise addRow si c'est un QFormLayout
                if hasattr(layout, "addRow"):
                    layout.addRow(group_box)
                else:
                    layout.addWidget(group_box)

    def add_spinbox(self, layout, field):
        container = QtWidgets.QWidget()
        form_layout = QtWidgets.QHBoxLayout(container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(field['label'])
        label.setObjectName("FormLabel")
        spinbox = QtWidgets.QSpinBox()
        spinbox.setRange(0, 2147483647)
        spinbox.setValue(field.get('default', 0))
        spinbox.setFixedHeight(36)
        spinbox.setObjectName("SpinBox")
        form_layout.addWidget(label)
        form_layout.addStretch()
        form_layout.addWidget(spinbox)
        layout.addWidget(container)
        setattr(self, field['name'], spinbox)

    def get_input_data(self):
        """
        Récupère de façon récursive toutes les données saisies par l'utilisateur, y compris les champs de type list.
        """
        def extract_fields(fields, parent_name=None):
            data = {}
            for field in fields:
                field_name = field["name"]
                full_name = f"{parent_name}_{field_name}" if parent_name else field_name
                field_type = field["type"]

                if field_type in ["spinbox", "checkbox", "combobox", "lineedit"]:
                    widget = getattr(self, full_name, None)
                    if widget:
                        if field_type == "spinbox":
                            data[field_name] = widget.value()
                        elif field_type == "checkbox":
                            data[field_name] = widget.isChecked()
                        elif field_type == "combobox":
                            data[field_name] = widget.currentText()
                        elif field_type == "lineedit":
                            data[field_name] = widget.text()

                elif field_type == "list":
                    data[field_name] = extract_fields(field['subfields'])

            return data

        # Charger le modèle depuis le JSON
        with open('building_types.json', 'r', encoding='utf-8') as file:
            building_types = json.load(file)

        input_data = {}
        if self.building_type in building_types:
            building_info = building_types[self.building_type]
            input_data = extract_fields(building_info["fields"])
        return input_data


# Exemple d'utilisation
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    form = BuildingInputForm(building_type="espace_public")
    form.show()
    sys.exit(app.exec_())
