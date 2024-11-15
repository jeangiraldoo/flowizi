from enum import Enum
from PyQt5.QtWidgets import QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from core.elements.element import ElementType


class ElemLabelStyle(Enum):
    DEFAULT = """QLabel{
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
    CLICKED = """QLabel{
                        background-color: #f19600;
                        color: white;
                        font-size: 20px;
                        height: 10px;
                        border: 2px solid white;
                        border-radius: 10px;
                 }"""


class ViewUtils():
    @staticmethod
    def create_btn(name):
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

    @staticmethod
    def create_sidebar_label(name):
        style = """background-color: #1c1c1b; padding-left: 3px; border-radius: 8px; font-size: 22px; color: white;"""
        label = QLabel(name)
        label.setStyleSheet(style)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        return label

    @staticmethod
    def generate_empty_grid_label(elem_type: ElementType) -> QLabel:
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
