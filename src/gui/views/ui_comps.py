from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
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
