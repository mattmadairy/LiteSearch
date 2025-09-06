import sqlite3

def fix_misaligned_records(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Notification_List")
    rows = cursor.fetchall()
    for row in rows:
        nature = row[7]
        # If Nature is a date, shift fields right and set Nature to empty string
        if nature and nature.count('-') == 2 and len(nature) == 10:
            # Save original values
            notification_date = nature
            notification_time = row[8]
            user_id = row[9]
            # Update record
            cursor.execute("UPDATE Notification_List SET Nature=?, Notification_date=?, Notification_time=?, USER_ID=? WHERE ID=?", ('', notification_date, notification_time, user_id, row[0]))
            print(f"Fixed record ID {row[0]}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_misaligned_records('litesearch.db')
    print("Database records checked and fixed if needed.")
