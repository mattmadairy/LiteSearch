import sqlite3

#create DB from CSV
def csv_to_db():
    # Placeholder for CSV to DB function. Requires pandas and CSV file.
    pass
#############################################################################################################################
#add column to table
def addColumn():
    # Example function to add a column to event_log table.
    conn = sqlite3.connect('litesearch.db')
    c = conn.cursor()
    c.execute("ALTER TABLE event_log ADD COLUMN date TEXT")
    conn.commit()
    conn.close()

#############################################################################################################################
def addTable():
    # Create Notification_List table with separate date and time columns
    connection = sqlite3.connect('litesearch.db')
    connection.execute("DROP TABLE IF EXISTS Notification_List")
    connection.execute('''CREATE TABLE IF NOT EXISTS Notification_List
            (ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            timestamp TIMESTAMP DEFAULT (datetime('now', 'localtime')),
            Request_date TEXT NOT NULL,
            Request_time TEXT NOT NULL,
            Unit TEXT NOT NULL,
            Location TEXT NOT NULL,
            Agency TEXT NOT NULL,
            Notification_date TEXT NOT NULL,
            Notification_time TEXT NOT NULL,
            USER_ID TEXT NOT NULL);''')
    connection.close()

#############################################################################################################################
def insertMultipleRecords(recordList):
    # Insert multiple records into Agency_Contact_Information
    try:
        sqliteConnection = sqlite3.connect('litesearch.db')
        cursor = sqliteConnection.cursor()
        sqliteConnection.execute('DROP TABLE IF EXISTS Agency_Contact_Information')
        sqliteConnection.execute('''CREATE TABLE Agency_Contact_Information
                                 (ID INTEGER PRIMARY KEY NOT NULL,
                                 Agency TEXT NOT NULL,
                                 Phone TEXT NOT NULL);''')
        sqlite_insert_query = "INSERT INTO Agency_Contact_Information (ID, Agency, Phone) VALUES (?, ?, ?);"
        cursor.executemany(sqlite_insert_query, recordList)
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert multiple records into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

## Example usage:
# recordsToInsert = [ ... ]
# insertMultipleRecords(recordsToInsert)

#############################################################################################################################
def wipe_event_log_table():
    # Creates the event_log table if it doesn't exist.
    conn = sqlite3.connect('litesearch.db')
    conn.execute("DROP TABLE IF EXISTS event_log")
    conn.execute('''CREATE TABLE IF NOT EXISTS event_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT (datetime('now', 'localtime')),
            user TEXT,
            event_type TEXT,
            message TEXT
        )''')
    conn.close()

#############################################################################################################################
addTable()