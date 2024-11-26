import math
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QGridLayout
from PyQt5.QtCore import Qt, pyqtSignal
from core.elements.element import Element, ElemType
from gui.views.styles import ElemLabelStyle


class ClickableLabel(QLabel):
    lbl_clicked_sig =pyqtSignal(int)
    lbl_dbl_click_sig = pyqtSignal(int)

    def __init__(self, txt):
        super().__init__()
        self.setStyleSheet(ElemLabelStyle.DEFAULT.value)
        self.setAlignment(Qt.AlignCenter)
        self.setText(txt)

    def set_pos(self, pos):
        self.pos = pos

    def mousePressEvent(self, event):
        """Handles the mouse press event and emits the signal."""
        self.lbl_clicked_sig.emit(self.pos)

    def mouseDoubleClickEvent(self, event):
        self.lbl_dbl_click_sig.emit(self.pos)


class ElemGridWidget(QWidget):
    lbl_sig = pyqtSignal(bool, int)
    lbl_dbl_click_sig = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

    def update(self, elem_type: ElemType, elem_list: list):
        """Replaces the current grid with a new one.

        Args:
            elem_type (ElemType): Type of elements to display.
            elem_list (list): Elements to populate the grid.
        """
        self._clear_grid_widget()
        self._set_grid(elem_type, elem_list)

    def _set_grid(self, elem_type: ElemType, elem_list: list):
        """Adds a widget grid to the layout."""
        self.layout().addWidget(self._get_grid(elem_type, elem_list))

    def _clear_grid_widget(self):
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
                label.lbl_clicked_sig.connect(self._clicked_label_handler)
                label.lbl_dbl_click_sig.connect(self._send_lbl_dbl_click_sig)
                current_env += 1

                if current_env == total_envs:
                    break

        return grid_widget

    def _clicked_label_handler(self, lbl_pos: int):
        res = self._style_clicked_elem(lbl_pos)
        self.lbl_sig.emit(res, lbl_pos)

    def _style_clicked_elem(self, lbl_pos: int) -> bool:
        """
        Updates styles for the clicked label and the previously clicked label.

        Applies the CLICKED or DEFAULT style based on the label's position and
        enables/disables associated buttons accordingly.

        Args:
            lbl_pos (int): The position of the clicked label in the grid.
        """
        item = self.layout().itemAt(0)
        if item is not None:
            grid_widget = item.widget()
            clicked_style = ElemLabelStyle.CLICKED.value
            default_style = ElemLabelStyle.DEFAULT.value
            prev_lbl_pos: int | None = self.get_clicked_elem_pos(grid_widget)
            clicked_label = grid_widget.layout().itemAt(lbl_pos).widget()

            enable_btns = prev_lbl_pos != lbl_pos
            clicked_lbl_style = clicked_style if enable_btns else default_style

            clicked_label.setStyleSheet(clicked_lbl_style)

            if prev_lbl_pos is not None:
                previous_label = grid_widget.layout().itemAt(prev_lbl_pos).widget()
                previous_label.setStyleSheet(ElemLabelStyle.DEFAULT.value)

            return enable_btns

    def get_clicked_elem_pos(self, current_grid: QWidget) -> int | None:
        """
        Gets the index of the currently clicked label.

        Args:
            current_grid (QWidget): The widget in the focused splitter's position.

        Returns:
            int | None: Index of the clicked label, or None if no label is selected.
        """
        total_elems = current_grid.layout().count()
        for i in range(total_elems):
            label = current_grid.layout().itemAt(i).widget()
            label_style = label.styleSheet()

            if ElemLabelStyle.CLICKED.value in label_style:
                return i

    def _send_lbl_dbl_click_sig(self, pos: int):
        """Emits a signal with the position of a label that was double-clicked.

        Args:
            pos (int): The position of the label that was double-clicked.
        """
        self.lbl_dbl_click_sig.emit(pos)
