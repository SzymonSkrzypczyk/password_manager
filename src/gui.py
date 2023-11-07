from warnings import simplefilter
from pathlib import Path
from uuid import uuid4
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea, QPushButton, QLabel, QDialog, QVBoxLayout,\
     QHBoxLayout, QMainWindow, QLineEdit, QFormLayout, QDialogButtonBox
from PySide6.QtGui import QFont, QAction
from PySide6.QtCore import Qt, Signal, QRunnable, Slot, QThreadPool, QTimer
import cv2

from src.db import DBControl
from src.face_rec_easier import recognize_gui, encode_known, new_face, IMAGE_PATH

"""
Dziala: dodawanie, update'owanie
Nie Dziala: usuwanie, usuwanie wszyskiego, login page na starcie, wykrywa caly czas ta sama osobe!!!
teraz trzeba dodac logike co gdy dany uzytkownik nie istnieje jeszcze w bazie
trzeba dodac dialog dla niewykrycia twarzy i moze jakis defaultowy profil w takim wypadku
trzebaby poprawic clear all i bedzie cacy
pojawiaja sie warningi
dodanie opcji zmiany profilu itd
moze trzeba encodowac po tym jak sie doda nowego uzytkownika(juz sie to dzieje jednak)
jebei sie usuwanie usera a potem update'owanie
"""
IMAGES = Path(__file__).parent.parent / 'images'
simplefilter("ignore")


class PasswordField(QWidget):
    delete_signal = Signal(int)

    def __init__(self, name: str, password: str, index: int, _main_window, parent=None):
        """trzeba dodac parametr dla main_window"""
        super(PasswordField, self).__init__(parent)
        self.main_window = _main_window
        self.hidden = True
        self.index = index
        self.name = name
        self.password = password
        self.lay1 = QHBoxLayout()
        self.lay1.addSpacing(20)

        self.password_name = QLabel(self.name)
        self.password_field = QLabel("*******")
        self.show_button = QPushButton("Show")
        self.show_button.clicked.connect(self._show)
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self._update)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete)

        self.lay1.addWidget(self.password_name)
        self.lay1.addWidget(self.password_field)
        self.lay1.addWidget(self.show_button)
        self.lay1.addWidget(self.update_button)
        self.lay1.addWidget(self.delete_button)

        self.setLayout(self.lay1)

    def _delete(self, e):
        self.delete_signal.emit(self.index)
        # self.main_window.db.delete_password(self.index)  # delete in db

    def _update(self, e):
        dialog = UpdatePasswordDialog(self.name, self.password, self.parent())
        if dialog.exec() == QDialog.Accepted:
            # db
            new_password = dialog.return_data()
            self.main_window.db.update_password(self.index, new_password)
            self.password = new_password
            self.password_field.setText(self.password)
            self.hidden = False
            self.main_window.refresh()

        self.update()

    def _show(self, e):
        if not self.hidden:
            self.password_field.setText("*******")
        else:
            self.password_field.setText(self.password)
        self.hidden = not self.hidden

    def get_index(self):
        return self.index


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
        self.login_button.clicked.connect(self.detect)
        self.login_button.setFont(self.font_button)

        self.create_button = QPushButton("Add Account")
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

    def _create(self, e):
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


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self) -> None:
        self.fn(*self.args, **self.kwargs)


class MainWindow(QMainWindow):
    """Powinno zapisywac na wyjsciu!"""
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Password Manager")
        self.setFixedSize(640, 480)
        self.info_font = QFont("helvetica")
        self.info_font.setPointSize(16)

        # variables essential for the correct future functioning of the app
        self.current_user = 0  # id
        self.user_name = "USERNAME"
        self.db = DBControl()

        # background tasks
        self.timer = QTimer()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.update_encoding)
        self.timer.start()
        self.threadpool = QThreadPool()

        # run login page on startup
        self.login_page = LoginDialog(self)
        self.hide()
        self.login_page.show()

        self.lay1 = QVBoxLayout()

        # widgets
        self.info_area = QHBoxLayout()
        self.info_text = QLabel(self.user_name)  # to be replaced!
        self.info_text.setFont(self.info_font)
        self.info_text.setAlignment(Qt.AlignCenter)
        self.info_area.addWidget(self.info_text)

        self.passwords_area = QScrollArea()
        self.passwords_lay = QVBoxLayout()
        self.load_at_startup()
        self.passwords_area.setLayout(self.passwords_lay)

        self.controls = QHBoxLayout()
        self.clear_all_button = QPushButton("Clear all")
        self.clear_all_button.clicked.connect(self._clear_all)
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._add)
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self._logout)
        self.controls.addWidget(self.clear_all_button)
        self.controls.addWidget(self.add_button)
        self.controls.addWidget(self.logout_button)

        # actions
        user_rename = QAction("Rename", self)
        user_rename.setStatusTip("Change your user name")
        user_rename.triggered.connect(self.rename_user)

        user_delete = QAction("Delete", self)
        user_delete.setStatusTip("Delete your user")
        user_delete.triggered.connect(self.delete_user)

        clear_action = QAction("Clear", self)
        clear_action.setStatusTip("Clear all passwords")
        clear_action.triggered.connect(self._clear_all)

        add_action = QAction("Add", self)
        add_action.setStatusTip("Add a new password")
        add_action.triggered.connect(self._add)

        logout_action = QAction("Logout", self)
        logout_action.setStatusTip("Logout")
        logout_action.triggered.connect(self._logout)

        # menu
        controls_menu = self.menuBar().addMenu("&Controls")
        controls_menu.addAction(clear_action)
        controls_menu.addAction(add_action)
        controls_menu.addSeparator()
        controls_menu.addAction(logout_action)

        user_menu = self.menuBar().addMenu("User")
        user_menu.addAction(user_rename)
        user_menu.addAction(user_delete)

        self.lay1.addLayout(self.info_area)
        self.lay1.addWidget(self.passwords_area)
        self.lay1.addLayout(self.controls)

        widget = QWidget()
        widget.setLayout(self.lay1)
        self.setCentralWidget(widget)

    def _clear_all(self, e):
        while self.passwords_lay.count():
            self.passwords_lay.takeAt(0).widget().deleteLater()
        """for child in self.passwords_lay.children():
            child.deleteLater()
        self.passwords_lay.children().clear()"""  # mozliwe ze nie jest to dobry pomysl
        if self.current_user is not None:  # bedzie mozna to potem usunac
            self.db.clear_passwords_user(self.current_user)  # dziala
        self.refresh()
        # self.current_index = 0

    def _add(self, e):
        dialog = AddPasswordDialog()
        if dialog.exec() == QDialog.Accepted and self.current_user is not None:
            # db
            name, password = dialog.return_data()
            index = self.db.add_password(name, password, self.current_user)
            pw_field = PasswordField(name, password, index, self)  # tu jest glowny problem dodawania i usuwania
            pw_field.delete_signal.connect(self._delete)
            self.passwords_lay.addWidget(pw_field)
        self.update()

    def _logout(self, e):
        while self.passwords_lay.count():
            self.passwords_lay.takeAt(0).widget().deleteLater()
        # self.timer.stop()
        self.hide()
        # nie bedzie mozliwosci edycji ustawien dla usera z poziomu login dialogu
        self.current_user = 0
        self.user_name = 'DEFAULT'
        # menu sie nie ukrywa
        self.menuBar().hide()
        self.login_page.show()

    def _delete(self, index):
        for i in range(self.passwords_lay.count()):
            if self.passwords_lay.itemAt(i).widget().index == index:
                self.passwords_lay.itemAt(i).widget().deleteLater()
                self.db.delete_password(index)
        self.refresh()
        # self.update()

    def refresh(self):
        """ma byc uzywane po wprowadzeniu zmiany do listy hasel"""
        # cos jest nie tak bo dodaje za duzo elementow
        while self.passwords_lay.count():
            self.passwords_lay.takeAt(0).widget().deleteLater()
        if self.current_user is not None:
            for i in self.db.get_user_passwords(self.current_user):
                pw_field = PasswordField(i.name, i.password, i.pk, self)
                pw_field.delete_signal.connect(self._delete)
                self.passwords_lay.addWidget(pw_field)

        self.update()

    def load_at_startup(self):
        for i in self.db.get_user_passwords(self.current_user):
            pw_field = PasswordField(i[1], i[2], i[0], self)
            pw_field.delete_signal.connect(self._delete)
            self.passwords_lay.addWidget(pw_field)
        self.update()
        self.login_page.hide()
        # self.timer.start()

    def update_encoding(self):
        worker = Worker(encode_known)
        self.threadpool.start(worker)

    def rename_user(self, e):
        if self.user_name != "DEFAULT" and self.current_user != 0:
            dialog = RenameDialog(self.user_name, self)
            if dialog.exec():
                # tu mozliwe ze nie zmienia sie nazwa do konca ale dziala XD
                new_name = dialog.return_data()
                file = (IMAGES / f"{self.user_name}.jpg")
                file.rename(file.parent / f'{new_name}.jpg')
                self.db.rename_user(self.current_user, new_name)
                self.user_name = new_name
                self.info_text.setText(new_name)
                self.update()
        else:
            WarningDialog("Renaming ERROR", "Cannot rename default user!").exec()

    def delete_user(self, e):
        if self.user_name != "DEFAULT" and self.current_user != 0:
            self.db.delete_user(self.current_user)
            (IMAGES / f"{self.user_name}.jpg").unlink()
            self._logout(None)
        else:
            WarningDialog("Deletion ERROR", "Cannot delete default user!").exec()


def start_app():
    app = QApplication([])
    main_window = MainWindow()
    main_window.hide()
    window = LoginDialog(main_window)
    window.show()
    app.exec()
