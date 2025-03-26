import sqlite3

# Define database path
db_path = "C:/Users/giann/Documents/AttendanceApp/database/attendance.db"  # Update with your actual path

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert two persons into the staff table
cursor.execute("INSERT INTO staff (id, name) VALUES (?, ?)", (1, "Gianne Ola"))
cursor.execute("INSERT INTO staff (id, name) VALUES (?, ?)", (2, "Samantha Baguio"))

# Save (commit) the changes
conn.commit()
print("Records added successfully!")

# Close the connection
conn.close()
