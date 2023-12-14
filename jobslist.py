import shlex
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QLabel, QScrollArea,  QDialog, QGridLayout, QLineEdit, QCheckBox, QComboBox
import persistence


"""
  about       
  authorize   
  backend     
  bisync      
  cat         
  check       
  checksum    
  cleanup     
  completion  
  config      
  copy        
  copyto      
  copyurl     
  cryptcheck  
  cryptdecode 
  dedupe      
  delete      
  deletefile  
  gendocs     
  hashsum     
  help        
  link        
  listremotes 
  ls          
  lsd         
  lsf         
  lsjson      
  lsl         
  md5sum      
  mkdir       
  mount       
  move        
  moveto      
  ncdu        
  obscure     
  purge       
  rc          
  rcat        
  rcd         
  rmdir       
  rmdirs      
  selfupdate  
  serve       
  settier     
  sha1sum     
  size        
  sync        
  test        
  touch       
  tree        
  version     
"""


class JobWidget(QWidget):
    def __init__(self, job, run_callback, edit_callback, delete_callback):
        super().__init__()
        layout = QHBoxLayout(self)

        label_text = [
            f"Action: {job['action']}",
            f"From: {job['from_source_name']}:{job['from_source_folder']}",
            f"To: {job['to_source_name']}:{job['to_source_folder']}",
            f"Schedule: Every {job['schedule']} minutes"
        ]
        self.job_label = QLabel(" | ".join(label_text))
        layout.addWidget(self.job_label, 1)

        run_button = QPushButton("Run")
        run_button.clicked.connect(lambda: run_callback(job))
        layout.addWidget(run_button, 0)  # No stretch factor for the button

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: edit_callback(job))
        layout.addWidget(edit_button, 0)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: delete_callback(job))
        layout.addWidget(delete_button, 0)


class JobListWidget(QWidget):
    def __init__(self, parent=None, sources=None):
        super().__init__(parent)
        self.sources = sources or []
        # Assume persistence for jobs similar to drives
        self.jobs = persistence.load_jobs()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Title and Add button
        title_layout = QHBoxLayout()
        title_label = QLabel("Scheduled Jobs")
        title_layout.addWidget(title_label, 1)
        add_job_button = QPushButton("Add Job")
        add_job_button.clicked.connect(self.add_job)
        title_layout.addWidget(add_job_button, 0)
        layout.addLayout(title_layout)

        # Scroll area for the jobs
        self.scroll_area = QScrollArea(self)
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        layout.addWidget(self.scroll_area)

        self.populate_jobs_list()

    def populate_jobs_list(self):
        # Clear existing widgets
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Add new job widgets
        for job in self.jobs:
            job_widget = JobWidget(
                job,
                self.run_job,
                self.edit_job, self.delete_job)
            self.scroll_area_layout.addWidget(job_widget)

        # Add a stretch to ensure that job widgets are aligned to the top
        self.scroll_area_layout.addStretch()

    def add_job(self):
        dialog = AddEditJobDialog(self, sources=self.sources)
        if dialog.exec_():
            new_job = {
                'action': dialog.action_combobox.currentText(),
                'from_source_name': dialog.from_source_name_combobox.currentText(),
                'from_source_folder': dialog.from_source_folder_input.text(),
                'to_source_name': dialog.to_source_name_combobox.currentText(),
                'to_source_folder': dialog.to_source_folder_input.text(),
                'schedule': int(dialog.schedule_input.text())
            }
            self.jobs.append(new_job)
            # Implement this in the persistence module
            persistence.save_jobs(self.jobs)
            self.populate_jobs_list()

    def run_job(self, job):

        # .\rclone.exe copy "C:\Users\user\Documents" GoogleDriveComputers:Documents --update -P --exclude "/.tmp.driveupload/**"  --exclude "*node_modules*" --transfers 10

        if job:

            rclone = self.mainWindow.rclone_config_widget.settings['rclone_path']

            args = [
                job['action'],
                f"{job['from_source_name']+':' if job['from_source_name'] else ''}:{job['from_source_folder']}",
                f"{job['to_source_name']+':' if job['to_source_name'] else ''}:{job['to_source_folder']}"
            ]

            title = job['action']+' '+job['from_source_name'] + \
                ' to '+job['to_source_name']

            if job['custom_args']:
                args = args + shlex.split(job['custom_args'], posix=False)

            # seems bug python's winpty is skipps the 1st arg
            cmd = [rclone, ''] + args
            print(cmd)

            self.mainWindow.terminal_tabs_widget.addTerminalTab(cmd, title)

    def edit_job(self, job):
        index = self.jobs.index(job)
        dialog = AddEditJobDialog(self, job=job, sources=self.sources)
        if dialog.exec_():
            updated_job = {
                'action': dialog.action_combobox.currentText(),
                'from_source_name': dialog.from_source_name_combobox.currentText(),
                'from_source_folder': dialog.from_source_folder_input.text(),
                'to_source_name': dialog.to_source_name_combobox.currentText(),
                'to_source_folder': dialog.to_source_folder_input.text(),
                'schedule': int(dialog.schedule_input.text())
            }
            self.jobs[index] = updated_job
            persistence.save_jobs(self.jobs)
            self.populate_jobs_list()

    def delete_job(self, job):
        if QMessageBox.question(self, 'Confirm Delete',
                                'Are you sure you want to delete this job?',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.jobs.remove(job)
            persistence.save_jobs(self.jobs)
            self.populate_jobs_list()


class AddEditJobDialog(QDialog):
    def __init__(self, parent=None, job=None, sources=[]):
        super().__init__(parent)
        self.setGeometry(100, 100, 600, 400)
        self.job = job or {}
        self.sources = sources
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Edit Job")
        layout = QGridLayout(self)

        row = 0

        # Action (Dropdown)
        self.action_combobox = QComboBox(self)
        self.action_combobox.addItems(["Copy", "Move"])
        layout.addWidget(QLabel("Action:"), row, 0)
        layout.addWidget(self.action_combobox, row, 1)
        row += 1

        # From Source Name (Editable ComboBox)
        self.from_source_name_combobox = QComboBox(self)
        self.from_source_name_combobox.setEditable(True)
        self.from_source_name_combobox.addItems(self.sources)
        layout.addWidget(QLabel("From Source Name:"), row, 0)
        layout.addWidget(self.from_source_name_combobox, row, 1)
        row += 1

        # From Source Folder (Text Field)
        self.from_source_folder_input = QLineEdit(self)
        layout.addWidget(QLabel("From Source Folder:"), row, 0)
        layout.addWidget(self.from_source_folder_input, row, 1)
        row += 1

        # To Source Name (Editable ComboBox)
        self.to_source_name_combobox = QComboBox(self)
        self.to_source_name_combobox.setEditable(True)
        self.to_source_name_combobox.addItems(self.sources)
        layout.addWidget(QLabel("To Source Name:"), row, 0)
        layout.addWidget(self.to_source_name_combobox, row, 1)
        row += 1

        # To Source Folder (Text Field)
        self.to_source_folder_input = QLineEdit(self)
        layout.addWidget(QLabel("To Source Folder:"), row, 0)
        layout.addWidget(self.to_source_folder_input, row, 1)
        row += 1

        # Schedule Configuration (Text Field)
        self.schedule_input = QLineEdit(self)
        layout.addWidget(QLabel("Schedule (in minutes):"), row, 0)
        layout.addWidget(self.schedule_input, row, 1)
        row += 1

        # Save Button
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button, row, 0, 1, 2)  # Span two columns

        # Populate fields if editing an existing job
        if self.job:
            self.action_combobox.setCurrentText(self.job.get('action', 'Copy'))
            self.from_source_name_combobox.setCurrentText(
                self.job.get('from_source_name', ''))
            self.from_source_folder_input.setText(
                self.job.get('from_source_folder', ''))
            self.to_source_name_combobox.setCurrentText(
                self.job.get('to_source_name', ''))
            self.to_source_folder_input.setText(
                self.job.get('to_source_folder', ''))
            self.schedule_input.setText(str(self.job.get('schedule', 60)))

    def save(self):
        self.accept()
