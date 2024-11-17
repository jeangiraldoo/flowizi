import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QTabWidget,
                             QFileDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QEventLoop
from gui.views.view import MainWindow
from gui.views.styles import ElemLabelStyle
from gui.views.custom_comps import ErrorWindow, InputDialog, AppDialog
from core.elements.element import ElementType, Environment
from core.elements.contained_element import ContainedElement
from core.text_res.feedback import Feedback
from flowizi import flowizi
from core.database.validations import Validations, ResultType


class Controller:
    def main(self):
        app = QApplication(sys.argv)
        self.view = MainWindow()
        self.view.show()
        self.current_view = ElementType.ENV
        self.current_env = None
        self.update_current_grid()
        self.current_tab_pos = None
        self.selected_app = None

        self.connect_signals_to_slots()
        self.set_btns_clickable(False)
        self.view.sidebar_widget.hide()

        sys.exit(app.exec_())

    def refresh_window(self):
        """Reloads the window by resetting the toolbar to its default state,
        hiding the sidebar, and refreshing the current grid to reflect any
        new changes.
        """
        self.refresh_left_widget()
        self.refresh_toolbar()
        self.view.sidebar_widget.hide()

    def refresh_toolbar(self):
        """
        Shows or hides specific buttons based on the current interaction state.

        This method is invoked after an action (e.g., adding a website) to
        disable buttons that interact with elements. It ensures that the
        user cannot click these buttons unless a label is selected,
        enhancing the user interface's usability and preventing unintended
        actions.
        """
        self.set_btns_clickable(False)

        if self.current_view == ElementType.ENV:
            self.view.start_btn.show()
            self.view.back_btn.hide()
        else:
            self.view.start_btn.hide()
            self.view.back_btn.show()

    def refresh_left_widget(self):
        """
        Replaces the first widget in the environments section or the current
        tab with an updated grid.

        This method is called after creating or deleting an element to display
        the updated information on the screen.
        """
        flowizi.update_environments()
        self.remove_left_widget()

        if self.current_view == ElementType.ENV:
            updated_grid = self.get_grid_widget(ElementType.ENV)
            self.view.splitter.insertWidget(0, updated_grid)
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

        if self.current_view == ElementType.ENV:
            self.current_env = pos
        self.refresh_sidebar(pos)
        self.style_clicked_elem(pos)

    def elem_double_clicked(self, pos):
        """Slot triggered when an environment is double clicked,
        revealing the websites, apps and files it holds."""
        if self.current_view == ElementType.ENV:
            self.view.sidebar_widget.hide()
            self.remove_left_widget()
            self.show_contained_elems()
            self.refresh_toolbar()

    def style_clicked_elem(self, lbl_pos: int):
        """Updates the style of the clicked label in the grid.

        Determines whether the clicked label should use the default or
        clicked style and enables or disables associated buttons based
        on whether its position matches the previously clicked label.

        Args:
            pos (int): Position of the clicked label in the grid.
        """
        clicked_style = ElemLabelStyle.CLICKED.value
        default_style = ElemLabelStyle.DEFAULT.value
        prev_lbl_pos: int | None = self.get_clicked_elem_pos()
        clicked_label = self.current_grid.itemAt(lbl_pos).widget()

        enable_btns = prev_lbl_pos != lbl_pos
        clicked_lbl_style = clicked_style if enable_btns else default_style

        self.set_btns_clickable(enable_btns)
        clicked_label.setStyleSheet(clicked_lbl_style)

        if prev_lbl_pos:
            previous_label = self.current_grid.itemAt(prev_lbl_pos).widget()
            previous_label.setStyleSheet(ElemLabelStyle.DEFAULT.value)

    def get_clicked_elem_pos(self) -> int | None:
        """Returns the index position of the clicked label in the currently
        displayed grid. If no label is selected, returns None.

        Returns:
        int or None: The index of the clicked label, or None if no label is selected."""
        total_elems = len(self.current_grid)
        for i in range(total_elems):
            label = self.current_grid.itemAt(i).widget()
            label_style = label.styleSheet()

            if ElemLabelStyle.CLICKED.value in label_style:
                return i

    def get_grid_widget(self, elem_type: ElementType) -> QWidget | QLabel:
        """Returns a QWidget containing a grid of elements.

        If there are no elements of the specified type, returns a QWidget with
        a single label.
        """
        if elem_type == ElementType.ENV:
            elems = flowizi.environment_list
        else:
            env = flowizi.environment_list[self.current_env]
            elems = getattr(env, elem_type.value)

        return self.view.get_grid(elem_type, elems)

    def remove_left_widget(self):
        """Removes the widget at index 0 of the splitter if the current view
        is "environments", or removes the currently displayed tab otherwise.

        This method is typically called after adding or deleting an element
        to ensure that the updated grid can be inserted into the appropriate
        position.
        """
        if self.current_view == ElementType.ENV:
            widget = self.view.splitter.widget(0)
        else:
            widget = self.tab_widget.widget(self.current_tab_pos)

        widget.deleteLater()

    def show_contained_elems(self):
        """Inserts a QTabWidget into the splitter at index 0.

        The QTabWidget contains tabs for each type of contained element,
        with each tab displaying a grid of instances corresponding to that
        element type within the current environment.
        """
        self.view.toolbar.addStretch()

        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.update_current_tab)
        self.tab_widget.setStyleSheet("""QTabBar::tab::selected{
                                        background-color: #f19600;
                                 }""")
        self.tab_widget.addTab(self.get_grid_widget(ElementType.WEBSITE), "Websites")
        self.tab_widget.addTab(self.get_grid_widget(ElementType.APP), "Apps")
        self.tab_widget.addTab(self.get_grid_widget(ElementType.FILE), "Files")
        font = QFont()
        font.setPointSize(12)
        self.tab_widget.tabBar().setFont(font)
        self.view.splitter.insertWidget(0, self.tab_widget)
        self.update_current_tab()

    def update_current_tab(self):
        """Updates the values of "current_tab_pos" and "current_view" based on
        the current view.

        This ensures that the application's state reflects the user's active
        tab/view.
        """
        self.current_tab_pos = self.tab_widget.currentIndex()

        if self.current_tab_pos == 0:
            self.current_view = ElementType.WEBSITE
        elif self.current_tab_pos == 1:
            self.current_view = ElementType.APP
        else:
            self.current_view = ElementType.FILE

        self.update_current_grid()

    def update_current_grid(self):
        """Updates the "current_grid" attribute to reflect the grid of the
        currently displayed view.
        """
        if self.current_view == ElementType.ENV:
            self.current_grid = self.view.splitter.widget(0).layout()
        elif self.current_view == ElementType.WEBSITE:
            self.current_grid = self.tab_widget.widget(0).layout()
        elif self.current_view == ElementType.APP:
            self.current_grid = self.tab_widget.widget(1).layout()
        else:
            self.current_grid = self.tab_widget.widget(2).layout()

    def back_btn_clicked(self):
        """Handles the back button click event by resetting the current view,
        tab position, and environment. This restores the application state to
        the initial view  or the state before double-clicking an environment.
        """
        self.current_view = ElementType.ENV
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
        if self.current_view == ElementType.ENV and elem_pos is not None:
            env_name = flowizi.environment_list[elem_pos].name
            Validations.delete_env_validation(env_name)
        elif self.current_tab_pos == 0 and elem_pos is not None:
            env = flowizi.environment_list[self.current_env]
            website_name = env.websites[elem_pos].name
            Validations.delete_elem_validation(env.name, ElementType.WEBSITE, website_name)
        elif self.current_tab_pos == 2 and elem_pos is not None:
            env = flowizi.environment_list[self.current_env]
            file_name = env.files[elem_pos].name
            Validations.delete_elem_validation(env.name, ElementType.FILE, file_name)
        else:
            env = flowizi.environment_list[self.current_env]
            app_name = env.applications[elem_pos].name
            Validations.delete_elem_validation(env.name, ElementType.APP, app_name)
        self.refresh_window()

    def create_btn_clicked(self):
        """Calls a method to create an element based on the current view"""
        if ((self.current_view == ElementType.APP and self.add_application())
           or (self.current_view == ElementType.FILE and self.add_file())):
            self.refresh_window()
        elif self.current_view == ElementType.WEBSITE or self.current_view == ElementType.ENV:
            singular_name = self.current_view.value[: len(self.current_view.value) - 1]
            title = f"Create {singular_name}"
            message = f"Enter the name of the new {singular_name}"
            self.get_input(title, message)

    def get_input(self, w_title, w_message):
        """Displays a message box prompting the user for input to create
        a website or environment.
        """
        msg_box = InputDialog()
        msg_box.set_window_title(w_title)
        msg_box.set_message(w_message)

        if msg_box.exec():
            self.validate_input(msg_box.get_text())

    def validate_input(self, input: str):
        """Validates if the user's input is valid."""
        if input == "":
            ErrorWindow.show("The name must have at least one character")
            return

        view = self.current_view
        res = self.add_env(input) if view == ElementType.ENV else self.add_web(input)
        if res:
            self.refresh_window()

    def add_env(self, env_name) -> bool:
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
            ErrorWindow.show(Feedback.ENV_ALREADY_EXISTS.value)

        return result

    def add_web(self, url) -> bool:
        """Attempts to create a website with the URL given by the user.

        Args:
            url (str): URL provided by the user for the website.

        Returns:
            bool: True if the site was successfully created, False otherwise.
        """
        env_name = flowizi.environment_list[self.current_env].name
        result = Validations.add_elem_validation(env_name, ElementType.WEBSITE, url)

        if not result == ResultType.SUCCESSFUL_OPERATION:
            if result == ResultType.INVALID_URL:
                message = Feedback.WEBSITE_INVALID_URL.value
            else:
                message = Feedback.WEBSITE_ALREADY_EXISTS.value

            ErrorWindow.show(message)

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
            result = Validations.add_elem_validation(env_name, ElementType.FILE, file_path)

            if not result == ResultType.SUCCESSFUL_OPERATION:
                ErrorWindow.show(Feedback.FILE_ALREADY_EXISTS.value)
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
            return self.app_result

    def handle_app_signal(self, value):
        self.app_result = value

    def handle_app_close_signal(self, value):
        self.user_app_close = value

    def refresh_sidebar(self, pos):
        """
        Updates the sidebar information based on the clicked label's position
        and current view.

        Args:
            pos (int): The index position of the clicked label.
        """
        self.view.sidebar_widget.show()
        if self.current_view == ElementType.ENV:
            self.refresh_env_sidebar(flowizi.environment_list[pos])
        else:
            env = flowizi.environment_list[self.current_env]
            elem = getattr(env, self.current_view.value)[pos]
            self.refresh_elem_sidebar(elem)

    def refresh_env_sidebar(self, env: Environment):
        """Refreshes the sidebar to display details of the specified environment.

        Args:
            env (Environment): The environment object whose details
                               are displayed in the sidebar.
        """
        self.view.sidebar_websites_label.show()
        self.view.sidebar_apps_label.show()
        self.view.sidebar_files_label.show()

        self.view.sidebar_name_label.setText(f"Name: {env.name}")
        self.view.sidebar_elem_info_label.setText(f"Screen recording: {env.record}")
        self.view.sidebar_websites_label.setText(f"Websites: {len(env.websites)}")
        self.view.sidebar_apps_label.setText(f"Apps: {len(env.applications)}")
        self.view.sidebar_files_label.setText(f"Files: {len(env.files)}")

    def refresh_elem_sidebar(self, elem: ContainedElement):
        """Refreshes the sidebar to display details of the specified element.

        Args:
            elem (ContainedElement): The ContainedElement object whose details
                               are displayed in the sidebar.
        """
        self.view.sidebar_websites_label.hide()
        self.view.sidebar_apps_label.hide()
        self.view.sidebar_files_label.hide()

        self.view.sidebar_name_label.setText(f"Name: {elem.name}")
        self.view.sidebar_elem_info_label.setText(f"URL: {elem.url}")

    def set_btns_clickable(self, clickable: bool):
        """Enable or disable the 'start' and 'delete' buttons.

        Sets the 'start' and 'delete' buttons to either enabled
        or disabled based on the value of the 'clickable' parameter.

        Args:
            clickable (bool): True to enable the buttons,
                              False to disable them.
        """
        self.view.start_btn.setEnabled(clickable)
        self.view.delete_btn.setEnabled(clickable)

    def connect_signals_to_slots(self):
        self.view.lbl_sig.connect(self.elem_clicked)
        self.view.lbl_dbl_click_sig.connect(self.elem_double_clicked)

        self.view.start_btn.clicked.connect(self.start_btn_clicked)
        self.view.create_btn.clicked.connect(self.create_btn_clicked)
        self.view.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.view.back_btn.clicked.connect(self.back_btn_clicked)
