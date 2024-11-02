from PyQt5.QtWidgets import QPushButton


class ViewUtils():
    BTN_MAX_SIZE = (100, 40)
    BTN_STYLE = """QPushButton{
                    color: white;
                    font-size: 20px;
                    }
                    QPushButton:hover{
                    background-color: #f19600;
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
