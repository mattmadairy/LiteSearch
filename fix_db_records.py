import sqlite3

def fix_misaligned_records(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Notification_List")
    rows = cursor.fetchall()
    for row in rows:
        # If Nature is a date, shift fields back
        nature = row[7]
        if nature and nature.count('-') == 2 and len(nature) == 10:
            # Move Nature to empty string, Notification_Date to nature, Notification_Time to notification_date, USER_ID to notification_time
            cursor.execute("UPDATE Notification_List SET Nature=?, Notification_date=?, Notification_time=?, USER_ID=? WHERE ID=?", ('', nature, row[8], row[9], row[0]))
            print(f"Fixed record ID {row[0]}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_misaligned_records('litesearch.db')
    print("Database records checked and fixed if needed.")
