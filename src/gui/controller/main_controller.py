import sys
from PyQt5.QtWidgets import (QApplication, QMessageBox, QVBoxLayout,
                             QHBoxLayout, QDialog, QLineEdit, QSizePolicy,
                             QLabel,QListWidget, QPushButton, QTabWidget, QFileDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
from gui.view.main_view import MainWindow
from gui.view.view_utils import ViewUtils
from flowizi import flowizi
from core.database import database
from commands import add, remove


class Controller:
    def main(self):
        app = QApplication(sys.argv)
        self.main_view = MainWindow()
        self.main_view.show()
        self.current_view = "environments"
        self.current_env = None
        self.current_tab_pos = None
        self.selected_app = None

        self.main_view.label_signal.connect(self.element_clicked)
        self.main_view.label_double_click_signal.connect(self.element_double_clicked)

        self.start_btn = ViewUtils.create_btn("Start")
        self.create_btn = ViewUtils.create_btn("Create")
        self.delete_btn = ViewUtils.create_btn("Delete")
        self.back_btn = ViewUtils.create_btn("Back")

        self.start_btn.clicked.connect(self.start_btn_clicked)
        self.create_btn.clicked.connect(self.create_btn_clicked)
        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.back_btn.clicked.connect(self.back_btn_clicked)

        self.main_view.toolbar.addWidget(self.back_btn)
        self.main_view.toolbar.addWidget(self.start_btn)
        self.main_view.toolbar.addWidget(self.create_btn)
        self.main_view.toolbar.addWidget(self.delete_btn)
        self.back_btn.hide()

        self.main_view.toolbar.addStretch()

                
        sys.exit(app.exec_())

    def element_clicked(self, pos):
        if self.current_view == "environments":
            self.environment_clicked(pos)
        else:
            self.contained_element_clicked(pos)

    def environment_clicked(self, pos):
        self.current_env = pos
        self.main_view.element_info_container.itemAt(1).widget().setText(f"Name: {flowizi.environment_list[pos].name}")
        self.main_view.element_info_container.itemAt(2).widget().setText(f"Screen recording: {flowizi.environment_list[pos].record}")
        self.main_view.element_info_container.itemAt(3).widget().setText(f"Websites: {len(flowizi.environment_list[pos].websites)}")
        self.main_view.element_info_container.itemAt(4).widget().setText(f"Apps: {len(flowizi.environment_list[pos].applications)}")
        self.main_view.element_info_container.itemAt(5).widget().setText(f"Files: {len(flowizi.environment_list[pos].files)}")

        self.highlight_clicked_element(pos)
        
    def contained_element_clicked(self, pos):
        environment = flowizi.environment_list[self.current_env]
        if self.current_view == "websites":
            contained_elements = environment.websites
        elif self.current_view == "applications":
            contained_elements = environment.applications
        elif self.current_view == "files":
            contained_elements = environment.files

        self.main_view.element_info_container.itemAt(1).widget().setText(f"Name: {contained_elements[pos].name}")
        self.main_view.element_info_container.itemAt(2).widget().setText(f"URL: {contained_elements[pos].url}")

        self.highlight_clicked_element(pos)

    def highlight_clicked_element(self, pos):
        for i in range(len(self.main_view.grid)):
            if pos == i:
                clicked_label = self.main_view.grid.itemAt(pos)
                clicked_label.widget().setStyleSheet(ViewUtils.ELEM_LABEL_CLICKED_STYLE)
            else:
                self.main_view.grid.itemAt(i).widget().setStyleSheet(ViewUtils.ELEM_LABEL_STYLE)

    def element_double_clicked(self, pos):
        self.current_view = "contained_elements"
        self.refresh_toolbar()
        self.remove_grid()
        self.set_contained_element_sidebar()
        self.show_environment_overview()

    def get_grid_widget(self, elem_type):
        """Returns a QWidget that contains a grid of elements or a label in case
        there is no elements of the given type"""
        if elem_type == "environments":
            elems = flowizi.environment_list
        else:
            env = flowizi.environment_list[self.current_env]
            elems = getattr(env, elem_type)

        return self.main_view.get_grid(elem_type, elems)

    def reset_environment_sidebar(self):
        self.main_view.element_info_container.itemAt(1).widget().setText("No environments selected")
        self.main_view.element_info_container.itemAt(2).widget().setText("")
        style = "background-color: #454541; font-size: 18px; color: white; padding: 20px;"
        websites_label = QLabel("")
        websites_label.setWordWrap(True)
        websites_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        websites_label.setStyleSheet(style)
        websites_label.setFixedHeight(65)

        applications_label = QLabel("")
        applications_label.setWordWrap(True)
        applications_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        applications_label.setStyleSheet(style)
        applications_label.setFixedHeight(65)

        files_label = QLabel("")
        files_label.setWordWrap(True)
        files_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        files_label.setStyleSheet(style)
        files_label.setFixedHeight(65)

        self.main_view.element_info_container.addWidget(websites_label)
        self.main_view.element_info_container.addWidget(applications_label)
        self.main_view.element_info_container.addWidget(files_label)


    def set_contained_element_sidebar(self):
        self.main_view.element_info_container.itemAt(1).widget().setText("No element selected")
        self.main_view.element_info_container.itemAt(2).widget().setText("")

        while self.main_view.element_info_container.count() > 3:
            item = self.main_view.element_info_container.takeAt(3)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def refresh_toolbar(self):
        if self.current_view == "environments":
            self.start_btn.show()
            self.back_btn.hide()
        else:
            self.start_btn.hide()
            self.back_btn.show()

    def remove_grid(self):
        self.main_view.splitter.widget(0).deleteLater()

    def show_environment_overview(self):
        self.main_view.toolbar.addStretch()

        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.update_current_tab)
        self.tab_widget.setStyleSheet("""QTabBar::tab::selected{
                                        background-color: #f19600;
                                 }""")
        self.tab_widget.addTab(self.get_grid_widget("websites"), "Websites")
        self.tab_widget.addTab(self.get_grid_widget("applications"), "Apps")
        self.tab_widget.addTab(self.get_grid_widget("files"), "Files")
        font = QFont()
        font.setPointSize(12)
        self.tab_widget.tabBar().setFont(font)
        self.main_view.splitter.insertWidget(0, self.tab_widget)

    def update_current_tab(self):
        self.current_tab_pos = self.tab_widget.currentIndex()

        if self.current_tab_pos == 0:
            self.current_view = "websites"
        elif self.current_tab_pos == 1:
            self.current_view = "applications"
        else:
            self.current_view = "files"

    def back_btn_clicked(self):
        self.current_view = "environments"
        self.current_tab_pos = None
        self.current_env = None
        self.refresh_toolbar()
        self.remove_grid()

        self.main_view.toolbar.addStretch()
        self.reset_environment_sidebar()
        environments = flowizi.environment_list
        env_grid = self.main_view.generate_grid(environments)
        self.main_view.splitter.insertWidget(0, env_grid)

    def start_btn_clicked(self):
        pos = self.get_clicked_element_pos()
        flowizi.environment_list[pos].start()

    def create_btn_clicked(self):
        if ((self.current_view == "applications" and self.add_application())
           or (self.current_view == "files" and self.add_file())):
            self.refresh_grid()
        elif self.current_view == "websites" or self.current_view == "environments":
            singular_name = self.current_view[: len(self.current_view) - 1]
            title = f"Create {singular_name}"
            message = f"Enter the name of the new {singular_name}"
            self.get_input(title, message)

    def get_input(self, w_title, w_message):
        msg_box = self.show_create_element_msg_box(w_title, w_message)

        if msg_box.exec():
            input = msg_box.get_text()
            if input == "":
                self.show_error_message("The name must have at least one character")
            else:
                self.validate_input(input)

    def validate_input(self, input):
        if self.current_view == "environments":
            result = self.add_environment(input)
        elif self.current_view == "websites":
            result = self.add_website(input)
        elif self.current_view == "applications":
            result = self.add_application()

        if result:
            self.refresh_grid()

    def refresh_grid(self):
        flowizi.update_environments()

        if self.current_view == "environments":
            self.remove_grid()
            updated_grid = self.get_grid_widget("environments")
            self.main_view.splitter.insertWidget(0, updated_grid)
        else:
            updated_grid = self.get_grid_widget(self.current_view)
            self.tab_widget.widget(self.current_tab_pos).deleteLater()
            self.tab_widget.insertTab(self.current_tab_pos, updated_grid, self.tab_widget.tabText(self.current_tab_pos))
            self.tab_widget.setCurrentWidget(updated_grid)

    def add_environment(self, env_name):
        result = add.add_environment("", env_name)
        if not result:
            message = f"There is already an environment called {env_name}"
            self.show_error_message(message)

        return result

    def add_website(self, url):
        env_name = flowizi.environment_list[self.current_env].name
        result = add.add_website("", env_name, url)
        if not result[0]:
            self.show_add_website_error(result[1], url)

        return result

    def add_file(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)  # Allows selecting only existing files
        dialog.setNameFilter("All files (*)")  # Filters by file type if desired
        if dialog.exec_():
            file_path = dialog.selectedFiles()[0]
            env_name = flowizi.environment_list[self.current_env].name
            result = add.add_file("", env_name, file_path)

            if not result:
                self.show_error_message("The selected file is already in the environment")
            return result

    def add_application(self):
        app_window = AppDialog(self.current_env)
        app_window.set_window_title("Create an app:")
        app_window.set_message("Double click one of the available apps:")
        result = app_window.result_signal.connect(self.get_app_insertion_result)
        app_window.exec_()

        return result

    def show_add_website_error(self, result, url):
        if result == "invalid_url":
            message = f"{url} is not a valid URL"
        else:
            message = f"There is already a website with the url {url}"

        self.show_error_message(message)

    def get_app_insertion_result(self, result):
        return result

    def delete_btn_clicked(self):
        element_pos = self.get_clicked_element_pos()
        if self.current_view == "environments" and element_pos is not None:
            env_name = flowizi.environment_list[element_pos].name
            remove.remove_environment(env_name)
        elif self.current_tab_pos == 0 and element_pos is not None:
            env = flowizi.environment_list[self.current_env]
            website_name = env.websites[element_pos].name
            remove.remove_website("", env.name, website_name)
        elif self.current_tab_pos == 2 and element_pos is not None:
            env = flowizi.environment_list[self.current_env]
            file_name = env.files[element_pos].name
            remove.remove_file("", env.name, file_name)
        else:
            env = flowizi.environment_list[self.current_env]
            app_name = env.applications[element_pos].name
            remove.remove_application("", env.name, app_name)
        self.refresh_grid()

    def get_clicked_element_pos(self):
        total_elements = len(self.main_view.grid)
        for i in range(total_elements):
            label = self.main_view.grid.itemAt(i).widget()
            label_style = label.styleSheet()

            if ViewUtils.ELEM_LABEL_CLICKED_STYLE in label_style:
                return i

    def show_create_element_msg_box(self, title, message):
        msg_box = InputDialog()
        msg_box.set_window_title(title)
        msg_box.set_message(message)
        return msg_box

    def show_error_message(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setDefaultButton(QMessageBox.Ok)
        error_box.exec_()


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


