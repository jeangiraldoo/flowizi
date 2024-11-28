from PySide6.QtWidgets import QHBoxLayout, QPushButton
from gui.views.components.styles import Styles
from core.elements.element import ElemType


class ToolbarWidget(QHBoxLayout):
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

    def update(self, current_view: ElemType):
        """
        Updates button visibility based on the app's state.

        Called after actions like adding a website, it disables buttons
        requiring a selected label to prevent unintended interactions.

        Args:
            current_view (ElemType): Current view displayed.
        """
        self.set_btns_clickable(False)

        if current_view == ElemType.ENV:
            self.start_btn.hide()
            self.back_btn.show()
        else:
            self.start_btn.show()
            self.back_btn.hide()

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
        btn.setStyleSheet(Styles.TOOLBAR_BTN.value)
        return btn

    def set_btns_clickable(self, clickable: bool):
        """
        Enable or disable buttons to allow or prevent the user from using them.

        Args:
            clickable (bool): True to enable the buttons, False otherwise.
        """
        self.start_btn.setEnabled(clickable)
        self.delete_btn.setEnabled(clickable)
