from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QDialog, QLineEdit)


class InputDialog(QDialog):
    def __init__(self, title, msg):
        super().__init__()
        self.setWindowTitle(title)
        self.message_label = QLabel()
        self.message_label.setText(msg)
        self.message_label.setStyleSheet("font-size: 17px")
        self.text_input = QLineEdit(self)

        btn_box = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.message_label)
        layout.addWidget(self.text_input)
        layout.addLayout(btn_box)
        self.setLayout(layout)
        self.resize(350, 150)

    def get_text(self):
        return self.text_input.text()
