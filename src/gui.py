import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                            QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QLayout)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from flowizi import flowizi


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.setWindowTitle("Flowizi")
        self.setWindowIcon(QIcon("../assets/logo.svg"))
        self.setStyleSheet("background-color: #30302f;")
        self.initUI()

    def initUI(self):
        number_elements_row = 4
        total_environments = len(flowizi.environment_list)
        total_rows = math.ceil(total_environments/number_elements_row)
        row_number = 0
        current_environment = 0

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        vbox = QVBoxLayout()
        central_widget.setLayout(vbox)
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(toolbar)
        start_button = QPushButton("Start")
        start_button.setMaximumWidth(100)
        start_button.setMaximumHeight(40)
        create_button = QPushButton("Create")
        create_button.setMaximumWidth(100)
        create_button.setMaximumHeight(40)
        create_button.setStyleSheet("""QPushButton{
                                        color: white;
                                        font-size: 20px;
                                    }
                                    QPushButton:hover{
                                        background-color: green;
                                    }""")
        start_button.setStyleSheet("""QPushButton{
                                        color: white;
                                        font-size: 20px;
                                    }
                                    QPushButton:hover{
                                        background-color: green;
                                    }""")
        toolbar.addWidget(start_button)
        toolbar.addWidget(create_button)
        toolbar.addStretch()
        grid = QGridLayout()
        grid.setSpacing(30)
        grid_widget = QWidget()  # New widget for the grid
        grid_widget.setLayout(grid)  # Set the grid layout on this widget

        # Optionally set a fixed size for the grid widget
        grid_widget.setFixedSize(1000, 500)
        for row in range(total_rows):
            for environment in range(number_elements_row):
                label = QLabel(f"{flowizi.environment_list[current_environment].name}")
                label.setStyleSheet("""QLabel{
                                    background-color: #454541;
                                    color: white;
                                    font-size: 20px;
                                    border: 2px solid white;
                                    border-radius: 10px;
                                    }
                                    QLabel:hover{
                                    background-color: #4d4c49;
                                    }""")
                #label.setMaximumSize(200, 200)
                label.setAlignment(Qt.AlignCenter)
                grid.addWidget(label, row, environment)
                current_environment += 1

                if current_environment == total_environments:
                    break
            row_number += 1
            grid.setRowStretch(row, 1)
        vbox.addWidget(grid_widget)
        vbox.setAlignment(grid_widget, Qt.AlignCenter)
        vbox.setStretch(1, 0)
        vbox.setStretch(0, 0)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
