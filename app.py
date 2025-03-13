# === IMPORTS ===
import cv2
import numpy as np
import face_recognition
import os
import mysql.connector
from datetime import datetime

IMAGE_PATH = "faces"  # Folder containing known faces

IP_CAMERA_URL = "rtsp://admin:appcase020525@192.168.254.64/stream"

# === DATABASE CONNECTION ===
DB_CONFIG = {
    "host": "localhost",
    "user": "admin",
    "password": "root",
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
            img_path = os.path.join(IMAGE_PATH, file)
            img = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                known_encodings.append(encodings[0])
                name = file.rsplit("_", 1)[0].replace("_", " ") if "_" in file else file.split(".")[0]
                known_names.append(name)
    return known_encodings, known_names

known_encodings, known_names = load_faces()
print(f"Loaded {len(known_names)} known faces:", known_names)

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
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
cap.set(cv2.CAP_PROP_FPS, 30)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Convert to RGB & Resize
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)

    # Detect Faces
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    for encoding, face_loc in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, encoding)
        face_distances = face_recognition.face_distance(known_encodings, encoding)
        name = "Unknown"

        if known_encodings:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]
                mark_attendance(name)

        # Scale face location back to full frame size
        top, right, bottom, left = [v * 2 for v in face_loc]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the output
    cv2.imshow("CCTV Feed", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()