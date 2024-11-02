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

        grid_widget = self.get_grid("environments", flowizi.environment_list)

        self.splitter.addWidget(grid_widget)
        self.vbox.addLayout(self.toolbar)
        self.vbox.addWidget(self.splitter)
        self.splitter.addWidget(right_widget)
        central_widget.setLayout(self.vbox)

    def generate_sidebar(self):
        env_name = ViewUtils.create_sidebar_label("No environments selected")
        self.element_info_container = QVBoxLayout()
        self.element_info_container.addStretch()
        self.element_info_container.addWidget(env_name)

        for i in range(4):
            label = ViewUtils.create_sidebar_label("")
            self.element_info_container.addWidget(label)

    def get_grid(self, element_type, element_list):
        if len(element_list):
            return self.generate_grid(element_list)
        else:
            return self.generate_empty_grid_label(element_type)

    def generate_grid(self, element_list) -> QWidget:
        self.grid = QGridLayout()
        self.grid.setSpacing(30)
        grid_widget = QWidget()
        grid_widget.setLayout(self.grid)

        num_elems_row = 4
        total_envs = len(element_list)
        total_rows = math.ceil(total_envs/num_elems_row)
        current_env = 0

        for row in range(total_rows):
            self.grid.setRowStretch(row, 1)
            for column in range(num_elems_row):
                label = ClickableLabel()
                label.setText(f"{element_list[current_env].name}")
                label.setStyleSheet(ViewUtils.ELEM_LABEL_STYLE)
                label.setAlignment(Qt.AlignCenter)

                self.grid.addWidget(label, row, column)
                label.set_pos(self.grid.indexOf(label))
                label.mousePressEvent = self.create_label_event(label.pos)
                label.label_double_click_signal.connect(self.create_label_double_click_event)
                current_env += 1

                if current_env == total_envs:
                    break

        return grid_widget

    def generate_empty_grid_label(self, element_type):
        label_text = f"No {element_type} have been created yet. Use the 'Create' button to create one"
        label = QLabel(label_text)
        label.setWordWrap(True)
        label.setStyleSheet("color: white; font-size: 20px; padding: 10px;")

        return label

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
