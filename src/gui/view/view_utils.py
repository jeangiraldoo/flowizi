from PyQt5.QtWidgets import QPushButton, QLabel, QSizePolicy


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
                    color: white;
                    font-size: 20px;
                    }
                    QPushButton:hover{
                    background-color: #f19600;
                    }""")
        return btn

    @staticmethod
    def create_sidebar_label(name):
        style = """background-color: #454541; font-size: 18px; color: white;
            padding: 20px; height: 1px;"""
        label = QLabel(name)
        label.setStyleSheet(style)
        label.setFixedHeight(60)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        return label
