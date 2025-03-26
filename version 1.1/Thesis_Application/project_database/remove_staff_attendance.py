import sqlite3

db_path = "project_database/attendance.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Delete the attendance record for today
cursor.execute("""
    DELETE FROM attendance 
    WHERE staff_id = (SELECT id FROM staff WHERE name = ?) 
    AND DATE(timestamp) = DATE('now')
""", ("Gianne Ola",))

cursor.execute("""
    DELETE FROM attendance 
    WHERE staff_id = (SELECT id FROM staff WHERE name = ?) 
    AND DATE(timestamp) = DATE('now')
""", ("Samantha Baguio",))

conn.commit()
conn.close()

print("Removed attendance records for today")
