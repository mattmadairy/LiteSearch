#DB Creator
#reads csv to pandas dataframe & sets up SQLite DataBase 
#imports
#import pandas as pd
#import csv
import sqlite3

#create DB from CSV
def csv_to_db():
    # data from CSV to pandas dataframe
    print("\nConverting CSV to dataframe...\n")

    df = pd.read_csv(
        filepath_or_buffer = r"LightBook Data - Sheet1.csv",
        header = 0
        )

    print("Connecting to DataBase...")

    #opens connection & creates db if none exists. replaces db if one does exist
    connection = sqlite3.connect(r'litesearch.db')
    df.to_sql(
        name = 'LiteBookData',
        con = connection,
        if_exists = "replace",
        index = False,
        dtype = {'MR': 'TEXT',
                'SR': 'TEXT',
                'MAINTAINED BY': 'INTEGER',
                '': 'TEXT'})

    print('Success!')
    connection.commit()
    connection.close()
#############################################################################################################################
#add column to table
def addColumn():
    conn=sqlite3.connect('litesearch.db')

    #create a cursor
    c= conn.cursor()

    #create a table
    c.execute("""CREATE TABLE event_log (first_name text,last_name text,email text)""") 

    #insert values in the columns of the table
    c.execute("INSERT INTO customers_table VALUES ('Mary','Dakota','mdakota@gmail.com')")
    c.execute("INSERT INTO customers_table VALUES ('Amy','Jackson','ajackson@gmail.com')")

    #Printing all the values before altering the table
    print("Table before using ALTER ..")

    c.execute("SELECT * FROM event_log")
    print(c.fetchall())

    #Alter the table
    c.execute("ALTER TABLE event_log ADD COLUMN date TEXT")

    #Print the table after altering
    print("Table after using ALTER ..")
    c.execute("SELECT * FROM event_log")
    print(c.fetchall())

    print("Command executed successfully...")
    conn.commit()
    #close our connection
    conn.close()

#############################################################################################################################
def addTable():
    # importing sqlite module 
    import sqlite3 
    
    # create connection to the database  
    
    connection = sqlite3.connect('litesearch.db') 
    #drop old table
    connection.execute("DROP TABLE IF EXISTS Notification_List")
    # create new table & columns 
    connection.execute('''CREATE TABLE IF NOT EXISTS Notification_List
            (ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            timestamp TIMESTAMP DEFAULT (datetime('now', 'localtime')),
            Request_date_time TEXT NOT NULL,
            Unit TEXT NOT NULL,            
            Location TEXT NOT NULL,
            Agency TEXT NOT NULL,           
            Notification_date_time TEXT NT NULL,
            USER_ID TEXT NOT NULL); ''')
    
    # close the connection 
    connection.close()

#############################################################################################################################
def insertMultipleRecords(recordList):
    try:
        sqliteConnection = sqlite3.connect('litesearch.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqliteConnection.execute('DROP TABLE IF EXISTS Agency_Contact_Information')
        sqliteConnection.execute('''CREATE TABLE Agency_Contact_Information
                                 (ID INTEGER PRIMARY KEY NOT NULL,
                                 Agency TEXT NOT NULL,
                                 Phone TEXT NOT NULL);''')
        sqlite_insert_query = """INSERT INTO Agency_Contact_Information
                          (ID, Agency, Phone) 
                          VALUES (?, ?, ?);"""

        cursor.executemany(sqlite_insert_query, recordList)
        sqliteConnection.commit()
        print("Total", cursor.rowcount, "Records inserted successfully into SqliteDb_developers table")
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert multiple records into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

#Not in order, to match the existing light book records.
""" recordsToInsert = [(0, 'PROPOSED', 'NUMBER UNKNOWN'),
                   (1,'MD Statewide Operations Center (SHA) 24/7', '410-582-5650'),
                   (2,'County Signal Shop (After Hours)', '410-967-7096'),
                   (3,'Mike Lorenzo', '410-967-7103 (Co. Cell)'),
                   (4,'Tim Price', '443-823-9390 (Pers. Cell)'),
                   (5, 'MDTA', '410-537-1230'),
                   (6,'Angelica Daniel', '410-207-9670 (Pers. Cell)'),
                   (7,'County Signal Shop (M-F, 0700-1600 hrs)', '410-887-8601'),
                   (8,'Baltimore City Traffic Management Center 24/7', '443-984-2189'),
                   (9, 'PRIVATE', 'NUMBER UNKNOWN')]

insertMultipleRecords(recordsToInsert) """

#############################################################################################################################
def wipe_event_log_table():
    """Creates the event_log table if it doesn't exist."""
    conn = sqlite3.connect('litesearch.db')
    conn.execute("DROP TABLE IF EXISTS event_log")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS event_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT (datetime('now', 'localtime')),
            user TEXT,
            event_type TEXT,
            message TEXT
        )
    ''')
    conn.close()

#############################################################################################################################
#csv_to_db()
#addColumn()
addTable()
#eventLogEntry
# #wipe_event_log_table()