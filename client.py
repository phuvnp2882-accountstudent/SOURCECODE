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
        self.submit_btn.pack(pady=15)
        
        # Nhãn hiển thị kết quả đúng/sai
        self.response_label = ttk.Label(self.frame_main, text="", font=("Helvetica", 16, "bold"), foreground="blue", wraplength=500) # Tăng font size, làm đậm và đổi màu cho dễ thấy
        self.response_label.pack(pady=10)

        # Thêm frame cho thống kê
        self.stats_frame = ttk.Frame(self.frame_main)
        self.stats_frame.pack(pady=5)
        
        self.score_label = ttk.Label(self.stats_frame, text="Điểm: 0", font=("Helvetica", 14, "bold"), foreground="blue")
        self.score_label.grid(row=0, column=0, padx=10)
        self.correct_label = ttk.Label(self.stats_frame, text="Đúng: 0", font=("Helvetica", 14, "bold"), foreground="green")
        self.correct_label.grid(row=0, column=1, padx=10)
        self.total_label = ttk.Label(self.stats_frame, text="Tổng: 0", font=("Helvetica", 14, "bold"), foreground="gray")
        self.total_label.grid(row=0, column=2, padx=10)
        self.percent_label = ttk.Label(self.stats_frame, text="Tỉ lệ: 0%", font=("Helvetica", 14, "bold"), foreground="purple")
        self.percent_label.grid(row=0, column=3, padx=10)
        
        self.timer_label = ttk.Label(self.frame_main, text=f"⏰ Thời gian: {QUESTION_TIME_LIMIT}s", font=("Helvetica", 16, "bold"), foreground="orange")
        self.timer_label.pack(pady=5)
        
        # Nút xem bảng xếp hạng
        self.rank_btn = ttk.Button(self.frame_main, text="🏆 Xem Bảng Xếp Hạng", command=self.show_score_history, bootstyle="info-outline")
        self.rank_btn.pack(pady=5)

        # ---- Biến trạng thái và Buffer dữ liệu ----
        self.data_buffer = "" # Nơi lưu trữ dữ liệu nhận được từ server
        self.expecting_question = True # True: đang đợi câu hỏi; False: đang đợi kết quả
        self.selected_answer = ""
        # Đăng ký sự kiện tự động chuyển câu hỏi
        self.master.bind("<<ContinueNextQuestion>>", self.auto_advance_question)

        # Khởi động luồng nhận dữ liệu từ server
        self.listen_thread = threading.Thread(target=self.receive_data, daemon=True)
        self.listen_thread.start()

        # Xử lý khi đóng cửa sổ
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def select_answer(self, event):
        """Xử lý khi người dùng chọn một đáp án."""
        self.selected_answer = event.widget.cget("text")
        self.drop_area.config(text=f"✅ {self.selected_answer}")

    def receive_data(self):
        """Luồng riêng biệt để nhận dữ liệu từ server."""
        while True:
            try:
                chunk = self.client_socket.recv(4096).decode()
                if not chunk:
                    break
                self.data_buffer += chunk
                
                # Gọi hàm xử lý buffer trên luồng chính của Tkinter để tránh lỗi luồng
                self.master.after_idle(self._process_data_from_buffer)

            except Exception as e:
                break

        # Xử lý phần còn lại của buffer khi kết nối đóng (nếu có)
        if self.data_buffer:
            self.master.after_idle(self._process_data_from_buffer)

    def _process_data_from_buffer(self):
        """
        Hàm này được gọi liên tục trên luồng chính của Tkinter để phân tích
        và xử lý dữ liệu trong self.data_buffer.
        """
        
        # Vòng lặp để xử lý nhiều thông điệp trong cùng một buffer (nếu có)
        while True:
            original_buffer_len_in_loop = len(self.data_buffer) # Kích thước buffer trước khi xử lý trong vòng lặp này

            # 1. Ưu tiên tìm kết quả cuối cùng (kết thúc game)
            if "Trò chơi kết thúc!" in self.data_buffer:
                final_start_idx = self.data_buffer.find("Trò chơi kết thúc!")
                final_message = self.data_buffer[final_start_idx:].strip()
                self.master.after(0, self.show_final_result_overlay, final_message)
                self.data_buffer = "" # Xóa buffer
                return # Thoát khỏi hàm và vòng lặp

            # 2. Xử lý kết quả đáp án (chỉ khi đang đợi kết quả, tức là vừa gửi đáp án)
            if not self.expecting_question:
                if "Đáp án đúng!" in self.data_buffer:
                    idx = self.data_buffer.find("Đáp án đúng!")
                    # Tìm điểm kết thúc của thông báo (thường là \n\n)
                    end_idx = self.data_buffer.find("\n\n", idx)
                    if end_idx == -1: # Trường hợp thông báo bị cắt
                        end_idx = len(self.data_buffer)
                    
                    message = self.data_buffer[idx:end_idx].strip()
                    self.master.after(0, self.show_answer_result, message)
                    self.master.after(0, self.disable_answer_submission) # Vô hiệu hóa nút gửi
                    self.data_buffer = self.data_buffer[end_idx:].strip() # Cắt bỏ phần đã xử lý
                    self.expecting_question = True # Sau khi hiển thị kết quả, chuyển sang đợi câu hỏi mới
                    self.master.after(2500, self.master.event_generate, "<<ContinueNextQuestion>>") # 2.5 giây sau overlay
                    continue # Quay lại đầu vòng lặp để kiểm tra xem có câu hỏi tiếp theo ngay lập tức trong buffer không

                elif "Đáp án sai!" in self.data_buffer:
                    idx = self.data_buffer.find("Đáp án sai!")
                    end_idx = self.data_buffer.find("\n\n", idx)
                    if end_idx == -1:
                        end_idx = len(self.data_buffer)
                    
                    message = self.data_buffer[idx:end_idx].strip()
                    self.master.after(0, self.show_answer_result, message)
                    self.master.after(0, self.disable_answer_submission) # Vô hiệu hóa nút gửi
                    self.data_buffer = self.data_buffer[end_idx:].strip() # Cắt bỏ phần đã xử lý
                    self.expecting_question = True # Sau khi hiển thị kết quả, chuyển sang đợi câu hỏi mới
                    self.master.after(2500, self.master.event_generate, "<<ContinueNextQuestion>>") # 2.5 giây sau overlay
                    continue # Quay lại đầu vòng lặp