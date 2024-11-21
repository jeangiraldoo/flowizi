from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QSizePolicy, QPushButton, QTabWidget)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.hide()
        self.setMinimumWidth(300)
        layout = QVBoxLayout()
        self.setLayout(layout)

        sidebar_icon = self.create_label("")
        sidebar_icon.setPixmap(QPixmap("logo.svg"))
        sidebar_icon.setAlignment(Qt.AlignCenter)
        self.name_label = self.create_label("")
        self.elem_info_label = self.create_label("")
        self.websites_label = self.create_label("")
        self.apps_label = self.create_label("")
        self.files_label = self.create_label("")

        layout.addWidget(sidebar_icon)
        layout.addWidget(self.name_label)
        layout.addWidget(self.elem_info_label)
        layout.addWidget(self.websites_label)
        layout.addWidget(self.apps_label)
        layout.addWidget(self.files_label)
        layout.addStretch()

    def create_label(self, text: str) -> QLabel:
        """
        Creates the labels used to display information about an element.

        Args:
            text (str): Text to display on the label.

        Returns:
            QLabel: QLabel instance with a set text.
        """
        style = """background-color: #1c1c1b; padding-left: 3px;
                   border-radius: 8px; font-size: 22px; color: white;
                """
        label = QLabel(text)
        label.setStyleSheet(style)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        return label


class Toolbar(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self.start_btn = self.create_button("Start")
        self.create_btn = self.create_button("Create")
        self.delete_btn = self.create_button("Delete")
        self.back_btn = self.create_button("Back")

        self.addWidget(self.back_btn)
        self.addWidget(self.start_btn)
        self.addWidget(self.create_btn)
        self.addWidget(self.delete_btn)
        self.back_btn.hide()
        self.addStretch()

    def create_button(self, btn_txt: str) -> QPushButton:
        """
        Creates a button to be displayed in the toolbar

        Args:
            btn_txt (str): Text to be displayed on the button.

        Returns:
            QPushButton: Customized button.
        """
        btn = QPushButton(btn_txt)
        btn.setMaximumSize(100, 40)
        btn.setStyleSheet("""QPushButton{
                    background-color: #f19600;
                    font-size: 20px;
                    }
                    QPushButton:hover{
                    background-color: #ffbb4d;
                    }""")
        return btn

    def set_btns_clickable(self, clickable: bool):
        """
        Enable or disable buttons to allow or prevent the user from using them.

        Args:
            clickable (bool): True to enable the buttons, False otherwise.
        """
        self.start_btn.setEnabled(clickable)
        self.delete_btn.setEnabled(clickable)


class TabBar(QTabWidget):
    def __init__(self):
        super().__init__()
        font = QFont()
        font.setPointSize(12)
        self.tabBar().setFont(font)
        self.setStyleSheet("""QTabBar::tab::selected{background-color: #f19600;}""")
        self._setup_tabs()

    def _setup_tabs(self):
        """Initializes the tabs within the tab widget."""
        tab_titles = ["Websites", "Apps", "Files"]

        for idx, title in enumerate(tab_titles):
            self.addTab(QWidget(), title)
            self.widget(idx).setLayout(QVBoxLayout())
