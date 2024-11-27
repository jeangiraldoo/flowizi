from PySide6.QtWidgets import QFileDialog


class FileDialog(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setFileMode(QFileDialog.ExistingFile)  # Allows selecting only existing files
        self.setNameFilter("All files (*)")  # Filters by file type if desired

    def get_selected_file(self):
        selected_files = self.selectedFiles()
        return selected_files[0]
