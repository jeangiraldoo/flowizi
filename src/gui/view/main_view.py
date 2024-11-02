import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                             QWidget, QVBoxLayout, QSplitter, QHBoxLayout,
                             QGridLayout, QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from flowizi import flowizi
from gui.view.view_utils import ViewUtils


class MainWindow(QMainWindow):
    label_signal = pyqtSignal(int)
    label_double_click_signal = pyqtSignal(int)

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
        self.vbox = QVBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #454541;")
        self.generate_sidebar()
        right_widget.setLayout(self.element_info_container)

        self.toolbar = QHBoxLayout()
        self.toolbar.setContentsMargins(0, 0, 0, 0)

        grid_widget = self.generate_element_grid(flowizi.environment_list)
        if not len(flowizi.environment_list):
            label_text = "No environments have been created yet. Use the 'Create' button to create one"
            grid_widget = QLabel(label_text)
            grid_widget.setWordWrap(True)
            grid_widget.setStyleSheet("color: white; font-size: 20px; padding: 10px;")

        self.splitter.addWidget(grid_widget)
        self.vbox.addLayout(self.toolbar)
        self.vbox.addWidget(self.splitter)
        self.splitter.addWidget(right_widget)
        central_widget.setLayout(self.vbox)

    def generate_sidebar(self):
        self.element_info_container = QVBoxLayout()
        env_name = ViewUtils.create_sidebar_label("No environments selected")

        self.element_info_container.addStretch()
        self.element_info_container.addWidget(env_name)

        for i in range(4):
            label = ViewUtils.create_sidebar_label("")
            self.element_info_container.addWidget(label)

    def generate_element_grid(self, element_list) -> QWidget:
        number_elements_row = 4
        total_environments = len(element_list)
        total_rows = math.ceil(total_environments/number_elements_row)
        row_number = 0
        current_environment = 0

        self.grid = QGridLayout()
        self.grid.setSpacing(30)
        grid_widget = QWidget()  # New widget for the grid
        grid_widget.setLayout(self.grid)  # Set the grid layout on this widget
        for row in range(total_rows):
            for environment in range(number_elements_row):
                label = ClickableLabel()
                label.setText(f"{element_list[current_environment].name}")
                label.setStyleSheet(ViewUtils.ELEM_LABEL_STYLE)
                label.setAlignment(Qt.AlignCenter)
                self.grid.addWidget(label, row, environment)
                label.set_pos(self.grid.indexOf(label))
                label.mousePressEvent = self.create_label_event(label.pos)
                label.label_double_click_signal.connect(self.create_label_double_click_event)
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

    def create_label_double_click_event(self, pos):
        self.label_double_click_signal.emit(pos)


class ClickableLabel(QLabel):
    label_double_click_signal = pyqtSignal(int)

    def set_pos(self, pos):
        self.pos = pos

    def mouseDoubleClickEvent(self, event):
        self.label_double_click_signal.emit(self.pos)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
