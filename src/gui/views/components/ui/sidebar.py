from PyQt5.QtWidgets import QSizePolicy, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from core.elements.element import Element, Environment, ElemType
from core.elements.contained_element import ContainedElement


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.hide()
        self.setMinimumWidth(300)
        self.setLayout(QVBoxLayout())
        self.define_lbl_txt()
        self.setup_widgets()

    def define_lbl_txt(self):
        logo = ""
        name = "Name: {elem.name}"
        screen_rec = "Screen recording: {elem.record}"
        web = "Websites: {elems_len}"
        app = "Apps: {elems_len}"
        file = "Files: {elems_len}"

        self.lbls = [logo, name, screen_rec, web, app, file]

    def setup_widgets(self):
        for i in range(len(self.lbls)):
            label = self.create_label("")
            if i == 0:
                label.setPixmap(QPixmap("logo.svg"))
                label.setAlignment(Qt.AlignCenter)

            self.layout().addWidget(label)

        self.layout().addStretch()

    def update(self, current_view: ElemType, elem: Element):
        """
        Updates labels with content based on the current view and element.

        Args:
            current_view (ElemType): The active view.
            elem (Element): The element to display.
        """
        self.show()
        if current_view == ElemType.ENV:
            self._update_env_sidebar(elem)
        else:
            self._update_elem_sidebar(elem)

    def _update_env_sidebar(self, env: Environment):
        """
        Displays and updates all labels with the given environment's information.

        Args:
            env (Environment): Environment to display.
        """
        elems = ["", "", "", ElemType.WEB, ElemType.APP, ElemType.FILE]

        for i in range(1, len(self.lbls)):
            lbl = self.layout().itemAt(i).widget()
            txt = self.lbls[i]
            if 0 < i < 3:
                format_txt = txt.format(elem=env)
            else:
                env_elem_len = len(getattr(env, elems[i].value))
                format_txt = txt.format(elems_len=env_elem_len)

            lbl.setText(format_txt)
            lbl.show()

    def _update_elem_sidebar(self, elem: ContainedElement):
        """
        Hides environment-specific labels and updates the remaining labels
        with the element's information.

        Args:
            elem (ContainedElement): Environment to display.
        """
        for i in range(1, len(self.lbls)):
            lbl = self.layout().itemAt(i).widget()
            if i == 1:
                lbl.setText(f"Name: {elem.name}")
            elif i == 2:
                lbl.setText(f"Url: {elem.url}")
            else:
                lbl.hide()

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
