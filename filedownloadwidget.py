import os
import zipfile
import time
from datetime import datetime, timedelta
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from config import _App
from dbhelper import _DB

def hourly_it(start, finish):
    while finish > start:
        yield start
        start = start + timedelta(hours=1)

class FileDownloadWidget(QtWidgets.QDialog):
    def __init__(self, MainWidget):
        super(FileDownloadWidget, self).__init__()
        uic.loadUi('downloadfiles.ui', self)

        self.MainWidget = MainWidget

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WA_ShowWithoutActivating)
        self.setModal(True)

        try:
            self.btnBrowse.clicked.disconnect()
            self.btnBrowse1.clicked.disconnect()
            self.btnDownload.clicked.disconnect()
            self.btnClose.clicked.disconnect()
        except:
            pass

        self.btnBrowse.clicked.connect(self.on_btnBrowse_clicked)
        self.btnBrowse1.clicked.connect(self.on_btnBrowse1_clicked)
        self.btnDownload.clicked.connect(self.on_btnDownload_clicked)
        self.btnClose.clicked.connect(self.reject)

        self.progressBar.setValue(0)

        self.editServer.setText(_App._Settings.SERVER_DIR)
        self.editDownload.setText(_App._Settings.DOWNLOAD_DIR)
        self.editDate.setDate(QDate.currentDate())
        self.loadServerDirectory()

        self.timediff = time.altzone / (60 * 60)

    def on_btnBrowse_clicked(self):
        server_dir = QFileDialog.getExistingDirectory(self, 'Select a directory', _App._Settings.SERVER_DIR)
        if server_dir == '':
            return

        self.editServer.setText(server_dir)
        _App._Settings.SERVER_DIR = server_dir

        self.loadServerDirectory()

    def on_btnBrowse1_clicked(self):
        download_dir = QFileDialog.getExistingDirectory(self, 'Select a directory', _App._Settings.DOWNLOAD_DIR)
        if download_dir == '':
            return

        self.editDownload.setText(download_dir)

    def on_btnDownload_clicked(self):
        checked_lanes = []
        server_dir = self.editServer.text()
        download_dir = self.editDownload.text()

        if server_dir == '':
            QMessageBox.warning(self, 'Error', 'Please select server directory.')
            self.btnBrowse.setFocus()
            return

        if download_dir == '':
            QMessageBox.warning(self, 'Error', 'Please select download directory.')
            self.btnBrowse1.setFocus()
            return

        date = self.editDate.date().toString('yyyyMMdd')
        date_from = datetime.strptime(date, '%Y%m%d')
        date_to = date_from + timedelta(days=1)
        if self.cmbHour.currentIndex() != 0:
            hour = self.cmbHour.currentIndex() - 1
            date = date + '_' + self.cmbHour.currentText()
            date_from = date_from + timedelta(hours=hour)
            date_to = date_from + timedelta(hours=1)

        date_from = date_from + timedelta(hours=self.timediff)
        date_to = date_to + timedelta(hours=self.timediff)

        sub_paths = []
        for hour in hourly_it(date_from, date_to):
            sub_paths.append('/{}/{}'.format(hour.strftime('%Y%m%d'), hour.strftime('%H')))

        '''
        date = self.editDate.date().toString('yyyyMMdd')
        sub_path = '/{}'.format(date)
        if self.cmbHour.currentIndex() != 0:
            hour = self.cmbHour.currentText()
            sub_path += '/{}'.format(hour)
        '''

        zip_filepath = '{}/download_{}.zip'.format(download_dir, date)

        if os.path.isfile(zip_filepath):
            reply = QMessageBox.question(self, 'Download', "Overwrite zip file?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        for index in range(self.listLanes.count()):
            if self.listLanes.item(index).checkState() == QtCore.Qt.Checked:
                checked_lanes.append(self.listLanes.item(index).text())

        if len(checked_lanes) == 0:
            QMessageBox.warning(self, 'Error', 'Please select lanes.')
            self.listLanes.setFocus()
            return

        zip_file = zipfile.ZipFile(zip_filepath, 'w')

        self.progressBar.setMaximum(len(checked_lanes))

        QtWidgets.QApplication.processEvents()
        
        for i, lane in enumerate(checked_lanes):
            for sub_path in sub_paths:
                path = '/{}{}'.format(lane, sub_path)
                self.zipfolder(zip_file, server_dir + path, server_dir)
                #zip_file.write(server_dir + path, path)
                self.progressBar.setValue(i + 1)

        zip_file.close()
        QMessageBox.information(self, 'Download', '{} successfully downloaded.'.format(zip_filepath))
        self.progressBar.setValue(0)
        _App._Settings.DOWNLOAD_DIR = self.editDownload.text()

    def zipfolder(self, zipobj, target_dir, base_dir):            
        #zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
        rootlen = len(base_dir) + 1
        for base, dirs, files in os.walk(target_dir):
            for file in files:
                fn = os.path.join(base, file)
                zipobj.write(fn, fn[rootlen:])

    def loadServerDirectory(self):
        server_dir = self.editServer.text()
        self.listLanes.clear()

        if server_dir == '' or not os.path.isdir(server_dir):
            return

        #subfolders= [f.name for f in os.scandir(server_dir) if f.is_dir()]
        for f in os.scandir(server_dir):
            if f.is_dir():
                item = QtWidgets.QListWidgetItem(f.name)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.listLanes.addItem(item)
