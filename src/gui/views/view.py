from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal, QEventLoop
from flowizi import flowizi
from core.database.validations import Validations, ResType
from core.text_res.feedback import Feedback
from core.elements.element import ElemType
from gui.views.states import GuiStateMachine
from gui.views.components.ui import SidebarWidget, ToolbarWidget, TabWidget, ElemGridWidget
from gui.views.components.dialogs import (InputDialog, FileDialog, AppDialog,
                                          ErrorWindow)


class View(QMainWindow):
    lbl_sig = Signal(int)
    lbl_dbl_click_sig = Signal(int)
    input_dialog_sig = Signal(str)
    AppDialog_sig = Signal(bool)
    tab_changed_sig = Signal(ElemType)

    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.setWindowTitle("Flowizi")
        self.setWindowIcon(QIcon("logo.svg"))
        self.setStyleSheet("background-color: hsl(60, 1%, 19%)")
        self._initUI()
        self.view_state = GuiStateMachine(self.grid_widget)

    def _initUI(self):
        """
        Initializes the main UI layout and its components.
        """
        root_widget = QWidget()
        root_layout = QVBoxLayout()
        root_widget.setLayout(root_layout)
        self.setCentralWidget(root_widget)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.grid_widget = ElemGridWidget()
        self.grid_widget.update(ElemType.ENV, flowizi.environment_list)
        self.toolbar = ToolbarWidget()
        self.sidebar_widget = SidebarWidget()
        self.tab_widget = TabWidget()
        self.splitter.addWidget(self.grid_widget)
        self.splitter.addWidget(self.sidebar_widget)
        self.splitter.addWidget(self.tab_widget)
        self.tab_widget.hide()
        self.connect_signals_to_slots()

        root_layout.addLayout(self.toolbar)
        root_layout.addWidget(self.splitter)
        self.toolbar.set_btns_clickable(False)

    def launch_create_elem_dialog(self):
        """
        Launches a dialog to create an element, chosen based on the current view.

        This method determines the appropriate dialog to display depending on the
        current view.
        """
        env_pos = self.view_state.get_current_env_pos()
        if self.view_state.state == ElemType.WEB or self.view_state.state == ElemType.ENV:
            self._launch_input_dialog(env_pos)
        else:
            self._launch_choice_dialog(env_pos)


    def _launch_input_dialog(self, current_env: int):
        """
        Prompts the user for input through a dialog to create an element.

        Args:
            elem_type (ElemType): Element type.
            current_env (int): Current environment position.
        """
        view_value = self.view_state.state
        singular_name = view_value.value[: len(view_value.value) - 1]
        title = f"Create {singular_name}"
        msg = f"Enter the name of the new {singular_name}"

        msg_box = InputDialog(title, msg)

        if msg_box.exec():
            self.update_element_widget(current_env)
            self.input_dialog_sig.emit(msg_box.get_text())

    def _launch_choice_dialog(self, current_env: int):
        """
        Creates an element without keyboard input, using a dialog window.

        Args:
            elem_type(ElemType): Element type.
            current_env (int): Current environment position.
        """
        if self.view_state.state == ElemType.APP:
            res = self._launch_AppDialog(current_env)
        else:
            res = self._launch_FileDialog(current_env)

        if res:
            self.update_element_widget(current_env)

    def _launch_AppDialog(self, current_env: int) -> bool:
        """
        Launches an AppDialog so that the user can choose the app to add.

        Args:
            current_env (int): Current environment position.

        Returns:
            bool: True if the app was successfully created, False otherwise.
        """
        app_window = AppDialog(current_env)
        self.loop = QEventLoop()
        app_window.result_signal.connect(self.handle_app_signal)
        app_window.user_close_signal.connect(self.handle_app_close_signal)
        app_window.exec_()

        if not self.user_app_close:
            return self.app_result

    def _launch_FileDialog(self, current_env: int) -> ResType:
        """
        Launches a FileDialog so that the user can choose the file to add.

        Args:
            current_env (int): Current environment position.

        Returns:
            bool: True if the file was successfully created, False otherwise.
        """
        dialog = FileDialog()
        if dialog.exec_():
            file_path = dialog.get_selected_file()
            env_name = flowizi.environment_list[current_env].name
            result = Validations.add_elem_validation(env_name, ElemType.FILE, file_path)

            if not result == ResType.SUCCESS:
                ErrorWindow.show(Feedback.FILE_ALREADY_EXISTS.value)
            return result

    def update_sidebar(self, current_view: ElemType, current_env: int, pos: int):
        """
        Displays element information in the sidebar labels.

        Args:
            current_view (ElemType): Current view being displayed.
            current_env (int): Current environment position.
            pos (int): The index position of the clicked label.
        """
        env = flowizi.environment_list[current_env]
        if current_view == ElemType.ENV:
            elem = env
        else:
            elem = getattr(env, current_view.value)[pos]
        self.sidebar_widget.update(current_view, elem)

    def change_elem_view(self):
        """
        Switches the displayed element view and updates the UI.

        Transitions the application from one element type to another, adjusting
        the grid, toolbar, and sidebar visibility based on the current view.
        """
        self.sidebar_widget.hide()
        self._change_sidebar_pos(self.view_state.state)
        self.toolbar.update(self.view_state.state)

        if self.view_state.state == ElemType.ENV:
            self._change_view_to_elems(self.view_state.get_current_env_pos())
        else:
            self._change_view_to_env()

    def _change_view_to_env(self):
        """
        Displays a grid with environments.
        """
        self.tab_widget.hide()
        self.grid_widget.show()
        self.grid_widget.update(ElemType.ENV, flowizi.environment_list)
        self.view_state.transition_state(ElemType.ENV, self.grid_widget)
        self.view_state.update_current_env_pos(None)

    def _change_view_to_elems(self, current_env: int):
        """
        Displays a grid for elements of the specified environment.

        Args:
            current_env (int): Position of environment whose elements will be shown.
        """
        self.grid_widget.hide()
        self.tab_widget.show()
        self._show_contained_elems(current_env)

        if self.tab_widget.currentIndex() != 0:
            self.tab_widget.setCurrentIndex(0)
        else:
            self.tab_widget.currentChanged.emit(0)

    def update_element_widget(self, current_env: int):
        """
        Replaces the displayed widget with an updated version.

        Called after adding or deleting an element to refresh the grid.

        Args:
            current_view (ElemType): Current view displayed.
            current_env (int): Active environment position.
        """
        flowizi.update_environments()
        self.sidebar_widget.hide()

        if self.view_state.state == ElemType.ENV:
            self.grid_widget.update(ElemType.ENV, flowizi.environment_list)
        else:
            self._show_contained_elems(current_env)

    def _show_contained_elems(self, current_env: int):
        """
        Adds a widget with contained element labels to each tab layout.

        Args:
            current_env (int): Active environment position.
        """
        env = flowizi.environment_list[current_env]
        web_dic = {ElemType.WEB: getattr(env, ElemType.WEB.value)}
        app_dic = {ElemType.APP: getattr(env, ElemType.APP.value)}
        file_dic = {ElemType.FILE: getattr(env, ElemType.FILE.value)}

        elem_list = [web_dic, app_dic, file_dic]

        for i in range(self.tab_widget.count()):
            current_dict = elem_list[i]
            current_elem, = current_dict.keys()
            tab = self.tab_widget.widget(i)
            tab.update(current_elem, current_dict[current_elem])

    def _change_sidebar_pos(self, current_view: ElemType):
        """
        Moves the sidebar to the right of the currently displayed grid.

        The sidebar's position is adjusted based on the displayed grid,
        ensuring it always appears to the right of the grid, regardless
        of the current view.

        Args:
            current_view (ElemType): The view currently being displayed.
        """
        self.sidebar_widget.setParent(None)
        if current_view == ElemType.ENV:
            self.splitter.insertWidget(3, self.sidebar_widget)
        else:
            self.splitter.insertWidget(1, self.sidebar_widget)

    def tab_changed(self):
        index = self.tab_widget.currentIndex()
        if index == 0:
            new_state = ElemType.WEB
            widget = self.tab_widget.widget(0)
        elif index == 1:
            new_state = ElemType.APP
            widget = self.tab_widget.widget(1)
        else:
            new_state = ElemType.FILE
            widget = self.tab_widget.widget(2)

        self.view_state.transition_state(new_state, widget)

    def _send_lbl_dbl_click_sig(self, pos: int):
        """Emits a signal with the position of a label that was double-clicked.

        Args:
            pos (int): The position of the label that was double-clicked.
        """
        self.lbl_dbl_click_sig.emit(pos)

    def _send_lbl_sig(self, lbl_highlighted, pos: int):
        """Creates a mouse event handler for a label and returns it.

        The returned handler emits a signal with the label's position when
        clicked, allowing the label's position to be used by other components.

        Args:
            pos (int): The position of the label within the grid.

        Returns:
            func: Emits "lbl_sig" with the label's position when clicked.
        """
        self.toolbar.set_btns_clickable(lbl_highlighted)
        self.lbl_sig.emit(pos)

    def handle_app_signal(self, value):
        self.app_result = value

    def handle_app_close_signal(self, value):
        self.user_app_close = value

    def connect_signals_to_slots(self):
        """Connects component signals to their corresponding slots."""
        self.grid_widget.lbl_sig.connect(self._send_lbl_sig)
        self.grid_widget.lbl_dbl_click_sig.connect(self._send_lbl_dbl_click_sig)
        self.tab_widget.lbl_sig.connect(self._send_lbl_sig)
        self.tab_widget.currentChanged.connect(self.tab_changed)

    def show_error_msg(self, msg):
        ErrorWindow.show(msg)
