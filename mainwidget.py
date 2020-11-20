import os
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import pyqtSignal, QObject, QDate, QDateTime
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QInputDialog, QMessageBox, QDialog, QVBoxLayout, QDateTimeEdit, QDialogButtonBox
from PyQt5.QtGui import QColor
import datetime
import csv
import xlsxwriter
import random
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet

from config import _App
from dbhelper import _DB

from reviewwidget import ReviewWidget

class SignalTrigger(QObject):
    # Define a new signal called 'trigger' that has no arguments.
    signal_item_loaded = pyqtSignal(int)
    signal_item_reviewed = pyqtSignal(int, str, str)


class MainWidget(QtWidgets.QWidget):
    def __init__(self, MainWindow):
        super(MainWidget, self).__init__()
        uic.loadUi('mainwidget.ui', self)

        self.MainWindow = MainWindow
        self.ReviewDlg = ReviewWidget(self)

        self.tabWidget.setCurrentIndex(0)

        self._data = []
        self._filter_data = []
        self._filtered = False

        self.report_data = []
        self.overall = 0.0
        self.report_data1 = []

        self.editDate1.setDate(QDate.currentDate().addMonths(-1))
        self.editDate2.setDate(QDate.currentDate())

        try:
            # Import Widget
            self.btnImport1.clicked.disconnect()
            self.btnImport2.clicked.disconnect()
            self.btnImport3.clicked.disconnect()

            self.btnRandom.clicked.disconnect()
            self.btnFilter.clicked.disconnect()

            # Report Widget
            self.btnRefresh.clicked.disconnect()
            self.btnExport1.clicked.disconnect()
            self.btnExport2.clicked.disconnect()
        except:
            pass

        self.btnImport1.clicked.connect(self.on_btnImport1_clicked)
        self.btnImport2.clicked.connect(self.on_btnImport2_clicked)
        self.btnImport3.clicked.connect(self.on_btnImport3_clicked)
        self.btnRandom.clicked.connect(self.on_btnRandom_clicked)
        self.btnFilter.clicked.connect(self.on_btnFilter_clicked)
        self.table.cellDoubleClicked.connect(self.on_table_doubleclicked)

        self.btnRefresh.clicked.connect(self.on_btnRefresh_clicked)
        self.btnExport1.clicked.connect(self.on_btnExport1_clicked)
        self.btnExport2.clicked.connect(self.on_btnExport2_clicked)
        self.table1.itemClicked.connect(self.on_table1_clicked)

        self.signals = SignalTrigger()
        self.signals.signal_item_loaded.connect(self.setLoadedItem)
        self.signals.signal_item_reviewed.connect(self.setReviewedItem)

    def itemLoaded(self, index):
        self.signals.signal_item_loaded.emit(index)

    def itemReviewed(self, index, review, color):
        self.signals.signal_item_reviewed.emit(index, review, color)

    def on_btnImport1_clicked(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File', './data', 'Data files (*.PTD)')
        if fname == '':
            return

        try:
            csv_data = list(csv.reader(open(fname), delimiter=';'))

            data = []

            for row in csv_data[1:]:
                path2 = row[10].replace('0.', '1.')
                row.insert(11, path2)

                data.append(row)
        except Exception as ex:
            print(ex)
            QMessageBox.warning(self, 'Error', 'Import failed. ' + str(ex))
            data = []

        self._data = data
        self._filtered = False
        self.resetDataTable()
        
        self.ReviewDlg.init(self._data)

    def on_btnImport2_clicked(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File', './data', 'Data files (*.PTD)')
        if fname == '':
            return

        try:
            csv_data = list(csv.reader(open(fname), delimiter=';'))

            data = []

            LID = ''
            TNO = ''
            DATE = ''
            for row in csv_data[1:]:
                if LID != row[4] or TNO != row[0] or DATE != row[2]:
                    row.insert(11, '')
                    data.append(row)
                    LID = row[4]
                    TNO = row[0]
                    DATE = row[2]
                else:
                    data[-1][11] = row[10]
        except Exception as ex:
            print(ex)
            QMessageBox.warning(self, 'Error', 'Import failed. ' + str(ex))
            data = []

        self._data = data
        self._filtered = False
        self.resetDataTable()

        self.ReviewDlg.init(self._data)

    def on_btnImport3_clicked(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File', './data', 'Data files (*.log)')
        if fname == '':
            return

        lane_id, ok = QInputDialog.getText(self, 'Import Cube Log', 'Input Lane ID')

        if ok is False or lane_id == '':
            return

        try:
            csv_data = list(csv.reader(open(fname), delimiter=';'))

            data = []

            for row in csv_data:
                date1 = datetime.datetime.strptime(row[0] + row[1], '%Y%m%d%H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f')
                path1 = '/img_hist/{}'.format(row[2])

                data.append(['', '', date1, '', lane_id, '', '', row[7], '', '', path1, '', '', ''])
        except Exception as ex:
            print(ex)
            QMessageBox.warning(self, 'Error', 'Import failed. ' + str(ex))
            data = []

        self._data = data
        self._filtered = False
        self.resetDataTable()

        self.ReviewDlg.init(self._data)

    def on_btnRandom_clicked(self):
        if len(self._data) == 0:
            return

        count, ok = QInputDialog.getInt(self, 'Random', 'Input count of entries', 200)

        if ok is False or count == 0:
            return

        _temp = []
        if self._filtered is True:
            _temp = self._filter_data[:]
        else:
            _temp = self._data[:]

        if len(_temp) < count:
            QMessageBox.warning(self, 'Error', 'Please input count less than {}.'.format(len(_temp)))
            return
        
        data = []

        while count > 0 :
            i = random.randint(0, len(_temp) - 1)
            data.append(_temp[i])

            _temp.pop(i)
            
            count -= 1

        self._filtered = True
        self._filter_data = data
        self.resetDataTable()
        self.ReviewDlg.setData(self._filter_data)

        self.btnFilter.setText('Clear Filter')

    def on_btnFilter_clicked(self):
        if self._filtered is True:
            self._filtered = False
            self.resetDataTable()
            self.ReviewDlg.setData(self._data)

            self.btnFilter.setText('Set Filter')
        else:
            lane_id, ok = QInputDialog.getText(self, 'Filter', 'Input Lane ID')

            if ok is False or lane_id == '':
                return
            
            self._filtered = True
            self._filter_data = [item for item in self._data if item[4] == lane_id]
            self.resetDataTable()
            self.ReviewDlg.setData(self._filter_data)

            self.btnFilter.setText('Clear Filter')
    

    def resetDataTable(self):
        data = []

        if self._filtered:
            data = self._filter_data
        else:
            data = self._data

        self.table.setRowCount(0)
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                titem = QTableWidgetItem(item)
                self.table.setItem(i, j, titem)
        
        self.resetTableColumnWidth()
        

    def resetTableColumnWidth(self):
        self.table.resizeColumnsToContents()
        
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(10, 150)
        self.table.setColumnWidth(11, 150)
        self.table.setColumnWidth(14, 100)

    def on_table_doubleclicked(self, row, col):
        #self.ReviewDlg.init(self._data, row)
        self.ReviewDlg.setCurrentRow(row)
        self.ReviewDlg.exec_()

    @QtCore.pyqtSlot(int)
    def setLoadedItem(self, index):
        self.table.selectRow(index)

    @QtCore.pyqtSlot(int, str, str)
    def setReviewedItem(self, index, review, color):
        self.table.setItem(index, 14, QTableWidgetItem(review))
        self.setColortoRow(self.table, index, color)

    def setColortoRow(self, table, rowIndex, color):
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(QColor(color))

    def on_btnRefresh_clicked(self):
        date1 = self.editDate1.date().toString('yyyy-MM-dd')
        date2 = self.editDate2.date().addDays(1).toString('yyyy-MM-dd')

        self.report_data, self.overall, self.report_data1 = _DB.get_report_data(date1, date2)

        self.lblOverall.setText('{:.2f}%'.format(self.overall))

        self.table1.setRowCount(0)
        self.table1.setRowCount(len(self.report_data))

        for i, row in enumerate(self.report_data):
            for j, item in enumerate(row):
                titem = QTableWidgetItem(str(item))
                if j > 3:
                    titem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.table1.setItem(i, j, titem)
        
        self.table2.setRowCount(0)
        self.table2.setRowCount(len( self.report_data1))

        for i, row in enumerate( self.report_data1):
            for j, item in enumerate(row):
                titem = QTableWidgetItem(str(item))
                self.table2.setItem(i, j, titem)

        self.table2.resizeColumnsToContents()
    
    def on_table1_clicked(self, item):
        lane_id = self.table1.item(item.row(), 3).text()
        date1 = self.editDate1.date().toString('yyyy-MM-dd')
        date2 = self.editDate2.date().addDays(1).toString('yyyy-MM-dd')

        data = _DB.get_reviewed_data(lane_id, date1, date2)

        self.table2.setRowCount(0)
        self.table2.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                titem = QTableWidgetItem(str(item))
                self.table2.setItem(i, j, titem)

        self.table2.resizeColumnsToContents()

    def on_btnExport1_clicked(self):
        print('Export CSV')
        if len(self.report_data) == 0:
            QMessageBox.warning(self, 'Warning', 'No report data')
            return

        fname, _ = QFileDialog.getSaveFileName(self, 'Save File', './', 'Excel file (*.xlsx)')
        if fname == '':
            return

        try:
            workbook = xlsxwriter.Workbook(fname)
            worksheet = workbook.add_worksheet()

            worksheet.set_column('A:A', 10)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:E', 20)
            worksheet.set_column('F:L', 15)
            worksheet.set_column('M:M', 20)

            worksheet.merge_range('A1:C4', None)
            worksheet.insert_image('A1', './res/versalogo.png')

            header = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#d9d9d9', 'border': 1 })

            worksheet.merge_range('D3:E3', None)
            worksheet.write('D3', 'Overall Site Performance', header)
            worksheet.write('F3', '{:.2f}%'.format(self.overall), header)

            worksheet.write('A6', '#', header)
            worksheet.write('B6', 'Lane', header)
            worksheet.write('C6', 'Description', header)
            worksheet.write('D6', 'Car Park', header)
            worksheet.write('E6', 'LPR Lane ID', header)
            worksheet.write('F6', 'Accuracy', header)
            worksheet.write('G6', 'No of Samples', header)
            worksheet.write('H6', 'Actual Samples', header)
            worksheet.write('I6', 'Good Readings', header)
            worksheet.write('J6', 'Bad Readings', header)
            worksheet.write('K6', 'False Triggers', header)
            worksheet.write('L6', 'Damaged Plate', header)
            worksheet.write('M6', 'Review Date', header)

            style1 = workbook.add_format({'align': 'right', 'bg_color': '#c8c8c8', 'border': 1})
            style2 = workbook.add_format({'align': 'left', 'bg_color': '#c8c8c8', 'border': 1})
            style3 = workbook.add_format({'align': 'center', 'bg_color': 'green', 'border': 1})
            style4 = workbook.add_format({'align': 'center', 'border': 1})

            for i, row in enumerate(self.report_data):
                worksheet.write('A{}'.format(7 + i), str(i + 1), style1)
                worksheet.write('B{}'.format(7 + i), row[0], style2)
                worksheet.write('C{}'.format(7 + i), row[1], style2)
                worksheet.write('D{}'.format(7 + i), row[2], style2)
                worksheet.write('E{}'.format(7 + i), row[3], style2)
                worksheet.write('F{}'.format(7 + i), row[4], style3)
                worksheet.write('G{}'.format(7 + i), row[5], style4)
                worksheet.write('H{}'.format(7 + i), row[6], style4)
                worksheet.write('I{}'.format(7 + i), row[7], style4)
                worksheet.write('J{}'.format(7 + i), row[8], style4)
                worksheet.write('K{}'.format(7 + i), row[9], style4)
                worksheet.write('L{}'.format(7 + i), row[10], style4)
                worksheet.write('M{}'.format(7 + i), row[11], style4)

            worksheet.freeze_panes(6, 3)

            worksheet = workbook.add_worksheet()

            worksheet.set_column('A:A', 10)
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 40)
            worksheet.set_column('E:H', 10)
            worksheet.set_column('I:I', 65)
            worksheet.set_column('J:J', 25)
            worksheet.set_column('K:L', 15)

            worksheet.write('A1', '#', header)
            worksheet.write('B1', 'Ticket Number', header)
            worksheet.write('C1', 'Ticket Typ', header)
            worksheet.write('D1', 'Date', header)
            worksheet.write('E1', 'Lane ID', header)
            worksheet.write('F1', 'Rego Result', header)
            worksheet.write('G1', 'Confident', header)
            worksheet.write('H1', 'Corrected Plate', header)
            worksheet.write('I1', 'Image Path', header)
            worksheet.write('J1', 'Date Edited', header)
            worksheet.write('K1', 'Attendance', header)
            worksheet.write('L1', 'Review', header)

            for i, row in enumerate(self.report_data1):
                worksheet.write('A{}'.format(2 + i), str(i + 1), style1)
                worksheet.write('B{}'.format(2 + i), row[0], style2)
                worksheet.write('C{}'.format(2 + i), row[1], style2)
                worksheet.write('D{}'.format(2 + i), row[2], style2)
                worksheet.write('E{}'.format(2 + i), row[3], style2)
                worksheet.write('F{}'.format(2 + i), row[4], style2)
                worksheet.write('G{}'.format(2 + i), row[5], style4)
                worksheet.write('H{}'.format(2 + i), row[6], style4)
                worksheet.write('I{}'.format(2 + i), row[7], style4)
                worksheet.write('J{}'.format(2 + i), row[8], style4)
                worksheet.write('K{}'.format(2 + i), row[9], style4)
                worksheet.write('L{}'.format(2 + i), row[10], style4)

            worksheet.freeze_panes(1, 0)

            workbook.close()
        except Exception as ex:
            print(ex)
            QMessageBox.warning(self, 'Error', str(ex))
            return
        
        QMessageBox.information(self, 'Report', 'Success to report as {}'.format(fname))

    def on_btnExport2_clicked(self):
        print('Export PDF')
        if len(self.report_data) == 0:
            QMessageBox.warning(self, 'Warning', 'No report data')
            return

        fname, _ = QFileDialog.getSaveFileName(self, 'Save File', './', 'Pdf file (*.pdf)')
        if fname == '':
            return

        try:
            elements = []

            # PDF Text
            # PDF Text - Styles
            styles = getSampleStyleSheet()
            styleNormal = styles['Normal']

            # PDF Text - Content
            line1 = 'Date: {}'.format(_App.getDateTimeStamp("%m/%d/%Y"))
            line2 = 'Overall Site Performance: {:.2f}%'.format(self.overall)

            elements.append(Image('./res/versalogo.png', 2 * inch, 0.5 * inch))
            elements.append(Paragraph(line1, styleNormal))
            elements.append(Paragraph(line2, styleNormal))
            elements.append(Spacer(inch, .25 * inch))

            # PDF Table
            # PDF Table - Styles
            # [(start_column, start_row), (end_column, end_row)]
            all_cells = [(0, 0), (-1, -1)]
            header = [(0, 0), (-1, 0)]
            column0 = [(0, 0), (0, -1)]
            column1 = [(1, 0), (1, -1)]
            column2 = [(2, 0), (2, -1)]
            column3 = [(3, 0), (3, -1)]
            column4 = [(4, 0), (4, -1)]
            column5 = [(5, 0), (5, -1)]
            column6 = [(6, 0), (6, -1)]
            column7 = [(7, 0), (7, -1)]
            column8 = [(8, 0), (8, -1)]
            column9 = [(9, 0), (9, -1)]
            column10 = [(10, 0), (10, -1)]
            column11 = [(11, 0), (11, -1)]
            table_style = TableStyle([
                ('VALIGN', all_cells[0], all_cells[1], 'TOP'),
                ('LINEBELOW', header[0], header[1], 1, colors.black),
                ('ALIGN', column0[0], column0[1], 'LEFT'),
                ('ALIGN', column1[0], column1[1], 'LEFT'),
                ('ALIGN', column2[0], column2[1], 'LEFT'),
                ('ALIGN', column3[0], column3[1], 'LEFT'),
                ('ALIGN', column4[0], column4[1], 'CENTER'),
                ('ALIGN', column5[0], column5[1], 'CENTER'),
                ('ALIGN', column6[0], column6[1], 'CENTER'),
                ('ALIGN', column7[0], column7[1], 'CENTER'),
                ('ALIGN', column8[0], column8[1], 'CENTER'),
                ('ALIGN', column9[0], column9[1], 'CENTER'),
                ('ALIGN', column10[0], column10[1], 'CENTER'),
                ('ALIGN', column11[0], column11[1], 'CENTER'),

                ('VALIGN', header[0], header[1], 'BOTTOM'),
                ('ALIGN', header[0], header[1], 'CENTER'),
                ('FONTSIZE', header[0], header[1], 12),
            ])

            # PDF Table - Column Widths
            colWidths = [
                2.2 * cm,  # Column 0
                4.0 * cm,  # Column 1
                4.0 * cm,  # Column 2
                2.3 * cm,  # Column 3
                3.0 * cm,  # Column 4
                2.0 * cm,  # Column 5
                2.0 * cm,  # Column 6
                2.0 * cm,  # Column 7
                2.0 * cm,  # Column 8
                2.0 * cm,  # Column 9
                2.0 * cm,  # Column 10
                4.0 * cm,  # Column 11
            ]

            # PDF Table - Strip '[]() and add word wrap to column 5
            '''
            for index, row in enumerate(data):
                for col, val in enumerate(row):
                    if col != 5 or index == 0:
                        data[index][col] = val.strip("'[]()")
                    else:
                        data[index][col] = Paragraph(val, styles['Normal'])
            '''

            # Add table to elements
            t = Table([['Lane', 'Description', 'Car Park', 'LPR\nLane ID', 'Accuracy', 'No of\nSamples', 'Actual\nSamples', 'Good\nReadings', 'Bad\nReadings', 'False\nTriggers', 'Damaged\nPlate', 'Review Date']] + self.report_data, colWidths = colWidths)
            t.setStyle(table_style)
            elements.append(t)


            table_style1 = TableStyle([
                ('VALIGN', all_cells[0], all_cells[1], 'TOP'),
                ('FONTSIZE', all_cells[0], all_cells[1], 8),
                ('LINEBELOW', header[0], header[1], 1, colors.black),
                ('ALIGN', column0[0], column0[1], 'LEFT'),
                ('ALIGN', column1[0], column1[1], 'LEFT'),
                ('ALIGN', column2[0], column2[1], 'LEFT'),
                ('ALIGN', column3[0], column3[1], 'LEFT'),
                ('ALIGN', column4[0], column4[1], 'LEFT'),
                ('ALIGN', column5[0], column5[1], 'CENTER'),
                ('ALIGN', column6[0], column6[1], 'CENTER'),
                ('ALIGN', column7[0], column7[1], 'CENTER'),
                ('ALIGN', column8[0], column8[1], 'CENTER'),
                ('ALIGN', column9[0], column9[1], 'CENTER'),
                ('ALIGN', column10[0], column10[1], 'CENTER'),

                ('VALIGN', header[0], header[1], 'BOTTOM'),
                ('ALIGN', header[0], header[1], 'CENTER'),
                ('FONTSIZE', header[0], header[1], 12),
            ])

            # PDF Table - Column Widths
            colWidths1 = [
                4.7 * cm,  # Column 0
                5.5 * cm,  # Column 1
                6.0 * cm,  # Column 2
                1.5 * cm,  # Column 3
                2.5 * cm,  # Column 4
                2.5 * cm,  # Column 5
                3.0 * cm,  # Column 6
                10.0 * cm,  # Column 7
                5.0 * cm,  # Column 8
                2.5 * cm,  # Column 9
                3.5 * cm,  # Column 10
            ]
            
            elements.append(Spacer(inch, .25 * inch))
            t1 = Table([['Ticket Number', 'Ticket Typ', 'Date', 'Lane ID', 'Rego Result', 'Confident', 'Corrected\nPlate', 'Image Path', 'Date Edited', 'Attendance', 'Review']] + self.report_data1, colWidths=colWidths1)
            t1.setStyle(table_style1)
            elements.append(t1)

            # Generate PDF
            archivo_pdf = SimpleDocTemplate(
                fname,
                pagesize = landscape((18*inch, 8.5*inch)),
                rightMargin = 40,
                leftMargin = 40,
                topMargin = 40,
                bottomMargin = 28)
            archivo_pdf.build(elements)
        except Exception as ex:
            print(ex)
            QMessageBox.warning(self, 'Error', str(ex))
            return
        
        QMessageBox.information(self, 'Report', 'Success to report as {}'.format(fname))

    def on_dbclear_triggered(self):
        print('Clear DB')
        date, time, ok = DateDialog.getDateTime()
        if ok is False:
            return
        _DB.clear_db(date)
        QMessageBox.information(self, 'Report', 'Success to clear')


    def on_dbclearall_triggerd(self):
        print('Clear All Db')
        _DB.clear_db()
        QMessageBox.information(self, 'DB', 'Success to clear all')
        

class DateDialog(QDialog):
    def __init__(self, parent = None):
        super(DateDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        # nice widget for editing the date
        self.datetime = QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent = None):
        dialog = DateDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime()
        return (date.date(), date.time(), result == QDialog.Accepted)