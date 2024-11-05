from PyQt5.QtWidgets import (QPushButton, QLabel, QSizePolicy, QDialog,
                             QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget)
from PyQt5.QtCore import pyqtSignal
from flowizi import flowizi
from commands import add


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


class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-size: 17px")
        self.text_input = QLineEdit(self)

        btn_box = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.message_label)
        layout.addWidget(self.text_input)
        layout.addLayout(btn_box)
        self.setLayout(layout)
        self.resize(350, 150)

    def set_window_title(self, title):
        self.setWindowTitle(title)

    def set_message(self, message):
        self.message_label.setText(message)

    def get_text(self):
        return self.text_input.text()


class AppDialog(QDialog):
    result_signal = pyqtSignal(bool)

    def __init__(self, env_name):
        super().__init__()
        self.current_env_name = env_name
        self.current_step = "app"
        self.apps = add.get_all_installed_apps()
        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-size: 17px")
        self.item_list = QListWidget(self)
        self.item_list.itemDoubleClicked.connect(self.update_list)
        self.set_items(self.apps)

        layout = QVBoxLayout()
        layout.addWidget(self.message_label)
        layout.addWidget(self.item_list)
        self.setLayout(layout)
        self.resize(450, 550)

    def set_window_title(self, title):
        self.setWindowTitle(title)

    def set_message(self, message):
        self.message_label.setText(message)

    def set_items(self, items):
        for i in items:
            self.item_list.addItem(i)

    def update_list(self, item):
        if self.current_step == "app":
            self.current_step = "execs"
            self.app_name = item.text()
            self.show_execs(self.app_name)
        elif self.current_step == "execs":
            path = self.execs[item.text()]
            env_name = flowizi.environment_list[self.current_env_name].name
            result = add.add_one_similar_app(env_name, self.app_name, path)
            self.result_signal.emit(result)
            self.close()

    def show_execs(self, app_name):
        path = self.apps[app_name]
        self.execs = add.get_exec_files("", path)
        self.message_label.setText("Choose the executable file of the application:")
        self.item_list.clear()
        self.set_items(self.execs)
