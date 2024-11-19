import math
from typing import List
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QVBoxLayout,
                             QSplitter, QPushButton, QHBoxLayout, QGridLayout,
                             QSizePolicy, QTabWidget)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QEventLoop
from gui.views.custom_comps import (FileDialog, AppDialog, InputDialog,
                                    ClickableLabel, ErrorWindow)
from flowizi import flowizi
from core.database.validations import Validations, ResType
from core.text_res.feedback import Feedback
from core.elements.element import Element, Environment, ElemType
from core.elements.contained_element import ContainedElement
from gui.views.styles import ElemLabelStyle


class MainWindow(QMainWindow):
    lbl_sig = pyqtSignal(int)
    lbl_dbl_click_sig = pyqtSignal(int)
    elem_dialog_created_sig = pyqtSignal(bool)
    input_dialog_sig = pyqtSignal(str)
    AppDialog_sig = pyqtSignal(bool)
    tab_changed_sig = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.setWindowTitle("Flowizi")
        self.setWindowIcon(QIcon("logo.svg"))
        self.setStyleSheet("background-color: #30302f;")
        self.initUI()

    def initUI(self):
        """Initializes the main UI layout and its components.

        This method sets up the central widget, main layout, and sidebar for
        the application. It includes:
        - A horizontal splitter containing the main grid and sidebar.
        - A vertical layout (vbox) that organizes the toolbar and splitter.
        - A toolbar.
        """
        root_widget = QWidget()
        root_layout = QVBoxLayout()
        root_widget.setLayout(root_layout)
        self.setCentralWidget(root_widget)

        self.splitter = QSplitter(Qt.Horizontal)

        self.setup_toolbar()
        self.setup_grid()
        self.setup_sidebar()

        root_layout.addLayout(self.toolbar)
        root_layout.addWidget(self.splitter)

    def set_btns_clickable(self, clickable: bool):
        """
        Enable or disable the 'start' and 'delete' buttons.

        Sets the 'start' and 'delete' buttons to either enabled
        or disabled based on the value of the 'clickable' parameter.

        Args:
            clickable (bool): True to enable the buttons,
                              False to disable them.
        """
        self.start_btn.setEnabled(clickable)
        self.delete_btn.setEnabled(clickable)

    def create_elem_input(self, elem_type: ElemType):
        """
        Prompts the user for input through a dialog to create an element.

        Args:
            elem_type (ElemType): Element type.
        """
        singular_name = elem_type.value[: len(elem_type.value) - 1]
        title = f"Create {singular_name}"
        msg = f"Enter the name of the new {singular_name}"

        msg_box = InputDialog(title, msg)

        if msg_box.exec():
            self.input_dialog_sig.emit(msg_box.get_text())

    def create_elem_dialog(self, elem_type, current_env):
        """
        Creates an element without keyboard input through a dialog window.

        Args:
            elem_type(ElemType): Element type.
        """
        if elem_type == ElemType.APP:
            res = self._launch_AppDialog(current_env)
        else:
            res = self._launch_FileDialog(current_env)

        if res:
            self.elem_dialog_created_sig.emit(True)

    def _launch_AppDialog(self, current_env):
        """
        Launches an AppDialog so that the user can choose the app to add.

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

    def _launch_FileDialog(self, current_env) -> bool:
        """
        Launches a FileDialog so that the user can choose the file to add.

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

    def handle_app_signal(self, value):
        self.app_result = value

    def handle_app_close_signal(self, value):
        self.user_app_close = value

    def show_error_msg(self, msg):
        ErrorWindow.show(msg)

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

    def generate_grid(self, element_list) -> QWidget:
        """Generates and returns a QWidget containing a grid layout
        of elements.

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
                label = ClickableLabel()
                label.setText(f"{element_list[current_env].name}")
                label.setStyleSheet(ElemLabelStyle.DEFAULT.value)
                label.setAlignment(Qt.AlignCenter)

                grid.addWidget(label, row, column)
                label.set_pos(grid.indexOf(label))
                label.mousePressEvent = self.send_lbl_sig(label.pos)
                label.label_double_click_signal.connect(self.send_lbl_dbl_click_sig)
                current_env += 1

                if current_env == total_envs:
                    break

        return grid_widget

    def send_lbl_sig(self, pos: int):
        """Creates a mouse event handler for a label and returns it.

        The returned handler emits a signal with the specified
        position when triggered, allowing the label's position to be processed
        by other components.

        Args:
            pos (int): The position of the label within the grid.

        Returns:
            function: An event handler function that emits "lbl_sig" with
            the label's position when a mouse event occurs.
        """
        def event(event):
            self.lbl_sig.emit(pos)
        return event

    def send_lbl_dbl_click_sig(self, pos: int):
        """Emits a signal with the position of a label that was double-clicked.

        Args:
            pos: The position of the label that was double-clicked.
        """
        self.lbl_dbl_click_sig.emit(pos)

    def setup_toolbar(self):
        self.toolbar = QHBoxLayout()
        self.toolbar.setContentsMargins(0, 0, 0, 0)

        self.start_btn = self.create_button("Start")
        self.create_btn = self.create_button("Create")
        self.delete_btn = self.create_button("Delete")
        self.back_btn = self.create_button("Back")

        self.toolbar.addWidget(self.back_btn)
        self.toolbar.addWidget(self.start_btn)
        self.toolbar.addWidget(self.create_btn)
        self.toolbar.addWidget(self.delete_btn)
        self.back_btn.hide()
        self.toolbar.addStretch()

    def setup_grid(self):
        grid_widget = self.get_grid(ElemType.ENV, flowizi.environment_list)
        self.splitter.addWidget(grid_widget)

    def setup_sidebar(self):
        self.sidebar_widget = QWidget()
        self.sidebar_widget.hide()
        self.sidebar_widget.setMinimumWidth(300)
        sidebar_layout = QVBoxLayout()
        self.sidebar_widget.setLayout(sidebar_layout)
        self.splitter.addWidget(self.sidebar_widget)

        sidebar_icon = self.create_sidebar_label("")
        icon = QPixmap("logo.svg")
        sidebar_icon.setPixmap(icon)
        sidebar_icon.setAlignment(Qt.AlignCenter)
        self.sidebar_name_label = self.create_sidebar_label("")
        self.sidebar_elem_info_label = self.create_sidebar_label("")
        self.sidebar_websites_label = self.create_sidebar_label("")
        self.sidebar_apps_label = self.create_sidebar_label("")
        self.sidebar_files_label = self.create_sidebar_label("")

        sidebar_layout.addWidget(sidebar_icon)
        sidebar_layout.addWidget(self.sidebar_name_label)
        sidebar_layout.addWidget(self.sidebar_elem_info_label)
        sidebar_layout.addWidget(self.sidebar_websites_label)
        sidebar_layout.addWidget(self.sidebar_apps_label)
        sidebar_layout.addWidget(self.sidebar_files_label)
        sidebar_layout.addStretch()

    def create_button(self, name):
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

    def create_sidebar_label(self, text: str):
        style = """background-color: #1c1c1b; padding-left: 3px;
                   border-radius: 8px; font-size: 22px; color: white;
                """
        label = QLabel(text)
        label.setStyleSheet(style)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        return label

    def generate_empty_grid_label(self, elem_type: ElemType) -> QLabel:
        """Creates and returns a QLabel indicating that there are no elements
        of the specified type.

        Args:
            elem_type (ElemType): Type of element to mention in the label.

        Returns:
            QLabel: A centered label prompting the user to create a new
            element.
        """
        label_text = f"No {elem_type.value} have been created yet. Use the 'Create' button to create one"
        label = QLabel(label_text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 30px; padding: 10px;")

        return label

    def update_sidebar(self, current_view: ElemType, current_env, pos: int):
        """
        Updates the sidebar information based on the clicked label's position
        and current view.

        Args:
            pos (int): The index position of the clicked label.
        """
        self.sidebar_widget.show()
        if current_view == ElemType.ENV:
            self.update_env_sidebar(flowizi.environment_list[pos])
        else:
            env = flowizi.environment_list[current_env]
            elem = getattr(env, current_view.value)[pos]
            self.update_elem_sidebar(elem)

    def update_env_sidebar(self, env: Environment):
        """
        Refreshes the sidebar to display details of the specified environment.

        Args:
            env (Environment): The environment object whose details
                               are displayed in the sidebar.
        """
        self.sidebar_websites_label.show()
        self.sidebar_apps_label.show()
        self.sidebar_files_label.show()

        self.sidebar_name_label.setText(f"Name: {env.name}")
        self.sidebar_elem_info_label.setText(f"Screen recording: {env.record}")
        self.sidebar_websites_label.setText(f"Websites: {len(env.websites)}")
        self.sidebar_apps_label.setText(f"Apps: {len(env.applications)}")
        self.sidebar_files_label.setText(f"Files: {len(env.files)}")

    def update_elem_sidebar(self, elem: ContainedElement):
        """
        Updates the sidebar to display details of the specified element.

        Args:
            elem (ContainedElement): The ContainedElement object whose details
                               are displayed in the sidebar.
        """
        self.sidebar_websites_label.hide()
        self.sidebar_apps_label.hide()
        self.sidebar_files_label.hide()

        self.sidebar_name_label.setText(f"Name: {elem.name}")
        self.sidebar_elem_info_label.setText(f"URL: {elem.url}")

    def update_toolbar(self, current_view):
        """
        Updates the visibility of specific buttons based on the app's state.

        This method is called after actions like adding a website or interacting
        with elements. It ensures buttons that require a selected label are
        disabled when no label is selected, preventing unintended interactions
        and enhancing the user experience.
        """
        self.set_btns_clickable(False)

        if current_view == ElemType.ENV:
            self.start_btn.show()
            self.back_btn.hide()
        else:
            self.start_btn.hide()
            self.back_btn.show()

    def show_contained_elems(self, current_env):
        """
        Inserts a QTabWidget into the splitter at index 0.

        The QTabWidget contains tabs for each type of contained element,
        with each tab displaying a grid of instances corresponding to that
        element type within the current environment.
        """
        env = flowizi.environment_list[current_env]
        websites = getattr(env, ElemType.WEB.value)
        apps = getattr(env, ElemType.APP.value)
        files = getattr(env, ElemType.FILE.value)
        self.toolbar.addStretch()

        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.tab_widget.setStyleSheet("""QTabBar::tab::selected{
                                        background-color: #f19600;
                                 }""")
        self.tab_widget.addTab(self.get_grid(ElemType.WEB, websites), "Websites")
        self.tab_widget.addTab(self.get_grid(ElemType.APP, apps), "Apps")
        self.tab_widget.addTab(self.get_grid(ElemType.FILE, files), "Files")
        font = QFont()
        font.setPointSize(12)
        self.tab_widget.tabBar().setFont(font)
        self.splitter.insertWidget(0, self.tab_widget)
        self.tab_changed()

    def remove_left_widget(self, current_view):
        """
        Removes the widget at index 0 of the splitter.

        This method is typically called after adding or deleting an element
        to ensure that the updated grid can be inserted into the appropriate
        position.
        """
        if current_view == ElemType.ENV:
            widget = self.splitter.widget(0)
        else:
            widget = self.tab_widget.widget(self.current_tab_pos)

        widget.deleteLater()

    def tab_changed(self):
        self.tab_changed_sig.emit(True)
