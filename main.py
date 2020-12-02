import sys, os

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QIcon
import enum

from config import _App

from dbhelper import _DB

from logindlg import LoginDialog
from mainwidget import MainWidget
from reviewwidget import ReviewWidget



class CurrentWidget(enum.Enum):
    NONE                    = -1
    MAIN_WIDGET             = 0
    #REVIEW_WIDGET           = 1

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)

        self.setWindowTitle(_App.APP_NAME)
        self.setWindowIcon(QIcon('./res/versaicon.png')) 

        self.currentWidget = CurrentWidget.NONE

        self.mainwidget = MainWidget(self)
        #self.reviewwidget = ReviewWidget(self)

        self.mainStacked.addWidget(self.mainwidget)
        #self.mainStacked.addWidget(self.reviewwidget)

        self.actionExit.triggered.connect(self.close)
        self.actionDbClear.triggered.connect(self.mainwidget.on_dbclear_triggered)
        self.actionDbClearAll.triggered.connect(self.mainwidget.on_dbclearall_triggerd)
        self.actionDownloadFiles.triggered.connect(self.mainwidget.on_downloadfiles_triggered)

        self.setMainWidget()

        self.showMaximized()

    def setMainWidget(self):
        self.currentWidget = CurrentWidget.MAIN_WIDGET
        self.mainStacked.setCurrentIndex(self.currentWidget.value)

    '''
    def setReviewWidget(self):
        self.currentWidget = CurrentWidget.REVIEW_WIDGET
        self.mainStacked.setCurrentIndex(self.currentWidget.value)
    '''
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            _DB.closeDB()
            _App._Settings.save()

            event.accept()
    
def confirmLogin(self, username, password):
    return True

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    login = LoginDialog()
    login.show()
    if login.exec_() == QtWidgets.QDialog.Rejected:
        sys.exit()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
