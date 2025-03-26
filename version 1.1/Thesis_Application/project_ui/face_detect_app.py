import cv2
import dlib
import numpy as np
import sqlite3
from scipy.spatial import distance
from ultralytics import YOLO
from PIL import Image, ImageTk
import customtkinter as ctk

# Load YOLO model
model = YOLO("trained_models/ojt_model_6.pt")

# Load dlib face detector & landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("trained_models/shape_predictor_68_face_landmarks.dat")

# Eye aspect ratio calculation
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# Indices for left & right eyes
LEFT_EYE = list(range(42, 48))
RIGHT_EYE = list(range(36, 42))

class FaceDetectionWindow(ctk.CTkToplevel):
    def __init__(self, login_window=None):
        super().__init__()
        self.login_window = login_window
        self.geometry("800x600")
        self.title("Face Detection")
        self.resizable(True, True)

        self.start_button = ctk.CTkButton(self, text="Start Capture", command=self.start_capture)
        self.start_button.pack(padx=10, pady=10)

        self.stop_button = ctk.CTkButton(self, text="Stop Capture", command=self.stop_capture)
        self.stop_button.pack(padx=10, pady=10)

        self.back_button = ctk.CTkButton(self, text="Back to Login", command=self.back_to_login)
        self.back_button.pack(padx=10, pady=10)

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(pady=20)

        self.cap = None
        self.running = False
        self.blink_count = 0
        self.frame_counter = 0

    def start_capture(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.process_video()

    def stop_capture(self):
        self.running = False
        if self.cap:
            self.cap.release()
            
        self.video_label.configure(image="")

    def process_video(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            results = model(frame)
            detected_persons = []

            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = getattr(box, "conf", getattr(box, "confidence", None))
                    if conf > 0.3:
                        conf = conf[0].item()

                    cls = int(box.cls[0].item())
                    person_name = model.names[cls]
                    detected_persons.append(person_name)

                    blink_detected = False
                    for face in faces:
                        shape = predictor(gray, face)
                        shape = np.array([[shape.part(i).x, shape.part(i).y] for i in range(68)])

                        left_eye = shape[LEFT_EYE]
                        right_eye = shape[RIGHT_EYE]

                        left_ear = eye_aspect_ratio(left_eye)
                        right_ear = eye_aspect_ratio(right_eye)
                        ear = (left_ear + right_ear) / 2.0

                        # Blink detection threshold
                        if ear < 0.25:
                            self.frame_counter += 1
                        else:
                            if self.frame_counter >= 2:  # If eyes were closed for 3+ frames, count as a blink
                                self.blink_count += 1
                            self.frame_counter = 0  # Reset counter
                        
                        if self.blink_count > 0:
                            blink_detected = True
                    
                    if not blink_detected:
                        self.blink_count = 0

                    # If blink count > 0, mark as real (green); else fake (red)
                    color = (0, 255, 0) if self.blink_count > 0 else (0, 0, 255)

                    # Draw bounding box and label
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, person_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if not detected_persons:
                self.blink_count = 0
            else:
                for person_name in detected_persons:
                    if self.blink_count > 0:
                        self.mark_attendance(person_name)
                
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)
            self.video_label.img_tk = img_tk
            self.video_label.configure(image=img_tk)

        self.after(10, self.process_video)

    def mark_attendance(self, person_name):
        db_path = "project_database/attendance.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM staff WHERE name=?", (person_name,))
        result = cursor.fetchone()

        if result:
            staff_id = result[0]
            cursor.execute("""
                SELECT COUNT(*) FROM attendance
                WHERE staff_id=? AND DATE(timestamp) = DATE ('now')
            """, (staff_id,))
            already_marked  = cursor.fetchone()[0]

            if already_marked == 0:
                cursor.execute("""
                    INSERT INTO attendance (staff_id, name, status)
                    VALUES (?, ?, 'Present')
                """, (staff_id, person_name))
                print(f"Marked {person_name} as Present.")
        
        conn.commit()
        conn.close()

    def back_to_login(self):
        self.destroy()
        if self.login_window:
            self.login_window.deiconify()
