from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview
import mysql.connector
from mysql.connector import errorcode
from datetime import date, timedelta, datetime
from CheckIn import *
from PayFines import *
from AddBorrower import *

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

class LibraryManagement:
    def __init__(self, root):
        self.parent = root
        self.parent.title("Library Management System")
        
        self.frame = Frame(self.parent, width=1000, height=500)
        self.frame.grid(row=0, column=0, sticky=N)

        self.search_string = None
        self.data = None
        self.borrowerId = None
        self.checkOutBook = None

        self.HeaderFrame = Frame(self.frame)
        self.HeaderFrame.grid(row=0, column=0, sticky=N)

        self.HeaderLabel = Label(self.HeaderFrame, text='Library Management System')
        self.HeaderLabel.grid(row=0, column=0, sticky=N)

        self.SearchLabel = Label(self.HeaderFrame, text='Search for books here')
        self.SearchLabel.grid(row=1, column=0, sticky=N)

        self.SearchFrame = Frame(self.frame)
        self.SearchFrame.grid(row=1, column=0, sticky=N)

        self.SearchBoxLabel = Label(self.SearchFrame, text='Search by ISBN, title, and/or Author(s)')
        self.SearchBoxLabel.grid(row=0, column=0)
        
        self.SearchTextBox = Entry(self.SearchFrame, text='Enter search string here...', width=70)
        self.SearchTextBox.grid(row=1, column=0)
        
        self.SearchButton = Button(self.SearchFrame, text='Search', command=self.search)
        self.SearchButton.grid(row=2, column=0)
        
        self.ListBooks = Frame(self.frame)
        self.ListBooks.grid(row=2, column=0, sticky=N)
        
        self.BooksTreeView = Treeview(self.ListBooks, columns=["ISBN", "Book Title", "Author(s)", "Availability"])
        self.BooksTreeView.grid(row=0, column=0, sticky=N)
        
        self.BooksTreeView.heading('#0', text="ISBN")
        self.BooksTreeView.heading('#1', text="Book Title")
        self.BooksTreeView.heading('#2', text="Author(s)")
        self.BooksTreeView.heading('#3', text="Availability")
        self.BooksTreeView.grid_columnconfigure(1, weight=1)

        self.Functionality = Frame(self.frame)
        self.Functionality.grid(row=3, column=0, sticky=N)
        
        self.checkOutBtn = Button(self.Functionality, text="Check Out Book", command=self.check_out_books)
        self.checkOutBtn.grid(row=0, column=0, padx=10, pady=10)

        self.checkInBtn = Button(self.Functionality, text="Check In Book", command=self.check_in)
        self.checkInBtn.grid(row=0, column=1, padx=10, pady=10)
        
        self.addBorrowerBtn = Button(self.Functionality, text="Add New Borrower", command=self.add_borrower)
        self.addBorrowerBtn.grid(row=0, column=4, padx=10, pady=10)
        
        self.updateFinesBtn = Button(self.Functionality, text="Updates Fines", command=self.update_fines)
        self.updateFinesBtn.grid(row=0, column=2, padx=10, pady=10)
        
        self.finesBtn = Button(self.Functionality, text="Pay Fines", command=self.pay_fines)
        self.finesBtn.grid(row=0, column=3, padx=10, pady=10)        
        

    def search(self):
        self.search_string = self.SearchTextBox.get()
        search_string_replace = self.search_string.replace(', ', ',')
        search_strings = search_string_replace.split(',')
        final_string = "select B.isbn, B.title, A.name from BOOK AS B join BOOK_AUTHOR AS BA on B.isbn = BA.isbn join AUTHOR AS A on BA.author_id = A.author_id where "
        for i in range(len(search_strings)):
            final_string += "B.title like concat('%', '" + search_strings[i] + "', '%') or "
            final_string += "A.name like concat('%', '" + search_strings[i] + "', '%') or "
            final_string += "B.isbn like concat('%', '" + search_strings[i] + "', '%')"
            if i < len(search_strings) - 1:
                final_string += " or "
        cursor = conn.cursor()
        cursor.execute(final_string)

        self.data = cursor.fetchall()
        self.tree_view_data()

    def tree_view_data(self):
        
        self.BooksTreeView.delete(*self.BooksTreeView.get_children())
        for data_table in self.data:
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS(SELECT BL.isbn from BOOK_LOANS AS BL where BL.isbn = '" + str(data_table[0]) + "')")
            result = cursor.fetchall()
            if result == [(0,)]:
                availability = "Available"
            else:
                cursor = conn.cursor()
                cursor.execute("SELECT BL.Date_in from BOOK_LOANS AS BL where BL.isbn = '" + str(data_table[0]) + "'")
                result = cursor.fetchall()
                if result[-1][0] is None:
                    availability = "Not Available"
                else:
                    availability = "Available"
            self.BooksTreeView.insert('', 'end', text=str(data_table[0]), values=(data_table[1], data_table[2], availability))


    def check_out_books(self):        
        self.checkOutBook = simpledialog.askstring("Check out the book", "Enter the 13 digit ISBN")
        all_books = self.checkOutBook.replace(', ',',')
        all_isbn = all_books.split(',')
        isbn_list = []
        for book in all_isbn:
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS(SELECT Isbn from BOOK_LOANS AS BL WHERE BL.Isbn = '" + book + "')")
            result = cursor.fetchall()
            print(result)
            if result != [(0,)]:
                messagebox.showinfo("Error", "Book with ISBN " + book + " is not available!")
                continue
            else:
                isbn_list.append(book)
        
        if len(isbn_list) == 0:
            messagebox.showinfo("Error", "Selected books are not available!")
            return
        self.borrowerId = simpledialog.askstring("Check Out Book", "Enter Borrower ID")
        if self.borrowerId[:2] == "ID":
            self.borrowerId = self.borrowerId[2:]

        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS(SELECT card_id from BORROWER AS BR WHERE BR.card_id = '" + str(self.borrowerId) + "')")
        result = cursor.fetchall()

        if result == [(0,)]:
            messagebox.showinfo("Error", "Borrower not in Database!")
            return None
        else:
            for avail_book in isbn_list:
                count = 0
                cursor = conn.cursor()
                cursor.execute("SELECT BL.Date_in from BOOK_LOANS AS BL WHERE BL.card_id = '" + str(self.borrowerId) + "'")
                result = cursor.fetchall()
                for book in result:
                    if book[0] is None:
                        count += 1
                if count >= 3:
                    messagebox.showinfo("Not Allowed!", "Borrower has loaned 3 books already!")
                    return None
                else:
                    cursor = conn.cursor()
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                    cursor.execute("INSERT INTO BOOK_LOANS (ISBN, card_id, Date_out, Due_date) VALUES(%s, %s, %s, %s)", ( avail_book, self.borrowerId, todays_date, todays_date + timedelta(days=14)))
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                    conn.commit()
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(Loan_Id) FROM BOOK_LOANS")
                    result = cursor.fetchall()
                    loan_id = result[0][0]
                    cursor.execute("INSERT INTO FINES (Loan_Id, fine_amt, paid) VALUES ('" + str(loan_id) + "', '0.00', '0')")
                    conn.commit()
                    messagebox.showinfo("Done","Book Loaned Out Successfully!")

    def check_in(self):
        self.checkInWindow = Toplevel(self.parent)
        self.checkInWindow.title("Check In Here")
        self.app = CheckIn(self.checkInWindow)

    def update_fines(self):
        cursor = conn.cursor()
        cursor.execute("SELECT BL.Loan_Id, BL.Date_in, BL.Due_date FROM BOOK_LOANS AS BL")
        result = cursor.fetchall()
        for loan in result:
            date_in =  loan[1]
            date_due = loan[2]
            if date_in is None:
                date_in = todays_date
            
            diff = date_in - date_due
            if diff.days > 0:
                fine = int(diff.days) * 0.25
            else:
                fine = 0

            cursor = conn.cursor()
            cursor.execute("UPDATE FINES SET FINES.fine_amt = '" + str(fine) + "' WHERE FINES.Loan_Id = '" + str(loan[0]) + "'")
            conn.commit()
        messagebox.showinfo("Done", "Fines have been computed!")

    def pay_fines(self):
        self.newPayFinesWindow = Toplevel(self.parent)
        self.newPayFinesWindow.title("Pay Fines")
        self.web = PayFines(self.newPayFinesWindow)

    def add_borrower(self):
        self.newBorrowerWindow = Toplevel(self.parent)
        self.newBorrowerWindow.title("Add New Borrower")
        self.web1 = AddBorrower(self.newBorrowerWindow)


if __name__ == '__main__':
    root = Tk()
    tool = LibraryManagement(root)
    root.mainloop()