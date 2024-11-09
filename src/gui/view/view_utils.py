from PyQt5.QtWidgets import (QPushButton, QLabel, QSizePolicy, QDialog,
                             QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
                             QMessageBox)
from PyQt5.QtCore import pyqtSignal
from flowizi import flowizi
from core.database import app_validation


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
    result_signal = pyqtSignal(list)
    user_close_signal = pyqtSignal(bool)

    def __init__(self, env_name: str):
        super().__init__()
        self.current_env_name = env_name
        self.current_view = "app"
        self.execs = None
        self.env_name = flowizi.environment_list[self.current_env_name].name
        self.apps = app_validation.get_installed_apps()
        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-size: 17px")
        self.item_list = QListWidget(self)
        self.item_list.itemDoubleClicked.connect(self.item_double_clicked)
        self.set_items(self.apps)

        layout = QVBoxLayout()
        layout.addWidget(self.message_label)
        layout.addWidget(self.item_list)
        self.setLayout(layout)
        self.resize(450, 550)

    def item_double_clicked(self, item):
        name = item.text()

        if self.current_view == "app":
            self.app_double_clicked(name, item)
        elif self.current_view == "execs":
            self.exe_double_clicked(name)

    def app_double_clicked(self, name: str, item):
        """Handles logic for when an application item is double-clicked. 

        Checks if there are executable files in the detected directory of the 
        application. If no executables are found, displays an error message with 
        guidance. If executables are found, prompts the user to either confirm 
        the executable chosen by Flowizi or manually select a different one.

        Args:
            name (str): The name of the application.
            item: The clicked item in the item list representing the application.
        """
        self.app_name = name
        app_path = self.apps[name]
        self.execs = app_validation.get_all_execs(app_path)

        if len(self.execs) == 0:
            msg = (
              "There are no executable files in the detected directory:"
              f"\n{app_path}\n\n"
              "If this is not the correct installation directory, you can go to"
              " the correct directory and add the executable file as a file"
              " instead of an application."
              )
            self.show_error(msg)
        else:
            self.request_exec_confirmation(name)

    def exe_double_clicked(self, name):
        """Handles the logic for when an executable item is double-clicked.

        This function retrieves the path of the selected executable and attempts
        to add it to the specified environment in the application database. If
        the executable or app name already exists in the environment, an error message is displayed.
        Finally, the function emits result signals and closes the dialog.

        Args:
            name (str): The name of the executable selected by the user.

        Signals:
            result_signal: Emits the result of the add operation along with an empty string.
            user_close_signal: Emits a signal indicating the dialog was closed programmatically.
        """
        path = self.execs[name]
        result = app_validation.finish_add_app(self.env_name, self.app_name, path)

        if not result:
            msg = (
              f"There is already an application called {self.app_name} or that uses {name} as an executable file in the {self.env_name} environment"
              )

            self.show_error(msg)
        self.result_signal.emit([result, ""])
        self.user_close_signal.emit(False)
        self.close()

    def request_exec_confirmation(self, app_name: str):
        """Prompts the user to confirm the detected executable file for an
        application.

        This method displays a dialog box with options for the user to either
        confirm the detected executable file or manually select a
        different one. The user's choice will determine whether the detected
        executable is accepted or if they are redirected to choose from
        alternative executables.

        Args:
            app_name (str): The name of the application for which the
            executable file is being confirmed.
        """
        exe_name, path = app_validation.get_final_path(app_name, self.execs)

        msg_box = CustomMessageBox()
        msg_box.setWindowTitle("App confirmation")
        message = ("This is the detected executable that will open the app:"
                   f"\n{exe_name}"
                   "\nDo you wish to use this one or to select a different one manually?"
                   )
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Use executable")
        msg_box.button(QMessageBox.No).setText("Choose")

        response = msg_box.exec()

        if not msg_box.user_closed and response == QMessageBox.Yes:
            self.accept_detected_exec(app_name, exe_name)
        elif not msg_box.user_closed and response == QMessageBox.No:
            self.set_exec_view()

    def accept_detected_exec(self, app_name: str, exe_name: str):
        """Attempts to add a detected executable to the application database.

        This method tries to register a detected executable file for the
        specified application within the designated environment. If an
        application with the same name or executable file already exists in
        the environment, an error message is displayed. The method then emits
        a result signal and closes the dialog.

        Args:
            app_name (str): The name of the application for which the
            executable is being added.
            exe_name (str): The name of the executable file being added.

        Signals:
            result_signal: Emits the result of the addition as a tuple.
            user_close_signal: Emits a signal indicating the dialog was closed
            programmatically.

        """
        result = app_validation.add_similar_app(self.env_name, app_name, self.apps, "GUI")
        if not result[0]:
            msg = (
              f"There is already an application called {app_name} or that uses {exe_name} as an executable file in the {self.env_name} environment"
              )

            self.show_error(msg)
        self.result_signal.emit(result)
        self.user_close_signal.emit(False)
        self.close()

    def show_error(self, msg):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(msg)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setDefaultButton(QMessageBox.Ok)
        error_box.exec_()

    def set_exec_view(self):
        self.current_view = "execs"
        self.item_list.clear()
        self.set_items(self.execs)

    def set_window_title(self, title):
        self.setWindowTitle(title)

    def set_message(self, message):
        self.message_label.setText(message)

    def set_items(self, items):
        for i in items:
            self.item_list.addItem(i)

    def closeEvent(self, event):
        if event.spontaneous():
            self.user_close_signal.emit(True)


class CustomMessageBox(QMessageBox):
    """
    A customized QMessageBox to distinguish between programmatic and
    user-initiated closures.

    This class overrides the "closeEvent" method to set a "user_closed"
    attribute, which allows other parts of the code to check whether the
    message box was closed by the user or programmatically. This behavior
    is especially useful in scenarios where validations or actions depend
    on how the window was closed.

    Attributes:
        user_closed (bool): Tracks if the message box was closed by the user.
                            Defaults to False; set to True if the user closes
                            the window.

    Methods:
        closeEvent(event): Overrides the default close event to set
                           "user_closed" to True if closed by the user, then
                           calls the parent class's closeEvent.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_closed = False

    def closeEvent(self, event):
        self.user_closed = True
        super().closeEvent(event)
