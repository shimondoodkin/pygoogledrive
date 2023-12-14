import shlex
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QLabel, QScrollArea,  QDialog, QGridLayout, QLineEdit, QCheckBox, QComboBox
import persistence


class DriveWidget(QWidget):
    def __init__(self, drive, run_callback, edit_callback, delete_callback):
        super().__init__()
        layout = QHBoxLayout(self)

        label_text = []
        label_text.append(
            f"Drive: {drive['drive_letter']} {'(Write cache enabled)' if drive['write_cache'] else ''}")

        label_text.append(
            f" Source: {drive['source_name']}:{drive['source_path']}")

        if 'root_folder_id' in drive and drive['root_folder_id']:
            label_text.append(f"Root Folder: {drive['root_folder_id']}")

        self.drive_label = QLabel(" ".join(label_text))
        # Add a stretch factor to the label
        layout.addWidget(self.drive_label, 1)

        run_button = QPushButton("Run")
        run_button.clicked.connect(lambda: run_callback(drive))
        layout.addWidget(run_button, 0)  # No stretch factor for the button

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: edit_callback(drive))
        layout.addWidget(edit_button, 0)  # No stretch factor for the button

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: delete_callback(drive))
        layout.addWidget(delete_button, 0)  # No stretch factor for the button


class DriveListWidget(QWidget):
    def __init__(self, parent=None, sources=None):
        super().__init__(parent)
        self.mainWindow = parent
        self.sources = sources or []
        self.drives = persistence.load_drives()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Title and Add button
        title_layout = QHBoxLayout()
        title_label = QLabel("Mounted Drives")
        title_layout.addWidget(title_label, 1)
        add_drive_button = QPushButton("Add Drive")
        add_drive_button.clicked.connect(self.add_drive)
        title_layout.addWidget(add_drive_button, 0)
        layout.addLayout(title_layout)

        # Scroll area for the drives
        self.scroll_area = QScrollArea(self)
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        layout.addWidget(self.scroll_area)

        self.populate_drives_list()

    def populate_drives_list(self):
        # Clear existing widgets
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Add new drive widgets
        for drive in self.drives:
            drive_widget = DriveWidget(
                drive,
                self.run_drive,
                self.edit_drive, self.delete_drive)
            self.scroll_area_layout.addWidget(drive_widget)

        # Add a stretch to ensure that drive widgets are aligned to the top
        self.scroll_area_layout.addStretch()

    def add_drive(self):
        dialog = AddEditDriveDialog(self, sources=self.sources)
        if dialog.exec_():
            new_drive = {
                'source_name': dialog.source_name_combobox.currentText(),
                'source_path': dialog.source_path_input.text(),
                'root_folder_id': dialog.root_folder_id_input.text(),
                'write_cache': dialog.write_cache_checkbox.isChecked(),
                'drive_letter': dialog.drive_letter_combobox.currentText(),
                'custom_args': dialog.custom_args_input.text()
            }
            self.drives.append(new_drive)
            persistence.save_drives(self.drives)
            self.populate_drives_list()

    def run_drive(self, drive):

        if drive:

            rclone = self.mainWindow.rclone_config_widget.settings['rclone_path']

            args = [
                'mount', f"{drive['source_name']}:{drive['source_path']}", drive['drive_letter']]
            title = 'drive '+drive['drive_letter']

            if drive['root_folder_id']:
                args = args+["--drive-root-folder-id", drive['root_folder_id']]

            if drive['write_cache']:
                # off|minimal|writes|full
                args = args + ["--vfs-cache-mode", "full"]

            if drive['custom_args']:
                args = args + shlex.split(drive['custom_args'], posix=False)

            # seems bug python's winpty is skipps the 1st arg
            cmd = [rclone, ''] + args
            print(cmd)

            self.mainWindow.terminal_tabs_widget.addTerminalTab(cmd, title)

    def edit_drive(self, drive):
        index = self.drives.index(drive)
        dialog = AddEditDriveDialog(self, drive=drive, sources=self.sources)
        if dialog.exec_():
            updated_drive = {
                'source_name': dialog.source_name_combobox.currentText(),
                'source_path': dialog.source_path_input.text(),
                'root_folder_id': dialog.root_folder_id_input.text(),
                'write_cache': dialog.write_cache_checkbox.isChecked(),
                'drive_letter': dialog.drive_letter_combobox.currentText(),
                'custom_args': dialog.custom_args_input.text()
            }
            self.drives[index] = updated_drive
            persistence.save_drives(self.drives)
            self.populate_drives_list()

    def delete_drive(self, drive):
        if QMessageBox.question(self, 'Confirm Delete',
                                'Are you sure you want to delete this drive?',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.drives.remove(drive)
            persistence.save_drives(self.drives)
            self.populate_drives_list()


class AddEditDriveDialog(QDialog):
    def __init__(self, parent=None, drive=None, sources=[]):
        super().__init__(parent)
        self.setGeometry(100, 100, 1400, 1000)
        self.drive = drive or {}
        self.sources = sources
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Edit Drive")
        layout = QGridLayout(self)

        row = 0

        # Source Name (Editable ComboBox)
        layout.addWidget(QLabel("Source Name:"), row, 0)
        self.source_name_combobox = QComboBox(self)
        self.source_name_combobox.setEditable(True)
        self.source_name_combobox.addItems(self.sources)
        layout.addWidget(self.source_name_combobox, row, 1)

        # Source Path (Text Field)
        layout.addWidget(QLabel("Source Path:"), row, 2)
        self.source_path_input = QLineEdit(self)
        layout.addWidget(self.source_path_input, row, 3)
        row += 1

        # Root Folder ID (Text Field)
        layout.addWidget(QLabel("Root Folder ID:"), row, 0)
        self.root_folder_id_input = QLineEdit(self)
        layout.addWidget(self.root_folder_id_input, row, 1)
        layout.addWidget(QLabel(
            "levae empty, (for Computers folder for example) in google drive web, copy folder id from url"), row, 2, 1, 2)

        row += 1

        # Drive Letter (Editable ComboBox)
        layout.addWidget(QLabel("Drive Letter:"), row, 0)
        self.drive_letter_combobox = QComboBox(self)
        self.drive_letter_combobox.setEditable(True)
        self.drive_letter_combobox.addItems(
            [chr(i)+":" for i in range(65, 91)])  # A-Z
        layout.addWidget(self.drive_letter_combobox, row, 1)

        layout.addWidget(QLabel("select not used drive letter"), row, 2, 1, 2)
        row += 1

        # Write Cache (Checkbox)
        layout.addWidget(QLabel("Write Cache:"), row, 0)
        self.write_cache_checkbox = QCheckBox(self)
        layout.addWidget(self.write_cache_checkbox, row, 1)
        row += 1

        # Custom Arguments (Text Field)
        layout.addWidget(QLabel("Custom Arguments:"), row, 0)
        self.custom_args_input = QLineEdit(self)
        layout.addWidget(self.custom_args_input, row, 1, 1, 4)
        row += 1

        # Save Button
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button, row, 0, 1, 4)  # Span two columns

        # Populate fields if editing an existing drive
        if self.drive:
            self.source_name_combobox.setCurrentText(
                self.drive.get('source_name', ''))
            self.source_path_input.setText(self.drive.get('source_path', '/'))
            self.root_folder_id_input.setText(
                self.drive.get('root_folder_id', ''))
            self.write_cache_checkbox.setChecked(
                self.drive.get('write_cache', False))
            self.drive_letter_combobox.setCurrentText(
                self.drive.get('drive_letter', ''))
            self.custom_args_input.setText(self.drive.get('custom_args', ''))

    def save(self):
        self.accept()
