# --- GLOBAL IMPORTS ---
from tkinter import Tk, Menu, Label, Entry, Toplevel, Frame, Button, StringVar, messagebox, Text, Scrollbar, VERTICAL, END, LEFT, RIGHT, BOTH, Y
from tkinter import ttk
from datetime import datetime, timedelta
import LiteSearchBackend
import sqlite3
import ctypes

LSB = LiteSearchBackend  # Use module as LSB

def center_window(win, width, height):
    try:
        win.update_idletasks()
        ws = win.winfo_screenwidth()
        hs = win.winfo_screenheight()
        x = (ws // 2) - (width // 2)
        y = (hs // 2) - (height // 2)
        win.geometry(f'{width}x{height}+{x}+{y}')
    except Exception:
        pass

# Top-level resetEntry function
def listBoxPop():
    # Clear all items from the Treeview
    notificationTree.delete(*notificationTree.get_children())
    notificationsList = LSB.listBoxData()
    # Configure tag for missing notification date/time
    notificationTree.tag_configure('missing_notification', background='yellow')
    for notification in notificationsList:
        if len(notification) >= 12:
            cleaned = [str(x).replace('\n', ' ') if isinstance(x, str) else x for x in notification]
            db_id = cleaned[0]
            request_date = cleaned[2]
            request_time = cleaned[3]
            unit = cleaned[4]
            incident = cleaned[11] if cleaned[11] is not None else ''
            location = cleaned[5]
            agency = cleaned[6]
            notification_date = cleaned[7]
            notification_time = cleaned[8]
            user = cleaned[9]
            nature = cleaned[10]
            record_added = cleaned[1]  # timestamp
            # Convert notification_date from ISO to MM-DD-YYYY for display
            try:
                notification_date_display = datetime.strptime(notification_date, '%Y-%m-%d').strftime('%m-%d-%Y')
            except Exception:
                notification_date_display = notification_date
            values = [
                db_id,
                f"{request_date} {request_time}",
                unit,
                incident,
                location,
                agency,
                nature,
                f"{notification_date_display} {notification_time}",
                user,
                record_added
            ]
            # Highlight if notification date or time missing
            if not notification_date.strip() or not notification_time.strip():
                notificationTree.insert('', 'end', values=values, tags=('missing_notification',))
            else:
                notificationTree.insert('', 'end', values=values)
        else:
            padded = [''] * 10
            notificationTree.insert('', 'end', values=padded)
def resetEntry():
    searchEntry.delete(0, END)
    notificationTree.delete(*notificationTree.get_children())
    listBoxPop()

# Top-level resetTreeSearchEntry function
def resetTreeSearchEntry():
    treeSearchEntry.delete(0, END)
    notificationTree.delete(*notificationTree.get_children())
    listBoxPop()  # Fully repopulate the treeview

# Print preview window for weekly report
def open_weekly_report_preview():
    preview_win = Toplevel()
    center_window(preview_win, 1250, 600)
    preview_win.focus_force()
    preview_win.grab_set()
    preview_win.title("Weekly Report Preview")
    preview_win.iconbitmap('imagery\\Traffic_Light.ico')

    # Calculate start and end dates
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    # Dates entry at top
    dates_frame = Frame(preview_win)
    dates_frame.pack(fill='x', padx=10, pady=(10, 0))
    Label(dates_frame, text="Start Date:", font=("Arial", 11, "bold")).pack(side='left', padx=(0, 5))
    start_date_var = StringVar(value=start_date.strftime('%Y-%m-%d'))
    start_date_entry = Entry(dates_frame, textvariable=start_date_var, font=("Arial", 11), width=12)
    start_date_entry.pack(side='left', padx=(0, 20))
    Label(dates_frame, text="End Date:", font=("Arial", 11, "bold")).pack(side='left', padx=(0, 5))
    end_date_var = StringVar(value=end_date.strftime('%Y-%m-%d'))
    end_date_entry = Entry(dates_frame, textvariable=end_date_var, font=("Arial", 11), width=12)
    end_date_entry.pack(side='left', padx=(0, 10))

    header_text = "LiteSearch\nWeekly Notification Report\n"
    def get_timeframe():
        return f"Timeframe: {start_date_var.get()} to {end_date_var.get()}"
    text = Text(preview_win, wrap='none', font=("Consolas", 10))
    text.pack(expand=True, fill='both', padx=10, pady=10)
    def populate_text_with_report():
        text.config(state='normal')
        text.delete('1.0', 'end')
        # Header
        text.insert('end', header_text)
        text.insert('end', get_timeframe() + "\n\n")
        try:
            start = datetime.strptime(start_date_var.get(), '%Y-%m-%d').date()
            end = datetime.strptime(end_date_var.get(), '%Y-%m-%d').date()
            end_inclusive = end + timedelta(days=1)
        except Exception:
            text.insert('end', "Invalid date format. Please use YYYY-MM-DD.\n")
            text.config(state='disabled')
            return
        conn = sqlite3.connect(LSB.db_name)
        cursor = conn.cursor()
        # Filter using timestamp field, make end date inclusive
        cursor.execute("SELECT * FROM Notification_List WHERE timestamp >= ? AND timestamp < ? ORDER BY timestamp DESC", (start.strftime('%Y-%m-%d'), end_inclusive.strftime('%Y-%m-%d')))
        rows = cursor.fetchall()
        conn.close()
        # --- FIXED INDENTATION ---
        if rows and len(rows) > 0:
            headers = [
                "Request Date/Time", "Unit", "Incident", "Location", "Agency", "Nature", "Notification Date/Time", "User", "Record Added"
            ]
            # Build all data rows first
            data_rows = []
            for row in rows:
                try:
                    notification_date_display = datetime.strptime(row[7], '%Y-%m-%d').strftime('%m-%d-%Y')
                except Exception:
                    notification_date_display = row[7]
                request_date_time = f"{row[2]} {row[3]}"
                unit = str(row[4])
                incident = str(row[11]) if len(row) > 11 else ''
                location = str(row[5])
                agency = str(row[6])
                nature = str(row[10])
                notification_time = str(row[8])
                notification_date_time = f"{notification_date_display} {notification_time}"
                user_id = str(row[9])
                record_added = str(row[1])
                values = [
                    request_date_time,
                    unit,
                    incident,
                    location,
                    agency,
                    nature,
                    notification_date_time,
                    user_id,
                    record_added
                ]
                data_rows.append(values)
            # Calculate max width for each column
            col_widths = [len(headers[i]) for i in range(len(headers))]
            for row in data_rows:
                for i, val in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(val)))
            def center_text(text, width):
                text = str(text)
                if len(text) >= width:
                    return text[:width]
                pad = width - len(text)
                left = pad // 2
                right = pad - left
                return ' ' * left + text + ' ' * right

            def wrap_text(text, width):
                text = str(text)
                return [text[i:i+width] for i in range(0, len(text), width)] or ['']

            # Header row
            # Center all column headers
            header_line = "|" + "|".join([center_text(h, col_widths[i]) for i, h in enumerate(headers)]) + "|\n"
            # Separator row
            sep_line = "|" + "|".join(["-" * col_widths[i] for i in range(len(col_widths))]) + "|\n"
            text.insert('end', header_line)
            text.insert('end', sep_line)
            for values in data_rows:
                # Wrap each column's value
                wrapped_cols = [wrap_text(values[i], col_widths[i]) for i in range(len(values))]
                max_lines = max(len(wrapped) for wrapped in wrapped_cols)
                # Pad columns so all have the same number of lines
                for i in range(len(wrapped_cols)):
                    if len(wrapped_cols[i]) < max_lines:
                        wrapped_cols[i].extend([''] * (max_lines - len(wrapped_cols[i])))
                # Print each line for this row
                for line_idx in range(max_lines):
                    line_parts = []
                    for i in range(len(wrapped_cols)):
                        cell = wrapped_cols[i][line_idx]
                        # Location = index 3, Agency = index 4
                        if i in [3, 4]:
                            part = str(cell).ljust(col_widths[i])
                        else:
                            part = center_text(cell, col_widths[i])
                        line_parts.append(part)
                    line = "|" + "|".join(line_parts) + "|\n"
                    text.insert('end', line)
        else:
            text.insert('end', "No records found.\n")
        text.config(state='disabled')
    generate_btn = Button(dates_frame, text="Generate", command=populate_text_with_report, width=12)
    generate_btn.pack(side='left', padx=(10, 0))
    populate_text_with_report()
    # ...existing code for open_weekly_report_preview (dates_frame, header_text, get_timeframe, text widget, populate_text_with_report, buttons, etc.)...

# Weekly report function
def generate_weekly_report():
    # ...existing code...
    conn = sqlite3.connect(LSB.db_name)
    cursor = conn.cursor()
    # Calculate date 7 days ago
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)
    # Query for records in the last 7 days (assuming Notification_date is in YYYY-MM-DD format)
    cursor.execute("SELECT * FROM Notification_List WHERE Notification_date >= ? ORDER BY Notification_date DESC", (seven_days_ago.strftime('%Y-%m-%d'),))
    rows = cursor.fetchall()
    conn.close()
    # Format report as a list of dicts
    report = []
    for row in rows:
        # ...existing code for formatting report rows...
        report.append(row)
    # Decreased width for Nature
    default_column_widths = {
        'Nature': 60,
        'Notification_Date/Time': 140,
        'USER_ID': 60,
        'Record_Added': 120
    }
    for col, width in default_column_widths.items():
        notificationTree.column(col, width=width, anchor='center', stretch=True)
    listBoxPop()  # Rebuild the Treeview

def logFiles():
    # ...existing code...
    LSB.log_event('REQUEST', 'LOG FILES TAB REQUESTED', 'MLM91')
    top = Toplevel()
    top.focus_force()
    top.grab_set()
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\\Traffic_Light.ico')
    menu = Menu(top)
    top.config(menu=menu)
    filemenu = Menu(menu)
    menu.add_cascade(label='File', menu=filemenu)
    filemenu.add_command(label='Print', command=lambda: None)
    logLabel = Label(top, text='Log Files', font=('Arial', 12, 'bold'))
    logLabel.pack()
    # Add Treeview widget for event_log table
    from tkinter import ttk
    columns = ('id', 'timestamp', 'user', 'event_type', 'message')
    tree = ttk.Treeview(top, columns=columns, show='headings', height=8)
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=80 if col == 'id' else 120, anchor='w')
    tree.pack(padx=10, pady=10, fill='x')

    import sqlite3
    conn = sqlite3.connect('litesearch.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, user, event_type, message FROM event_log ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        tree.insert('', 'end', values=row)
    center_window(top, 600, 300)

def about():
    LSB.log_event('REQUEST', 'REQUEST ABOUT INFO', 'MLM91')
    top = Toplevel()
    center_window(top, 425, 200)
    top.focus_force()
    top.grab_set()
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\\Traffic_Light.ico')
    with open('about.txt', 'r') as aboutFile:
        aboutContent = aboutFile.read()
    aboutLabel = Label(top, text=aboutContent, wraplength=375, justify='left')
    aboutLabel.pack()

def license():
    LSB.log_event('REQUEST', 'REQUEST LICENSE INFO', 'MLM91')
    top = Toplevel()
    center_window(top, 425, 350)
    top.focus_force()
    top.grab_set()
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
    center_window(top, 425, 365)
    top.focus_force()
    top.grab_set()
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


def show_treeview_context_menu(event):
    item_id = notificationTree.identify_row(event.y)
    if item_id:
        notificationTree.selection_set(item_id)
        notificationTree.focus(item_id)
        context_menu.post(event.x_root, event.y_root)
    else:
        context_menu.unpost()

def displayResults():
    top = Toplevel(root)
    center_window(top, 600, 450)
    top.focus_force()
    top.grab_set()
    #top.geometry('550x400')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\Traffic_Light.ico')
    header_frame = Frame(top)
    header_frame.pack(fill='x', pady=(10,0))
    entryLabel = Label(header_frame, text='Create Notification Record', font=('Arial', 16, 'bold'))
    entryLabel.pack(padx=10, pady=5)
    entryLabel.configure(anchor='center', justify='center')
    # Show search data
    entry = searchEntry.get()
    entryData = Label(header_frame, text=f'Search: \n{entry}', font=('Arial', 12, 'italic'))
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
        # Fetch agency info using time-based decision structure
        agency_info = None
        if maintained_by_num:
            agency_info = LSB.contactInfo(maintained_by_num)
            # ...removed debug print statement...

        # Display location and agency info
        locationLabel = Label(info_frame, text='Location:', font=('Arial', 12))
        locationLabel.pack(anchor='center', padx=10, pady=2)
        locationData = Label(info_frame, text=location_value, font=('Arial', 14, 'bold'), justify='center')
        locationData.pack(anchor='center')
        agencyLabel = Label(info_frame, text='Agency Info:', font=('Arial', 12))
        agencyLabel.pack(anchor='center', padx=10, pady=2)

    if agency_info:
        window_bg = info_frame.winfo_toplevel().cget('bg')
        agency_parts = [str(x).strip() for x in agency_info[1:]]
        agency_text = ' | '.join(agency_parts)
        agencyTextWidget = Text(
            info_frame,
            font=('Arial', 14, 'bold'),
            height=1,
            width=len(agency_text)+2,
            borderwidth=0,
            highlightthickness=0,
            bg=window_bg
        )
        agencyTextWidget.insert('end', agency_parts[0])
        for part in agency_parts[1:]:
            agencyTextWidget.insert('end', ' | ')
            start_idx = agencyTextWidget.index('end-1c')
            agencyTextWidget.insert('end', part)
            end_idx = agencyTextWidget.index('end-1c')
            agencyTextWidget.tag_add('highlight', start_idx, end_idx)
        # Center the text horizontally
        agencyTextWidget.tag_configure('center', justify='center')
        agencyTextWidget.tag_add('center', '1.0', 'end')
        agencyTextWidget.tag_configure('highlight', foreground='red')  # Change color as needed
        agencyTextWidget.config(state='disabled')
        agencyTextWidget.pack(anchor='center')
    else:
        agencyData = Label(info_frame, text='No agency info found.', font=('Arial', 14, 'bold'), justify='center', bg=info_frame.winfo_toplevel().cget('bg'))
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
    # All widgets created above are already parented to form_frame
    requestDateLabel.grid(row=1, column=0, padx=10, pady=5, sticky='e')
    requestDateEntry.grid(row=1, column=1, padx=5, pady=5)
    requestTimeLabel.grid(row=2, column=0, padx=10, pady=5, sticky='e')
    requestTimeEntry.grid(row=2, column=1, padx=5, pady=5)
    unitLabel.grid(row=3, column=0, padx=10, pady=5, sticky='e')
    unitEntry.grid(row=3, column=1, padx=5, pady=5)
    incidentLabel = Label(form_frame, text='Incident Number:', font=('Arial', 12))
    incidentEntry = Entry(form_frame, font=('Arial', 12), width=13)
    incidentLabel.grid(row=4, column=0, padx=10, pady=5, sticky='e')
    incidentEntry.grid(row=4, column=1, padx=5, pady=5)
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
        incident = incidentEntry.get()
        location = locationEntry.get()
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
        # Mandatory fields: Nature, Request Date, Request Time, User
        if not nature.strip():
            from tkinter import messagebox
            messagebox.showerror('Input Error', 'Nature must be filled.')
            return
        if not request_date.strip():
            from tkinter import messagebox
            messagebox.showerror('Input Error', 'Request Date must be filled.')
            return
        if not request_time.strip():
            from tkinter import messagebox
            messagebox.showerror('Input Error', 'Request Time must be filled.')
            return
        if not user.strip():
            from tkinter import messagebox
            messagebox.showerror('Input Error', 'User must be filled.')
            return
        # Save to DB with correct mapping
        conn = sqlite3.connect(db_name)
        sql = ("INSERT INTO Notification_List (Request_date, Request_time, Unit, Location, Agency, Notification_date, Notification_time, USER_ID, Nature, Incident) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        conn.execute(sql, (request_date, request_time, unit, location, agency, notification_date, notification_time, user, nature, incident))
        conn.commit()
        conn.close()
        listBoxPop()
        top.destroy()
    saveButton.config(command=save_new_record)

def edit_selected_record():
    item_id = notificationTree.focus()
    if not item_id:
        return
    values = notificationTree.item(item_id, 'values')
    if not values:
        messagebox.showwarning("No selection", "Please select a record to edit.")
        return
    db_id = values[0]  # Use DB_ID from Treeview values for DB lookup
    conn = sqlite3.connect(LSB.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Notification_List WHERE ID=?", (db_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        messagebox.showerror("Error", f"No record found with DB_ID {db_id}.")
        return
    # Correct mapping based on your debug output and actual DB order
    request_date_value = row[2] if row[2] is not None else ''
    request_time_value = row[3] if row[3] is not None else ''
    unit_value = row[4] if row[4] is not None else ''
    location_value = row[5] if row[5] is not None else ''
    agency_value = row[6] if row[6] is not None else ''
    nature_value = row[10] if row[10] is not None else ''
    notification_date_value = row[7] if row[7] is not None else ''
    notification_time_value = row[8] if row[8] is not None else ''
    user_value = row[9] if row[9] is not None else ''
    record_added_value = row[1] if row[1] is not None else ''
    incident_value = row[11] if len(row) > 11 and row[11] is not None else ''
    entry_values = [
        request_date_value,
        request_time_value,
        unit_value,
        incident_value,
        location_value,
        agency_value,
        nature_value,
        notification_date_value,
        notification_time_value,
        user_value,
        record_added_value
    ]
    labels = ['Request Date:', 'Request Time:', 'Unit:', 'Incident Number:', 'Location:', 'Agency:', 'Nature:', 'Notification Date:', 'Notification Time:', 'User:', 'Record Added:']
    edit_win = Toplevel(root)
    edit_win.focus_force()
    edit_win.grab_set()
    edit_win.title('Baltimore County Police Dispatch LiteSearch')
    edit_win.geometry('425x490')
    center_window(edit_win, 425, 490)
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
        if label in ['Location:', 'Agency:']:
            entry.config(state='readonly')
        entry.grid(row=i, column=1, padx=10, pady=2)
        entries.append(entry)
    # ...existing code...
    def auto_populate_date(event):
        today = datetime.today().strftime('%m-%d-%Y')
        event.widget.delete(0, END)
        event.widget.insert(0, today)
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    def auto_populate_time(event):
        now = datetime.now().strftime('%H:%M')
        event.widget.delete(0, END)
        event.widget.insert(0, now)
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    def highlight_entry(event):
        event.widget.select_range(0, END)
        event.widget.icursor(END)
    # Request Date (entries[0]) and Notification Date (entries[7]) get date
    entries[0].bind('<FocusIn>', auto_populate_date)
    entries[7].bind('<FocusIn>', auto_populate_date)
    # Request Time (entries[1]) and Notification Time (entries[8]) get time
    entries[1].bind('<FocusIn>', auto_populate_time)
    entries[8].bind('<FocusIn>', auto_populate_time)
    # Highlight on focus for all date/time fields
    for idx in [0,1,7,8]:
        entries[idx].bind('<FocusIn>', highlight_entry, add='+')
    def save_edits():
        new_values = [e.get() for e in entries]
        if not new_values[0].strip() or not new_values[1].strip():
            # ...existing code...
            messagebox.showerror('Input Error', 'Request Date and Request Time must be filled.')
            return
        # Explicit mapping to Notification_List columns
        req_date = new_values[0]              # Request_date
        req_time = new_values[1]              # Request_time
        unit = new_values[2]                  # Unit
        incident = new_values[3]              # Incident
        location = new_values[4]              # Location
        agency = new_values[5]                # Agency
        nature = new_values[6]                # Nature
        notif_date = new_values[7]            # Notification_date
        notif_time = new_values[8]            # Notification_time
        user = new_values[9]                  # USER_ID
        # record_added = new_values[10] # Not updated
        selected_item = notificationTree.focus()
        values = notificationTree.item(selected_item, 'values') if selected_item else None
        db_id = values[0] if values else None
        if db_id is not None:
            import sqlite3
            conn = sqlite3.connect(LSB.db_name)
            sql = ("UPDATE Notification_List SET Request_date=?, Request_time=?, Unit=?, Incident=?, Location=?, Agency=?, Nature=?, Notification_date=?, Notification_time=?, USER_ID=? WHERE ID=?")
            conn.execute(sql, (req_date, req_time, unit, incident, location, agency, nature, notif_date, notif_time, user, db_id))
            conn.commit()
            conn.close()
            listBoxPop()
        else:
            pass
        edit_win.destroy()
    Button(edit_win, text='Save', command=save_edits, width=20).pack(pady=10)
    Button(edit_win, text='Cancel', command=edit_win.destroy, width=20).pack(pady=(0, 20))

### --- Main Window Initialization --- ###
root = Tk()
root.title('Baltimore County Police Dispatch LiteSearch')
root.configure(bg='white')
root.iconbitmap('imagery\Traffic_Light.ico')
center_window(root, 1270, 600)
LSB.log_event('PROGRAM START', 'PROGRAM STARTED SUCCESSFULLY', 'SYS')

# Context menu for Treeview
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label='Edit Record', command=lambda: edit_selected_record())

# Treeview for saved notifications
columns = (
    'DB_ID', 'Request_Date/Time', 'Unit', 'Incident', 'Location', 'Agency', 'Nature', 'Notification_Date/Time', 'USER_ID', 'Record_Added'
)
# Revert to original layout
notificationTree = ttk.Treeview(root, columns=columns, show='headings', height=15)
scrollbarY = Scrollbar(root, orient=VERTICAL, command=notificationTree.yview)
notificationTree.config(yscrollcommand=scrollbarY.set)
# Unified column widths for both initialization and resetEntry
column_widths = {
    'DB_ID': 0,  # Hide DB_ID column
    'Request_Date/Time': 120,
    'Unit': 60,
    'Incident': 60,
    'Location': 280,
    'Agency': 230,  # Increased width for Agency
    'Nature': 60,   # Decreased width for Nature
    'Notification_Date/Time': 120,
    'USER_ID':60,
    'Record_Added': 120
}
for col in columns:
    heading_text = 'User ID' if col == 'USER_ID' else col.replace('_', ' ')
    notificationTree.heading(col, text=heading_text)
    notificationTree.column(col, width=column_widths[col], anchor='w' if col == 'Location' else 'center', stretch=True)
notificationTree.column('DB_ID', width=0, stretch=False)  # Hide DB_ID column

#Menu bar
menu = Menu(root)
root.config(menu=menu)
#File menu
filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='Log', command=logFiles)
filemenu.add_command(label='Generate Weekly Report', command=open_weekly_report_preview)
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

# Make main search dynamic

# Improved filter: always repopulate full list if query is empty (including after backspace)
def filter_main_search(event=None):
    query = searchEntry.get().strip().lower()
    notificationTree.delete(*notificationTree.get_children())
    notificationsList = LSB.listBoxData()
    if not query:
        # Repopulate all
        for notification in notificationsList:
            if len(notification) >= 11:
                cleaned = [str(x).replace('\n', ' ') if isinstance(x, str) else x for x in notification]
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
                notification_date_display = notification_date
                try:
                    notification_date_display = datetime.strptime(notification_date, '%Y-%m-%d').strftime('%m-%d-%Y')
                except Exception:
                    pass
                values = [
                    db_id,
                    f"{request_date} {request_time}",
                    unit,
                    location,
                    agency,
                    nature,
                    f"{notification_date_display} {notification_time}",
                    user,
                    record_added
                ]
                notificationTree.insert('', 'end', values=values)
            else:
                padded = [''] * 9
                notificationTree.insert('', 'end', values=padded)
        return
    # Filtered results
    for notification in notificationsList:
        if len(notification) >= 11:
            cleaned = [str(x).replace('\n', ' ') if isinstance(x, str) else x for x in notification]
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
            notification_date_display = notification_date
            try:
                notification_date_display = datetime.strptime(notification_date, '%Y-%m-%d').strftime('%m-%d-%Y')
            except Exception:
                pass
            values = [
                db_id,
                f"{request_date} {request_time}",
                unit,
                location,
                agency,
                nature,
                f"{notification_date_display} {notification_time}",
                user,
                record_added
            ]
            if any(query in str(v).lower() for v in values):
                notificationTree.insert('', 'end', values=values)
        else:
            padded = [''] * 9
            # Only show padded if query is empty (already handled above)
            pass

# Add extra space before Treeview search bar
Frame(root, height=16, bg='white').pack()
# Create a frame for the search bar and reset button, but do NOT pack it here
treeSearchFrame = Frame(root, bg='white')
treeSearchLabel = Label(treeSearchFrame, text='Search Notifications:', font=('Arial', 10, 'bold'), background='white')
treeSearchLabel.pack(side='left', padx=(0, 5))
treeSearchEntry = Entry(treeSearchFrame, width=40, background='white')
treeSearchEntry.pack(side='left', padx=(0, 5), pady=2.5)

# Remove dynamic search and add button-based search for notifications
def search_notifications():
    query = treeSearchEntry.get().strip().lower()
    # Reattach all items first
    for item in notificationTree.get_children():
        notificationTree.reattach(item, '', 'end')
    if not query:
        return
    # Detach items that do not match
    for item in notificationTree.get_children():
        values = notificationTree.item(item, 'values')
        if not any(query in str(v).lower() for v in values):
            notificationTree.detach(item)

# Add the search button before the reset button
searchNotificationsButton = Button(treeSearchFrame, text='Search', width=12, command=search_notifications)
searchNotificationsButton.pack(side='left', padx=(5, 0), pady=2.5)
searchBarResetButton = Button(treeSearchFrame, text='Reset', width=12, command=resetTreeSearchEntry)
searchBarResetButton.pack(side='left', padx=(5, 0), pady=2.5)

masterLabel.pack()
headerLabel.pack()
searchLabel.pack(padx=3)
searchEntry.pack(padx=5, pady=2.5)
searchButton.pack(pady=2.5)
# Add vertical padding above the search bar
Frame(root, height=16, bg='white').pack()
treeSearchFrame.pack(fill='x', padx=5, pady=(5, 0))
notificationTree.pack(side=LEFT, fill=BOTH, expand=True)
scrollbarY.pack(side=RIGHT, fill=Y)
# Ensure Location column stays left-justified
notificationTree.column('Location', anchor='w')
notificationTree.bind('<Button-3>', show_treeview_context_menu)

# Global Variables
db_name = "litesearch.db"
table_name = "LiteBookData"
# Track all Treeview item IDs to ensure complete deletion
all_treeview_ids = set()

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


def add_incident_column_to_db():
    import sqlite3
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Notification_List)")
    columns = [row[1].lower() for row in cursor.fetchall()]
    if 'incident' not in columns:
        try:
            cursor.execute("ALTER TABLE Notification_List ADD COLUMN Incident TEXT")
            conn.commit()
        except Exception:
            pass
    conn.close()

# Call these once at startup
remove_notes_column_from_db()
add_incident_column_to_db()

listBoxPop()  # Populate treeview with data on program start
# Force centering after all widgets are packed
center_window(root, 1270, 600)
root.mainloop()