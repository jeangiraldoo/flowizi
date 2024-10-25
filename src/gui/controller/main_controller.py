import sys
from PyQt5.QtWidgets import QApplication
from gui.view.main_view import MainWindow
from flowizi import flowizi


class Controller:
    def main(self):
        app = QApplication(sys.argv)
        self.main_view = MainWindow()
        self.main_view.show()
        self.main_view.label_signal.connect(self.element_clicked)

        sys.exit(app.exec_())

    def element_clicked(self, pos):
        self.main_view.element_info_container.itemAt(1).widget().setText(f"Name: {flowizi.environment_list[pos].name}")
        self.main_view.element_info_container.itemAt(2).widget().setText(f"Screen recording: {flowizi.environment_list[pos].record}")
        self.main_view.element_info_container.itemAt(3).widget().setText(f"Websites: {len(flowizi.environment_list[pos].websites)}")
        self.main_view.element_info_container.itemAt(4).widget().setText(f"Apps: {len(flowizi.environment_list[pos].applications)}")
        self.main_view.element_info_container.itemAt(5).widget().setText(f"Files: {len(flowizi.environment_list[pos].files)}")

        for i in range(len(self.main_view.grid)):
            if pos == i:
                clicked_label = self.main_view.grid.itemAt(pos)
                clicked_label.widget().setStyleSheet(self.main_view.label_clicked_style)
            else:
                self.main_view.grid.itemAt(i).widget().setStyleSheet(self.main_view.label_default_style)
