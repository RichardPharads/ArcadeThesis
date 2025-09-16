import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# Removed camera imports - using ultrasonic sensor instead

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

        # Ultrasonic sensor button
        sensor_btn = tk.Button(root, text="🔊 Start Ultrasonic Detection", font=("Segoe UI", 18, "bold"),
                              bg="#4ecca3", fg="#1a1a2e", command=self.start_ultrasonic_detection)
        sensor_btn.pack(pady=20, ipadx=10, ipady=10)

    def launch_game1(self):
        subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "GameShooter", "asteriodShooter.py")])
        self.root.destroy()

    def launch_game2(self):
        subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "Cycleforest", "main.py")])
        self.root.destroy()

    def launch_game3(self):
        subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "TrafficDash", "main.py")])
        self.root.destroy()

    def start_ultrasonic_detection(self):
        """Start the ultrasonic sensor detection system"""
        try:
            subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "ultrasonic_detector.py")])
            messagebox.showinfo("Ultrasonic Detection", "Ultrasonic sensor detection started!\nPlace an object within 30cm to trigger games.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start ultrasonic detection: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArcadeApp(root)
    root.mainloop()