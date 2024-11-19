import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from gui.views.view import MainWindow
from gui.views.styles import ElemLabelStyle
from core.elements.element import ElemType
from core.text_res.feedback import Feedback
from flowizi import flowizi
from core.database.validations import Validations, ResType


class Controller:
    def main(self):
        app = QApplication(sys.argv)
        self.view = MainWindow()
        self.view.show()
        self.current_view = ElemType.ENV
        self.current_env = None
        self.update_current_grid()
        self.current_tab_pos = None
        self.selected_app = None

        self.connect_signals_to_slots()
        self.view.set_btns_clickable(False)

        sys.exit(app.exec_())

    def refresh_window(self):
        """
        Refreshes the UI to reflect changes in the app's state.

        This method ensures the UI stays in sync with the application's state
        after actions such as adding, selecting, or deleting an element.
        """
        self.refresh_left_widget()
        self.view.update_toolbar(self.current_view)
        self.view.sidebar_widget.hide()

    def refresh_left_widget(self):
        """
        Refreshes the grid by replacing it with an updated version.

        Called after creating or deleting an element to ensure the screen
        reflects the latest state of the application.
        """
        flowizi.update_environments()
        self.view.remove_left_widget(self.current_view)

        if self.current_view == ElemType.ENV:
            updated_grid = self.get_grid_widget(ElemType.ENV)
            self.view.splitter.insertWidget(0, updated_grid)
        else:
            updated_grid = self.get_grid_widget(self.current_view)
            self.tab_widget.insertTab(self.current_tab_pos, updated_grid, self.tab_widget.tabText(self.current_tab_pos))
            self.tab_widget.setCurrentWidget(updated_grid)

        self.update_current_grid()

    def elem_clicked(self, pos: int):
        """Slot triggered when a label is clicked.

        Updates the sidebar with information about the clicked element and
        sets the CLICKED style to it, while setting the DEFAULT style to any
        previously selected elements.
        """
        if self.current_view == ElemType.ENV:
            self.current_env = pos
        self.view.update_sidebar(self.current_view, self.current_env, pos)
        self.style_clicked_elem(pos)

    def elem_double_clicked(self, pos: int):
        """
        Displays the elements in an environment after double-clicking it.

        Args:
            pos (int): Position of the clicked environment.
        """
        if self.current_view == ElemType.ENV:
            self.view.sidebar_widget.hide()
            self.view.remove_left_widget(self.current_view)
            self.view.show_contained_elems(self.current_env)
            self.view.update_toolbar(self.current_view)

    def style_clicked_elem(self, lbl_pos: int):
        """
        Updates the style of the clicked label in the grid.

        Determines whether the clicked label should use the DEFAULT or
        CLICKED style and enables or disables associated buttons based
        on whether its position matches the previously clicked label.

        Args:
            lbl_pos (int): Position of the clicked label in the grid.
        """
        clicked_style = ElemLabelStyle.CLICKED.value
        default_style = ElemLabelStyle.DEFAULT.value
        prev_lbl_pos: int | None = self.get_clicked_elem_pos()
        clicked_label = self.current_grid.itemAt(lbl_pos).widget()

        enable_btns = prev_lbl_pos != lbl_pos
        clicked_lbl_style = clicked_style if enable_btns else default_style

        self.view.set_btns_clickable(enable_btns)
        clicked_label.setStyleSheet(clicked_lbl_style)

        if prev_lbl_pos is not None:
            previous_label = self.current_grid.itemAt(prev_lbl_pos).widget()
            previous_label.setStyleSheet(ElemLabelStyle.DEFAULT.value)

    def get_clicked_elem_pos(self) -> int | None:
        """
        Returns the index position of the currently clicked label.

        Returns:
            int | None: The index of the clicked label, or None if no label is
                        selected.
        """
        total_elems = len(self.current_grid)
        for i in range(total_elems):
            label = self.current_grid.itemAt(i).widget()
            label_style = label.styleSheet()

            if ElemLabelStyle.CLICKED.value in label_style:
                return i

    def get_grid_widget(self, elem_type: ElemType) -> QWidget | QLabel:
        """
        Returns a new grid or empty label.

        Args:
            elem_type (ElemType): Element type.

        Returns:
            QWidget | QLabel: A widget containing a grid or an empty label if
                              there are no elements of the specified type.
        """
        if elem_type == ElemType.ENV:
            elems = flowizi.environment_list
        else:
            env = flowizi.environment_list[self.current_env]
            elems = getattr(env, elem_type.value)

        return self.view.get_grid(elem_type, elems)

    def update_current_tab(self):
        """
        Updates the values of "current_tab_pos" and "current_view" based on
        the current view.

        This ensures that the application's state reflects the user's active
        tab/view.
        """
        self.current_tab_pos = self.view.tab_widget.currentIndex()

        if self.current_tab_pos == 0:
            self.current_view = ElemType.WEB
        elif self.current_tab_pos == 1:
            self.current_view = ElemType.APP
        else:
            self.current_view = ElemType.FILE

        self.update_current_grid()

    def update_current_grid(self):
        """
        Updates the "current_grid" attribute based on the App's state.
        """
        if self.current_view == ElemType.ENV:
            self.current_grid = self.view.splitter.widget(0).layout()
        elif self.current_view == ElemType.WEB:
            self.current_grid = self.view.tab_widget.widget(0).layout()
        elif self.current_view == ElemType.APP:
            self.current_grid = self.view.tab_widget.widget(1).layout()
        else:
            self.current_grid = self.view.tab_widget.widget(2).layout()

    def back_btn_clicked(self):
        """
        Slot triggered when the back button is clicked.

        Resets the current view, tab position, and environment. This restores
        the application state to the initial view  or the state before
        double-clicking an environment.
        """
        self.current_view = ElemType.ENV
        self.current_tab_pos = None
        self.current_env = None
        self.refresh_window()

    def start_btn_clicked(self):
        """
        Opens the clicked environment's elements after using the start button.
        """
        pos = self.get_clicked_elem_pos()
        if pos is not None:
            flowizi.environment_list[pos].start()

    def delete_btn_clicked(self):
        """Deletes the element associated with the clicked label"""
        elem_pos = self.get_clicked_elem_pos()
        if self.current_view == ElemType.ENV and elem_pos is not None:
            self.delete_env(elem_pos)
        else:
            self.delete_elem(self.current_view, elem_pos)

        self.refresh_window()

    def delete_env(self, env_pos: int):
        """
        Deletes the environment corresponding to the clicked label's position.

        Args:
            env_pos (int): Index of the environment to delete.
        """
        env_name = flowizi.environment_list[env_pos].name
        Validations.delete_env_validation(env_name)

    def delete_elem(self, elem_type: ElemType, elem_pos: int):
        """
        Deletes the element corresponding to the clicked label's position.

        Args:
            elem_type (ElemType): The type of the element (e.g., WEB, APP,
                                  or FILE).
            elem_pos (int): The index or position of the element to delete.
        """
        env = flowizi.environment_list[self.current_env]
        env_elem_list = getattr(env, elem_type.value)
        elem_name = env_elem_list[elem_pos].name

        Validations.delete_elem_validation(env.name, elem_type, elem_name)

    def create_btn_clicked(self):
        """Calls a method to create an element based on the current view."""
        if self.current_view == ElemType.WEB or self.current_view == ElemType.ENV:
            self.view.create_elem_input(self.current_view)
        else:
            self.view.create_elem_dialog(self.current_view, self.current_env)

    def validate_input(self, input: str):
        """
        Validates if the user's input is valid.

        Args:
            input (str): String given by the user.
        """
        if input == "":
            res, msg = "", "The name must have at least one character"
        elif self.current_view == ElemType.ENV:
            res, msg = self.validate_env_input(input)
        else:
            res, msg = self.validate_web_input(input)

        self.finish_validate_input(res, msg)

    def validate_env_input(self, input: str) -> str:
        """
        Validates if the user's input is a valid environment name.

        Args:
            input (str): User input.
        """
        res = Validations.add_env_validation(input)
        msg = Feedback.ENV_ALREADY_EXISTS.value

        return res, msg

    def validate_web_input(self, input: str) -> str:
        """
        Validates if the user's input is a valid web URL.

        Args:
            input (str): User input.
        """
        env_name = flowizi.environment_list[self.current_env].name
        inv_url_msg = Feedback.WEBSITE_INVALID_URL.value
        web_already_exist = Feedback.WEBSITE_ALREADY_EXISTS.value
        res = Validations.add_elem_validation(env_name, ElemType.WEB, input)
        msg = inv_url_msg if res == ResType.INVALID_URL else web_already_exist

        return res, msg

    def finish_validate_input(self, res, msg):
        if res != ResType.ENV_CREATED and res != ResType.SUCCESS:
            self.view.show_error_msg(msg)
        else:
            self.refresh_window()

    def connect_signals_to_slots(self):
        self.view.lbl_sig.connect(self.elem_clicked)
        self.view.lbl_dbl_click_sig.connect(self.elem_double_clicked)
        self.view.input_dialog_sig.connect(self.validate_input)
        self.view.elem_dialog_created_sig.connect(self.refresh_window)
        self.view.tab_changed_sig.connect(self.update_current_tab)

        self.view.toolbar.start_btn.clicked.connect(self.start_btn_clicked)
        self.view.toolbar.create_btn.clicked.connect(self.create_btn_clicked)
        self.view.toolbar.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.view.toolbar.back_btn.clicked.connect(self.back_btn_clicked)
