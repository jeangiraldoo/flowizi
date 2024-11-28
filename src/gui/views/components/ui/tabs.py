from PySide6.QtWidgets import QTabWidget
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from gui.views.components.styles import Styles
from core.elements.element import ElemType
from gui.views.components.ui.grid import GridWidget


class TabWidget(QTabWidget):
    lbl_sig = Signal(bool, int)

    def __init__(self):
        super().__init__()
        font = QFont()
        font.setPointSize(12)
        self.tabBar().setFont(font)
        self.setStyleSheet(Styles.FOCUSED_TAB.value)
        self._setup_tabs()

    def update(self):
        self.clear_grid_widget()

    def clear_grid_widget(self):
        """Removes the widget found in every tab."""
        for i in range(self.count()):
            self.widget(i).clear_grid_widget()

    def _setup_tabs(self):
        """Initializes the tabs within the tab widget."""
        tab_titles = [ElemType.WEB, ElemType.APP, ElemType.FILE]

        for idx, title in enumerate(tab_titles):
            widget = GridWidget()
            widget.lbl_sig.connect(self._send_lbl_sig)
            self.addTab(widget, title.value)

    def _send_lbl_sig(self, lbl_highlighted: bool, pos: int):
        """Creates a mouse event handler for a label and returns it.

        The returned handler emits a signal with the label's position when
        clicked, allowing the label's position to be used by other components.

        Args:
            pos (int): The position of the label within the grid.

        Returns:
            func: Emits "lbl_sig" with the label's position when clicked.
        """
        self.lbl_sig.emit(lbl_highlighted, pos)
