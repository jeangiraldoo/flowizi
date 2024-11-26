from PyQt5.QtWidgets import QMessageBox


class ErrorWindow():
    @staticmethod
    def show(msg):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(msg)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setDefaultButton(QMessageBox.Ok)
        error_box.exec_()
