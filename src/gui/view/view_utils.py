from PyQt5.QtWidgets import QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import Qt


class ViewUtils():
    ELEM_LABEL_STYLE = """QLabel{
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
    ELEM_LABEL_CLICKED_STYLE = """QLabel{
                        background-color: #f19600;
                        color: white;
                        font-size: 20px;
                        height: 10px;
                        border: 2px solid white;
                        border-radius: 10px;
                        }"""

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
