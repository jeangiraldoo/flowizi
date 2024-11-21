import sys
from PyQt5.QtWidgets import QApplication
from gui.views.view import MainWindow
from core.elements.element import ElemType
from core.text_res.feedback import Feedback
from flowizi import flowizi
from core.database.validations import Validations, ResType


class Controller:
    def main(self):
        app = QApplication(sys.argv)
        self.view = MainWindow()
        self.view.show()
        self.update_current_view(ElemType.ENV)
        self.current_env = None
        self.connect_signals_to_slots()

        sys.exit(app.exec_())

    def elem_clicked(self, elem_pos: int):
        """
        Handles label click by updating the sidebar and applying the CLICKED
        style to the selected element, resetting the previous one to DEFAULT.

        Args:
            elem_pos (int): Clicked label's position.
        """
        if self.current_view == ElemType.ENV:
            self.current_env = elem_pos

        self.view.update_sidebar(self.current_view, self.current_env, elem_pos)
        self.view.style_clicked_elem(self.current_grid, elem_pos)

    def elem_double_clicked(self, pos: int):
        """
        Displays the elements in an environment after double-clicking it.

        Args:
            pos (int): Position of the clicked environment.
        """
        if self.current_view == ElemType.ENV:
            self.view.change_elem_view(self.current_view, self.current_env)
            self.update_current_view(ElemType.WEB)

    def update_current_view(self, current_view: ElemType):
        """
        Updates the "current_view" to align with the user's active view.

        Args:
            current_view (ElemType): The element type of the currently displayed grid.
        """
        self.current_view = current_view
        self.update_current_grid(current_view)

    def update_current_grid(self, current_view: ElemType):
        """
        Updates the "current_grid" attribute based on the active view.

        Args:
            current_view (ElemType): The element type of the currently displayed grid.
        """
        if current_view == ElemType.ENV:
            self.current_grid = self.view.grid_widget.layout().itemAt(0).widget()
        elif current_view == ElemType.WEB:
            self.current_grid = self.view.tab_widget.widget(0).layout().itemAt(0).widget()
        elif current_view == ElemType.APP:
            self.current_grid = self.view.tab_widget.widget(1).layout().itemAt(0).widget()
        else:
            self.current_grid = self.view.tab_widget.widget(2).layout().itemAt(0).widget()

    def back_btn_clicked(self):
        """
        Resets the current_view/grid attributes and displays environments.
        """
        self.view.change_elem_view(self.current_view, self.current_env)
        self.update_current_view(ElemType.ENV)
        self.current_env = None

    def start_btn_clicked(self):
        """
        Opens the clicked environment's elements after using the start button.
        """
        pos = self.get_clicked_elem_pos(self.current_grid)
        if pos is not None:
            flowizi.environment_list[pos].start()

    def delete_btn_clicked(self):
        """
        Deletes the element associated with the clicked label.
        """
        elem_pos = self.view.get_clicked_elem_pos(self.current_grid)
        if self.current_view == ElemType.ENV and elem_pos is not None:
            self.delete_env(elem_pos)
        else:
            self.delete_elem(self.current_view, elem_pos)

        self.view.update_element_widget(self.current_view, self.current_env)
        self.update_current_grid(self.current_view)

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
            elem_type (ElemType): The type of the element.
            elem_pos (int): The index or position of the element to delete.
        """
        env = flowizi.environment_list[self.current_env]
        env_elem_list = getattr(env, elem_type.value)
        elem_name = env_elem_list[elem_pos].name

        Validations.delete_elem_validation(env.name, elem_type, elem_name)

    def create_btn_clicked(self):
        """
        Calls a method to create an element based on the current view.
        """
        if self.current_view == ElemType.WEB or self.current_view == ElemType.ENV:
            self.view.create_elem_input(self.current_view, self.current_env)
        else:
            self.view.create_elem_dialog(self.current_view, self.current_env)
        self.update_current_grid(self.current_view)

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

    def finish_validate_input(self, res: ResType, msg: str):
        """
        Completes validation by either showing an error or updating the grid.
        """
        if res != ResType.ENV_CREATED and res != ResType.SUCCESS:
            self.view.show_error_msg(msg)
        else:
            self.view.update_element_widget(self.current_view, self.current_env)

    def connect_signals_to_slots(self):
        """
        Connects view signals to their corresponding slots.
        """
        self.view.lbl_sig.connect(self.elem_clicked)
        self.view.lbl_dbl_click_sig.connect(self.elem_double_clicked)
        self.view.input_dialog_sig.connect(self.validate_input)
        self.view.tab_changed_sig.connect(self.update_current_view)

        self.view.toolbar.start_btn.clicked.connect(self.start_btn_clicked)
        self.view.toolbar.create_btn.clicked.connect(self.create_btn_clicked)
        self.view.toolbar.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.view.toolbar.back_btn.clicked.connect(self.back_btn_clicked)
