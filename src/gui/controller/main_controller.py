import sys
from PyQt5.QtWidgets import QApplication
from gui.view.main_view import MainWindow


class Controller:
    def main(self):
        app = QApplication(sys.argv)
        self.main_view = MainWindow()
        self.main_view.show()
        sys.exit(app.exec_())
