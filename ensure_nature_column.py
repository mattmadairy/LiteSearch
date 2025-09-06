import sqlite3

def ensure_nature_column(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Notification_List)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'Nature' not in columns:
        cursor.execute("ALTER TABLE Notification_List ADD COLUMN Nature TEXT")
        conn.commit()
        print("Nature column added to Notification_List.")
    else:
        print("Nature column already exists.")
    conn.close()

if __name__ == "__main__":
    ensure_nature_column('litesearch.db')
