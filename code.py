# -- PyQt5: pip3 install PyQt5

# -- Tkinter: pip3 install tkinter

# -- Kivy: pip3 install kivy

from tkinter import *
from tkinter import messagebox
from tkinter import ttk

import sqlite3

#create tkinter window

root = Tk()

root.title('Library Management System')

root.geometry("800x600") #x-axis y-axis place

def add_borrower():
    # Connect to the database
    conn = sqlite3.connect('part2.db')
    cur = conn.cursor()

    # Borrower details (replace these with input from GUI fields)
    first_name = "John"
    last_name = "Doe"
    address = "123 Library St"
    phone = "555-1234"

    # Insert the new Borrower
    cur.execute(
        "INSERT INTO book_loans (first_name, last_name, address, phone) VALUES (?, ?, ?, ?)",
        (first_name, last_name, address, phone)
    )

    # Retrieve the new CardNo
    cur.execute("SELECT CardNo FROM Borrower WHERE rowid = last_insert_rowid()")
    new_card_no = cur.fetchone()[0]

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"New Borrower added with CardNo: {new_card_no}")		

###	Frame1
Frame1 = Frame(root)
Frame1.pack(fill=X, pady=(5,0))

def selectBookWindow(borrowerName, cardNo):
	selectedBookTitle = StringVar()
	selectedBookCopyInfo = StringVar()
	
	# create a new window
	selectBookWindow = Toplevel(root)
	selectBookWindow.title("Select Book")
	selectBookWindow.geometry("500x500")
	topFrame = Frame(selectBookWindow)
	topFrame.pack(fill=X)

	# access the db
	conn = sqlite3.connect('part2.db')
	cur = conn.cursor()

	def onSelectedBook(event):
		conn = sqlite3.connect('part2.db')
		cur = conn.cursor()
		index = bookList.curselection()
		if index:
			book = bookList.get(index)
			selectedBookTitle.set(book)
			cur.execute("""
				SELECT lb.branch_name, bc.no_of_copies, b.book_id 
				FROM BOOK B 
				NATURAL JOIN book_copies bc 
				NATURAL JOIN library_branch lb 
				WHERE b.title = ?
			""", (selectedBookTitle.get(),))
			branch, copies, id = cur.fetchone()
			selectedBookCopyInfoLabel = Label(topFrame, textvariable=selectedBookCopyInfo).grid(row=0,column=2)
			if copies is None or branch is None or id is None:
				selectedBookCopyInfo.set("error")
			else:
				selectedBookCopyInfo.set(f"{branch}: {copies} copies, Book ID: {id}")
		conn.close()

	#display all books
	bookList = Listbox(topFrame, width = 30, height = 10)
	bookList.grid(row=0,column=0)
	scrollbar = Scrollbar(topFrame, orient=VERTICAL, command=bookList.yview)
	scrollbar.grid(row=0,column=1,sticky='ns')
	bookList.config(yscrollcommand=scrollbar.set)
	#get book selection
	bookList.bind('<<ListboxSelect>>', onSelectedBook)
	# GUI query and display list of books
	cur.execute("SELECT b.title from BOOK B")
	rows = cur.fetchall()
	for row in rows:
		bookList.insert(END, row[0])
	conn.close()
	
	#display the name and card number
	borrowerNameLabel = Label(selectBookWindow, text = f"Borrower Name: {borrowerName}").pack(pady = 10, padx = 10, ipadx = 100)
	cardNoLabel = Label(selectBookWindow, text = f"Card Number: {cardNo}").pack(pady = 10, padx = 10, ipadx = 100)

	#Submit button to checkout book
	def submitCheckout():
		conn = sqlite3.connect('part2.db')
		cur = conn.cursor()

		cur.execute("""
			  create trigger if not exists decrease_copies
			  after insert on book_loans
			  for each row
			  begin
			  	update book_copies
			  	set no_of_copies = no_of_copies - 1
			  	where book_id = NEW.book_id and branch_id = NEW.branch_id;
			  end;
			  """)
		if selectedBookTitle.get() != "":
			# get book id, branch id
			book_id, branch_id = cur.execute("""
			   select b.book_id, bc.branch_id
			   from book b
			   natural join book_copies bc
			   natural join library_branch lb
			   where b.title = ?
			""", (selectedBookTitle.get(),)).fetchone()
			# print(f"Book ID: {book_id}, Branch ID: {branch_id}")
			cur.execute(
			"INSERT INTO book_loans (book_id, branch_id, card_no, date_out, due_date) VALUES (?, ?, ?, DATE('now'), DATE('now', '+14 days'))",
			(book_id, branch_id, cardNo)
			)

			cur.execute("""select b.title, bl.date_out, bl.due_date, lb.branch_name 
			   			from book b 
			   			natural join book_loans bl
						natural join library_branch lb
						where card_no = ? and book_id = ?""", (cardNo,book_id))
			t, do, dd, bn = cur.fetchone()

			cur.execute("""select b.title, bc.no_of_copies, lb.branch_name 
			   			from book b 
			   			natural join book_loans bl
						natural join library_branch lb
						natural join book_copies bc
						where card_no = ? and book_id = ?""", (cardNo,book_id))
			t2, cps, brnch = cur.fetchone()

			output1 = f"Book Title: {t}, Date Out: {do}, Due Date: {dd}, Branch Name: {bn}"
			output2 = f"Book Title: {t2}, Copies left: {cps}, Branch Name: {brnch}"
			

			checkoutCompleteWindow = Toplevel(root)
			checkoutCompleteWindow.title("Checkout Success")
			checkoutCompleteWindow.geometry("700x200")

			Label(checkoutCompleteWindow, text = output1).pack()
			Label(checkoutCompleteWindow, text = output2).pack()
			selectBookWindow.destroy()
			conn.commit()
		else:
			print("No book selected")
		conn.close()

	submitCheckoutButton = Button(selectBookWindow, text = "Submit Checkout", command = submitCheckout).pack(pady = 10, padx = 10, ipadx = 100)

def getCardNoWindow():
	borrowerName = StringVar()
	cardNo = StringVar()

	# create a new window
	cardNoWindow = Toplevel(root)
	cardNoWindow.title("Enter Card Number")
	cardNoWindow.geometry("350x100")

	# access the db
	conn = sqlite3.connect('part2.db')
	cur = conn.cursor()

	# get the card number then open a new window when it is valid
	cardNoLabel = Label(cardNoWindow, text ='Enter Card Number: ')
	cardNoLabel.pack(padx = 10, ipadx = 100)
	cardNoEntry = Entry(cardNoWindow, width = 10)
	cardNoEntry.pack(padx = 10, ipadx = 100)

	def submitCardNo():
		cardNo.set(cardNoEntry.get())
		conn = sqlite3.connect('part2.db')
		cur = conn.cursor()
		cur.execute("SELECT name from Borrower WHERE Card_no = ?", (cardNo.get(),))
		name = cur.fetchone()
		if name is not None:
			borrowerName.set(name[0])
			selectBookWindow(borrowerName.get(), cardNo.get())
			conn.close()
			cardNoWindow.destroy()
		else:
			borrowerName.set("Borrower Not Found")
			validCardNo = False
	submitCardNoButton = Button(cardNoWindow, text = "Submit Card Number", command = submitCardNo).pack(pady = 10, padx = 10, ipadx = 100)
	borrowerNameLabel = Label(cardNoWindow, textvariable=borrowerName).pack(padx = 10, ipadx = 100)	

# Checkout Book Button
checkoutButton = Button(Frame1, text="Checkout Book", command=getCardNoWindow).pack(pady = 10, padx = 10, ipadx = 100)

### Frame2
# frame2: section of main window(root) with red background. height of 100 pixels
# and fill the x-axis
Frame2 = Frame(root, bg = "red", height = 100)
Frame2.pack(fill = X, padx = 10, pady = 10)

def addBorrowerWindow():
    # new database connection for this function
    borrowerConn = sqlite3.connect('part2.db')
    # .cursor(): primary interface for interacting with the db
    borrowerCur = borrowerConn.cursor()
    
    # Create new window
    # toplevel(root): creates a new window on top of the main window
    addWindow = Toplevel(root)
    addWindow.title("Add New Borrower")
    addWindow.geometry("400x300")
    
    # Create form fields
    # .pack(): places the widget in the window after the previous widget
    # pady: adds padding around the widget on y-axis
    Label(addWindow, text = "Name (first last):").pack(pady = (20,5))
    nameEntry = Entry(addWindow, width = 30)
    nameEntry.pack()
    
    Label(addWindow, text = "Address (street, state, abbrev.state zip):").pack(pady = (10,5))
    addressEntry = Entry(addWindow, width = 30)
    addressEntry.pack()
    
    Label(addWindow, text = "Phone (xxx-xxx-xxxx):").pack(pady = (10,5))
    phoneEntry = Entry(addWindow, width = 30)
    phoneEntry.pack()

    def submitBorrower():
        name = nameEntry.get().strip()
        address = addressEntry.get().strip()
        phone = phoneEntry.get().strip()
        
        if not name or not address or not phone:
            messagebox.showerror("Error", "Please fill all fields", parent = addWindow)
            return
        
        try:
            # add new borrower to the database
			# .execute(): executes a SQL command
            borrowerCur.execute("""
                INSERT INTO borrower (name, address, phone)
                VALUES (?, ?, ?)
            """, (name, address, phone))
            
            # get ID of last new row
            borrowerCur.execute("SELECT card_no FROM borrower ORDER BY card_no DESC LIMIT 1")
            # .fetchone(): fetches the next row of a query result set
            newCard = borrowerCur.fetchone()[0]
            
			# commit the changes to the database
            borrowerConn.commit()
            
            # success message window
            messagebox.showinfo("Success", 
				f"Borrower added successfully!\nCard Number: {newCard}", parent = addWindow)
            
            # close window
            addWindow.destroy()
            
            # close connection
            borrowerConn.close()
            
        except sqlite3.Error as e:
            # rollback the transaction in case of error
            borrowerConn.rollback()
            # str(e): converts the error to a string
            messagebox.showerror("Database Error", str(e), parent = addWindow)
            borrowerConn.close()
    
    # add submit button
    submitButton = Button(addWindow, text = "Submit", command = submitBorrower)
    submitButton.pack(pady = 20, ipadx = 50)

# add borrower button
addBorrowerButton = Button(Frame2, text = "Add Borrower", command = addBorrowerWindow)
addBorrowerButton.pack(pady = 10, padx = 10, ipadx = 100)

###	Frame3
Frame3 = Frame(root, bg = "green", height = 100)
Frame3.pack(fill = X, padx = 10, pady = 10)

def addBookWindow():
    # new database connection for this function
	bookConn = sqlite3.connect('part2.db')
	bookCur = bookConn.cursor()
      
	# Create new window	
	addWindow = Toplevel(root)
	addWindow.title("Add New Book")
	addWindow.geometry("400x300")
      
	# Create form fields
	Label(addWindow, text = "Title:").pack(pady = (20,5))
	titleEntry = Entry(addWindow, width = 30)
	titleEntry.pack()
      
	Label(addWindow, text="Publisher:").pack(pady = (10,5))
	bookCur.execute("SELECT publisher_name FROM publisher")
	publishers = [name[0] for name in bookCur.fetchall()]
	# Select publisher from the list only
	publisherCombo = ttk.Combobox(addWindow, width = 30, values = publishers, state = 'readonly')
	publisherCombo.pack(pady = 5)
	publisherCombo.set("Select a publisher")      
      
	Label(addWindow, text = "Author:").pack(pady = (10,5))
	authorEntry = Entry(addWindow, width = 30)
	authorEntry.pack()
      
	def submitBook():
		title = titleEntry.get().strip()
		publisher = publisherCombo.get()
		author = authorEntry.get().strip()

		if not title or publisher == "Select a publisher" or not author:
			messagebox.showerror("Error", "Please fill all fields", parent = addWindow)
			return
        
		try:
            # Add book
			bookCur.execute("""
                INSERT INTO book (title, book_publisher)
                VALUES (?, ?)
            """, (title, publisher))
            
            # get ID of last new row
			bookCur.execute("SELECT book_id FROM book ORDER BY book_id DESC LIMIT 1")
			newBookId = bookCur.fetchone()[0]
            
            # Add author
			bookCur.execute("""
                INSERT INTO book_authors (book_id, author_name)
                VALUES (?, ?)
            """, (newBookId, author))
            
            # all current branches
			bookCur.execute("SELECT branch_id FROM library_branch")
			branches = bookCur.fetchall()

			# Add 5 copies of the new book to each branch
			for branch in branches:
				branch_id = branch[0]
				bookCur.execute("""
					INSERT INTO book_copies (book_id, branch_id, no_of_copies)
					VALUES (?, ?, 5)
				""", (newBookId, branch_id))
            
            # commit the changes to the database
			bookConn.commit()
            
            # success message window
			messagebox.showinfo("Success", 
            	f"Book '{title}' successfully added with ID: {newBookId}\n5 copies added to each branch.", parent = addWindow)            
            
			# close window
			addWindow.destroy()
			
			# Close connection
			bookConn.close()
            
		except sqlite3.Error as e:
			bookConn.rollback()
			messagebox.showerror("Database Error", str(e), parent = addWindow)
        
    # add submit button
	submitButton = Button(addWindow, text = "Add Book", command = submitBook)
	submitButton.pack(pady = 20, ipadx = 50)


# add book button
addBookButton = Button(Frame3, text="Add New Book", command = addBookWindow)
addBookButton.pack(pady = 10, padx = 10, ipadx = 100)

###	Frame4
Frame4 = Frame(root, height = 100)
Frame4.pack(fill=X, padx = 10, pady= 10)

def checkCopies():
	selectedBookTitle = StringVar()

	# create a new window
	checkCopiesWindow = Toplevel(root)
	checkCopiesWindow.title("Check Number of Copies")
	checkCopiesWindow.geometry("400x300")
	topFrame = Frame(checkCopiesWindow)
	topFrame.pack(fill=X)

	# access the db
	conn = sqlite3.connect('part2.db')
	cur = conn.cursor()

	# Create form fields
	def onSelectedBook(event):
		local_conn = sqlite3.connect('part2.db')
		local_cur = local_conn.cursor()
		index = bookList.curselection()
		if index:
			book = bookList.get(index)
			selectedBookTitle.set(book)
			local_cur.execute("""
				select lb.branch_name, bc.no_of_copies, b.book_id 
				from BOOK B 
				natural join book_copies bc 
				natural join library_branch lb 
				where b.title = ?
			""", (selectedBookTitle.get(),))
			#selectedBookCopyInfoLabel = Label(topFrame, textvariable=selectedBookCopyInfo).grid(row=0,column=2)
		local_conn.close()

	#display all books
	bookList = Listbox(topFrame, width = 30, height = 10)
	bookList.grid(row=0,column=0)
	scrollbar = Scrollbar(topFrame, orient=VERTICAL, command=bookList.yview)
	scrollbar.grid(row=0,column=1,sticky='ns')
	bookList.config(yscrollcommand=scrollbar.set)
	#get book selection
	bookList.bind('<<ListboxSelect>>', onSelectedBook)
	# GUI query and display list of books
	cur.execute("select b.title from book B")
	rows = cur.fetchall()
	for row in rows:
		bookList.insert(END, row[0])
	conn.close()

	def submitCheck():
		title = selectedBookTitle.get()
		if not title:
			messagebox.showerror("Error", "Please fill all fields", parent = checkCopiesWindow)
			return

		try:
			check_conn = sqlite3.connect('part2.db')
			check_cur = check_conn.cursor()
			
			check_cur.execute("""
				select lb.branch_name, bc.no_of_copies 
				from book b 
				natural join book_copies bc 
				natural join library_branch lb 
				where b.title = ?
			""", (title,))
			rows = check_cur.fetchall()
			if rows:
				result = "\n".join([f"{branch}: {copies} copies" for branch, copies in rows])
				messagebox.showinfo("Number of Copies", result, parent=checkCopiesWindow)
			else:
				messagebox.showinfo("Number of Copies", "No copies found for this book.", parent=checkCopiesWindow)
			
			check_conn.close()

		except sqlite3.Error as e:
			messagebox.showerror("Database Error", str(e), parent=checkCopiesWindow)

	# add submit button
	submitButton = Button(checkCopiesWindow, text="Check Copies", command=submitCheck)
	submitButton.pack(pady=20, ipadx=50)

checkNumCopiesButton = Button(Frame4, text="Check Number of Copies", command=checkCopies)
checkNumCopiesButton.pack(pady = 10, padx = 10, ipadx = 100)

###	Frame5
Frame5 = Frame(root, height = 100)
Frame5.pack(fill=X, padx= 10, pady= 10)

def lateBookLoans():
	lateBookLoansWindow = Toplevel(root)
	lateBookLoansWindow.title("Late Book Loans")
	lateBookLoansWindow.geometry("400x300")

	# Create form fields
	Label(lateBookLoansWindow, text = "Enter Start Date (YYYY-MM-DD):").pack(pady = (20,5))
	startDateEntry = Entry(lateBookLoansWindow, width = 30)
	startDateEntry.pack()

	Label(lateBookLoansWindow, text = "Enter End Date (YYYY-MM-DD):").pack(pady = (10,5))
	endDateEntry = Entry(lateBookLoansWindow, width = 30)
	endDateEntry.pack()

	def submitLateBookLoans():
		startDate = startDateEntry.get()
		endDate = endDateEntry.get()

		if not startDate or not endDate:
			messagebox.showerror("Error", "Please fill all fields", parent=lateBookLoansWindow)
			return

		conn = sqlite3.connect('part2.db')
		cur = conn.cursor()
		cur.execute("""
			select 
				lb.branch_name, 
				b.title,
				bo.name,
				bl.card_no,
				bl.due_date,
					bl.Returned_date, 
				julianday(bl.Returned_date) - julianday(bl.due_date) as days_late
			from book_loans bl
			natural join book b
			join library_branch lb on bl.branch_id = lb.branch_id
			join borrower bo on bl.card_no = bo.card_no
			where bl.due_date BETWEEN ? and ? 
			   	and bl.Returned_date is not  "NULL"
				and bl.Returned_date > bl.due_date
			order by days_late desc
		""", (startDate, endDate))
			
		# create table window
		tableWindow = Toplevel(lateBookLoansWindow)
		tableWindow.title("Late Books Table")
		tableWindow.geometry("800x400")

		cols = ('Branch', 'Title', 'Borrower', 'Card No', 'Due Date', 'Returned Date', 'Days Late')
		tree = ttk.Treeview(tableWindow, columns=cols, show='headings')

		for col in cols:
			tree.heading(col, text=col)
			tree.column(col, width=100)

		# Add data to treeview
		rows = cur.fetchall()
		for row in rows:
			tree.insert("", "end", values=row)
		scrollbar = ttk.Scrollbar(tableWindow, orient=VERTICAL, command=tree.yview)
		tree.configure(yscrollcommand=scrollbar.set)
		
		# Pack widgets
		tree.pack(side=LEFT, fill=BOTH, expand=1)
		scrollbar.pack(side=RIGHT, fill=Y)

		conn.close()

	submitButton = Button(lateBookLoansWindow, text="Submit", command=submitLateBookLoans)
	submitButton.pack(pady=20)

lateBookLoansButton = Button(Frame5, text="Late Book Loans", command=lateBookLoans)
lateBookLoansButton.pack(pady = 10, padx = 10, ipadx = 100)

###	Frame6
Frame6a = Frame(root, bg = "blue", height = 100)
Frame6a.pack(fill=X, padx = 10, pady = 10)

def addLoanWindow():
    # new database connection for this function
    loanConn = sqlite3.connect('part2.db')
    loanCur = loanConn.cursor()
      
    # Create new window	
    addWindow = Toplevel(root)
    addWindow.title("View Loans")
    addWindow.geometry("1200x600")

    # Filter search frame
    filterFrame = Frame(addWindow, bg = "lightblue", height = 200)
    filterFrame.pack(fill = X, padx = 10, pady = 10)

    # Create form fields
    Label(filterFrame, text = "Filter Search by:").pack(pady = (5,5))

    Label(filterFrame, text = "Card Number:").pack(pady = (5,5))
    cardNumberEntry = Entry(filterFrame, width = 30)
    cardNumberEntry.pack()

    Label(filterFrame, text = "Name:").pack(pady = (5,5))
    nameEntry = Entry(filterFrame, width = 30)
    nameEntry.pack()

    Label(filterFrame, text = "Book ID:").pack(pady = (5,5))
    bookEntry = Entry(filterFrame, width = 30)
    bookEntry.pack()

    Label(filterFrame, text = "Title:").pack(pady = (5,5))
    titleEntry = Entry(filterFrame, width = 30)
    titleEntry.pack()

    # Scrollbar frame
    scrollbarFrame = Frame(addWindow, bg = "lightgreen", height = 200)
    scrollbarFrame.pack(fill = X, padx = 10, pady = 10)

    # create scrollbar
    scrollbar = Scrollbar(scrollbarFrame, orient=VERTICAL)
    # stretch to fill both the y-axis and x-axis
    scrollbar.pack(side=RIGHT, fill=BOTH)

    # Text inside the scrollbar
    # connecting the Text widget to the scrollbar
    resultsText = Text(scrollbarFrame, width = 110, height = 20, yscrollcommand=scrollbar.set)
    resultsText.pack(side=LEFT, fill=BOTH, expand=True)
    # configures the scrollbar to control the Text widget's vertical scrolling
    scrollbar.config(command=resultsText.yview)

    def setupDatabase():
		# Execute commands one at a time to avoid error

        # First try to create the columns and view
        try:
            loanCur.execute("ALTER TABLE book_loans ADD COLUMN Late INTEGER")
            loanConn.commit()
        except sqlite3.OperationalError:
            # if the column already exists, just continue
            pass
            
        try:
            loanCur.execute("""
                UPDATE book_loans
                SET Late = CASE
                    WHEN (julianday(returned_date) > julianday(due_date)) THEN 1
                    ELSE 0
                END
            """)
            loanConn.commit()
        except sqlite3.OperationalError as e:
            # Rollback the transaction in case of error
            loanConn.rollback()
            print(f"Error updating Late column: {e}")
            pass
        
        try:
            loanCur.execute("ALTER TABLE library_branch ADD COLUMN LateFee double")
            loanConn.commit()
        except sqlite3.OperationalError:
            # if the column already exists, just continue
            pass
            
        try:
            loanCur.execute("UPDATE library_branch SET LateFee = branch_id + 0.99")
            loanConn.commit()
        except sqlite3.OperationalError as e:
            # Rollback the transaction in case of error
            loanConn.rollback()
            print(f"Error updating LateFee column: {e}")
            pass
        
        # drop the view if it exists to recreate it
        try:
            loanCur.execute("DROP VIEW IF EXISTS vBookLoanInfo")
            loanConn.commit()
            
            loanCur.execute("""
                CREATE VIEW vBookLoanInfo AS
                SELECT
                    BL.card_no as Card_no,
                    BO.name as "Borrower Name",
                    BL.date_out as Date_Out,
                    BL.due_date as Due_Date,
                    BL.Returned_date as Returned_date,
                    
                    CASE
                        WHEN BL.Returned_date IS NOT NULL THEN
                            julianday(BL.Returned_date) - julianday(BL.date_out)
                        ELSE NULL
                    END as TotalDays,
                    
                    B.title as "Book Title",
					B.book_id as book_id,
                    
                    CASE
                        WHEN BL.Returned_date IS NULL THEN NULL
                        WHEN julianday(BL.Returned_date) > julianday(BL.due_date) THEN
                            julianday(BL.Returned_date) - julianday(BL.due_date)
                        ELSE 0
                    END as "Num of days returned late",
                    
                    BL.branch_id as "Branch ID",
                    
                    CASE
                        WHEN BL.Returned_date IS NULL THEN NULL
                        WHEN julianday(BL.Returned_date) > julianday(BL.due_date) THEN
                            (julianday(BL.Returned_date) - julianday(BL.due_date)) * LB.LateFee
                        ELSE 0
                    END as LateFeeBalance
                FROM book_loans BL
                JOIN borrower BO on BL.card_no = BO.card_no
                JOIN book B on BL.book_id = B.book_id
                JOIN library_branch LB on LB.branch_id = BL.branch_id
            """)
            loanConn.commit()    
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error creating view: {str(e)}", parent=addWindow)
            # Rollback the transaction in case of error
            loanConn.rollback()
            # if error, propagate to other exceptions
            raise

    def runSearch():
        # Clear previous results
        resultsText.delete(1.0, END)
        
        # Get search filters
        cardNo = cardNumberEntry.get().strip()
        name = nameEntry.get().strip()
        bookid = bookEntry.get().strip()
        title = titleEntry.get().strip()
        
        try:
            # Base query to get all loan information
            query = """
                SELECT 
                    x.Card_no,
                    x."Borrower Name",
                    x.Date_Out,
                    x.Due_Date,
                    x.Returned_date,
                    x.TotalDays,
                    x."Book Title",
					x.book_id,
                    x."Num of days returned late",
                    x."Branch ID",
                    COALESCE(x.LateFeeBalance, 0) AS LateFeeBalance
                FROM 
                    vBookLoanInfo x
            """
            
            # Add WHERE clause if search filters are provided
            whereClause = []
            params = []
            
            if cardNo:
                whereClause.append("x.Card_no = ?")
                params.append(cardNo)
            
            if name:
                whereClause.append("x.\"Borrower Name\" LIKE ?")
                params.append(f"%{name}%")

            if bookid:
                whereClause.append("x.book_id LIKE ?")
                params.append(f"%{bookid}%")

            if title:
                whereClause.append("x.\"Book Title\" LIKE ?")
                params.append(f"%{title}%")
            
            if whereClause:
                # AND separates multiple conditions
                query += " WHERE " + " AND ".join(whereClause)
            
            # add ORDER BY clause at the end
			# Sort by LateFeeBalance in descending order
            query += """
                ORDER BY LateFeeBalance DESC
            """
            
            # Execute the query
            # auto subs ? with values from params
            loanCur.execute(query, params)
            
			# Get column names .description
            columnNames = [description[0] for description in loanCur.description]
            # Display column names in the results text
            resultsText.insert(END, "("  + ", ".join(columnNames) + ")" + "\n\n")
            
            results = loanCur.fetchall()
            
            if not results:
                resultsText.insert(END, "No matching records found.")
                return
            
            for row in results:
                # Convert row to a list so we can modify values
                row_list = list(row)
                
                # access last element in list.
                if row_list[-1] is None:
                    row_list[-1] = "$0.00"  # NULL case
                elif row_list[-1] == 0:
                    row_list[-1] = "$0.00"  # Zero case
                else:
                    # assign a .2 decimal float format
                    row_list[-1] = f"${row_list[-1]:.2f}"
                
                # Insert the formatted row
                resultsText.insert(END, str(tuple(row_list)) + "\n")
            
        except sqlite3.Error as e:
            resultsText.insert(END, f"Database Error: {str(e)}")
    
    # add submit button
    searchButton = Button(filterFrame, text = "Filter Search", command = runSearch)
    searchButton.pack(pady = 5, ipadx = 25)

    # show all records by default
    setupDatabase()
    runSearch()

# add view loan button
viewLoanButton = Button(Frame6a, text = "View Loans", command = addLoanWindow)
viewLoanButton.pack(pady = 10, padx = 10, ipadx = 100)

root.mainloop()