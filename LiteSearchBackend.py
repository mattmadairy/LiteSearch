### LiteSearch SQLite DB search block
import sqlite3
import datetime as dt


db_name = 'litesearch.db'

# Date and time logic
today = dt.date.today()
t = dt.datetime.now().time()
day = today.strftime('%a')
time = t.strftime('%H%M')

weekend = day in ['Sat', 'Sun']
weekday = not weekend
businessHours = '0700' < time < '1600'
    

#DB location search 
def search_database(db_name, table_name, col1, col2, search_term1, search_term2):
    """Searches an SQLite database and returns matching rows."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name} WHERE {col1} LIKE ? AND {col2} LIKE ?"
    cursor.execute(query, (f"%{search_term1}%", f"%{search_term2}%"))
    results = cursor.fetchall()
    conn.close()
    return results

def log_event(event_type, message, user):
    """Inserts a new event into the event_log table."""
    conn = sqlite3.connect(db_name)
    conn.execute("INSERT INTO event_log (event_type, message, user) VALUES (?, ?, ?)", (event_type, message, user))
    conn.commit()
    conn.close()

def support_request(name, email, reason):
    """Inserts a support request into the Support_Requests table."""
    log_event('SUBMIT', 'SUPPORT REQUEST SUBMITTED', 'MLM91')
    conn = sqlite3.connect(db_name)
    conn.execute("INSERT INTO Support_Requests (Name, Email, Reason) VALUES (?, ?, ?)", (name, email, reason))
    conn.commit()
    conn.close()
  
def contactInfo(id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    query = "SELECT * FROM Agency_Contact_Information WHERE id = ?"
    # Time decision structure
    now = dt.datetime.now()
    current_time = int(now.strftime('%H%M'))
    weekday = now.weekday() >= 0 and now.weekday() <= 4  # Monday=0, Friday=4
    business_hours = current_time >= 700 and current_time <= 1600
    print(f"DEBUG: Today is {weekday} ({now.weekday()}), Time: {now.strftime('%H:%M')}, current_time={current_time}, weekday={weekday}, business_hours={business_hours}, id={id}")
    if id == 7:
        print(f"DEBUG: Branch decision for id==7: weekday={weekday}, business_hours={business_hours}")
        if weekday and business_hours:
            print("DEBUG: Bulletproof: SELECT agency 7 (weekday and business hours)")
            cursor.execute(query, (7,))
            agency_row = cursor.fetchone()
            print(f"DEBUG: Bulletproof: Returned agency row: {agency_row}")
            conn.close()
            return agency_row
        else:
            print("DEBUG: Bulletproof: SELECT agency 2 (not weekday or not business hours)")
            cursor.execute(query, (2,))
            agency_row = cursor.fetchone()
            print(f"DEBUG: Bulletproof: Returned agency row: {agency_row}")
            if agency_row is None:
                print("DEBUG: No record found for agency id 2 in Agency_Contact_Information table!")
            conn.close()
            return agency_row
    else:
        print(f"DEBUG: Bulletproof: SELECT agency {id} info (id not 7)")
        cursor.execute(query, (id,))
        agency_row = cursor.fetchone()
        print(f"DEBUG: Bulletproof: Returned agency row: {agency_row}")
        conn.close()
        return agency_row

def notificationRecord(requestDate, requestTime, unit, location, agency, notificationDate, notificationTime, UserId):
    """Inserts a new notification record into Notification_List with separate date and time columns."""
    log_event('REQUEST', 'NOTIFICATION ENTRY REQUEST', 'MLM91')
    conn = sqlite3.connect(db_name)
    conn.execute("INSERT INTO Notification_List (Request_date, Request_time, Unit, Location, Agency, Notification_date, Notification_time, USER_ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (requestDate, requestTime, unit, location, agency, notificationDate, notificationTime, UserId))
    conn.commit()
    conn.close()

def listBoxData():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT * FROM Notification_List')
    notifications = c.fetchall()
    conn.close()
    return notifications