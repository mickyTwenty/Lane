from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QMessageBox

from config import _App

class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        uic.loadUi('logindialog.ui', self)

        try:
            self.btnLogin.clicked.disconnect()
            self.btnCancel.clicked.disconnect()
        except:
            pass

        self.btnLogin.clicked.connect(self.on_btnLogin_clicked)
        self.btnCancel.clicked.connect(self.on_btnCancel_clicked)

    def on_btnLogin_clicked(self):
        username = self.editUsername.text()
        if username == '':
            QMessageBox.warning(self, 'Error', 'Please input user name.')
            self.editUsername.setFocus()
            return
        
        password = self.editPassword.text()
        if password == '':
            self.editPassword.setFocus()
            QMessageBox.warning(self, 'Error', 'Please input password')
            return
        
        if self.confirmLogin(username, password) is True:
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Username/Password is incorrect.')
            return
        

    def on_btnCancel_clicked(self):
        self.reject()

    def confirmLogin(self, username, password):
        if username != _App.USER_NAME:
            return False

        if password != _App.USER_PASSWORD:
            return False

        return True

