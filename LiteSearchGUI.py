from tkinter import *
from tkinter import ttk
import LiteSearchBackend as LSB
import ctypes
import datetime

# Utility functions
def resetEntry():
    LSB.log_event('RESET', 'MAIN WINDOW RESET', 'SYS')
    searchEntry.delete(0, END)
    try:
        treeSearchEntry.delete(0, END)
    except Exception:
        pass
    listBoxPop()  # Rebuild the Treeview

def logFiles():
    print('Log Files Requested')
    LSB.log_event('REQUEST', 'LOG FILES TAB REQUESTED', 'MLM91')
    top = Toplevel()
    top.geometry('425x200')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\\Traffic_Light.ico')
    menu = Menu(top)
    top.config(menu=menu)
    filemenu = Menu(menu)
    menu.add_cascade(label='File', menu=filemenu)
    filemenu.add_command(label='Print', command=lambda: print('print log window'))
    logLabel = Label(top, text='Log Files', font=('Arial', 12, 'bold'))
    logLabel.pack()

def about():
    LSB.log_event('REQUEST', 'REQUEST ABOUT INFO', 'MLM91')
    top = Toplevel()
    top.geometry('425x200')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\\Traffic_Light.ico')
    with open('about.txt', 'r') as aboutFile:
        aboutContent = aboutFile.read()
    aboutLabel = Label(top, text=aboutContent, wraplength=375, justify='left')
    aboutLabel.pack()

def license():
    LSB.log_event('REQUEST', 'REQUEST LICENSE INFO', 'MLM91')
    top = Toplevel()
    top.geometry('425x350')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\\Traffic_Light.ico')
    with open('LICENSE', 'r') as licenseFile:
        licenseContent = licenseFile.read()
    aboutLabel = Label(top, text=licenseContent, wraplength=375, justify='left')
    aboutLabel.pack()

def support():
    def commandSet():
        commandArgs = LSB.support_request(nameEntry.get(), emailEntry.get(), textBox.get(1.0, END))
        top.destroy()
        return commandArgs
    def resetEntry():
        LSB.log_event('RESET', 'SUPPORT WINDOW RESET', 'SYS')
        nameEntry.delete(0, END)
        emailEntry.delete(0, END)
        textBox.delete(1.0, END)
    LSB.log_event('REQUEST', 'REQUEST SUPPORT WINDOW', 'MLM91')
    top = Toplevel()
    top.geometry('425x365')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\\Traffic_Light.ico')
    supportLabel = Label(top, text='\nContact Support\n', font=('Arial', 12, 'bold'))
    nameLabel = Label(top, text='Name:', font=('Arial', 12, 'bold'))
    nameEntry = Entry(top, width=50)
    emailLabel = Label(top, text='Email Address:', font=('Arial', 12, 'bold'))
    emailEntry = Entry(top, width=50)
    textBoxLabel = Label(top, text='Reason:', font=('arial', 12, 'bold'))
    textBox = Text(top, height=6, width=50)
    submitButton = Button(top, text='Submit', width=25, command=commandSet)
    resetButton = Button(top, text='Reset', width=25, command=resetEntry)
    supportLabel.pack()
    nameLabel.pack(anchor='w', padx=10)
    nameEntry.pack(anchor='w', padx=10)
    emailLabel.pack(anchor='w', padx=10)
    emailEntry.pack(anchor='w', padx=10)
    textBoxLabel.pack(anchor='w', padx=10)
    textBox.pack()
    submitButton.pack(padx=2.5, pady=10)
    resetButton.pack(padx=2.5)

def format_dt(dt_str):
    import datetime
    try:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.datetime.strptime(dt_str, fmt)
                return dt.strftime("%m-%d-%Y    %H:%M")
            except ValueError:
                continue
        return dt_str
    except Exception:
        return dt_str

def listBoxPop():
    notificationTree.delete(*notificationTree.get_children())
    notificationsList = LSB.listBoxData()
    for notification in notificationsList:
        if len(notification) >= 11:
            cleaned = [str(x).replace('\n', ' ') if isinstance(x, str) else x for x in notification]
            if cleaned[0] is None or cleaned[0] == 'None':
                print('DEBUG: Skipping record with None ID:', cleaned)
                continue
            db_id = cleaned[0]
            request_date = cleaned[2]
            request_time = cleaned[3]
            unit = cleaned[4]
            location = cleaned[5]
            agency = cleaned[6]
            notification_date = cleaned[7]
            notification_time = cleaned[8]
            user = cleaned[9]
            nature = cleaned[10]
            record_added = cleaned[1]
            # Only display the correct columns
            values = [
                f"{request_date}    {request_time}",  # Request_Date/Time
                unit,                                    # Unit
                location,                                # Location
                agency,                                  # Agency
                nature,                                  # Nature
                f"{notification_date}    {notification_time}", # Notification_Date/Time
                user,                                    # USER_ID
                record_added,                            # Record_Added
            ]
            notificationTree.insert('', 'end', iid=db_id, values=values)  # Use db_id as iid for internal reference
        else:
            padded = [''] * 8
            notificationTree.insert('', 'end', values=padded)

def show_treeview_context_menu(event):
    item_id = notificationTree.identify_row(event.y)
    if item_id:
        notificationTree.selection_set(item_id)
        notificationTree.focus(item_id)
        context_menu.post(event.x_root, event.y_root)
    else:
        context_menu.unpost()

def edit_selected_record():
    item_id = notificationTree.focus()
    if not item_id:
        return
    db_id = item_id  # Use item iid for DB lookup
    import sqlite3
    conn = sqlite3.connect(LSB.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Notification_List WHERE ID=?", (db_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        print('DEBUG: No record found in DB for ID:', db_id)
        return
    print('DEBUG: DB row for edit:', row)
    # Correct mapping based on your debug output and actual DB order
    request_date_value = row[2] if row[2] is not None else ''
    request_time_value = row[3] if row[3] is not None else ''
    unit_value = row[4] if row[4] is not None else ''
    location_value = row[5] if row[5] is not None else ''
    agency_value = row[6] if row[6] is not None else ''
    nature_value = row[10] if row[10] is not None else ''  # Nature is last column
    notification_date_value = row[7] if row[7] is not None else ''
    notification_time_value = row[8] if row[8] is not None else ''
    user_value = row[9] if row[9] is not None else ''
    record_added_value = row[1] if row[1] is not None else ''
    entry_values = [
        request_date_value,
        request_time_value,
        unit_value,
        location_value,
        agency_value,
        nature_value,
        notification_date_value,
        notification_time_value,
        user_value,
        record_added_value
    ]
    print('DEBUG: Entry values for edit form:', entry_values)
    labels = ['Request Date:', 'Request Time:', 'Unit:', 'Location:', 'Agency:', 'Nature:', 'Notification Date:', 'Notification Time:', 'User:', 'Record Added:']
    edit_win = Toplevel(root)
    edit_win.title('Baltimore County Police Dispatch LiteSearch')
    edit_win.geometry('425x490')
    edit_win.iconbitmap('imagery\\Traffic_Light.ico')
    masterLabel = Label(edit_win, text='Edit Notification Record', font=('Arial', 14, 'bold'))
    masterLabel.pack(pady=10)
    form_frame = Frame(edit_win)
    form_frame.pack(expand=True)
    entries = []
    for i, (label, value) in enumerate(zip(labels, entry_values)):
        Label(form_frame, text=label, font=('Arial', 12)).grid(row=i, column=0, padx=10, pady=2, sticky='e')
        entry = Entry(form_frame, width=35, justify='left')
        entry.insert(0, value)
        entry.grid(row=i, column=1, padx=10, pady=2)
        entries.append(entry)
    import datetime
    def auto_populate_date(event):
        today = datetime.date.today().strftime('%m-%d-%Y')
        event.widget.delete(0, END)
        event.widget.insert(0, today)
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    def auto_populate_time(event):
        now = datetime.datetime.now().strftime('%H:%M')
        event.widget.delete(0, END)
        event.widget.insert(0, now)
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    def highlight_entry(event):
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    entries[0].bind('<FocusIn>', auto_populate_date)
    entries[1].bind('<FocusIn>', auto_populate_time)
    entries[6].bind('<FocusIn>', auto_populate_date)
    entries[7].bind('<FocusIn>', auto_populate_time)
    for idx in [0,1,6,7]:
        entries[idx].bind('<FocusIn>', highlight_entry, add='+')
    def save_edits():
        new_values = [e.get() for e in entries]
        print('DEBUG: Saving edits with values:', new_values)
        print('DEBUG: db_id:', db_id)
        if not new_values[0].strip() or not new_values[1].strip():
            from tkinter import messagebox
            messagebox.showerror('Input Error', 'Request Date and Request Time must be filled.')
            return
        if not new_values[6].strip() or not new_values[7].strip():
            from tkinter import messagebox
            messagebox.showerror('Input Error', 'Notification Date and Notification Time must be filled.')
            return
        req_date = new_values[0]
        req_time = new_values[1]
        unit = new_values[2]
        location = new_values[3]
        agency = new_values[4]
        nature = new_values[5]
        notif_date = new_values[6]
        notif_time = new_values[7]
        user = new_values[8]
        # record_added = new_values[9] # Not updated
        if db_id is not None:
            import sqlite3
            conn = sqlite3.connect(LSB.db_name)
            sql = ("UPDATE Notification_List SET Request_date=?, Request_time=?, Unit=?, Location=?, Agency=?, Notification_date=?, Notification_time=?, USER_ID=?, Nature=? WHERE ID=?")
            print('DEBUG: SQL:', sql)
            print('DEBUG: Params:', (req_date, req_time, unit, location, agency, notif_date, notif_time, user, nature, db_id))
            conn.execute(sql, (req_date, req_time, unit, location, agency, notif_date, notif_time, user, nature, db_id))
            conn.commit()
            conn.close()
            listBoxPop()
        else:
            print('DEBUG: db_id is None, update not performed.')
        edit_win.destroy()
    Button(edit_win, text='Save', command=save_edits, width=20).pack(pady=10)
    Button(edit_win, text='Cancel', command=edit_win.destroy, width=20).pack(pady=(0, 20))

def resetNotificationTable():
    import SQLiteDBTools
    SQLiteDBTools.addTable()
    print('Notification_List table has been reset.')

def displayResults():
    top = Toplevel(root)
    top.minsize(425, 300)
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\\Traffic_Light.ico')

    header_frame = Frame(top)
    header_frame.pack(fill='x', pady=(10,0))
    entryLabel = Label(header_frame, text='Create Notification Record', font=('Arial', 14, 'bold'))
    entryLabel.pack(padx=10, pady=5)
    entryLabel.configure(anchor='center', justify='center')

    # Show search data
    entry = searchEntry.get()
    entryData = Label(header_frame, text=f'Search: {entry}', font=('Arial', 12, 'italic'))
    entryData.pack(pady=2)

    # Show database match
    info_frame = Frame(top)
    info_frame.pack(fill='x', pady=(5,0))
    col1 = "MR"
    col2 = "SR"
    entry1, entry2 = (entry.split('&', 1) if '&' in entry else (entry, ''))
    entry1 = entry1.strip()
    entry2 = entry2.strip()
    results = LSB.search_database(db_name, table_name, col1, col2, entry1, entry2)
    success = bool(results)
    location_value = ''
    maintained_by_num = None
    agency_info = None
    if not success:
        col1 = "SR"
        col2 = "MR"
        results = LSB.search_database(db_name, table_name, col1, col2, entry1, entry2)
        success = bool(results)
    if not success:
        resultsFromDB = Label(info_frame, text='NO RESULTS FOUND. PLEASE TRY AGAIN.', font=('Arial', 12, 'italic'))
        resultsFromDB.pack()
    else:
        # Get location and maintained by number from LiteBookData
        result = [item for t in results for item in t]
        location_value = f"{result[0]} & {result[1]}"
        maintained_by_num = result[2] if len(result) > 2 else None
        # Fetch agency info from Agency_Contact_Information
        agency_info = None
        if maintained_by_num:
            import sqlite3
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Agency_Contact_Information WHERE id=?", (maintained_by_num,))
            agency_info = cursor.fetchone()
            conn.close()
        # Display location and agency info
        locationLabel = Label(info_frame, text='Location:', font=('Arial', 12))
        locationLabel.pack(anchor='center', padx=10, pady=2)
        locationData = Label(info_frame, text=location_value, font=('Arial', 10, 'bold'), justify='center')
        locationData.pack(anchor='center')
        agencyLabel = Label(info_frame, text='Agency Info:', font=('Arial', 12))
        agencyLabel.pack(anchor='center', padx=10, pady=2)
        if agency_info:
            agencyData = Label(info_frame, text=' | '.join(str(x) for x in agency_info[1:]), font=('Arial', 10, 'bold'), justify='center')
            agencyData.pack(anchor='center')
        else:
            agencyData = Label(info_frame, text='No agency info found.', font=('Arial', 10, 'bold'), justify='center')
            agencyData.pack(anchor='center')

    form_frame = Frame(top)
    form_frame.pack(pady=10)
    natureLabel = Label(form_frame, text='Nature:', font=('Arial', 12))
    natureEntry = Entry(form_frame)
    requestDateLabel = Label(form_frame, text='Request Date:', font=('Arial', 12))
    requestDateEntry = Entry(form_frame)
    requestTimeLabel = Label(form_frame, text='Request Time:', font=('Arial', 12))
    requestTimeEntry = Entry(form_frame)
    unitLabel = Label(form_frame, text='Unit:', font=('Arial', 12))
    unitEntry = Entry(form_frame)
    locationLabel = Label(form_frame, text='Location:', font=('Arial', 12))
    locationEntry = Entry(form_frame)
    locationEntry.insert(0, location_value)  # Auto-fill location
    agencyLabel = Label(form_frame, text='Agency:', font=('Arial', 12))
    agencyEntry = Entry(form_frame)
    if agency_info:
        agencyEntry.insert(0, str(agency_info[1]))  # Insert agency acronym
    notificationDateLabel = Label(form_frame, text='Notification Date:', font=('Arial', 12))
    notificationDateEntry = Entry(form_frame)
    notificationTimeLabel = Label(form_frame, text='Notification Time:', font=('Arial', 12))
    notificationTimeEntry = Entry(form_frame)
    userLabel = Label(form_frame, text='User:', font=('Arial', 12))
    userEntry = Entry(form_frame)
    # Add right padding to notification entry fields
    notificationDateEntry.grid(row=1, column=3, padx=(5,12), pady=5)
    notificationTimeEntry.grid(row=2, column=3, padx=(5,12), pady=5)
    userEntry.grid(row=3, column=3, padx=(5,12), pady=5)
    # Nature field above all others
    natureLabel.grid(row=0, column=0, padx=10, pady=5, sticky='e')
    natureEntry.grid(row=0, column=1, columnspan=3, padx=(5,12), pady=5, sticky='we')
    # Shift all other fields down by 1 row
    requestDateLabel.grid(row=1, column=0, padx=10, pady=5, sticky='e')
    requestDateEntry.grid(row=1, column=1, padx=5, pady=5)
    requestTimeLabel.grid(row=2, column=0, padx=10, pady=5, sticky='e')
    requestTimeEntry.grid(row=2, column=1, padx=5, pady=5)
    unitLabel.grid(row=3, column=0, padx=10, pady=5, sticky='e')
    unitEntry.grid(row=3, column=1, padx=5, pady=5)
    notificationDateLabel.grid(row=1, column=2, padx=10, pady=5, sticky='e')
    notificationTimeLabel.grid(row=2, column=2, padx=10, pady=5, sticky='e')
    userLabel.grid(row=3, column=2, padx=10, pady=5, sticky='e')

    buttons_frame = Frame(top)
    buttons_frame.pack(pady=(0, 20))
    saveButton = Button(buttons_frame, text = 'Save', width = 20)
    resetButton = Button(buttons_frame, text = 'Reset', width = 20)
    saveButton.pack(side='left', padx=10)
    resetButton.pack(side='left', padx=10)

    import datetime
    def auto_populate_date(event):
        today = datetime.date.today().strftime('%m-%d-%Y')
        event.widget.delete(0, END)
        event.widget.insert(0, today)
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    def auto_populate_time(event):
        now = datetime.datetime.now().strftime('%H:%M')
        event.widget.delete(0, END)
        event.widget.insert(0, now)
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    def highlight_entry(event):
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    # Bind auto-populate and highlight to date/time fields in entry form
    requestDateEntry.bind('<FocusIn>', auto_populate_date)
    requestTimeEntry.bind('<FocusIn>', auto_populate_time)
    notificationDateEntry.bind('<FocusIn>', auto_populate_date)
    notificationTimeEntry.bind('<FocusIn>', auto_populate_time)
    for entry in [requestDateEntry, requestTimeEntry, notificationDateEntry, notificationTimeEntry]:
        entry.bind('<FocusIn>', highlight_entry, add='+')

    def save_new_record():
        nature = natureEntry.get()
        request_date = requestDateEntry.get()
        request_time = requestTimeEntry.get()
        unit = unitEntry.get()
        location = locationEntry.get()
        # Fetch agency value from column 4 of LiteBookData
        import sqlite3
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        entry1, entry2 = (searchEntry.get().split('&', 1) if '&' in searchEntry.get() else (searchEntry.get(), ''))
        entry1 = entry1.strip()
        entry2 = entry2.strip()
        cursor.execute(f"SELECT * FROM {table_name} WHERE MR=? AND SR=?", (entry1, entry2))
        row = cursor.fetchone()
        if row and len(row) > 4:
            agency = str(row[4])
        else:
            agency = agencyEntry.get()
        notification_date = notificationDateEntry.get()
        notification_time = notificationTimeEntry.get()
        user = userEntry.get()
        conn.close()
        if not request_date.strip() or not request_time.strip():
            from tkinter import messagebox
            messagebox.showerror('Input Error', 'Request Date and Request Time must be filled.')
            return
        if not notification_date.strip() or not notification_time.strip():
            from tkinter import messagebox
            messagebox.showerror('Input Error', 'Notification Date and Notification Time must be filled.')
            return
        # Save to DB with correct mapping
        conn = sqlite3.connect(db_name)
        sql = ("INSERT INTO Notification_List (Request_date, Request_time, Unit, Location, Agency, Notification_date, Notification_time, USER_ID, Nature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
        print('DEBUG: Saving new record:', (request_date, request_time, unit, location, agency, notification_date, notification_time, user, nature))
        conn.execute(sql, (request_date, request_time, unit, location, agency, notification_date, notification_time, user, nature))
        conn.commit()
        conn.close()
        listBoxPop()
        top.destroy()
    saveButton.config(command=save_new_record)

### --- Main Window Initialization --- ###
root = Tk()
root.minsize(525, 525)
root.title('Baltimore County Police Dispatch LiteSearch')
root.configure(bg='white')
root.iconbitmap('imagery\\Traffic_Light.ico')
LSB.log_event('PROGRAM START', 'PROGRAM STARTED SUCCESSFULLY', 'SYS')

# Context menu for Treeview
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label='Edit Record', command=lambda: edit_selected_record())

# Treeview for saved notifications
columns = (
    'Request_Date/Time', 'Unit', 'Location', 'Agency', 'Nature', 'Notification_Date/Time', 'USER_ID', 'Record_Added'
)
notificationTree = ttk.Treeview(root, columns=columns, show='headings', height=15)
column_widths = {
    'Request_Date/Time': 120,
    'Unit': 60,
    'Location': 300,
    'Agency': 110,
    'Nature': 180,
    'Notification_Date/Time': 140,
    'USER_ID': 70,
    'Record_Added': 120
}
for col in columns:
    notificationTree.heading(col, text=col.replace('_', ' '))
    notificationTree.column(col, width=column_widths[col], anchor='center', stretch=True)
scrollbarY = Scrollbar(root, orient=VERTICAL, command=notificationTree.yview)
notificationTree.config(yscrollcommand=scrollbarY.set)

#Menu bar
menu = Menu(root)
root.config(menu=menu)
#File menu
filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='Log', command=logFiles)
filemenu.add_command(label='Reset Notification Table', command=resetNotificationTable)
#Help Menu
helpmenu = Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='About', command=about)
helpmenu.add_command(label='License', command=license)
helpmenu.add_command(label='Contact Support', command=support)

#Title header
masterLabel = Label(root, text='LiteSearch', font=('Arial', 16, 'bold', 'italic'), bg='white')
headerLabel = Label(root, text='\nPlease enter the intersection below for agency\n responsible for traffic light maintenance.', font=('Arial', 12), background='white')

# Integrated Search Entry
searchLabel = Label(root, text='Intersection (Main Rd & Cross St)', font=('Arial', 10, 'bold'), background='white')
searchEntry = Entry(root, width=50, background='white')

# Buttons
searchButton = Button(root, text='Create Record', width=25, command=displayResults)
resetButton = Button(root, text='Reset', width=25, command=resetEntry)

# Add extra space before Treeview search bar
Frame(root, height=16, bg='white').pack()
treeSearchLabel = Label(root, text='Search Notifications:', font=('Arial', 10, 'bold'), background='white')
treeSearchEntry = Entry(root, width=50, background='white')

def filter_treeview(event=None):
    query = treeSearchEntry.get().lower()
    for item in notificationTree.get_children():
        values = notificationTree.item(item, 'values')
        if any(query in str(v).lower() for v in values):
            notificationTree.reattach(item, '', 'end')
        else:
            notificationTree.detach(item)
treeSearchEntry.bind('<KeyRelease>', filter_treeview)

masterLabel.pack()
headerLabel.pack()
searchLabel.pack(padx=3)
searchEntry.pack(padx=5, pady=2.5)
searchButton.pack(pady=2.5)
treeSearchLabel.pack(padx=3)
treeSearchEntry.pack(padx=5, pady=2.5)
resetButton.pack(pady=2.5)
notificationTree.pack(side=LEFT, fill=BOTH, expand=True)
scrollbarY.pack(side=RIGHT, fill=Y)
notificationTree.column('Location', width=200, anchor='center', stretch=True)
notificationTree.bind('<Button-3>', show_treeview_context_menu)

# Global Variables
db_name = "litesearch.db"
table_name = "LiteBookData"

# Sets the appid for the program. This is used to set the icon in the taskbar.
myappid = u'Madairy.LiteSearch.1.0.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def remove_notes_column_from_db():
    import sqlite3
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Notification_List)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'notes' in [c.lower() for c in columns]:
        # Get all columns except 'notes'
        keep_cols = [c for c in columns if c.lower() != 'notes']
        keep_cols_str = ', '.join(keep_cols)
        # Create new table
        cursor.execute(f"CREATE TABLE IF NOT EXISTS Notification_List_new AS SELECT {keep_cols_str} FROM Notification_List")
        conn.commit()
        # Drop old table
        cursor.execute("DROP TABLE Notification_List")
        conn.commit()
        # Rename new table
        cursor.execute("ALTER TABLE Notification_List_new RENAME TO Notification_List")
        conn.commit()
    conn.close()

# Call this once at startup to ensure 'notes' column is removed
remove_notes_column_from_db()

listBoxPop()  # Populate treeview with data on program start

root.mainloop()