from PySide2.QtWidgets import QApplication, QWidget, QScrollArea, QPushButton, QLabel, QDialog, QVBoxLayout,\
     QHBoxLayout, QMainWindow, QLineEdit, QFormLayout, QDialogButtonBox
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt, Signal


class PasswordField(QWidget):
    delete_signal = Signal(int)

    def __init__(self, name: str, password: str, index: int, parent=None):
        super(PasswordField, self).__init__(parent)
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

    def _update(self, e):
        ...

    def _show(self, e):
        if not self.hidden:
            self.password_field.setText("*******")
        else:
            self.password_field.setText(self.password)
        self.hidden = not self.hidden


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
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Password Manager")

        self.font_text = QFont("Montserrat")
        self.font_text.setPointSize(34)
        self.font_button = QFont("Lora")
        self.font_button.setPointSize(26)

        self.setFixedSize(640, 480)
        self.lay = QVBoxLayout()
        self.lay.setMargin(10)
        self.lay.setSpacing(20)

        self.text = QLabel("Hello!\nPress the login button\n in order to have\n your face scanned :)")
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setFont(self.font_text)
        self.button = QPushButton("Login")
        self.button.clicked.connect(self.detect)
        self.button.setFont(self.font_button)

        self.lay.addWidget(self.text)
        self.lay.addWidget(self.button)

        self.setLayout(self.lay)

    def detect(self):
        """Dummy method"""
        self.accept()
        self.parent().show()
        return True


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Password Manager")
        self.setFixedSize(640, 480)
        self.info_font = QFont("helvetica")
        self.info_font.setPointSize(16)

        # variables essential for the correct future functioning of the app
        self.current_user = None  # id
        self.current_index = 0

        # run login page on startup
        self.login_page = LoginDialog(self)
        self.login_page.show()
        self.hide()

        self.lay1 = QVBoxLayout()

        # widgets
        self.info_area = QHBoxLayout()
        self.info_text = QLabel("USER NAME")  # to be replaced!
        self.info_text.setFont(self.info_font)
        self.info_text.setAlignment(Qt.AlignCenter)
        self.info_area.addWidget(self.info_text)

        self.passwords_area = QScrollArea()
        self.passwords_lay = QVBoxLayout()
        self.passwords_lay.addWidget(PasswordField("Xd", "XDD", self))
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

        self.lay1.addLayout(self.info_area)
        self.lay1.addWidget(self.passwords_area)
        self.lay1.addLayout(self.controls)

        widget = QWidget()
        widget.setLayout(self.lay1)
        self.setCentralWidget(widget)

    def _clear_all(self, e):
        # db delete
        while self.passwords_lay.count():
            self.passwords_lay.takeAt(0).widget().deleteLater()
        self.update()
        self.current_index = 0

    def _add(self, e):
        dialog = AddPasswordDialog()
        if dialog.exec_() == QDialog.Accepted:
            # db
            name, password = dialog.return_data()
            pw_field = PasswordField(name, password, self.current_index)
            self.current_index += 1  # mozliwe ze bedzie do usuniecia
            pw_field.delete_signal.connect(self._delete)
            self.passwords_lay.addWidget(pw_field)
        self.update()

    def _logout(self, e):
        self.hide()
        self.login_page.show()

    def _delete(self, index):
        self.passwords_lay.takeAt(0).widget().deleteLater()  # nie bedzie dzialac po usunieciu jakiegos elementu
        self.update()


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
