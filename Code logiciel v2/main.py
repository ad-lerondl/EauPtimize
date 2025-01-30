from PyQt5 import QtWidgets
import calculation
from input_form import InputForm
from result_display import ResultDisplay


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Calculateur d\'économies d\'eau')
        self.setStyleSheet(open('styles.css').read())

        layout = QtWidgets.QHBoxLayout()

        self.input_form = InputForm()
        self.result_display = ResultDisplay()

        self.input_form.calculate_button.clicked.connect(self.calculate_savings)

        layout.addWidget(self.input_form, 1)
        layout.addWidget(self.result_display, 2)


        self.setLayout(layout)

    def calculate_savings(self):
        input_data = self.input_form.get_input_data()
        resources = calculation.calculate_resources(input_data)
        needs = calculation.calculate_needs(input_data)
        
        
        water_resources=[resources["hab"],resources["trav"],resources["pluie"]]
        water_needed=[needs['conso_tot_hab'],needs['conso_tot_trav'],needs['conso_tot_net'],needs["garden_water"]]
        total_water_resources=sum(water_resources)
        total_water_needed=sum(water_needed)

        self.result_display.display_results(water_needed,water_resources,total_water_resources, total_water_needed,input_data)#, required_storage, solutions, savings)
        


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
