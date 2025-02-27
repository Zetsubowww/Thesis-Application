import tkinter as tk
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
    
root = tk.Tk()

root.title("Dashboard")

root.geometry("900x600")
root.minsize(900,600)
root.maxsize(900,600)

video_frame = tk.Frame(root, width=860, height=450, bg="black")
video_frame.pack(pady=20, fill="both", expand=True)

video_label = tk.Label(video_frame)
video_label.pack(fill="both", expand=True)

cap = cv2.VideoCapture(0)

def start_feed():
    update_feed()

def update_feed():
    global cap
    if cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            
           results = model.predict(frame, show=False)  
           frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
           
           for result in results:
               for box in result.boxes:
                   x1,y1,x2,y2 = map(int, box.xyxy[0])
                   conf = box.conf[0].item()
                   cls = int(box.cls[0].item())
                   
                   cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                   
                   label = f"{model.names[cls]} {conf:.2f}"
                   cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2) 
           
           img = Image.fromarray(frame)
           img_tk = ImageTk.PhotoImage(image=img)
           
           video_label.config(image=img_tk)
           video_label.image = img_tk
        
        root.after(10, update_feed)
        
btn = tk.Button(root, text="Capture Video", command=start_feed)
btn.pack(pady=10)

root.mainloop()