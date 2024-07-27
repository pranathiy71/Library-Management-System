from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview
import mysql.connector
from mysql.connector import errorcode
from datetime import date, timedelta, datetime

config = {
  'user': 'root',
  'password': 'pLaster@123',
  'host': 'localhost',
  'database': 'LIBRARY',
  'unix_socket': "/tmp/mysql.sock",
  'raise_on_warnings': True
}

try:
    conn = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("User name or password is wrong")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

cursor = None
todays_date = date.today()
due_date = todays_date + timedelta(days=14)

class PayFines:
    def __init__(self, master):
        self.parent = master
        self.totalFine = StringVar()
        self.borrowerHeading = Label(self.parent, text="Enter Borrower ID").grid(row=0, column=0, padx=20, pady=20)
        self.borrowerIDEntry = Entry(self.parent)
        self.borrowerIDEntry.grid(row=1, column=0, padx=20, pady=20)
        self.showFineBtn = Button(self.parent, text="Display Fines", command=self.display_fines).grid(row=2, column=0, padx=20, pady=20)
        self.fineLabel = Label(self.parent, textvariable=self.totalFine).grid(row=3, column=0, padx=20, pady=20)
        self.payFineBtn = Button(self.parent, text="Pay Fine", command=self.pay_fine).grid(row=4, column=0, padx=20, pady=20)

    def display_fines(self):
        borrower_id = self.borrowerIDEntry.get()
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS(SELECT Card_id FROM BORROWER AS BR WHERE BR.Card_id = '" + str(borrower_id) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            messagebox.showinfo("Error", "Borrower does not exist in data")
        else:
            cursor.execute("SELECT F.fine_amt, F.paid FROM FINES AS F JOIN BOOK_LOANS AS BL ON F.Loan_Id = BL.Loan_Id WHERE BL.Card_id = '" + str(borrower_id) + "'")
            result = cursor.fetchall()
            total_fine = 0
            for fine in result:
                if fine[1] == 0:
                    total_fine += float(fine[0])

        self.totalFine.set("Fine: $" + str(total_fine))

    def pay_fine(self):
        borrower_id = self.borrowerIDEntry.get()
        cursor = conn.cursor()
        cursor.execute("SELECT F.Loan_Id FROM FINES AS F JOIN BOOK_LOANS AS BL ON F.Loan_Id = BL.Loan_Id WHERE BL.card_id = '" + str(borrower_id) + "'")
        result = cursor.fetchall()
        for br_fine in result:
            cursor = conn.cursor()
            cursor.execute("UPDATE FINES SET FINES.paid = 1 WHERE FINES.Loan_Id = '" + str(br_fine[0]) + "'")
            conn.commit()
        messagebox.showinfo("Info", "Fines Paid!")
        self.parent.destroy()

