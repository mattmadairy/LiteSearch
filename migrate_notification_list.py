import sqlite3

def migrate_notification_list(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Get current columns
    cursor.execute("PRAGMA table_info(Notification_List)")
    columns = [row[1] for row in cursor.fetchall()]
    # Create new table with correct schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Notification_List_new (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Record_Added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Request_date TEXT,
            Request_time TEXT,
            Unit TEXT,
            Location TEXT,
            Agency TEXT,
            Nature TEXT,
            Notification_date TEXT,
            Notification_time TEXT,
            USER_ID TEXT
        )
    """)
    # Copy valid records (skip those with None for ID)
    cursor.execute("SELECT * FROM Notification_List")
    for row in cursor.fetchall():
        # Only migrate records with valid Request_date
        if row[2] is not None:
            cursor.execute("""
                INSERT INTO Notification_List_new (
                    Request_date, Request_time, Unit, Location, Agency, Nature, Notification_date, Notification_time, USER_ID
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
    conn.commit()
    # Drop old table and rename new one
    cursor.execute("DROP TABLE Notification_List")
    cursor.execute("ALTER TABLE Notification_List_new RENAME TO Notification_List")
    conn.commit()
    conn.close()
    print("Notification_List table migrated and fixed.")

if __name__ == "__main__":
    migrate_notification_list('litesearch.db')
