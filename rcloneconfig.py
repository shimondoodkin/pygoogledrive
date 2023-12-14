from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QMessageBox)
import requests
import zipfile
import io
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox

import subprocess
import os
# import webbrowser
import persistence


class RcloneConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = persistence.load_rclone_config()  # Load saved config
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Rclone Path Configuration
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(self.settings['rclone_path'], self)
        path_layout.addWidget(QLabel("Rclone Path:"), 1)
        path_layout.addWidget(self.path_input, 4)

        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_rclone)
        path_layout.addWidget(browse_button, 1)

        download_button = QPushButton("Download rclone.exe", self)
        download_button.clicked.connect(self.download_rclone)
        path_layout.addWidget(download_button, 1)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_rclone_path)
        path_layout.addWidget(self.save_button, 1)

        layout.addLayout(path_layout)

    def browse_rclone(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Rclone Executable", os.path.expanduser("~"))
        if filename:
            self.path_input.setText(filename)

    def save_rclone_path(self):
        path = self.path_input.text()
        if os.path.isfile(path) and path.endswith("rclone.exe"):  # Basic validation
            self.settings['rclone_path'] = path
            persistence.save_rclone_config(self.settings)
            QMessageBox.information(
                self, "Path Saved", "Rclone path saved successfully.")
        else:
            QMessageBox.warning(self, "Invalid Path",
                                "Please select a valid Rclone executable. executable needs to be named rclone.exe")

    def download_rclone(self):
        # webbrowser.open("https://rclone.org/downloads/")

        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            rclone_exe_path = self.download_and_extract(
                "https://downloads.rclone.org/rclone-current-windows-amd64.zip", folder)
            if rclone_exe_path:
                QMessageBox.information(
                    self, "Success", f"rclone.exe downloaded and extracted to: {rclone_exe_path}")
                self.save_rclone_path()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to download or extract rclone.exe")
        else:
            QMessageBox.warning(self, "Warning", "No folder selected")

    def download_and_extract(self, url, extract_to):
        try:
            response = requests.get(url)
            zip_in_memory = io.BytesIO(response.content)

            with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith('rclone.exe'):
                        zip_ref.extract(file, extract_to)
                        return os.path.join(extract_to, file)
        except Exception as e:
            print(e)
            return None
