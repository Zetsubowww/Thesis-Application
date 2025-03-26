import sqlite3

db_path = "project_database/attendance.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               staff_id TEXT NOT NULL,
               name TEXT NOT NULL,
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
               status TEXT DEFAULT 'Present',
               FOREIGN KEY (staff_id) REFERENCES staff(id)
)
""")

conn.commit()
conn.close()

print("Done")
