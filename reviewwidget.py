import os
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QPixmap
from pathlib import Path
from shutil import copyfile, copy

from config import _App
from dbhelper import _DB

subdirs = ['Correct', 'Incorrect']

class ReviewWidget(QtWidgets.QDialog):
    def __init__(self, MainWidget):
        super(ReviewWidget, self).__init__()
        uic.loadUi('reviewwidget.ui', self)

        self.MainWidget = MainWidget

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WA_ShowWithoutActivating)
        self.setModal(True)

        self._data = []
        self._index = -1
        self._rowid = -1
        self._item = []
        self._lanes = {}
        self.imgfile1 = ''
        self.imgfile2 = ''

        try:
            self.btnPrev.clicked.disconnect()
            self.btnNext.clicked.disconnect()
            self.btnSetValue1.clicked.disconnect()
            self.btnSetValue2.clicked.disconnect()
            self.btnSetValue3.clicked.disconnect()
            self.btnSetValue4.clicked.disconnect()
            self.btnClose.clicked.disconnect()
        except:
            pass

        self.btnPrev.clicked.connect(self.on_btnPrev_clicked)
        self.btnNext.clicked.connect(self.on_btnNext_clicked)

        self.btnSetValue1.clicked.connect(self.on_btnSetValue1_clicked)
        self.btnSetValue2.clicked.connect(self.on_btnSetValue2_clicked)
        self.btnSetValue3.clicked.connect(self.on_btnSetValue3_clicked)
        self.btnSetValue4.clicked.connect(self.on_btnSetValue4_clicked)

        self.btnClose.clicked.connect(self.reject)

    def init(self, data):
        self._data = data
        self._index = -1
        self._rowid = -1
        self._item = []
        self._lanes = {}
        self.lanetable.setRowCount(0)
        #self.loadItem()

    def setCurrentRow(self, index):
        self._index = index
        self.loadItem()
    
    def setData(self, data):
        self._data = data

    def loadItem(self):
        item_data, self._rowid = _DB.select_item(self._data[self._index])

        self.lblLaneID.setText(item_data[5])
        self.lblLaneName.setText(item_data[6])
        self.lblLaneType.setText(item_data[7])
        self.lblTicketNo.setText(item_data[1])
        self.lblTicketType.setText(item_data[2])
        self.lblDate1.setText(item_data[3])
        self.lblDate2.setText(item_data[4])
        self.lblDate3.setText(item_data[13])
        self.lblAttendance.setText(item_data[14])
        self.lblImagePath.setText(item_data[11])
        self.lblImagePath2.setText(item_data[12])
        
        self.lblResult.setText(item_data[8])
        self.lblConfident.setText(item_data[9])
        self.lblNewPlate.setText(item_data[10])

        self.imgfile1 = item_data[11]
        img1 = QPixmap(_App.img_path + self.imgfile1)
        if img1.isNull() is False:
            img1 = self.scaleImage(img1, self.lblImage1.width(), self.lblImage1.height())
            self.lblImage1.setPixmap(img1)
        else:
            self.lblImage1.setPixmap(QPixmap())

        self.imgfile2 = item_data[12]
        img2 = QPixmap(_App.img_path + self.imgfile2)
        if img2.isNull() is False:
            img2 = self.scaleImage(img2, self.lblImage2.width(), self.lblImage2.height())
            self.lblImage2.setPixmap(img2)
        else:
            self.lblImage2.setPixmap(QPixmap())

        if self._rowid != -1:
            review_str = _App.REVIEW_STR[item_data[15]]
            review_style = _App.REVIEW_STYLE[item_data[15]]
            review_color = _App.REVIEW_COLOR[item_data[15]]
            self.lblReview.setText(review_str)
            self.lblReview.setStyleSheet(review_style)
            self.MainWidget.itemReviewed(self._index, review_str, review_color)

            if len(self._data[self._index]) == 14:
                self.updateLanes(item_data[5])
                self._data[self._index].append(True)

        else:
            self.lblReview.setText('')


        if self._index == 0:
            self.btnPrev.setEnabled(False)
            self.btnNext.setEnabled(True)
        elif self._index == len(self._data) - 1:
            self.btnPrev.setEnabled(True)
            self.btnNext.setEnabled(False)
        else:
            self.btnPrev.setEnabled(True)
            self.btnNext.setEnabled(True)

        self._item = item_data
        self.MainWidget.itemLoaded(self._index)

    def loadNextItem(self):
        if self._index < len(self._data) - 1:
            self._index += 1
        self.loadItem()

    def scaleImage(self, image, lblW, lblH):
        w = min(image.width(), lblW)
        h = min(image.height(), lblH)
        return  image.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

    def on_btnPrev_clicked(self):
        if len(self._data) == 0:
            return

        self._index = self._index - 1
        self.loadItem()

    def on_btnNext_clicked(self):
        if len(self._data) == 0:
            return
        
        self._index = self._index + 1
        self.loadItem()

    def on_btnSetValue1_clicked(self):
        if self.setReview(0) is True:
            self.loadNextItem()

    def on_btnSetValue2_clicked(self):
        if self.setReview(1) is True:
            self.loadNextItem()

    def on_btnSetValue3_clicked(self):
        if self.setReview(2) is True:
            self.loadNextItem()

    def on_btnSetValue4_clicked(self):
        if self.setReview(3) is True:
            self.loadNextItem()

    def setReview(self, value):
        item = self._data[self._index]
        if item is None:
            return False

        if self._rowid != -1 and self._item[15] == value:
            return True

        if self._rowid != -1 and ( self._item[15] == 0  or self._item[15] == 1 ) :
            path1 = '/Lane{}/{}/'.format(item[4], subdirs[self._item[15]]) + os.path.basename(self._item[11])
            path2 = '/Lane{}/{}/'.format(item[4], subdirs[self._item[15]]) + os.path.basename(self._item[12])

            if self._item[11] != '' and os.path.exists(_App.review_path + path1):
                os.remove(_App.review_path + path1)

            if self._item[12] != '' and os.path.exists(_App.review_path + path2):
                os.remove(_App.review_path + path2)
                
        _DB.set_item_review(item, value, self._rowid)

        if self._rowid == -1:
            self.updateLanes(item[4])
            self._data[self._index].append(True)

        if value == 0 or value == 1:
            target_dir = '/Lane{}/{}'.format(item[4], subdirs[value])

            #if os.path.exists(_App.review_path + target_dir) is False:
            Path(_App.review_path + target_dir).mkdir(parents=True, exist_ok=True)

            if self.imgfile1 != ''  and os.path.exists(_App.img_path + self.imgfile1):
                copy(_App.img_path + self.imgfile1, _App.review_path + target_dir)

            if self.imgfile2 != ''  and os.path.exists(_App.img_path + self.imgfile2):
                copy(_App.img_path + self.imgfile2, _App.review_path + target_dir)

        review_str = _App.REVIEW_STR[value]
        review_style = _App.REVIEW_STYLE[value]
        review_color = _App.REVIEW_COLOR[value]
        self.lblReview.setText(review_str)
        self.lblReview.setStyleSheet(review_style)
        self.MainWidget.itemReviewed(self._index, review_str, review_color)

        
        return True

    def updateLanes(self, id):        
        lane_id = 'Lane{}'.format(id)
        if lane_id in self._lanes:
            self._lanes[lane_id] += 1
        else:
            self._lanes[lane_id] = 1

        is_new = True
        for i in range(self.lanetable.rowCount()):
            if self.lanetable.item(i, 0).text() == lane_id:
                is_new = False
                self.lanetable.item(i, 1).setText(str(self._lanes[lane_id]))
                self.lanetable.selectRow(i)
        
        if is_new:
            row_count = self.lanetable.rowCount()
            self.lanetable.insertRow(row_count)
            item1 = QtWidgets.QTableWidgetItem(lane_id)
            item2 = QtWidgets.QTableWidgetItem(str(self._lanes[lane_id]))
            self.lanetable.setItem(row_count, 0, item1)
            self.lanetable.setItem(item1.row(), 1, item2)
            self.lanetable.selectRow(item1.row())
        


    
    





        
