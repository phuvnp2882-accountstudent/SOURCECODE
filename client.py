import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 9999
QUESTION_TIME_LIMIT = 30  

class QuizClient:
    def __init__(self, master):
        self.master = master
        self.master.title("🎮 Trắc Nghiệm Online")
        self.master.geometry("600x600")
        self.master.resizable(False, False)

        # Thêm biến cho điểm số và thời gian
        self.current_score = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.timer_running = False
        self.time_remaining = QUESTION_TIME_LIMIT
        self.player_name = "Khách"
        self.score_history_file = "score_history.json"

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối đến server: {e}")
            self.master.destroy()
            return

        # ---- Gửi tên người chơi và tín hiệu bắt đầu ----
        try:
            welcome = self.client_socket.recv(1024).decode()
            
            # Nếu server yêu cầu tên
            if "nhập tên" in welcome.lower():
                name = simpledialog.askstring("Nhập tên", "Nhập tên người chơi của bạn:")
                if not name:
                    name = "Khách" # Mặc định nếu người dùng không nhập hoặc đóng
                self.player_name = name  # Lưu tên người chơi
                self.client_socket.sendall(name.encode())

                # Nhận yêu cầu bắt đầu game (nhấn 0)
                start_msg = self.client_socket.recv(1024).decode()
                if "bắt đầu" in start_msg.lower():
                    self.client_socket.sendall(b"0")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khởi tạo hoặc gửi tên/bắt đầu game: {e}")
            self.master.destroy()
            return

        # ---- Cấu hình giao diện ----
        self.frame_main = ttk.Frame(master, padding=20)
        self.frame_main.pack(fill="both", expand=True)

        self.title_label = ttk.Label(self.frame_main, text="🧠 Trắc Nghiệm Online", font=("Helvetica", 20, "bold"))
        self.title_label.pack(pady=10)

        self.question_label = ttk.Label(self.frame_main, text="Đang tải câu hỏi...", wraplength=550, font=("Helvetica", 14))
        self.question_label.pack(pady=10)

        self.answer_var = tk.StringVar()
        self.answer_container = ttk.Frame(self.frame_main)
        self.answer_container.pack(pady=10)

        self.option_buttons = []
        for i in range(4):
            btn = ttk.Button(self.answer_container, text=f"Đáp án {i+1}", bootstyle="danger-solid", width=25)
            btn.pack(fill="x", padx=10, pady=5)
            self.option_buttons.append(btn)
            btn.bind("<Button-1>", self.select_answer)

        self.drop_area = ttk.Label(self.frame_main, text="⬇️ Kéo đáp án vào đây", font=("Helvetica", 14), bootstyle="warning", width=30, padding=10)
        self.drop_area.pack(pady=20)

        self.submit_btn = ttk.Button(self.frame_main, text="🚀 Gửi Đáp Án", command=self.send_answer, bootstyle="success-solid")