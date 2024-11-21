from PyQt5.QtWidgets import (QPushButton, QLabel, QDialog,
                             QVBoxLayout, QHBoxLayout, QLineEdit,
                             QMessageBox, QListWidget, QFileDialog)
from PyQt5.QtCore import pyqtSignal, Qt
from core.platform import sys_apps
from core.database.validations import Validations, ResType
from core.elements.element import ElemType
from gui.views.styles import ElemLabelStyle
from flowizi import flowizi


class InputDialog(QDialog):
    def __init__(self, title, msg):
        super().__init__()
        self.setWindowTitle(title)
        self.message_label = QLabel()
        self.message_label.setText(msg)
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

    def get_text(self):
        return self.text_input.text()


class ChoiceDialog(QMessageBox):
    """
    A customized QMessageBox to prompt the user to choose between 2 actions.

    Notes:
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

    def __init__(self, title, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_closed = False
        self.setWindowTitle(title)
        self.setText(msg)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    def closeEvent(self, event):
        self.user_closed = True
        super().closeEvent(event)


class FileDialog(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setFileMode(QFileDialog.ExistingFile)  # Allows selecting only existing files
        self.setNameFilter("All files (*)")  # Filters by file type if desired

    def get_selected_file(self):
        selected_files = self.selectedFiles()
        return selected_files[0]


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


class AppDialog(QDialog):
    result_signal = pyqtSignal(bool)
    user_close_signal = pyqtSignal(bool)

    def __init__(self, env_name: str):
        super().__init__()
        self.setWindowTitle("Create an app")
        self.current_env_name = env_name
        self.current_view = "app"
        self.execs = None
        self.env_name = flowizi.environment_list[self.current_env_name].name
        self.apps = sys_apps.get_apps()
        self.message_label = QLabel()
        self.message_label.setText("Double click one of the available apps:")
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
        application. If no executables are found, displays an error message
        with guidance. If executables are found, prompts the user to either
        confirm the executable chosen by Flowizi or manually select a different
        one.

        Args:
            name (str): The name of the application.
            item: The clicked item in the item list representing the application.
        """
        self.app_name = name
        app_path = self.apps[name]
        self.execs = sys_apps.get_execs(app_path)

        if len(self.execs) == 0:
            msg = (
              "There are no executable files in the detected directory:"
              f"\n{app_path}\n\n"
              "If this is not the correct installation directory, you can go to"
              " the correct directory and add the executable file as a file"
              " instead of an application."
              )
            ErrorWindow.show(msg)
        else:
            self.request_exec_confirmation(name)

    def exe_double_clicked(self, name):
        """Handles the logic for when an executable item is double-clicked.

        This function retrieves the path of the selected executable and attempts
        to add it to the specified environment in the application database. If
        the executable or app name already exists in the environment, an error
        message is displayed.

        Finally, the function emits result signals and closes the dialog.

        Args:
            name (str): The name of the executable selected by the user.

        Signals:
            result_signal: Emits the result of the add operation along with an
            empty string.
            user_close_signal: Emits a signal indicating the dialog was closed
            programmatically.
        """
        path = self.execs[name]
        result = Validations.add_elem_validation(self.env_name, ElemType.APP, path)

        if result == ResType.FAILURE:
            msg = (
              f"There is already an application called {self.app_name} or that uses {name} as an executable file in the {self.env_name} environment"
              )

            ErrorWindow.show(msg)
            self.result_signal.emit(False)
        else:
            self.result_signal.emit(True)
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
        exe_name, path = sys_apps.detect_exe(app_name, self.execs)
        message = ("This is the detected executable that will open the app:"
                   f"\n{exe_name}"
                   "\nDo you wish to use this one or to select a different one manually?"
                   )

        msg_box = ChoiceDialog("App confirmation", message)
        msg_box.button(QMessageBox.Yes).setText("Use executable")
        msg_box.button(QMessageBox.No).setText("Choose")

        response = msg_box.exec()

        if not msg_box.user_closed and response == QMessageBox.Yes:
            self.accept_detected_exec(app_name, exe_name, path)
        elif not msg_box.user_closed and response == QMessageBox.No:
            self.set_exec_view()

    def accept_detected_exec(self, app_name: str, exe_name, path: str):
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
        result = Validations.add_elem_validation(self.env_name, ElemType.APP, path)
        if result == ResType.FAILURE:
            msg = (
              f"There is already an application called {app_name} or that uses {exe_name} as an executable file in the {self.env_name} environment"
              )

            ErrorWindow.show(msg)
            self.result_signal.emit(False)
        else:
            self.result_signal.emit(True)
        self.user_close_signal.emit(False)
        self.close()

    def set_exec_view(self):
        self.current_view = "execs"
        self.item_list.clear()
        self.set_items(self.execs)

    def set_items(self, items):
        for i in items:
            self.item_list.addItem(i)

    def closeEvent(self, event):
        if event.spontaneous():
            self.user_close_signal.emit(True)


class ErrorWindow():
    @staticmethod
    def show(msg):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(msg)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setDefaultButton(QMessageBox.Ok)
        error_box.exec_()
