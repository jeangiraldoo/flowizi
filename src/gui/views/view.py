import math
from typing import List
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QVBoxLayout,
                             QSplitter, QGridLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QEventLoop
from gui.views.custom_comps import (FileDialog, AppDialog, InputDialog,
                                    ClickableLabel, ErrorWindow)
from gui.views.ui_comps import Sidebar, Toolbar, TabBar
from flowizi import flowizi
from core.database.validations import Validations, ResType
from core.text_res.feedback import Feedback
from core.elements.element import Element, Environment, ElemType
from core.elements.contained_element import ContainedElement
from gui.views.styles import ElemLabelStyle


class MainWindow(QMainWindow):
    lbl_sig = pyqtSignal(int)
    lbl_dbl_click_sig = pyqtSignal(int)
    input_dialog_sig = pyqtSignal(str)
    AppDialog_sig = pyqtSignal(bool)
    tab_changed_sig = pyqtSignal(ElemType)

    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.setWindowTitle("Flowizi")
        self.setWindowIcon(QIcon("logo.svg"))
        self.setStyleSheet("background-color: #30302f;")
        self._initUI()

    def _initUI(self):
        """
        Initializes the main UI layout and its components.
        """
        root_widget = QWidget()
        root_layout = QVBoxLayout()
        root_widget.setLayout(root_layout)
        self.setCentralWidget(root_widget)
        self.splitter = QSplitter(Qt.Horizontal)

        self.setup_grid()
        self.toolbar = Toolbar()
        self.sidebar_widget = Sidebar()
        self.tab_widget = TabBar()
        self.tab_widget.addTab(QWidget(), "Websites")
        self.tab_widget.addTab(QWidget(), "Apps")
        self.tab_widget.addTab(QWidget(), "Files")
        self.tab_widget.widget(0).setLayout(QVBoxLayout())
        self.tab_widget.widget(1).setLayout(QVBoxLayout())
        self.tab_widget.widget(2).setLayout(QVBoxLayout())
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.splitter.addWidget(self.sidebar_widget)
        self.splitter.addWidget(self.tab_widget)
        self.tab_widget.hide()

        root_layout.addLayout(self.toolbar)
        root_layout.addWidget(self.splitter)
        self.set_btns_clickable(False)

    def set_btns_clickable(self, clickable: bool):
        """
        Enable or disable buttons to allow or prevent the user from using them.

        Args:
            clickable (bool): True to enable the buttons, False otherwise.
        """
        self.toolbar.start_btn.setEnabled(clickable)
        self.toolbar.delete_btn.setEnabled(clickable)

    def create_elem_input(self, elem_type: ElemType, current_env: int):
        """
        Prompts the user for input through a dialog to create an element.

        Args:
            elem_type (ElemType): Element type.
            current_env (int): Current environment position.
        """
        singular_name = elem_type.value[: len(elem_type.value) - 1]
        title = f"Create {singular_name}"
        msg = f"Enter the name of the new {singular_name}"

        msg_box = InputDialog(title, msg)

        if msg_box.exec():
            self.update_element_widget(elem_type, current_env)
            self.input_dialog_sig.emit(msg_box.get_text())

    def create_elem_dialog(self, elem_type: ElemType, current_env: int):
        """
        Creates an element without keyboard input, using a dialog window.

        Args:
            elem_type(ElemType): Element type.
            current_env (int): Current environment position.
        """
        if elem_type == ElemType.APP:
            res = self._launch_AppDialog(current_env)
        else:
            res = self._launch_FileDialog(current_env)

        if res:
            self.update_element_widget(elem_type, current_env)

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

    def get_grid(self, elem_type: ElemType, elem_list: List[Element]) -> QLabel | QWidget:
        """Returns a widget containing a grid layout if "elem_list" has
        elements, or a QLabel if "elem_list" is empty.

        Args:
            elem_type (ElemType): The type of elements in the grid.
            elem_list (List[Element]): List of elements to display in the grid.

        Returns:
            QLabel | QWidget: A QWidget with a grid layout if elements
            exist, or a QLabel indicating an empty grid otherwise.
        """
        if len(elem_list):
            return self.generate_grid(elem_list)
        else:
            return self.generate_empty_grid_label(elem_type)

    def generate_grid(self, element_list: List[Element]) -> QWidget:
        """Returns a QWidget containing a grid layout with labels.

        Each element in "element_list" is represented by a label in the grid,
        arranged with a specified number of items per row. The labels display
        the element's name and have connected mouse events for interaction.

        Args:
            element_list (List[Element]): List of elements to display.

        Returns:
            QWidget: A QWidget containing the grid of clickable labels, each
            label positioned according to its order in "element_list".
        """
        grid = QGridLayout()
        grid.setSpacing(30)

        grid_widget = QWidget()
        grid_widget.setLayout(grid)

        num_elems_row = 4
        total_envs = len(element_list)
        total_rows = math.ceil(total_envs/num_elems_row)
        current_env = 0

        for row in range(total_rows):
            grid.setRowStretch(row, 1)
            for column in range(num_elems_row):
                label = ClickableLabel(f"{element_list[current_env].name}")
                grid.addWidget(label, row, column)
                label.set_pos(grid.indexOf(label))
                label.mousePressEvent = self._send_lbl_sig(label.pos)
                label.lbl_dbl_click_sig.connect(self._send_lbl_dbl_click_sig)
                current_env += 1

                if current_env == total_envs:
                    break

        return grid_widget

    def setup_grid(self):
        """
        Sets up the QWidget that will hold all of the environment labels.
        """
        self.grid_widget = QWidget()
        self.grid_widget.setLayout(QVBoxLayout())
        self.grid_widget.layout().addWidget(self.get_grid(ElemType.ENV, flowizi.environment_list))
        self.splitter.addWidget(self.grid_widget)

    def generate_empty_grid_label(self, elem_type: ElemType) -> QLabel:
        """
        Returns a label displaying that there are no elements of the given type.

        Args:
            elem_type (ElemType): Type of element to mention in the label.

        Returns:
            QLabel: A label prompting the user to create a new element.
        """
        label_text = f"No {elem_type.value} have been created yet. Use the 'Create' button to create one"
        label = QLabel(label_text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 30px; padding: 10px;")

        return label

    def update_sidebar(self, current_view: ElemType, current_env: int, pos: int):
        """
        Displays element information in the sidebar labels.

        Args:
            current_view (ElemType): Current view being displayed.
            current_env (int): Current environment position.
            pos (int): The index position of the clicked label.
        """
        self.sidebar_widget.show()
        if current_view == ElemType.ENV:
            self._update_env_sidebar_widget(flowizi.environment_list[pos])
        else:
            env = flowizi.environment_list[current_env]
            elem = getattr(env, current_view.value)[pos]
            self._update_elem_sidebar_widget(elem)

    def _update_env_sidebar_widget(self, env: Environment):
        """
        Displays environment information in the sidebar labels.

        Args:
            env (Environment): The environment to display.
        """
        self.sidebar_widget.websites_label.show()
        self.sidebar_widget.apps_label.show()
        self.sidebar_widget.files_label.show()

        self.sidebar_widget.name_label.setText(f"Name: {env.name}")
        self.sidebar_widget.elem_info_label.setText(f"Screen recording: {env.record}")
        self.sidebar_widget.websites_label.setText(f"Websites: {len(env.websites)}")
        self.sidebar_widget.apps_label.setText(f"Apps: {len(env.applications)}")
        self.sidebar_widget.files_label.setText(f"Files: {len(env.files)}")

    def _update_elem_sidebar_widget(self, elem: ContainedElement):
        """
        Displays element information in the sidebar labels.

        Args:
            elem (ContainedElement): The ContainedElement to display.
        """
        self.sidebar_widget.websites_label.hide()
        self.sidebar_widget.apps_label.hide()
        self.sidebar_widget.files_label.hide()

        self.sidebar_widget.name_label.setText(f"Name: {elem.name}")
        self.sidebar_widget.elem_info_label.setText(f"URL: {elem.url}")

    def _update_toolbar(self, current_view: ElemType):
        """
        Updates button visibility based on the app's state.

        Called after actions like adding a website, it disables buttons
        requiring a selected label to prevent unintended interactions.

        Args:
            current_view (ElemType): Current view displayed.
        """
        self.set_btns_clickable(False)

        if current_view == ElemType.ENV:
            self.toolbar.start_btn.hide()
            self.toolbar.back_btn.show()
        else:
            self.toolbar.start_btn.show()
            self.toolbar.back_btn.hide()

    def change_elem_view(self, current_view: ElemType, current_env: int):
        """
        Switches the displayed element view and updates the UI.

        Transitions the application from one element type to another, adjusting
        the grid, toolbar, and sidebar visibility based on the current view.

        Args:
            current_view (ElemType): The view being transitioned from.
            current_env (int): The position of the active environment in the
                               current view.
        """
        self.clear_grid(current_view)
        self.sidebar_widget.hide()
        self._change_sidebar_pos(current_view)
        self._update_toolbar(current_view)
        if current_view == ElemType.ENV:
            self.grid_widget.hide()
            self.tab_widget.show()
            self.tab_widget.setCurrentIndex(0)
            self._show_contained_elems(current_env)
        else:
            self.grid_widget.show()
            self.tab_widget.hide()
            self._show_envs(current_view)

    def update_element_widget(self, current_view: ElemType, current_env: int):
        """
        Replaces the displayed widget with an updated version.

        Called after adding or deleting an element to refresh the grid.

        Args:
            current_view (ElemType): Current view displayed.
            current_env (int): Active environment position.
        """
        flowizi.update_environments()
        self.sidebar_widget.hide()
        self.clear_grid(current_view)

        if current_view == ElemType.ENV:
            self._show_envs(current_view)
        else:
            self._show_contained_elems(current_env)

    def clear_grid(self, current_view: ElemType):
        """
        Prepares the UI for updating by removing the displayed widget.

        Args:
            current_view (ElemType): The currently displayed view.
        """
        if current_view == ElemType.ENV:
            self._clear_grid_widget()
        else:
            self._clear_tab_widget()

    def _clear_grid_widget(self):
        """
        Deletes the widget from the grid layout.
        """
        widget = self.grid_widget.layout().itemAt(0).widget()
        self.grid_widget.layout().removeWidget(widget)
        widget.deleteLater()

    def _clear_tab_widget(self):
        """
        Deletes the widgets in each tab's layout.
        """
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            layout = tab.layout()
            if layout:
                item = layout.takeAt(0)
                widget = item.widget()
                widget.deleteLater()

    def _show_envs(self, current_view: ElemType):
        """
        Adds a widget with environment labels to the grid layout.

        Args:
            current_view (ElemType): Current view displayed.
        """
        new_elements = flowizi.environment_list
        new_grid = self.get_grid(current_view, new_elements)
        self.grid_widget.layout().addWidget(new_grid)

    def _show_contained_elems(self, current_env: int):
        """
        Adds a widget with contained element labels to each tab layout.

        Args:
            current_env (int): Active environment position.
        """
        self.toolbar.addStretch()
        env = flowizi.environment_list[current_env]
        env_webs = getattr(env, ElemType.WEB.value)
        env_apps = getattr(env, ElemType.APP.value)
        env_files = getattr(env, ElemType.FILE.value)

        web_widget = self.get_grid(ElemType.WEB, env_webs)
        app_widget = self.get_grid(ElemType.APP, env_apps)
        file_widget = self.get_grid(ElemType.FILE, env_files)
        widgets = [web_widget, app_widget, file_widget]

        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            layout = tab.layout()
            layout.addWidget(widgets[i])

        self.tab_changed()

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

    def _send_lbl_dbl_click_sig(self, pos: int):
        """Emits a signal with the position of a label that was double-clicked.

        Args:
            pos (int): The position of the label that was double-clicked.
        """
        self.lbl_dbl_click_sig.emit(pos)

    def _send_lbl_sig(self, pos: int):
        """Creates a mouse event handler for a label and returns it.

        The returned handler emits a signal with the label's position when
        clicked, allowing the label's position to be used by other components.

        Args:
            pos (int): The position of the label within the grid.

        Returns:
            func: Emits "lbl_sig" with the label's position when clicked.
        """
        def event(event):
            self.lbl_sig.emit(pos)
        return event

    def tab_changed(self):
        index = self.tab_widget.currentIndex()
        if index == 0:
            current_view = ElemType.WEB
        elif index == 1:
            current_view = ElemType.APP
        else:
            current_view = ElemType.FILE
        self.tab_changed_sig.emit(current_view)

    def style_clicked_elem(self, current_grid: QWidget, lbl_pos: int):
        """
        Updates styles for the clicked label and the previously clicked label.

        Applies the CLICKED or DEFAULT style based on the label's position and
        enables/disables associated buttons accordingly.

        Args:
            current_grid (QWidget): The widget in the focused splitter's position.
            lbl_pos (int): The position of the clicked label in the grid.
        """
        clicked_style = ElemLabelStyle.CLICKED.value
        default_style = ElemLabelStyle.DEFAULT.value
        prev_lbl_pos: int | None = self.get_clicked_elem_pos(current_grid)
        clicked_label = current_grid.layout().itemAt(lbl_pos).widget()

        enable_btns = prev_lbl_pos != lbl_pos
        clicked_lbl_style = clicked_style if enable_btns else default_style

        self.set_btns_clickable(enable_btns)
        clicked_label.setStyleSheet(clicked_lbl_style)

        if prev_lbl_pos is not None:
            previous_label = current_grid.layout().itemAt(prev_lbl_pos).widget()
            previous_label.setStyleSheet(ElemLabelStyle.DEFAULT.value)

    def get_clicked_elem_pos(self, current_grid: QWidget) -> int | None:
        """
        Gets the index of the currently clicked label.

        Args:
            current_grid (QWidget): The widget in the focused splitter's position.

        Returns:
            int | None: Index of the clicked label, or None if no label is selected.
        """
        total_elems = current_grid.layout().count()
        for i in range(total_elems):
            label = current_grid.layout().itemAt(i).widget()
            label_style = label.styleSheet()

            if ElemLabelStyle.CLICKED.value in label_style:
                return i

    def handle_app_signal(self, value):
        self.app_result = value

    def handle_app_close_signal(self, value):
        self.user_app_close = value

    def show_error_msg(self, msg):
        ErrorWindow.show(msg)
