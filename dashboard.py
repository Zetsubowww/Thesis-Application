import tkinter as tk
from tkinter import ttk
import mysql.connector
import ttkbootstrap as tb  # Modern UI styling

# === MySQL Configuration ===
DB_CONFIG = {
    "host": "localhost",
    "user": "attendance_user",
    "password": "your_password",
    "database": "attendance_system"
}

# === Fetch Attendance Data ===
def fetch_attendance():
    """Fetch attendance records from MySQL and update table."""
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor()
    cursor.execute("SELECT name, status, timestamp FROM attendance ORDER BY timestamp DESC")
    records = cursor.fetchall()
    cursor.close()
    db.close()

    # Clear old data
    for row in table.get_children():
        table.delete(row)

    # Insert new data
    for record in records:
        table.insert("", "end", values=record)

    # Refresh every 5 seconds
    root.after(5000, fetch_attendance)

# === UI Setup ===
root = tb.Window(themename="darkly")  # Modern dark UI theme
root.title("Attendance Dashboard")
root.geometry("700x400")  # Starting window size
root.minsize(500, 300)  # Prevent extreme shrinking

# === Styling ===
title_label = tb.Label(root, text="📊 Attendance Dashboard", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

# === Table Frame ===
table_frame = ttk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=5)

# === Scrollable Table ===
columns = ("Name", "Status", "Timestamp")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center")

scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")
table.pack(fill="both", expand=True)

fetch_attendance()
root.mainloop()