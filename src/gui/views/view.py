import math
from typing import List
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QVBoxLayout,
                             QSplitter, QPushButton, QHBoxLayout, QGridLayout,
                             QSizePolicy)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from gui.views.custom_comps import ClickableLabel
from flowizi import flowizi
from core.elements.element import Element, ElementType
from gui.views.styles import ElemLabelStyle


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
        - A vertical layout (vbox) that organizes the toolbar and splitter.
        - A toolbar.
        """
        root_widget = QWidget()
        root_layout = QVBoxLayout()
        root_widget.setLayout(root_layout)
        self.setCentralWidget(root_widget)

        self.splitter = QSplitter(Qt.Horizontal)

        self.setup_toolbar()
        self.setup_grid()
        self.setup_sidebar()

        root_layout.addLayout(self.toolbar)
        root_layout.addWidget(self.splitter)

    def get_grid(self, elem_type: ElementType, elem_list: List[Element]) -> QLabel | QWidget:
        """Returns a widget containing a grid layout if "elem_list" has
        elements, or a QLabel if "elem_list" is empty.

        Args:
            elem_type (ElementType): The type of elements in the grid (used for label
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
                label.setStyleSheet(ElemLabelStyle.DEFAULT.value)
                label.setAlignment(Qt.AlignCenter)

                grid.addWidget(label, row, column)
                label.set_pos(grid.indexOf(label))
                label.mousePressEvent = self.send_label_signal(label.pos)
                label.label_double_click_signal.connect(self.create_label_double_click_event)
                current_env += 1

                if current_env == total_envs:
                    break

        return grid_widget

    def send_label_signal(self, pos: int):
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

    def setup_toolbar(self):
        self.toolbar = QHBoxLayout()
        self.toolbar.setContentsMargins(0, 0, 0, 0)

        self.start_btn = self.create_button("Start")
        self.create_btn = self.create_button("Create")
        self.delete_btn = self.create_button("Delete")
        self.back_btn = self.create_button("Back")

        self.toolbar.addWidget(self.back_btn)
        self.toolbar.addWidget(self.start_btn)
        self.toolbar.addWidget(self.create_btn)
        self.toolbar.addWidget(self.delete_btn)
        self.back_btn.hide()
        self.toolbar.addStretch()

    def setup_grid(self):
        grid_widget = self.get_grid(ElementType.ENV, flowizi.environment_list)
        self.splitter.addWidget(grid_widget)

    def setup_sidebar(self):
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setMinimumWidth(300)
        sidebar_layout = QVBoxLayout()
        self.sidebar_widget.setLayout(sidebar_layout)
        self.splitter.addWidget(self.sidebar_widget)

        sidebar_icon = self.create_sidebar_label("")
        icon = QPixmap("logo.svg")
        sidebar_icon.setPixmap(icon)
        sidebar_icon.setAlignment(Qt.AlignCenter)
        self.sidebar_name_label = self.create_sidebar_label("")
        self.sidebar_elem_info_label = self.create_sidebar_label("")
        self.sidebar_websites_label = self.create_sidebar_label("")
        self.sidebar_apps_label = self.create_sidebar_label("")
        self.sidebar_files_label = self.create_sidebar_label("")

        sidebar_layout.addWidget(sidebar_icon)
        sidebar_layout.addWidget(self.sidebar_name_label)
        sidebar_layout.addWidget(self.sidebar_elem_info_label)
        sidebar_layout.addWidget(self.sidebar_websites_label)
        sidebar_layout.addWidget(self.sidebar_apps_label)
        sidebar_layout.addWidget(self.sidebar_files_label)
        sidebar_layout.addStretch()

    def create_button(self, name):
        btn = QPushButton(name)
        btn.setMaximumSize(100, 40)
        btn.setStyleSheet("""QPushButton{
                    background-color: #f19600;
                    font-size: 20px;
                    }
                    QPushButton:hover{
                    background-color: #ffbb4d;
                    }""")
        return btn

    def create_sidebar_label(self, text: str):
        style = """background-color: #1c1c1b; padding-left: 3px;
                   border-radius: 8px; font-size: 22px; color: white;
                """
        label = QLabel(text)
        label.setStyleSheet(style)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        return label

    def generate_empty_grid_label(self, elem_type: ElementType) -> QLabel:
        """Creates and returns a QLabel indicating that there are no elements
        of the specified type.

        Args:
            elem_type (ElementType): The type of element to mention in the label text
            (e.g., "files").

        Returns:
            QLabel: A centered label prompting the user to create a new
            element.
        """
        label_text = f"No {elem_type.value} have been created yet. Use the 'Create' button to create one"
        label = QLabel(label_text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 30px; padding: 10px;")

        return label
