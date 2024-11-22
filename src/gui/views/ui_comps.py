import math
from PyQt5.QtWidgets import (QSizePolicy, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QTabWidget, QPushButton, QGridLayout)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from core.elements.element import Element, ElemType
from gui.views.styles import ElemLabelStyle


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.hide()
        self.setMinimumWidth(300)
        layout = QVBoxLayout()
        self.setLayout(layout)

        sidebar_icon = self.create_label("")
        sidebar_icon.setPixmap(QPixmap("logo.svg"))
        sidebar_icon.setAlignment(Qt.AlignCenter)
        self.name_label = self.create_label("")
        self.elem_info_label = self.create_label("")
        self.websites_label = self.create_label("")
        self.apps_label = self.create_label("")
        self.files_label = self.create_label("")

        layout.addWidget(sidebar_icon)
        layout.addWidget(self.name_label)
        layout.addWidget(self.elem_info_label)
        layout.addWidget(self.websites_label)
        layout.addWidget(self.apps_label)
        layout.addWidget(self.files_label)
        layout.addStretch()

    def create_label(self, text: str) -> QLabel:
        """
        Creates the labels used to display information about an element.

        Args:
            text (str): Text to display on the label.

        Returns:
            QLabel: QLabel instance with a set text.
        """
        style = """background-color: #1c1c1b; padding-left: 3px;
                   border-radius: 8px; font-size: 22px; color: white;
                """
        label = QLabel(text)
        label.setStyleSheet(style)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        return label


class Toolbar(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self.start_btn = self.create_button("Start")
        self.create_btn = self.create_button("Create")
        self.delete_btn = self.create_button("Delete")
        self.back_btn = self.create_button("Back")

        self.addWidget(self.back_btn)
        self.addWidget(self.start_btn)
        self.addWidget(self.create_btn)
        self.addWidget(self.delete_btn)
        self.back_btn.hide()
        self.addStretch()

    def create_button(self, btn_txt: str) -> QPushButton:
        """
        Creates a button to be displayed in the toolbar

        Args:
            btn_txt (str): Text to be displayed on the button.

        Returns:
            QPushButton: Customized button.
        """
        btn = QPushButton(btn_txt)
        btn.setMaximumSize(100, 40)
        btn.setStyleSheet("""QPushButton{
                    background-color: #f19600;
                    font-size: 20px;
                    }
                    QPushButton:hover{
                    background-color: #ffbb4d;
                    }""")
        return btn

    def set_btns_clickable(self, clickable: bool):
        """
        Enable or disable buttons to allow or prevent the user from using them.

        Args:
            clickable (bool): True to enable the buttons, False otherwise.
        """
        self.start_btn.setEnabled(clickable)
        self.delete_btn.setEnabled(clickable)


class TabBar(QTabWidget):
    lbl_sig = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        font = QFont()
        font.setPointSize(12)
        self.tabBar().setFont(font)
        self.setStyleSheet("""QTabBar::tab::selected{background-color: #f19600;}""")
        self._setup_tabs()

    def clear_grid_widget(self):
        """Removes the widget found in every tab."""
        for i in range(self.count()):
            self.widget(i).clear_grid_widget()

    def _setup_tabs(self):
        """Initializes the tabs within the tab widget."""
        tab_titles = [ElemType.WEB, ElemType.APP, ElemType.FILE]

        for idx, title in enumerate(tab_titles):
            widget = ElemGridWidget()
            widget.lbl_sig.connect(self._send_lbl_sig)
            self.addTab(widget, title.value)

    def _send_lbl_sig(self, pos: int):
        """Creates a mouse event handler for a label and returns it.

        The returned handler emits a signal with the label's position when
        clicked, allowing the label's position to be used by other components.

        Args:
            pos (int): The position of the label within the grid.

        Returns:
            func: Emits "lbl_sig" with the label's position when clicked.
        """
        self.lbl_sig.emit(pos)


class ElemGridWidget(QWidget):
    lbl_sig = pyqtSignal(int)
    lbl_dbl_click_sig = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

    def set_grid(self, elem_type: ElemType, elem_list: list):
        """Adds a widget grid to the layout."""
        self.layout().addWidget(self._get_grid(elem_type, elem_list))

    def clear_grid_widget(self):
        """
        Deletes the grid widget if present

        The grid widget is deleted if it is present, if no grid has been set nothing is done.
        """
        if self.layout().count() > 0:
            widget = self.layout().itemAt(0).widget()
            self.layout().removeWidget(widget)
            widget.deleteLater()

    def _get_grid(self, elem_type: ElemType, elem_list: list[Element]) -> QLabel | QWidget:
        """Returns a widget containing a grid layout if "elem_list" has
        elements, or a QLabel if "elem_list" is empty.

        Args:
            elem_type (ElemType): The type of elements in the grid.
            elem_list (List[Element]): List of elements to display in the grid.

        Returns:
            QLabel | QWidget: A QWidget with a grid layout if elements
            exist, or a QLabel indicating an empty grid otherwise.
        """
        if len(elem_list):
            return self._generate_grid(elem_list)
        else:
            return self._generate_empty_grid_label(elem_type)

    def _generate_empty_grid_label(self, elem_type: ElemType) -> QLabel:
        """
        Returns a label displaying that there are no elements of the given type.

        Args:
            elem_type (ElemType): Type of element to mention in the label.

        Returns:
            QLabel: A label prompting the user to create a new element.
        """
        label_text = f"No {elem_type.value} have been created yet. Use the 'Create' button to create one"
        label = QLabel(label_text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 30px; padding: 10px;")

        return label

    def _generate_grid(self, element_list: list[Element]) -> QWidget:
        """Returns a QWidget containing a grid layout with labels.

        Each element in "element_list" is represented by a label in the grid,
        arranged with a specified number of items per row. The labels display
        the element's name and have connected mouse events for interaction.

        Args:
            element_list (List[Element]): List of elements to display.

        Returns:
            QWidget: A QWidget containing the grid of clickable labels, each
            label positioned according to its order in "element_list".
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
                label = ClickableLabel(f"{element_list[current_env].name}")
                grid.addWidget(label, row, column)
                label.set_pos(grid.indexOf(label))
                label.mousePressEvent = self._send_lbl_sig(label.pos)
                label.lbl_dbl_click_sig.connect(self._send_lbl_dbl_click_sig)
                current_env += 1

                if current_env == total_envs:
                    break

        return grid_widget

    def _send_lbl_dbl_click_sig(self, pos: int):
        """Emits a signal with the position of a label that was double-clicked.

        Args:
            pos (int): The position of the label that was double-clicked.
        """
        self.lbl_dbl_click_sig.emit(pos)

    def _send_lbl_sig(self, pos: int):
        """Creates a mouse event handler for a label and returns it.

        The returned handler emits a signal with the label's position when
        clicked, allowing the label's position to be used by other components.

        Args:
            pos (int): The position of the label within the grid.

        Returns:
            func: Emits "lbl_sig" with the label's position when clicked.
        """
        def event(event):
            self.lbl_sig.emit(pos)
        return event


class ClickableLabel(QLabel):
    lbl_dbl_click_sig = pyqtSignal(int)

    def __init__(self, txt):
        super().__init__()
        self.setStyleSheet(ElemLabelStyle.DEFAULT.value)
        self.setAlignment(Qt.AlignCenter)
        self.setText(txt)

    def set_pos(self, pos):
        self.pos = pos

    def mouseDoubleClickEvent(self, event):
        self.lbl_dbl_click_sig.emit(self.pos)
