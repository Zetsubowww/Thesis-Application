import customtkinter as ctk
import sys, json, os, base64
from tkinter import messagebox
from DatabaseHooking import connect_db, create_tables, verify_user, create_default_users


def load_config():
    config_file = "config.json"
    default = {
        "theme": "Light",
        "db_host": "",
        "db_username": "",
        "db_password": "",
        "camera_type": "Default Webcam",
        "camera_url": "",
        "camera_types": ["Default Webcam", "LAN IP Camera", "WiFi Camera"],
        "camera_simple_mode": False,
        "camera_protocol": "RTSP",
        "camera_user": "",
        "camera_pass": "",
        "camera_ip": "",
        "camera_port": ""
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            if config.get("db_username"):
                config["db_username"] = base64.b64decode(config["db_username"].encode()).decode()
            if config.get("db_password"):
                config["db_password"] = base64.b64decode(config["db_password"].encode()).decode()

            if "camera_types" not in config:
                config["camera_types"] = default["camera_types"]

            for key in default:
                if key not in config:
                    config[key] = default[key]

            return config
        except Exception:
            return default
    else:
        return default

def save_config(theme, db_host, db_username, db_password,
                camera_type, camera_url, camera_types,
                camera_simple_mode=False, camera_protocol="RTSP",
                camera_user="", camera_pass="", camera_ip="", camera_port=""):
    config_file = "config.json"
    try:
        enc_username = base64.b64encode(db_username.encode()).decode() if db_username else ""
        enc_password = base64.b64encode(db_password.encode()).decode() if db_password else ""

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({
                "theme": theme,
                "db_host": db_host,
                "db_username": enc_username,
                "db_password": enc_password,
                "camera_type": camera_type,
                "camera_url": camera_url,
                "camera_types": camera_types,
                "camera_simple_mode": camera_simple_mode,
                "camera_protocol": camera_protocol,
                "camera_user": camera_user,
                "camera_pass": camera_pass,
                "camera_ip": camera_ip,
                "camera_port": camera_port
            }, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Error saving config:", e)

config = load_config()

default_camera_types = {
    "Webcam mặc định": "Default Webcam",
    "Camera IP LAN": "LAN IP Camera",
    "Camera WiFi": "WiFi Camera"
}

# Convert camera types to English if necessary
config["camera_type"] = default_camera_types.get(config["camera_type"], config["camera_type"])
config["camera_types"] = [default_camera_types.get(t, t) for t in config["camera_types"]]


def open_camera_config(self):
    CameraConfigWindow(self, self.camera_types)


def on_camera_type_change(self, value):
    if value == "Default Webcam":
        self.entry_camera_url.delete(0, "end")
        self.entry_camera_url.configure(state="disabled")
    else:
        self.entry_camera_url.configure(state="normal")


def toggle_simple_mode(self):
    self.simple_mode = not self.simple_mode
    if self.simple_mode:
        self.show_simple_mode()
    else:
        self.hide_simple_mode()


def show_simple_mode(self):
    self.frame_simple.grid()


def hide_simple_mode(self):
    self.frame_simple.grid_remove()


def generate_camera_url(self):
    protocol = self.optionmenu_protocol.get().strip()
    user = self.entry_camera_user.get().strip()
    pwd = self.entry_camera_pass.get().strip()
    ip = self.entry_camera_ip.get().strip()
    port = self.entry_camera_port.get().strip()

    link = ""
    if protocol == "RTSP":
        link = f"rtsp://{user}:{pwd}@{ip}:{port}/stream"
    elif protocol == "HTTP":
        link = f"http://{user}:{pwd}@{ip}:{port}/"
    elif protocol == "HTTPS":
        link = f"https://{user}:{pwd}@{ip}:{port}/"
    elif protocol == "ONVIF":
        link = f"http://{user}:{pwd}@{ip}:{port}/onvif"
    elif protocol == "RTP":
        link = f"rtp://{ip}:{port}"
    elif protocol == "HLS":
        link = f"http://{ip}:{port}/hls/stream.m3u8"
    elif protocol == "WebRTC":
        link = "webrtc://..."

    self.entry_camera_url.configure(state="normal")
    self.entry_camera_url.delete(0, "end")
    self.entry_camera_url.insert(0, link)


def toggle_theme(self):
    if self.current_mode == "Light":
        ctk.set_appearance_mode("Dark")
        self.current_mode = "Dark"
    else:
        ctk.set_appearance_mode("Light")
        self.current_mode = "Light"


def handle_login(self):
    db_host = self.entry_db_host.get().strip()
    db_username = self.entry_db_username.get().strip()
    db_password = self.entry_db_password.get().strip()

    if not db_username or not db_password:
        messagebox.showerror("Error", "❌ Please enter database username and password.")
        return

    cnx, cursor = connect_db(db_username, db_password, db_host)
    if cnx is None:
        messagebox.showerror("Database Error",
                             "❌ Database connection failed! Please check your MySQL credentials or run the setup operation.")
        return

    create_tables(cursor)
    create_default_users(cursor, cnx)

    camera_type = self.combo_camera_type.get().strip()
    camera_url = self.entry_camera_url.get().strip()

    self.selected_protocol = self.optionmenu_protocol.get().strip()
    self.camera_user = self.entry_camera_user.get().strip()
    self.camera_pass = self.entry_camera_pass.get().strip()
    self.camera_ip = self.entry_camera_ip.get().strip()
    self.camera_port = self.entry_camera_port.get().strip()

    if self.checkbox_remember.get():
        save_config(self.current_mode, db_host, db_username, db_password, camera_type, camera_url, self.camera_types,
                    camera_simple_mode=self.simple_mode, camera_protocol=self.selected_protocol,
                    camera_user=self.camera_user, camera_pass=self.camera_pass, camera_ip=self.camera_ip,
                    camera_port=self.camera_port)
    else:
        save_config(self.current_mode, "", "", "", camera_type, camera_url, self.camera_types,
                    camera_simple_mode=self.simple_mode, camera_protocol=self.selected_protocol,
                    camera_user=self.camera_user, camera_pass=self.camera_pass, camera_ip=self.camera_ip,
                    camera_port=self.camera_port)

    self.destroy()
    from control_panel import open_user_login_window
    open_user_login_window(cnx, cursor)


def exit_app(self):
    save_config(self.current_mode, self.entry_db_host.get().strip(), self.entry_db_username.get().strip(),
                self.entry_db_password.get().strip(), self.combo_camera_type.get().strip(),
                self.entry_camera_url.get().strip(), self.camera_types, camera_simple_mode=self.simple_mode,
                camera_protocol=self.optionmenu_protocol.get().strip(),
                camera_user=self.entry_camera_user.get().strip(), camera_pass=self.entry_camera_pass.get().strip(),
                camera_ip=self.entry_camera_ip.get().strip(), camera_port=self.entry_camera_port.get().strip())
    self.destroy()
    sys.exit(0)


class UserLoginWindow(ctk.CTk):
    def __init__(self, cnx, cursor):
        super().__init__()
        self.cnx = cnx
        self.cursor = cursor
        self.current_mode = "Light"
        self.geometry("1200x800")
        try:
            self.state("zoomed")
        except Exception:
            pass
        self.resizable(True, True)
        self.create_widgets()

    def create_widgets(self):
        self.label_title = ctk.CTkLabel(self, text="User Login", font=("Arial", 24))
        self.label_title.pack(pady=20)

        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(pady=10, padx=40, fill="both", expand=True)

        self.label_username = ctk.CTkLabel(self.frame_form, text="Username")
        self.label_username.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_username = ctk.CTkEntry(self.frame_form)
        self.entry_username.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.label_password = ctk.CTkLabel(self.frame_form, text="Password")
        self.label_password.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_password = ctk.CTkEntry(self.frame_form, show="*")
        self.entry_password.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    def handle_user_login(self):
        user_username = self.entry_username.get().strip()
        user_password = self.entry_password.get().strip()
        if not user_username or not user_password:
            messagebox.showerror("Error", "❌ Please enter username and password.")
            return

        user_info = verify_user(self.cursor, user_username, user_password)
        if user_info is None:
            messagebox.showerror("Login Failed", "❌ Invalid username or password!")
            return

        self.destroy()
        from control_panel import open_control_panel
        open_control_panel(user_info, self.cnx, self.cursor)


def main():
    app = MySQLLoginWindow()
    try:
        app.state("zoomed")
    except Exception:
        pass
    app.mainloop()


if __name__ == "__main__":
    main()

