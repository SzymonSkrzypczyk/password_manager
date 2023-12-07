import csv
from warnings import simplefilter
from pathlib import Path
from uuid import uuid4
from PySide6.QtWidgets import QPushButton, QLabel, QDialog, QVBoxLayout,\
     QLineEdit, QFormLayout, QDialogButtonBox, QFileDialog
from PySide6.QtGui import QFont, QMovie
from PySide6.QtCore import Qt, QSize
import cv2

from src.db import Password
from src.face_rec_easier import recognize_gui, encode_known, new_face, IMAGE_PATH

IMAGES = Path(__file__).parent.parent / 'images'
MANUALS = Path(__file__).parent.parent.parent / 'data' / 'manuals.gif'
simplefilter("ignore")


class LoadDialog(QDialog):
    def __init__(self, _main_window, parent=None):
        super(LoadDialog, self).__init__(parent)
        self.main_window = _main_window
        self.path = None
        self.passwords = []

        self.lay1 = QVBoxLayout()

        self.file_button = QPushButton("File Select")
        self.file_button.clicked.connect(self._set_path)
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self._load)

        self.lay1.addWidget(self.file_button)
        self.lay1.addWidget(self.confirm_button)

        self.setLayout(self.lay1)

    def _set_path(self):
        path = QFileDialog().getOpenFileName(self, filter="*.csv")
        if Path(path[0]).exists():
            self.path = Path(path[0])

    def _load(self):
        if self.path is not None:
            with self.path.open('r') as csv_file:
                csv_reader = csv.DictReader(csv_file, fieldnames=("pk", "name", "password"))
                next(csv_reader)
                for i in csv_reader:
                    self.passwords.append(Password(i["pk"], i["name"], i["password"]))
            self.accept()

    def get_file(self):
        print(self.passwords)
        return self.passwords


class ExportDialog(QDialog):
    def __init__(self, _main_window, parent=None):
        super(ExportDialog, self).__init__(parent)
        self.main_window = _main_window
        self.directory_path = None

        self.lay1 = QVBoxLayout()

        self.file_name = QLineEdit()
        self.file_name.setPlaceholderText("Exported File Name")

        # raczej nie w ten sposob
        self.directory = QPushButton("Directory")
        self.directory.clicked.connect(self._set_directory)

        self.button = QPushButton("Export")
        self.button.clicked.connect(self._export)

        self.lay1.addWidget(self.file_name)
        self.lay1.addWidget(self.directory)
        self.lay1.addWidget(self.button)

        self.setLayout(self.lay1)

    def _export(self, _):
        # mozna dodac opcje wybierania sciezki
        # tu trzeba poprawic calosc z wybieraniem pliku
        if self.directory_path is not None:
            exported_file = self.directory_path / f'{self.file_name.text()}.csv'
            exported_file.touch(exist_ok=True)
            with exported_file.open('w') as file:
                fields = ['pk', 'name', 'password']
                writer = csv.DictWriter(file, fields)
                writer.writeheader()
                for i in self.main_window.db.get_user_passwords(self.main_window.current_user):
                    writer.writerow({"pk": i.pk, "name": i.name, "password": i.password})
            self.accept()

    def _set_directory(self, _):
        directory = QFileDialog().getExistingDirectory(self)
        # print(directory)
        self.directory_path = Path(directory)


class ManualDialog(QDialog):
    """Manuale jako gif z dzialania aplikacji"""
    def __init__(self, logged_out: bool, parent=None):
        super(ManualDialog, self).__init__(parent)
        self.movie = QMovie(str(MANUALS))
        self.logged_out = logged_out

        self.lay1 = QVBoxLayout()

        self.gif_label = QLabel()
        self.gif_label.setMovie(self.movie)
        self.gif_label.show()
        self.movie.start()

        self.leave_button = QPushButton("Leave")
        self.leave_button.clicked.connect(self._leave)

        self.lay1.addWidget(self.gif_label)
        self.lay1.addWidget(self.leave_button)

        self.setLayout(self.lay1)

    def resizeEvent(self, _):
        # bylo event, a nie e!!!
        rect = self.geometry()
        size = QSize(min(rect.width(), rect.height()), min(rect.width(), rect.height()))

        movie = self.gif_label.movie()
        movie.setScaledSize(size)

    def __del__(self):
        # tu moze bedize trzeba poeksperymentowac z dzialaniem destruktora
        self.movie.stop()

    def _leave(self, _):
        self.movie.stop()
        self.accept()


class RenameDialog(QDialog):
    def __init__(self, old_name: str, parent=None):
        super(RenameDialog, self).__init__(parent)

        self.lay1 = QVBoxLayout()

        self.current_name = QLineEdit()
        self.current_name.setPlaceholderText(old_name)
        self.current_name.setDisabled(True)

        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("New name")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.lay1.addWidget(self.current_name)
        self.lay1.addWidget(self.new_name)
        self.lay1.addWidget(self.buttonBox)

        self.setLayout(self.lay1)

    def return_data(self):
        return self.new_name.text()


class WarningDialog(QDialog):
    def __init__(self, title, text, parent=None):
        super(WarningDialog, self).__init__(parent)
        self.lay1 = QVBoxLayout()
        self.setWindowTitle(title)
        self.text = QLabel(text)
        self.text.setAlignment(Qt.AlignCenter)
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.accept)

        self.lay1.addWidget(self.text)
        self.lay1.addWidget(self.button)

        self.setLayout(self.lay1)


class UpdatePasswordDialog(QDialog):  # trzeba jeszce podpiac
    def __init__(self, name, old_password, parent=None):  # usuwam password_id!
        super(UpdatePasswordDialog, self).__init__(parent)
        self.lay1 = QVBoxLayout()
        self.input_lay = QFormLayout()

        self.name_text = QLineEdit(name)
        self.name_text.setDisabled(True)
        self.password_text = QLineEdit()
        self.password_text.setPlaceholderText(old_password)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.input_lay.addRow(QLabel("Name: "), self.name_text)
        self.input_lay.addRow(QLabel("Password"), self.password_text)

        self.lay1.addLayout(self.input_lay)
        self.lay1.addWidget(self.buttonBox)

        self.setLayout(self.lay1)

    def return_data(self):
        return self.password_text.text()


class AddPasswordDialog(QDialog):
    def __init__(self, parent=None):
        """Jest opcja z globalna lista i odswiezaniem listy co jakis czas!"""
        super(AddPasswordDialog, self).__init__(parent)

        self.lay1 = QVBoxLayout()
        self.lay_input = QFormLayout()
        self.setWindowTitle("Add Password")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.name_input = QLineEdit()
        self.password_input = QLineEdit()
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.lay1.addLayout(self.lay_input)
        self.lay_input.addRow(QLabel("Name: "), self.name_input)
        self.lay_input.addRow(QLabel("Password: "), self.password_input)
        self.lay1.addLayout(self.lay_input)
        self.lay1.addWidget(self.buttonBox)

        self.setLayout(self.lay1)

    def return_data(self):
        return self.name_input.text(), self.password_input.text()


class LoginDialog(QDialog):
    """Musi przekazywac id usera!
    i sprawdzac czy user juz istnieje
    """
    def __init__(self, _main_window, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Password Manager")
        self.main_window = _main_window

        self.font_text = QFont("Montserrat")
        self.font_text.setPointSize(34)
        self.font_button = QFont("Lora")
        self.font_button.setPointSize(26)

        self.setFixedSize(640, 480)
        self.lay = QVBoxLayout()
        # self.lay.setMargin(10)
        self.lay.setSpacing(20)

        self.text = QLabel("Hello!\nPress the login button\n in order to have\n your face scanned :)")
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setFont(self.font_text)

        self.login_button = QPushButton("Login")
        self.login_button.setStatusTip("Logs in an user")
        self.login_button.clicked.connect(self.detect)
        self.login_button.setFont(self.font_button)

        self.create_button = QPushButton("Add Account")
        self.create_button.setStatusTip("Creates an account for a new user")
        self.create_button.clicked.connect(self._create)
        self.create_button.setFont(self.font_button)

        self.lay.addWidget(self.text)
        self.lay.addWidget(self.login_button)
        self.lay.addWidget(self.create_button)

        self.setLayout(self.lay)

    def detect(self):
        """Dummy method"""
        # przekazywanie id usera do maina
        # placeholder
        name = recognize_gui(self.main_window)
        self.main_window.user_name = name
        self.main_window.info_text.setText(name)
        self.main_window.update()
        if name == 'DEFAULT':
            WarningDialog("No face detected!", "No face has been detected\nDefault user enabled").exec()
            # should not go further
            # default profile maybe
            # name is not shown in mainWindow
        self.accept()
        self.main_window.menuBar().show()
        self.main_window.show()
        '''detected_id = 1
        if self.main_window.db.check_user(detected_id):
            self.main_window.current_user = 1
            self.main_window.load_at_startup()
        else:
            # losowa nazwa na ten moment
            # mam nadzieje ze zadziala
            index = self.main_window.db.add_user(str(uuid4()))
            self.main_window.current_user = index
            self.main_window.load_at_startup()'''

    def _create(self, _):
        name = str(uuid4())
        index = self.main_window.db.add_user(name)
        self.main_window.user_name = name
        self.main_window.info_text.setText(name)
        self.main_window.current_user = index
        self.main_window.update()
        self.accept()
        self.main_window.show()
        image = new_face()
        cv2.imwrite(str((IMAGE_PATH / name).with_suffix('.jpg')), image)
        encode_known()
