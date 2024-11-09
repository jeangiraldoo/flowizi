import math
from typing import List
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QVBoxLayout,
                             QSplitter, QHBoxLayout, QGridLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from flowizi import flowizi
from core.elements.element import Element
from gui.view.view_utils import ViewUtils


class MainWindow(QMainWindow):
    label_signal = pyqtSignal(int)
    label_double_click_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.setWindowTitle("Flowizi")
        self.setWindowIcon(QIcon("logo.svg"))
        self.setStyleSheet("background-color: #30302f;")
        self.initUI()

    def initUI(self):
        """Initializes the main UI layout and its components.

        This method sets up the central widget, main layout, and sidebar for
        the application. It includes:
        - A horizontal splitter containing the main grid and sidebar.
        - A vertical layout (`vbox`) that organizes the toolbar and splitter.
        - A toolbar.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.vbox = QVBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setMinimumWidth(300)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_widget.setLayout(self.sidebar_layout)

        self.toolbar = QHBoxLayout()
        self.toolbar.setContentsMargins(0, 0, 0, 0)

        grid_widget = self.get_grid("environments", flowizi.environment_list)

        self.splitter.addWidget(grid_widget)
        self.vbox.addLayout(self.toolbar)
        self.vbox.addWidget(self.splitter)
        self.splitter.addWidget(self.sidebar_widget)
        central_widget.setLayout(self.vbox)

    def get_grid(self, elem_type: str, elem_list: List[Element]) -> QLabel | QWidget:
        """Returns a widget containing a grid layout if "elem_list" has
        elements, or a QLabel if "elem_list" is empty.

        Args:
            elem_type (str): The type of elements in the grid (used for label
            display).
            elem_list (List[Element]): List of elements to display in the grid.

        Returns:
            QLabel | QWidget: A QWidget with a grid layout if elements
            exist, or a QLabel indicating an empty grid otherwise.
        """
        if len(elem_list):
            return self.generate_grid(elem_list)
        else:
            return self.generate_empty_grid_label(elem_type)

    def generate_grid(self, element_list) -> QWidget:
        """Generates and returns a QWidget containing a grid layout
        of elements.

        Each element in "element_list" is represented by a label in the grid,
        arranged with a specified number of items per row. The labels display
        the element's name and have connected mouse events for interaction.

        Args:
            element_list (List[Element]): List of elements to display.

        Returns:
            QWidget: A QWidget containing the grid of clickable labels, each
            label positioned according to its order in "element_list".

        Notes:
            - "num_elems_row" defines the number of labels per row.
            - Mouse events and double-click signals are connected to each label
              for custom interactions.
        """
        grid = QGridLayout()
        grid.setSpacing(30)

        grid_widget = QWidget()
        grid_widget.setLayout(grid)

        num_elems_row = 4
        total_envs = len(element_list)
        total_rows = math.ceil(total_envs/num_elems_row)
        current_env = 0

        for row in range(total_rows):
            grid.setRowStretch(row, 1)
            for column in range(num_elems_row):
                label = ClickableLabel()
                label.setText(f"{element_list[current_env].name}")
                label.setStyleSheet(ViewUtils.ELEM_LABEL_STYLE)
                label.setAlignment(Qt.AlignCenter)

                grid.addWidget(label, row, column)
                label.set_pos(grid.indexOf(label))
                label.mousePressEvent = self.create_label_event(label.pos)
                label.label_double_click_signal.connect(self.create_label_double_click_event)
                current_env += 1

                if current_env == total_envs:
                    break

        return grid_widget

    def generate_empty_grid_label(self, elem_type) -> QLabel:
        """Creates and returns a QLabel indicating that there are no elements
        of the specified type.

        Args:
            elem_type (str): The type of element to mention in the label text
            (e.g., "files").

        Returns:
            QLabel: A centered label prompting the user to create a new
            element.
        """
        label_text = f"No {elem_type} have been created yet. Use the 'Create' button to create one"
        label = QLabel(label_text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 30px; padding: 10px;")

        return label

    def create_label_event(self, pos):
        """Creates a mouse event handler for a label and returns it.

        The returned handler emits a `label_signal` with the specified
        position when triggered, allowing the label's position to be processed
        by other components.

        Args:
            pos (int): The position of the label within the grid.

        Returns:
            function: An event handler function that emits "label_signal" with
            the label's position when a mouse event occurs.
        """
        def event(event):
            self.label_signal.emit(pos)
        return event

    def create_label_double_click_event(self, pos):
        """Emit a signal indicating that a label was double-clicked.

        This method is called when a label is double-clicked, emitting the
        label_double_click_signal with the position of the label.

        Args:
            pos: The position of the label that was double-clicked.
        """
        self.label_double_click_signal.emit(pos)


class ClickableLabel(QLabel):
    label_double_click_signal = pyqtSignal(int)

    def set_pos(self, pos):
        self.pos = pos

    def mouseDoubleClickEvent(self, event):
        self.label_double_click_signal.emit(self.pos)
