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
        layout = QGridLayout()
        layout.setSpacing(30)
        self.setLayout(layout)

    def update(self, elem_type: ElemType, elem_list: list):
        """
        Updates the layout by replacing the current widgets with new ones.

        Args:
            elem_type (ElemType): The type of elements to display.
            elem_list (list): A list of elements to populate the layout.
        """
        self._clear_layout()
        self._populate_layout(elem_type, elem_list)

    def _clear_layout(self):
        """
        Deletes all widgets from the layout to prepare it for adding new ones.

        The deletion begins only if a layout exists and contains at least one widget.
        """
        layout = self.layout()
        if layout is not None and layout.count():
            for i in range(layout.count()):
                item = layout.takeAt(0)
                widget =  item.widget()
                widget.deleteLater()

    def _populate_layout(self, elem_type: ElemType, elem_list: list[Element]):
        """
        Populates the layout with one or more labels.

        If the provided element list is empty, a label with feedback on how to create 
        an element is added to the layout. Otherwise, the layout is populated with 
        labels, each representing an element from the given list.

        Args:
            elem_type (ElemType): The type of the elements in the list.
            elem_list (list[Element]): A list of elements to be represented as labels.
        """
        if len(elem_list):
            self._generate_grid_labels(self.layout(), elem_list)
        else:
            self.layout().addWidget(self._generate_empty_label(elem_type), 0, 0)
        
    def get_layout(self) -> QGridLayout:
        """
        Retrieve the layout associated with this instance.

        Provides access to the "QGridLayout" that manages the labels displayed in the widget. 
        This method helps decouple other parts of the program from the internal structure 
        of the "ElemGridWidget" class.

        Returns:
            QGridLayout: The grid layout containing the labels for this widget.
        """
        return self.layout()

    def _generate_empty_label(self, elem_type: ElemType) -> QLabel:
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

    def _generate_grid_labels(self, layout: QGridLayout, elem_list: list[Element]):
        """
        Populates the layout with labels representing the provided elements.

        Each element in "elem_list" is displayed as a label in the grid layout, arranged 
        in rows with a predefined number of items per row. The labels show the name of each 
        element and support mouse interactions for additional functionality.

        Args:
            elem_list (list[Element]): List of elements to be represented as labels in the layout.
        """
        num_elems_row = 4
        total_envs = len(elem_list)
        total_rows = math.ceil(total_envs/num_elems_row)
        current_env = 0

        for row in range(total_rows):
            # layout.setRowStretch(row, 1)
            for column in range(num_elems_row):
                label = ClickableLabel(f"{elem_list[current_env].name}")
                layout.addWidget(label, row, column)
                label.set_pos(layout.indexOf(label))
                label.lbl_clicked_sig.connect(self._clicked_label_handler)
                label.lbl_dbl_click_sig.connect(self._send_lbl_dbl_click_sig)
                current_env += 1
                if current_env == total_envs:
                    break

    def _clicked_label_handler(self, lbl_pos: int):
        res = self._style_clicked_elem(lbl_pos)
        self.lbl_sig.emit(res, lbl_pos)

    def _style_clicked_elem(self, lbl_pos: int) -> bool:
        """
        Updates styles for the clicked label and the previously clicked label.

        Applies the CLICKED or DEFAULT style based on the label's position and
        enables/disables associated buttons accordingly.

        Args:
            lbl_pos (int): The position of the clicked label in the layout.
        """
        if self.layout().count():
            clicked_style = ElemLabelStyle.CLICKED.value
            default_style = ElemLabelStyle.DEFAULT.value
            prev_lbl_pos: int | None = self.get_clicked_elem_pos(self.layout())
            clicked_label = self.layout().itemAt(lbl_pos).widget()

            enable_btns = prev_lbl_pos != lbl_pos
            clicked_lbl_style = clicked_style if enable_btns else default_style

            clicked_label.setStyleSheet(clicked_lbl_style)

            if prev_lbl_pos is not None:
                previous_label = self.layout().itemAt(prev_lbl_pos).widget()
                previous_label.setStyleSheet(ElemLabelStyle.DEFAULT.value)

            return enable_btns

    def get_clicked_elem_pos(self, layout: QGridLayout) -> int | None:
        """
        Retrieve the index of the currently clicked label.

        Args:
            layout (QGridLayout): The layout containing the labels.

        Returns:
            int | None: The index of the clicked label, or None if no label is clicked.
        """
        total_elems = layout.count()
        for i in range(total_elems):
            label = layout.itemAt(i).widget()
            label_style = label.styleSheet()

            if ElemLabelStyle.CLICKED.value in label_style:
                return i

    def _send_lbl_dbl_click_sig(self, pos: int):
        """Emits a signal with the position of a label that was double-clicked.

        Args:
            pos (int): The position of the label that was double-clicked.
        """
        self.lbl_dbl_click_sig.emit(pos)
