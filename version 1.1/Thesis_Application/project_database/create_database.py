import sqlite3
import os

db_folder = "C:/Codes/AppCase/Thesis Application/project_database"

os.makedirs(db_folder, exist_ok=True)

db_path = os.path.join(db_folder, "attendance.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database and table created")
