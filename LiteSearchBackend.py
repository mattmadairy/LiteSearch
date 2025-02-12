### LiteSearch SQLite DB search block
import sqlite3
import datetime as dt
from tkinter import *


db_name = 'litesearch.db'


today = dt.date.today()
t = dt.datetime.now().time()
day = today.strftime('%a')
time = t.strftime('%H%M')

if day == 'Sat' or day == 'Sun':
    weekend = True
    weekday = False
    
else:
    weekend  = False
    weekday = True
    

if time >= '1600' or time <= '0700':
    businessHours = False
    
else:
    businessHours = True
    

#DB location search 
def search_database(db_name, table_name, col1, col2, search_term1, search_term2):
    """Searches an SQLite database and prints matching rows."""

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    query = f"SELECT * FROM {table_name} WHERE {col1} LIKE ? AND {col2} LIKE ?"
    cursor.execute(query, (f"%{search_term1}%", f"%{search_term2}%"))

    results = cursor.fetchall()

    conn.close()
    
    return results

def log_event(event_type, message, user):
    """Inserts a new event into the event_log table."""
    conn = sqlite3.connect('litesearch.db')
    conn.execute("INSERT INTO event_log (event_type, message, user) VALUES (?, ?, ?)", (event_type, message, user))
    conn.commit()
    conn.close()

def support_request(name, email, reason):
    """Inserts a new event into the event_log table."""
    log_event('SUBMIT', 'SUPPORT REQUEST SUBMITTED', 'MLM91')
    conn = sqlite3.connect('litesearch.db')
    conn.execute("INSERT INTO Support_Requests (Name, Email, Reason) VALUES (?, ?, ?)", (name, email, reason))
    conn.commit()
    conn.close()
  
def contactInfo(id):
    conn = sqlite3.connect('litesearch.db')
    cursor = conn.cursor()

    query = "SELECT *  FROM Agency_Contact_Information WHERE id = ?"
    cursor.execute(query, (id,))

    queryReturn = cursor.fetchone()

    if queryReturn:
        qrtReturn = list(queryReturn)
                    
    else:
        print('No record found with ID:', id)
    
    if qrtReturn[0] == 7: 
        if weekday == False or businessHours == False:
            cursor.execute(query, ('2'))
            afterHours = cursor.fetchone()
            conn.close()
            return afterHours
        else:
            return qrtReturn

    else:
        conn.close()
        return qrtReturn

def notificationRecord(requestDateTime, unit, location, agency, notificationDateTime, UserId):
    """Inserts a new event into the event_log table."""
    log_event('REQUEST','NOTIFICATION ENTRY REQUEST','MLM91')
    conn = sqlite3.connect('litesearch.db')
    conn.execute("INSERT INTO Notification_List (Request_date_time, Unit, Location, Agency, Notification_date_time, USER_ID) VALUES (?, ?, ?, ?, ?, ?)",
                 (requestDateTime, unit, location, agency, notificationDateTime, UserId))
    conn.commit()
    conn.close()

def listBoxData():
    conn = sqlite3.connect('litesearch.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Notification_List')
    notifications = c.fetchall()
    conn.close()
    return notifications