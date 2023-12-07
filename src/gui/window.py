from warnings import simplefilter
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,\
    QMainWindow, QDialog
from PySide6.QtCore import QRunnable, Slot, QThreadPool, QTimer, Signal, Qt
from PySide6.QtGui import QFont, QAction
from src.gui.dialogs import LoadDialog, ExportDialog, ManualDialog, RenameDialog, WarningDialog, UpdatePasswordDialog,\
    AddPasswordDialog, LoginDialog
from src.db import DBControl
from src.face_rec_easier import encode_known

simplefilter("ignore")
IMAGES = Path(__file__).parent.parent / 'images'
MANUALS = Path(__file__).parent.parent / 'data' / 'manuals.gif'


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

    def _delete(self, _):
        self.delete_signal.emit(self.index)
        # self.main_window.db.delete_password(self.index)  # delete in db

    def _update(self, _):
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

    def _show(self, _):
        if not self.hidden:
            self.password_field.setText("*******")
        else:
            self.password_field.setText(self.password)
        self.hidden = not self.hidden

    def get_index(self):
        return self.index


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
        # starts at login dialog hence an user is logged out
        self.logged_out = True

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
        # tu byl blad z duplikowaniem
        # self.load_at_startup()
        self.passwords_area.setLayout(self.passwords_lay)

        self.controls = QHBoxLayout()
        self.clear_all_button = QPushButton("Clear all")
        self.clear_all_button.setStatusTip("Clears all passwords")
        self.clear_all_button.clicked.connect(self._clear_all)
        self.add_button = QPushButton("Add")
        self.add_button.setStatusTip("Adds a new password")
        self.add_button.clicked.connect(self._add)
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStatusTip("Logs out an user")
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

        export_action = QAction("Export", self)
        export_action.setStatusTip("Export your passwords in csv format")
        export_action.triggered.connect(self.export_passwords)

        load_action = QAction("Load", self)
        load_action.setStatusTip("Load passwords from a csv file")
        load_action.triggered.connect(self.load_passwords)

        logout_action = QAction("Logout", self)
        logout_action.setStatusTip("Logout")
        logout_action.triggered.connect(self._logout)

        manual_action = QAction("Manual", self)
        manual_action.setStatusTip("Apps's manuals")
        manual_action.triggered.connect(self.load_manuals)

        # menu
        controls_menu = self.menuBar().addMenu("&Controls")
        controls_menu.addAction(clear_action)
        controls_menu.addAction(add_action)
        controls_menu.addAction(export_action)
        controls_menu.addAction(load_action)
        controls_menu.addSeparator()
        controls_menu.addAction(logout_action)

        user_menu = self.menuBar().addMenu("User")
        user_menu.addAction(user_rename)
        user_menu.addAction(user_delete)

        manual_menu = self.menuBar().addMenu("Manual")
        manual_menu.addAction(manual_action)

        self.lay1.addLayout(self.info_area)
        self.lay1.addWidget(self.passwords_area)
        self.lay1.addLayout(self.controls)

        widget = QWidget()
        widget.setLayout(self.lay1)
        self.setCentralWidget(widget)

    def _clear_all(self, _):
        while self.passwords_lay.count():
            self.passwords_lay.takeAt(0).widget().deleteLater()
        """for child in self.passwords_lay.children():
            child.deleteLater()
        self.passwords_lay.children().clear()"""  # mozliwe ze nie jest to dobry pomysl
        if self.current_user is not None:  # bedzie mozna to potem usunac
            self.db.clear_passwords_user(self.current_user)  # dziala
        self.refresh()
        # self.current_index = 0

    def _add(self, _):
        dialog = AddPasswordDialog()
        if dialog.exec() == QDialog.Accepted and self.current_user is not None:
            # db
            name, password = dialog.return_data()
            index = self.db.add_password(name, password, self.current_user)
            pw_field = PasswordField(name, password, index, self)  # tu jest glowny problem dodawania i usuwania
            pw_field.delete_signal.connect(self._delete)
            self.passwords_lay.addWidget(pw_field)
        self.update()

    def _logout(self, _):
        if not self.logged_out:
            while self.passwords_lay.count():
                self.passwords_lay.takeAt(0).widget().deleteLater()
            # self.timer.stop()
            self.hide()
            # nie bedzie mozliwosci edycji ustawien dla usera z poziomu login dialogu
            self.current_user = 0
            self.user_name = 'DEFAULT'
            self.logged_out = True
            # menu sie nie ukrywa
            self.menuBar().hide()
            self.login_page.show()
        else:
            WarningDialog("Wrong Action", "You cannot log out while already being logged out!").exec()

    def _delete(self, index):
        # requires two clicks to delete
        # ale po update'cie juz nie
        # w skrocie jest Kongo XD
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
            pw_field = PasswordField(i.name, i.password, i.pk, self)
            pw_field.delete_signal.connect(self._delete)
            self.passwords_lay.addWidget(pw_field)
        self.update()
        self.login_page.hide()
        # logged in
        self.logged_out = False
        # self.timer.start()

    def update_encoding(self):
        worker = Worker(encode_known)
        self.threadpool.start(worker)

    def rename_user(self, _):
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

    def export_passwords(self, _):
        ExportDialog(self).exec()

    def load_passwords(self, _):
        dialog = LoadDialog(self)
        if dialog.exec():
            for i in dialog.get_file():
                self.db.add_password(i.name, i.password, self.current_user)
        self.refresh()

    def load_manuals(self, _):
        ManualDialog(self.logged_out, self).exec()


def start_app():
    app = QApplication([])
    main_window = MainWindow()
    main_window.hide()
    window = LoginDialog(main_window)
    window.show()
    app.exec()
