import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QLabel, QScrollArea
from driveslist import DriveListWidget
from jobslist import JobListWidget
from rcloneconfig import RcloneConfigWidget
from terminaltabs import TerminalTabWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sources = ["LocalPath", "GoogleDrive"]  # Dummy list of sources
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Google Drive and Job Management")
        self.setGeometry(100, 100, 1800, 2000)

        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        # Rclone Config Widget
        self.rclone_config_widget = RcloneConfigWidget(self)
        main_layout.addWidget(self.rclone_config_widget)

        # Configure Rclone Button
        config_button = QPushButton("Configure Rclone", self)
        config_button.clicked.connect(self.configure_rclone)
        main_layout.addWidget(config_button)

        # Terminal Tabs
        self.terminal_tabs_widget = TerminalTabWidget(self)
        main_layout.addWidget(self.terminal_tabs_widget)

        # Drive List Widget
        self.drive_list_widget = DriveListWidget(self, sources=self.sources)
        main_layout.addWidget(self.drive_list_widget)

        # Job List Widget
        self.job_list_widget = JobListWidget(self, sources=self.sources)
        main_layout.addWidget(self.job_list_widget)

        self.setCentralWidget(main_widget)

    def configure_rclone(self):
        if not os.path.isfile(self.rclone_config_widget .settings['rclone_path']):
            QMessageBox.warning(
                self, "Rclone Not Found", "Rclone executable not found. Please configure the path.")
            return
        rclone = self.rclone_config_widget.settings['rclone_path']
        self.terminal_tabs_widget.addTerminalTab(
            [rclone, 'seems_bug_it_skipps_the_1st_arg', 'config'], 'config')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
