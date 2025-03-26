import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from face_detect_app import FaceDetectionWindow

class UserLoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        try:
            self.state("zoomed")
        except Exception:
            pass
        self.resizable(True, True)
        
        self.label_title = ctk.CTkLabel(self, text="Staff Login", font=("Arial", 24))
        self.label_title.pack(pady=20)

        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(pady=10, padx=40, fill="both", expand=True)
        self.frame_form.grid_rowconfigure((0,1,2), weight=1)
        self.frame_form.grid_columnconfigure(0, weight=1)
        self.frame_form.grid_columnconfigure(1, weight=1)

        self.label_name = ctk.CTkLabel(self.frame_form, text="Name")
        self.label_name.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_name = ctk.CTkEntry(self.frame_form)
        self.entry_name.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.label_id = ctk.CTkLabel(self.frame_form, text="ID Number")
        self.label_id.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_id = ctk.CTkEntry(self.frame_form, show="*")
        self.entry_id.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.button_login = ctk.CTkButton(self.frame_form, text="Login", command=self.verify_login)
        self.button_login.grid(row=2, columnspan=2, pady=20)

        self.frame_form.place(relx=0.5, rely=0.5, anchor="center")

    def verify_login(self):
        user_name = self.entry_name.get()
        user_id = self.entry_id.get()

        conn = sqlite3.connect("C:/Codes/AppCase/Thesis Application/project_database/attendance.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM staff WHERE id = ? AND name = ?", (user_id, user_name))
        result = cursor.fetchone()

        if result:
            messagebox.showinfo("Login Successful", "Initializing face detection for verification...")
            self.open_face_detection()
        else:
            messagebox.showerror("Login Failed", "Incorrect ID or Name. Please try again")
        
        conn.close()

    def open_face_detection(self):
        self.withdraw()
        face_window = FaceDetectionWindow(self)
        face_window.grab_set()
