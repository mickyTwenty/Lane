from PyQt5.QtCore import QMutex
import sqlite3
from sqlite3 import Error

from config import _App

global _DB

db_file = "./data.db"


class DBHelper():
    def __init__(self):
        self.mutex = QMutex()

        try:
            print("DB Connecting...")
            self.conn = sqlite3.connect(db_file)
            print("DB Connected: ", db_file)

        except Error as e:
            print(e)
    
    def closeDB(self):
        print("DB Closing...")
        self.conn.commit()
        self.conn.close()

    def insert_new_row(self, data):
        row_id = None

        try:
            self.mutex.lock()
            cur = self.conn.cursor()

            cur.execute("SELECT ID FROM tbl_datas WHERE TICKET_NO=:T_NO AND DATE1=:DATE1 AND DATE2=:DATE2", {"T_NO": data[0], "DATE1": data[2], "DATE2": data[3]})
            row_id = cur.fetchone()

            if row_id is None:
                row_id = cur.execute("INSERT INTO tbl_datas(TICKET_NO, TICKET_TYPE, DATE1, DATE2, LANE_ID, LANE_NAME, LANE_TYPE, REGO_RESULT, CONFIDENT, CORRECTED_PLATE, IMAGE_PATH1, DATE_EDITED, ATTENDANCE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
                self.conn.commit()

        except Error as e:
            print(e)
        finally:
            self.mutex.unlock()
            return row_id
    
    def select_item(self, data):
        row = None
        rowid = -1

        try:
            self.mutex.lock()
            cur = self.conn.cursor()

            cur.execute("SELECT * FROM tbl_datas WHERE LANE_ID=:L_ID AND TICKET_NO=:T_NO AND DATE1=:DATE1 AND DATE2=:DATE2", {"L_ID": data[4], "T_NO": data[0], "DATE1": data[2], "DATE2": data[3]})
            row = cur.fetchone()

            if row is None:
                row = [''] + data
            else:
                row = list(row)
                rowid = row[0]

        except Error as e:
            print(e)
        finally:
            self.mutex.unlock()
            return row, rowid

    def set_item_review(self, data, review, plate, rowid):
        try:
            self.mutex.lock()
            cur = self.conn.cursor()

            if rowid == -1:
                data.extend([review, plate, _App.getDateTimeStamp("%m/%d/%Y %H:%M:%S"), _App.getDateTimeStamp("%m/%d/%Y %H:%M:%S")])
                rowid = cur.execute("INSERT INTO tbl_datas(TICKET_NO, TICKET_TYPE, DATE1, DATE2, LANE_ID, LANE_NAME, LANE_TYPE, REGO_RESULT, CONFIDENT, CORRECTED_PLATE, IMAGE_PATH1, IMAGE_PATH2, DATE_EDITED, ATTENDANCE, REVIEW_STATE, CORRECT_PLATE, CREATE_DATE, REVIEW_DATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
            else:
                #data.extend([review, _App.getDateTimeStamp("%m/%d/%Y %H:%M:%S")])
                cur.execute("UPDATE tbl_datas SET REVIEW_STATE=:REVIEW, CORRECT_PLATE=:PLATE, REVIEW_DATE=:DATE WHERE ID=:ID", {"REVIEW": review, "PLATE": plate, "DATE": _App.getDateTimeStamp("%m/%d/%Y %H:%M:%S"), "ID": rowid})

            self.conn.commit()
        except Error as e:
            print(e)
        finally:
            self.mutex.unlock()
            return rowid

    def get_report_data(self, date_from, date_to):
        data = []
        data1 = []
        overall = 0

        where_date = " and date1 > '{}' and date2 < '{}'".format(date_from, date_to)
        try:
            self.mutex.lock()
            cur = self.conn.cursor()

            cur.execute("SELECT DISTINCT(lane_id), lane_name FROM tbl_datas WHERE 1 {} ORDER BY lane_id".format(where_date))
            lane_ids = cur.fetchall()

            for lane_id in lane_ids:
                cur.execute("SELECT t1.cnt, t2.cnt, t3.cnt, t4.cnt, t5.cnt, t6.date FROM \
                    (SELECT COUNT(*) AS cnt FROM tbl_datas WHERE lane_id=:LANE_ID " + where_date + ") as t1, \
                    (SELECT COUNT(*) AS cnt FROM tbl_datas WHERE lane_id=:LANE_ID AND review_state == 0 " + where_date + ") as t2, \
                    (SELECT COUNT(*) AS cnt FROM tbl_datas WHERE lane_id=:LANE_ID AND review_state == 1 " + where_date + ") as t3, \
                    (SELECT COUNT(*) AS cnt FROM tbl_datas WHERE lane_id=:LANE_ID AND review_state == 2 " + where_date + ") as t4, \
                    (SELECT COUNT(*) AS cnt FROM tbl_datas WHERE lane_id=:LANE_ID AND review_state == 3 " + where_date + ") as t5, \
                    (SELECT review_date AS date FROM tbl_datas WHERE lane_id=:LANE_ID " + where_date + " ORDER BY review_date DESC LIMIT 1) as t6", {"LANE_ID": lane_id[0]})
                d = cur.fetchone()
                acc = round(d[1] / (d[1] + d[2]) * 100, 2)
                overall += acc
                data.append([lane_id[1], '', '', lane_id[0], '{}%'.format(acc), d[0], d[1] + d[2], d[1], d[2], d[3], d[4], d[5]])

                cur.execute("SELECT ticket_no, ticket_type, date1, lane_id, rego_result, confident, corrected_plate, image_path1, date_edited, attendance, rv.review, correct_plate FROM tbl_datas LEFT JOIN tbl_review_code rv ON tbl_datas.review_state = rv.id WHERE lane_id=:LANE_ID {} ORDER BY date1".format(where_date), {"LANE_ID": lane_id[0]})
                d = cur.fetchall()
                data1.extend(d)
            
            overall = overall / len(lane_ids)

        except Error as e:
            print(e)
        finally:
            self.mutex.unlock()
            return data, overall, data1

    def get_reviewed_data(self, lane_id, date_from, date_to):
        data = []

        where_date = " and date1 > '{}' and date2 < '{}'".format(date_from, date_to)
        try:
            self.mutex.lock()
            cur = self.conn.cursor()

            cur.execute("SELECT ticket_no, ticket_type, date1, lane_id, rego_result, confident, corrected_plate, image_path1, date_edited, attendance, rv.review, correct_plate FROM tbl_datas LEFT JOIN tbl_review_code rv ON tbl_datas.review_state = rv.id WHERE lane_id=:LANE_ID {} ORDER BY date1".format(where_date), {"LANE_ID": lane_id})
            data = cur.fetchall()

        except Error as e:
            print(e)
        finally:
            self.mutex.unlock()
            return data

    def clear_db(self, date = None):
        try:
            self.mutex.lock()
            cur = self.conn.cursor()

            if date == None:
                cur.execute("DELETE FROM tbl_datas")
            else:
                #data.extend([review, _App.getDateTimeStamp("%m/%d/%Y %H:%M:%S")])
                where_date = date.addDays(1).toString('yyyy-MM-dd')
                cur.execute("DELETE FROM tbl_datas WHERE date1 < '{}'".format(where_date))

            self.conn.commit()
        except Error as e:
            print(e)
        finally:
            self.mutex.unlock()




_DB = DBHelper()