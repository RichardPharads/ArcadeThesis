import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# For camera
import cv2
from PIL import Image, ImageTk

class ArcadeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recycle Arcade (Raspberry Pi)")
        self.root.geometry("800x480")
        self.root.configure(bg="#1a1a2e")

        # Title
        label = tk.Label(root, text="Welcome to\nRecycle Arcade", font=("Segoe UI", 28, "bold"),
                         fg="#4ecca3", bg="#16213e", pady=20)
        label.pack(pady=10)

        # Game buttons
        btn1 = tk.Button(root, text="🚀 Play Asteroid Game", font=("Segoe UI", 18, "bold"),
                         bg="#0f3460", fg="white", command=self.launch_game1)
        btn1.pack(pady=10, ipadx=10, ipady=10)

        btn2 = tk.Button(root, text="🌲 Play Cycle Forest", font=("Segoe UI", 18, "bold"),
                         bg="#0f3460", fg="white", command=self.launch_game2)
        btn2.pack(pady=10, ipadx=10, ipady=10)

        btn3 = tk.Button(root, text="🚗 Play Traffic Dash", font=("Segoe UI", 18, "bold"),
                         bg="#0f3460", fg="white", command=self.launch_game3)
        btn3.pack(pady=10, ipadx=10, ipady=10)

        # Camera button
        cam_btn = tk.Button(root, text="📷 Open Camera", font=("Segoe UI", 18, "bold"),
                            bg="#4ecca3", fg="#1a1a2e", command=self.open_camera)
        cam_btn.pack(pady=20, ipadx=10, ipady=10)

    def launch_game1(self):
        subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "GameShooter", "asteriodShooter.py")])
        self.root.destroy()

    def launch_game2(self):
        subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "Cycleforest", "main.py")])
        self.root.destroy()

    def launch_game3(self):
        subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "TrafficDash", "main.py")])
        self.root.destroy()

    def open_camera(self):
        cam_window = tk.Toplevel(self.root)
        cam_window.title("Camera")
        cam_window.geometry("640x480")
        lmain = tk.Label(cam_window)
        lmain.pack()

        cap = cv2.VideoCapture(0)

        def show_frame():
            _, frame = cap.read()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            lmain.after(10, show_frame)

        show_frame()

        def on_close():
            cap.release()
            cam_window.destroy()

        cam_window.protocol("WM_DELETE_WINDOW", on_close)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArcadeApp(root)
    root.mainloop()