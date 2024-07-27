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

class AddBorrower:
    def __init__(self, root):
        self.parent = root

        self.titleLabel = Label(self.parent, text="Enter Details")
        self.titleLabel.grid(row=0, column=0, padx=20, pady=20)
        
        self.fnameLabel = Label(self.parent, text="First Name").grid(row=1, column=0, padx=10, pady=5)
        self.fname = Entry(self.parent)
        self.fname.grid(row=2, column=0, padx=10, pady=5)
        
        self.lnameLabel = Label(self.parent, text="Last Name").grid(row=3, column=0, padx=10, pady=5)
        self.lname = Entry(self.parent)
        self.lname.grid(row=4, column=0, padx=10, pady=5)
        
        self.ssnLabel = Label(self.parent, text="SSN").grid(row=5, column=0, padx=10, pady=5)
        self.ssn = Entry(self.parent)
        self.ssn.grid(row=6, column=0, padx=10, pady=5)
        
        self.addressLabel = Label(self.parent, text="Street Address").grid(row=7, column=0, padx=10, pady=5)
        self.address = Entry(self.parent)
        self.address.grid(row=8, column=0, padx=10, pady=5)
        
        self.cityLabel = Label(self.parent, text="City").grid(row=9, column=0, padx=10, pady=5)
        self.city = Entry(self.parent)
        self.city.grid(row=10, column=0, padx=10, pady=5)
        
        self.stateLabel = Label(self.parent, text="State").grid(row=11, column=0, padx=10, pady=5)
        self.state = Entry(self.parent)
        self.state.grid(row=12, column=0, padx=10, pady=5)
        
        self.numberLabel = Label(self.parent, text="Phone Number").grid(row=13, column=0, padx=10, pady=5)
        self.number = Entry(self.parent)
        self.number.grid(row=14, column=0, padx=10, pady=5)
        
        self.addBtn = Button(self.parent, text="Add", command=self.add_borrower)
        self.addBtn.grid(row=15, column=0, padx=10, pady=5)

    def add_borrower(self):
        ssn = self.ssn.get()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(card_id) from BORROWER")
        result = cursor.fetchall()
        new_card_id = str(int(result[0][0]) + 1)
        cursor.execute("SELECT EXISTS(SELECT Ssn FROM BORROWER AS B WHERE B.ssn = '" + str(ssn) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            if self.fname.get() == "" or self.lname.get() == "":
                messagebox.showinfo("Error", "All fields are necessary!")
                return
            address = ', '.join([self.address.get(), self.city.get(), self.state.get()])
            bname = ' '.join([self.fname.get(), self.lname.get()])
            
            cursor.execute("Insert into BORROWER (card_id, ssn, Bname, address, phone) Values ('" + new_card_id + "', '" + ssn + "', '" + str(bname) + "', '" + str(address) + "', '" + str(self.number.get()) + "')")
            conn.commit()
            self.parent.destroy()
            messagebox.showinfo("Done", "New borrower Added!")
        else:
            messagebox.showinfo("Error", "Borrower Already Exists!")
