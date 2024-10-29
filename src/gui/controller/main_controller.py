import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QHBoxLayout, QDialog, QLineEdit, QSizePolicy, QLabel, QPushButton, QTabWidget
from PyQt5.QtGui import QFont
from gui.view.main_view import MainWindow
from flowizi import flowizi


class Controller:
    def main(self):
        app = QApplication(sys.argv)
        self.main_view = MainWindow()
        self.main_view.show()
        self.current_view = "environments"
        self.current_environment = None
        self.current_tab = None
        self.main_view.label_signal.connect(self.element_clicked)
        self.main_view.label_double_click_signal.connect(self.element_double_clicked)
        self.main_view.start_button.clicked.connect(self.start_button_clicked)
        self.main_view.create_button.clicked.connect(self.create_button_clicked)

        sys.exit(app.exec_())

    def element_clicked(self, pos):
        if self.current_view == "environments":
            self.environment_clicked(pos)
        elif self.current_view == "contained_elements":
            self.contained_element_clicked(pos)
            
    def environment_clicked(self, pos):
        self.current_environment = pos
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

    def contained_element_clicked(self, pos):
        environment = flowizi.environment_list[self.current_environment]
        if self.current_tab == 0:
            contained_elements = environment.websites
        elif self.current_tab == 1:
            contained_elements = environment.applications
        elif self.current_tab == 2:
            contained_elements = environment.websites

        self.main_view.element_info_container.itemAt(1).widget().setText(f"Name: {contained_elements[pos].name}")
        self.main_view.element_info_container.itemAt(2).widget().setText(f"URL: {contained_elements[pos].url}")

    def element_double_clicked(self, pos):
        self.current_view = "contained_elements"
        self.remove_widgets()        
        self.set_contained_element_sidebar()
        self.show_environment_overview(pos)
        
    def get_grid(self, pos, element_type):
        environment = flowizi.environment_list[pos]
        elements = getattr(environment, element_type)
        if elements:
            return self.main_view.generate_element_grid(elements)
        else:
            empty_label = QLabel(f"There are no {element_type} in the {flowizi.environment_list[pos].name} environment.")
            empty_label.setStyleSheet("background-color: white; font-size: 20px; padding: 10px;")
            return empty_label

    def reset_environment_sidebar(self):
        self.main_view.element_info_container.itemAt(1).widget().setText("No environments selected")
        self.main_view.element_info_container.itemAt(2).widget().setText("")
        style = "background-color: #454541; font-size: 18px; color: white; padding: 20px;"
        websites_label = QLabel("")
        websites_label.setWordWrap(True)
        websites_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        websites_label.setStyleSheet(style)
        websites_label.setFixedHeight(65)

        applications_label = QLabel("")
        applications_label.setWordWrap(True)
        applications_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        applications_label.setStyleSheet(style)
        applications_label.setFixedHeight(65)

        files_label = QLabel("")
        files_label.setWordWrap(True)
        files_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        files_label.setStyleSheet(style)
        files_label.setFixedHeight(65)

        self.main_view.element_info_container.addWidget(websites_label)
        self.main_view.element_info_container.addWidget(applications_label)
        self.main_view.element_info_container.addWidget(files_label)


    def set_contained_element_sidebar(self):
        self.main_view.element_info_container.itemAt(1).widget().setText("No element selected")
        self.main_view.element_info_container.itemAt(2).widget().setText("")

        while self.main_view.element_info_container.count() > 3:
            item = self.main_view.element_info_container.takeAt(3)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def remove_widgets(self):
        while self.main_view.toolbar.count():
            item = self.main_view.toolbar.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.main_view.splitter.widget(0).deleteLater()

    def show_environment_overview(self, pos):
        back_button = QPushButton("Back")
        back_button.setMaximumSize(100, 40)
        back_button.clicked.connect(self.back_button_clicked)
        back_button.setStyleSheet("""QPushButton{
                                        background-color: white;
                                        font-size: 20px;
                                        }
                                    QPushButton:hover{
                                        background-color: #f19600;
                                    }""")
        self.main_view.toolbar.addWidget(back_button)
        self.main_view.toolbar.addStretch()

        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.update_current_tab)
        self.tab_widget.setStyleSheet("""QTabBar::tab::selected{
                                        background-color: #f19600;
                                 }""")
        self.tab_widget.addTab(self.get_grid(pos, "websites"), "Websites")
        self.tab_widget.addTab(self.get_grid(pos, "applications"), "Apps")
        self.tab_widget.addTab(self.get_grid(pos, "files"), "Files")
        font = QFont()
        font.setPointSize(12)
        self.tab_widget.tabBar().setFont(font)
        self.main_view.splitter.insertWidget(0, self.tab_widget)

    def update_current_tab(self):
        self.current_tab = self.tab_widget.currentIndex()

    def back_button_clicked(self):
        self.current_view = "environments"
        self.current_tab = None
        self.current_environment = None
        self.remove_widgets()

        start_button = QPushButton("Start")
        start_button.setMaximumWidth(100)
        start_button.setMaximumHeight(40)
        start_button.clicked.connect(self.start_button_clicked)
        create_button = QPushButton("Create")
        create_button.setMaximumWidth(100)
        create_button.setMaximumHeight(40)
        create_button.setStyleSheet("""QPushButton{
                                        color: white;
                                        font-size: 20px;
                                    }
                                    QPushButton:hover{
                                        background-color: #f19600;
                                    }""")
        start_button.setStyleSheet("""QPushButton{
                                        color: white;
                                        font-size: 20px;
                                    }
                                    QPushButton:hover{
                                        background-color: #f19600;
                                    }""")

        self.main_view.toolbar.addWidget(start_button)
        self.main_view.toolbar.addWidget(create_button)
        self.main_view.toolbar.addStretch()
        self.reset_environment_sidebar()
        environments = flowizi.environment_list
        env_grid = self.main_view.generate_element_grid(environments)
        self.main_view.splitter.insertWidget(0, env_grid)

    def start_button_clicked(self):
        for i in range(len(self.main_view.grid)):
            label = self.main_view.grid.itemAt(i).widget()
            label_style = label.styleSheet()

            if self.main_view.label_clicked_style in label_style:
                flowizi.environment_list[i].start()

    def create_button_clicked(self):
        msg_box = InputDialog()
        msg_box.set_window_title("Create environment")
        msg_box.set_message("Enter the name of the new environment")

        msg_box.exec_()
        env_name = msg_box.get_text()
        if env_name == "":
            self.show_invalid_input("The name must have at least one character")

    def show_invalid_input(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setDefaultButton(QMessageBox.Ok)

        # Display the error box
        error_box.exec_()


class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-size: 17px")
        self.text_input = QLineEdit(self)

        button_box = QHBoxLayout()
        ok_button = QPushButton("Create")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(self.message_label)
        layout.addWidget(self.text_input)
        layout.addLayout(button_box)
        self.setLayout(layout)
        self.resize(350, 150)

    def set_window_title(self, title):
        self.setWindowTitle(title)

    def set_message(self, message):
        self.message_label.setText(message)

    def get_text(self):
        return self.text_input.text()
