import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                            QWidget, QVBoxLayout, QSplitter, QHBoxLayout, QGridLayout, QSizePolicy, QLayout)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from flowizi import flowizi


class MainWindow(QMainWindow):
    label_signal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.setWindowTitle("Flowizi")
        self.setWindowIcon(QIcon("../assets/logo.svg"))
        self.setStyleSheet("background-color: #30302f;")
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        vbox = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #454541;")
        self.generate_element_sidebar()
        right_widget.setLayout(self.element_info_container)
        
        self.start_button = QPushButton("Start")
        self.start_button.setMaximumWidth(100)
        self.start_button.setMaximumHeight(40)
        create_button = QPushButton("Create")
        create_button.setMaximumWidth(100)
        create_button.setMaximumHeight(40)
        create_button.setStyleSheet("""QPushButton{
                                        color: white;
                                        font-size: 20px;
                                    }
                                    QPushButton:hover{
                                        background-color: #f19600;
                                    }""")
        self.start_button.setStyleSheet("""QPushButton{
                                        color: white;
                                        font-size: 20px;
                                    }
                                    QPushButton:hover{
                                        background-color: #f19600;
                                    }""")
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.addWidget(self.start_button)
        toolbar.addWidget(create_button)
        toolbar.addStretch()

        grid_widget = self.generate_environment_grid()
        splitter.addWidget(grid_widget)
        vbox.addLayout(toolbar)
        vbox.addWidget(splitter)
        splitter.addWidget(right_widget)
        central_widget.setLayout(vbox)

    def generate_element_sidebar(self):
        style = "background-color: #454541; font-size: 18px; color: white; padding: 20px;"
        self.element_info_container = QVBoxLayout()
        env_name = QLabel("No environments selected")
        env_name.setWordWrap(True)
        env_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        env_name.setStyleSheet(style)
        env_name.setFixedHeight(65)

        env_screen_rec_setting = QLabel("")
        env_screen_rec_setting.setStyleSheet(f"{style} height: 1px;")
        env_screen_rec_setting.setFixedHeight(60)

        env_num_websites = QLabel("")
        env_num_websites.setStyleSheet(f"{style} height: 1px;")
        env_num_websites.setFixedHeight(60)

        env_num_files = QLabel("")
        env_num_files.setStyleSheet(f"{style} height: 1px;")
        env_num_files.setFixedHeight(60)

        env_num_apps = QLabel("")
        env_num_apps.setStyleSheet(f"{style} height: 1px;")
        env_num_apps.setFixedHeight(60)

        self.element_info_container.addStretch()
        self.element_info_container.addWidget(env_name)
        self.element_info_container.addWidget(env_screen_rec_setting)
        self.element_info_container.addWidget(env_num_websites)
        self.element_info_container.addWidget(env_num_apps)
        self.element_info_container.addWidget(env_num_files)


    def generate_environment_grid(self) -> QWidget:
        number_elements_row = 4
        total_environments = len(flowizi.environment_list)
        total_rows = math.ceil(total_environments/number_elements_row)
        row_number = 0
        current_environment = 0
#f19600;
        self.label_default_style = """QLabel{
                                    background-color: #454541;
                                    color: white;
                                    font-size: 20px;
                                    height: 10px;
                                    border: 2px solid white;
                                    border-radius: 10px;
                                    }
                                    QLabel:hover{
                                    background-color: #4d4c49;
                                    }"""
        self.label_clicked_style =  """QLabel{
                                    background-color: #f19600;
                                    color: white;
                                    font-size: 20px;
                                    height: 10px;
                                    border: 2px solid white;
                                    border-radius: 10px;
                                    }"""

 
        self.grid = QGridLayout()
        self.grid.setSpacing(30)
        grid_widget = QWidget()  # New widget for the grid
        grid_widget.setLayout(self.grid)  # Set the grid layout on this widget
        for row in range(total_rows):
            for environment in range(number_elements_row):
                label = QLabel(f"{flowizi.environment_list[current_environment].name}")
                label.setStyleSheet(self.label_default_style)
                label.setAlignment(Qt.AlignCenter)
                self.grid.addWidget(label, row, environment)
                label.mousePressEvent = self.create_label_event(self.grid.indexOf(label))
                current_environment += 1

                if current_environment == total_environments:
                    break
            row_number += 1
            self.grid.setRowStretch(row, 1)
        return grid_widget

    def create_label_event(self, pos):
        def event(event):
            self.label_signal.emit(pos)
        return event


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
