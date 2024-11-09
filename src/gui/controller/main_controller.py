import sys
from typing import Optional
from PyQt5.QtWidgets import (QWidget, QApplication, QMessageBox,
                             QLabel, QTabWidget, QFileDialog)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QEventLoop
from gui.view.main_view import MainWindow
from gui.view.view_utils import ViewUtils
from gui.view.custom_components import InputDialog, AppDialog
from flowizi import flowizi
from core.database.validations import Validations, ResultType


class Controller:
    def main(self):
        app = QApplication(sys.argv)
        self.main_view = MainWindow()
        self.main_view.show()
        self.current_view = "environments"
        self.current_env = None
        self.update_current_grid()
        self.current_tab_pos = None
        self.selected_app = None

        # Connect label signals to slots
        self.main_view.label_signal.connect(self.elem_clicked)
        self.main_view.label_double_click_signal.connect(self.elem_double_clicked)

        # Create toolbar buttons
        self.start_btn = ViewUtils.create_btn("Start")
        self.create_btn = ViewUtils.create_btn("Create")
        self.delete_btn = ViewUtils.create_btn("Delete")
        self.back_btn = ViewUtils.create_btn("Back")
        self.disable_buttons()

        # Connect button signals to slots
        self.start_btn.clicked.connect(self.start_btn_clicked)
        self.create_btn.clicked.connect(self.create_btn_clicked)
        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.back_btn.clicked.connect(self.back_btn_clicked)

        # Add buttons to toolbar
        self.main_view.toolbar.addWidget(self.back_btn)
        self.main_view.toolbar.addWidget(self.start_btn)
        self.main_view.toolbar.addWidget(self.create_btn)
        self.main_view.toolbar.addWidget(self.delete_btn)
        self.back_btn.hide()
        self.main_view.toolbar.addStretch()

        # Create sidebar icon and labels
        self.sidebar_icon = ViewUtils.create_sidebar_label("")
        icon = QPixmap("logo.svg")
        self.sidebar_icon.setPixmap(icon)
        self.sidebar_icon.setAlignment(Qt.AlignCenter)
        self.sidebar_name_label = ViewUtils.create_sidebar_label("")
        self.sidebar_elem_info_label = ViewUtils.create_sidebar_label("")
        self.sidebar_websites_label = ViewUtils.create_sidebar_label("")
        self.sidebar_apps_label = ViewUtils.create_sidebar_label("")
        self.sidebar_files_label = ViewUtils.create_sidebar_label("")

        # Add icon and labels to the sidebar
        self.main_view.sidebar_layout.addWidget(self.sidebar_icon)
        self.main_view.sidebar_layout.addWidget(self.sidebar_name_label)
        self.main_view.sidebar_layout.addWidget(self.sidebar_elem_info_label)
        self.main_view.sidebar_layout.addWidget(self.sidebar_websites_label)
        self.main_view.sidebar_layout.addWidget(self.sidebar_apps_label)
        self.main_view.sidebar_layout.addWidget(self.sidebar_files_label)
        self.main_view.sidebar_layout.addStretch()
        self.hide_sidebar()

        sys.exit(app.exec_())

    def refresh_window(self):
        """Reloads the window by resetting the toolbar to its default state,
        hiding the sidebar, and refreshing the current grid to reflect any
        new changes.
        """
        self.refresh_left_widget()
        self.refresh_toolbar()
        self.hide_sidebar()

    def refresh_toolbar(self):
        """
        Shows or hides specific buttons based on the current interaction state.

        This method is invoked after an action (e.g., adding a website) to
        disable buttons that interact with elements. It ensures that the
        user cannot click these buttons unless a label is selected,
        enhancing the user interface's usability and preventing unintended
        actions.
        """
        self.disable_buttons()

        if self.current_view == "environments":
            self.start_btn.show()
            self.back_btn.hide()
        else:
            self.start_btn.hide()
            self.back_btn.show()

    def refresh_left_widget(self):
        """
        Replaces the first widget in the environments section or the current
        tab with an updated grid.

        This method is called after creating or deleting an element to display
        the updated information on the screen.
        """
        flowizi.update_environments()
        self.remove_left_widget()

        if self.current_view == "environments":
            updated_grid = self.get_grid_widget("environments")
            self.main_view.splitter.insertWidget(0, updated_grid)
        else:
            updated_grid = self.get_grid_widget(self.current_view)
            self.tab_widget.insertTab(self.current_tab_pos, updated_grid, self.tab_widget.tabText(self.current_tab_pos))
            self.tab_widget.setCurrentWidget(updated_grid)

        self.update_current_grid()

    def elem_clicked(self, pos):
        """Slot triggered when an element is clicked, updating the sidebar with
        information about the clicked element and visually highlighting it,
        while unhighlighting any previously selected elements.
        """

        if self.current_view == "environments":
            self.current_env = pos
        self.refresh_sidebar(pos)
        self.style_clicked_elem(pos)

    def elem_double_clicked(self, pos):
        """Slot triggered when an environment is double clicked,
        revealing the websites, apps and files it holds."""
        if self.current_view == "environments":
            self.hide_sidebar()
            self.remove_left_widget()
            self.show_contained_elems()
            self.refresh_toolbar()

    def style_clicked_elem(self, pos):
        """Changes the style of the label on a given position"""
        self.disable_buttons()
        clicked_pos = self.get_clicked_elem_pos()

        new_label = self.current_grid.itemAt(pos).widget()
        if clicked_pos is not None and clicked_pos == pos: #Enters if the previous clicked label is the same as the current one
            old_label = self.current_grid.itemAt(clicked_pos).widget()
            old_label.setStyleSheet(ViewUtils.ELEM_LABEL_STYLE)
        elif clicked_pos is not None:
            old_label = self.current_grid.itemAt(clicked_pos).widget()
            old_label.setStyleSheet(ViewUtils.ELEM_LABEL_STYLE)
            new_label.setStyleSheet(ViewUtils.ELEM_LABEL_CLICKED_STYLE)

            self.enable_buttons()
        else:  # This code will only run the first time a label is clicked
            new_label.setStyleSheet(ViewUtils.ELEM_LABEL_CLICKED_STYLE)
            self.enable_buttons()

    def get_clicked_elem_pos(self) -> Optional[int]:
        """Returns the index position of the clicked label in the currently
        displayed grid. If no label is selected, returns None.

        Returns:
        int or None: The index of the clicked label, or None if no label is selected."""
        total_elems = len(self.current_grid)
        for i in range(total_elems):
            label = self.current_grid.itemAt(i).widget()
            label_style = label.styleSheet()

            if ViewUtils.ELEM_LABEL_CLICKED_STYLE in label_style:
                return i

    def get_grid_widget(self, elem_type) -> QWidget | QLabel:
        """Returns a QWidget containing a grid of elements.

        If there are no elements of the specified type, returns a QWidget with
        a single label.
        """
        if elem_type == "environments":
            elems = flowizi.environment_list
        else:
            env = flowizi.environment_list[self.current_env]
            elems = getattr(env, elem_type)

        return self.main_view.get_grid(elem_type, elems)

    def remove_left_widget(self):
        """Removes the widget at index 0 of the splitter if the current view
        is "environments", or removes the currently displayed tab otherwise.

        This method is typically called after adding or deleting an element
        to ensure that the updated grid can be inserted into the appropriate
        position.
        """
        if self.current_view == "environments":
            self.main_view.splitter.widget(0).deleteLater()
        else:
            self.tab_widget.widget(self.current_tab_pos).deleteLater()

    def show_contained_elems(self):
        """Inserts a QTabWidget into the splitter at index 0.

        The QTabWidget contains tabs for each type of contained element,
        with each tab displaying a grid of instances corresponding to that
        element type within the current environment.
        """
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
        self.update_current_tab()

    def update_current_tab(self):
        """Updates the values of "current_tab_pos" and "current_view" based on
        the current view.

        This ensures that the application's state reflects the user's active
        tab/view.
        """
        self.current_tab_pos = self.tab_widget.currentIndex()

        if self.current_tab_pos == 0:
            self.current_view = "websites"
        elif self.current_tab_pos == 1:
            self.current_view = "applications"
        else:
            self.current_view = "files"

        self.update_current_grid()

    def update_current_grid(self):
        """Updates the "current_grid" attribute to reflect the grid of the
        currently displayed view.
        """
        if self.current_view == "environments":
            self.current_grid = self.main_view.splitter.widget(0).layout()
        elif self.current_view == "websites":
            self.current_grid = self.tab_widget.widget(0).layout()
        elif self.current_view == "applications":
            self.current_grid = self.tab_widget.widget(1).layout()
        else:
            self.current_grid = self.tab_widget.widget(2).layout()

    def back_btn_clicked(self):
        """Handles the back button click event by resetting the current view,
        tab position, and environment. This restores the application state to
        the initial view  or the state before double-clicking an environment.
        """
        self.current_view = "environments"
        self.current_tab_pos = None
        self.current_env = None
        self.refresh_window()

    def start_btn_clicked(self):
        """If an environment is selected, the elements contained within it
        will be launched.
        """
        pos = self.get_clicked_elem_pos()
        if pos is not None:
            flowizi.environment_list[pos].start()

    def delete_btn_clicked(self):
        """Deletes the element associated with the clicked label"""
        elem_pos = self.get_clicked_elem_pos()
        if self.current_view == "environments" and elem_pos is not None:
            env_name = flowizi.environment_list[elem_pos].name
            Validations.delete_env_validation(env_name)
        elif self.current_tab_pos == 0 and elem_pos is not None:
            env = flowizi.environment_list[self.current_env]
            website_name = env.websites[elem_pos].name
            Validations.delete_elem_validation(env.name, "websites", website_name)
        elif self.current_tab_pos == 2 and elem_pos is not None:
            env = flowizi.environment_list[self.current_env]
            file_name = env.files[elem_pos].name
            Validations.delete_elem_validation(env.name, "files", file_name)
        else:
            env = flowizi.environment_list[self.current_env]
            app_name = env.applications[elem_pos].name
            Validations.delete_elem_validation(env.name, "applications", app_name)
        self.refresh_window()

    def create_btn_clicked(self):
        """Calls a method to create an element based on the current view"""
        if ((self.current_view == "applications" and self.add_application())
           or (self.current_view == "files" and self.add_file())):
            self.refresh_window()
        elif self.current_view == "websites" or self.current_view == "environments":
            singular_name = self.current_view[: len(self.current_view) - 1]
            title = f"Create {singular_name}"
            message = f"Enter the name of the new {singular_name}"
            self.get_input(title, message)

    def get_input(self, w_title, w_message):
        """Displays a message box prompting the user for input to create
        a website or environment.
        """
        msg_box = self.show_create_elem_msg_box(w_title, w_message)

        if msg_box.exec():
            input = msg_box.get_text()
            if input == "":
                self.show_error_message("The name must have at least one character")
            else:
                self.validate_input(input)

    def validate_input(self, input: str):
        """Validates the user's input. If the input is valid, refreshes
        the window to display the updated information.
        """
        if self.current_view == "environments":
            result = self.add_environment(input)
        else:
            result = self.add_website(input)

        if result:
            self.refresh_window()

    def add_environment(self, env_name) -> bool:
        """Tries to create an environment with the name given by the user.
        Displays an error if there is already an environment with that name.

        Args:
        env_name (str): Name provided by the user for the environment.

        Returns:
        bool: True if the environment was successfully created,
        False otherwise.
        """
        result: bool = Validations.add_env_validation(env_name)
        if not result:
            message = f"There is already an environment called {env_name}"
            self.show_error_message(message)

        return result

    def add_website(self, url) -> bool:
        """Tries to create a website with the URL given by the user.
        Calls show_add_website_error to display an error if there is already
        a website with that URL, or the URL is not valid.

        Args:
        url (str): URL provided by the user for the website.

        Returns:
        bool: True if the website was successfully created, False otherwise.
        """
        env_name = flowizi.environment_list[self.current_env].name
        result = Validations.add_elem_validation(env_name, "websites", url)
        if not result == ResultType.SUCCESSFUL_OPERATION:
            self.show_add_website_error(result, url)

        return result

    def add_file(self) -> bool:
        """Launches a QFileDialog so that the user can choose the file to add.

        Once a file is selected, the path to the file will be stored. If
        that path is not already in the database for the current environment,
        it will be added.

        Returns:
            bool: True if the file was successfully created and added,
            False otherwise.
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)  # Allows selecting only existing files
        dialog.setNameFilter("All files (*)")  # Filters by file type if desired
        if dialog.exec_():
            file_path = dialog.selectedFiles()[0]
            env_name = flowizi.environment_list[self.current_env].name
            result = Validations.add_elem_validation(env_name, "files", file_path)

            if not result == ResultType.SUCCESSFUL_OPERATION:
                self.show_error_message("The selected file is already in the environment")
            return result

    def add_application(self) -> bool:
        """Launches an AppDialog so that the user can choose the application
        to add.

        Once an executable file is selected, the path will be stored. If
        that path is not already in the database for the current environment,
        it will be added.

        Returns:
            bool: True if the application was successfully created and added,
            False otherwise.
        """
        app_window = AppDialog(self.current_env)
        app_window.set_window_title("Create an app")
        app_window.set_message("Double click one of the available apps:")
        self.loop = QEventLoop()
        app_window.result_signal.connect(self.handle_app_signal)
        app_window.user_close_signal.connect(self.handle_app_close_signal)
        app_window.exec_()

        if not self.user_app_close:
            return self.app_result[0]

    def handle_app_signal(self, value):
        self.app_result = value

    def handle_app_close_signal(self, value):
        self.user_app_close = value

    def show_add_website_error(self, result, url):
        """Launches a window that displays an error message"""
        if result == ResultType.INVALID_URL:
            message = f"{url} is not a valid URL"
        else:
            message = f"There is already a website with the url {url}"

        self.show_error_message(message)

    def refresh_sidebar(self, pos):
        """
        Updates the sidebar information based on the clicked label's position.

        This method determines which element's information to display in the
        sidebar based on the position of the label clicked by the user. The
        position corresponds to the index of the element whose details will be
        shown.

        Args:
            pos (int): The index position of the clicked label.
        """
        self.main_view.sidebar_widget.show()
        if self.current_view == "environments":
            env = flowizi.environment_list[pos]
            self.sidebar_name_label.setText(f"Name: {env.name}")

            self.sidebar_elem_info_label.setText(f"Screen recording: {env.record}")

            self.sidebar_websites_label.show()
            self.sidebar_websites_label.setText(f"Websites: {len(env.websites)}")

            self.sidebar_apps_label.show()
            self.sidebar_apps_label.setText(f"Apps: {len(env.applications)}")

            self.sidebar_files_label.show()
            self.sidebar_files_label.setText(f"Files: {len(env.files)}")
        else:
            env = flowizi.environment_list[self.current_env]
            elems = getattr(env, self.current_view)
            elem = elems[pos]
            self.sidebar_name_label.setText(f"Name: {elem.name}")
            self.sidebar_elem_info_label.setText(f"URL: {elem.url}")

            self.sidebar_websites_label.hide()
            self.sidebar_apps_label.hide()
            self.sidebar_files_label.hide()

    def hide_sidebar(self):
        """Hides the sidebar from the UI when no label has been selected."""
        self.main_view.sidebar_widget.hide()

    def enable_buttons(self):
        """Enables specific buttons so that the user can interact with them
        after selecting a label
        """
        self.start_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def disable_buttons(self):
        """Disables specific buttons so that the user can't use them unless
        they click a label first, preventing unintended behaviour.
        """
        self.start_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def show_create_elem_msg_box(self, title, message):
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
