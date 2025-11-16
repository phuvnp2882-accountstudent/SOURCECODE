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