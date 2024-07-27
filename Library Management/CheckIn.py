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

class CheckIn:
    def __init__(self, root):
        self.parent = root

        self.checkInBookID = None
        self.search_string = None
        self.data = None

        self.searchLabel = Label(self.parent, text="Search here: Borrower ID, Borrower Name or ISBN")
        self.searchLabel.grid(row=0, column=0, padx=20, pady=20)
        
        self.searchTextBox = Entry(self.parent)
        self.searchTextBox.grid(row=1, column=0)
        
        self.searchBtn = Button(self.parent, text="Search", command=self.search_book_loans)
        self.searchBtn.grid(row=2, column=0)
        
        self.table = Treeview(self.parent, columns=["Loan ID", "ISBN", "Borrower ID", "Title"])
        self.table.grid(row=3, column=0)
        self.table.heading('#0', text="Loan ID")
        self.table.heading('#1', text="ISBN")
        self.table.heading('#2', text="Borrower ID")
        self.table.heading('#3', text="Book Title")
        self.table.bind('<ButtonRelease-1>', self.select_book_for_checkin)
        
        self.checkInBtn = Button(self.parent, text="Check In", command=self.check_in)
        self.checkInBtn.grid(row=4, column=0)

    def search_book_loans(self):
        self.search_string = self.searchTextBox.get()
        cursor = conn.cursor()
        cursor.execute("select BL.Loan_Id, BL.ISBN, BL.card_id, BO.title, BL.Date_in from BOOK_LOANS AS BL "
                       "join BORROWER AS B on BL.card_id = B.card_id "
                       "join BOOK AS BO on BL.ISBN = BO.ISBN "
                       "where BL.ISBN like concat('%', '" + self.search_string + "', '%') or "
                        "B.Bname like concat('%', '" + self.search_string + "', '%') or "
                        "BL.card_id like concat('%', '" + self.search_string + "', '%')")

        self.data = cursor.fetchall()
        self.books_view_data()

    def books_view_data(self):
        self.table.delete(*self.table.get_children())
        for ret in self.data:
            if ret[4] is None:
                self.table.insert('', 'end', text=str(ret[0]), values=(ret[1], ret[2], ret[3]))

    def select_book_for_checkin(self, a):
        curItem = self.table.focus()
        self.checkInBookID = self.table.item(curItem)['text']

    def check_in(self):
        if self.checkInBookID is None:
            messagebox.showinfo("Warning", "Select Book to Check In First!")
            return None

        cursor = conn.cursor()
        cursor.execute("SELECT BL.Date_in FROM BOOK_LOANS AS BL WHERE BL.Loan_Id = '" + str(self.checkInBookID) + "'")
        result = cursor.fetchall()

        if result[0][0] is None:
            cursor.execute("UPDATE BOOK_LOANS SET BOOK_LOANS.Date_in = '" + str(todays_date) + "' WHERE BOOK_LOANS.Loan_Id = '"
                           + str(self.checkInBookID) + "'")
            conn.commit()
            messagebox.showinfo("Done", "Book Checked In Successfully!")
            self.parent.destroy()
        else:
            return None
