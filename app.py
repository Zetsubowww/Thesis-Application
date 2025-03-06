import cv2
import numpy as np
import face_recognition
import os
import mysql.connector
from datetime import datetime

# === CONFIG ===
IP_CAMERA_URL = "rtsp://username:password@your_camera_ip/stream"  # Replace with actual CCTV feed
IMAGE_PATH = "faces"  # Folder containing face images

# === CONNECT TO MYSQL ===
DB_CONFIG = {
    "host": "localhost",
    "user": "attendance_user",
    "password": "your_password",
    "database": "attendance_system"
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

# === CREATE TABLE IF NOT EXISTS ===
def create_table():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            status ENUM('In', 'Out'),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    cursor.close()
    db.close()

create_table()

# === LOAD KNOWN FACES ===
def load_faces():
    known_encodings, known_names = [], []
    for file in os.listdir(IMAGE_PATH):
        if file.endswith((".jpg", ".png", ".jpeg")):
            img = face_recognition.load_image_file(os.path.join(IMAGE_PATH, file))
            encoding = face_recognition.face_encodings(img)
            if encoding:
                known_encodings.append(encoding[0])
                name = file.split(".")[0]  # Extract name from filename
                known_names.append(name)
    return known_encodings, known_names

known_encodings, known_names = load_faces()

# === MARK ATTENDANCE ===
def mark_attendance(name):
    db = connect_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT status FROM attendance WHERE name = %s ORDER BY timestamp DESC LIMIT 1", (name,))
    last_status = cursor.fetchone()
    
    new_status = "In" if not last_status or last_status[0] == "Out" else "Out"
    
    cursor.execute("INSERT INTO attendance (name, status) VALUES (%s, %s)", (name, new_status))
    db.commit()
    
    cursor.close()
    db.close()

# === PROCESS CCTV FEED ===
cap = cv2.VideoCapture(IP_CAMERA_URL)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)

    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    for encoding, face_loc in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_encodings, encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]
                mark_attendance(name)

cap.release()
cv2.destroyAllWindows()
