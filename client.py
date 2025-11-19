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

class ModernQuizClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Game Đố Mẹo Trắc Nghiệm")
        
        # Lấy kích thước màn hình và thiết lập kích thước cửa sổ vừa màn hình
        self.setup_window_size()
        
        # Biến trạng thái
        self.current_score = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.timer_running = False
        self.time_remaining = QUESTION_TIME_LIMIT
        self.player_name = "Khách"
        self.score_history_file = "score_history.json"
        self.selected_answer = ""
        self.data_buffer = ""
        self.expecting_question = True
        self.timer_after_id = None


        # Kết nối server
        self.setup_connection()
        if not hasattr(self, 'client_socket'):
            return

        # Tạo giao diện
        self.create_welcome_screen()

    def setup_window_size(self):
        """Thiết lập kích thước cửa sổ vừa với màn hình laptop"""
        # Lấy kích thước màn hình
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        # Tính toán kích thước phù hợp (80-90% màn hình)
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        
        # Vị trí để căn giữa
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Thiết lập kích thước và vị trí
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.master.resizable(True, True)
        
        # Lưu kích thước để sử dụng sau này
        self.window_width = window_width
        self.window_height = window_height

    def setup_connection(self):
        """Thiết lập kết nối với server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            
            # Xử lý đăng nhập
            welcome = self.client_socket.recv(1024).decode()
            if "nhập tên" in welcome.lower():
                name = self.show_login_dialog()
                if not name:
                    self.master.destroy()
                    return
                self.player_name = name
                self.client_socket.sendall(name.encode())
                
                start_msg = self.client_socket.recv(1024).decode()
                if "bắt đầu" in start_msg.lower():
                    self.client_socket.sendall(b"0")
                    
            # Bắt đầu luồng nhận dữ liệu
            self.listen_thread = threading.Thread(target=self.receive_data, daemon=True)
            self.listen_thread.start()
            
        except Exception as e:
            messagebox.showerror("Lỗi Kết Nối", 
                               f"Không thể kết nối đến server:\n{e}\n\n"
                               f"Vui lòng kiểm tra:\n• Server đã chạy chưa?\n• Địa chỉ {HOST}:{PORT}")
            self.master.destroy()

    def show_login_dialog(self):
        """Hiển thị dialog đăng nhập đẹp hơn"""
        dialog = ttk.Toplevel(self.master)
        dialog.title("Đăng Nhập")
        
        # Tính toán kích thước dialog dựa trên cửa sổ chính
        dialog_width = 400
        dialog_height = 250
        x = self.master.winfo_x() + (self.window_width - dialog_width) // 2
        y = self.master.winfo_y() + (self.window_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=30)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Nhập Tên Của Bạn", 
                 font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=(0, 20))
        
        name_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=name_var, font=("Helvetica", 14), 
                         width=25, justify="center")
        entry.pack(pady=10)
        entry.focus()
        
        def on_submit():
            name = name_var.get().strip()
            if name:
                dialog.result = name
                dialog.destroy()
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập tên!")
        
        def on_cancel():
            dialog.result = None
            dialog.destroy()
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="BẮT ĐẦU", command=on_submit, 
                  bootstyle="success-solid", width=12).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="THOÁT", command=on_cancel,
                  bootstyle="danger-solid", width=12).pack(side="left", padx=5)
        
        entry.bind('<Return>', lambda e: on_submit())
        
        self.master.wait_window(dialog)
        return getattr(dialog, 'result', None)

    def create_welcome_screen(self):
        """Tạo màn hình chào mừng"""
        self.clear_screen()
        
        # Tạo main container với padding
        main_container = ttk.Frame(self.master, padding=10)
        main_container.pack(fill="both", expand=True)
        
        # Header với gradient effect
        header_frame = ttk.Frame(main_container, bootstyle="dark")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="GAME ĐỐ MẸO TRẮC NGHIỆM", 
                 font=("Helvetica", 24, "bold"), bootstyle="inverse-dark").pack(pady=5)
        
        # Main content - sử dụng grid để responsive
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill="both", expand=True)
        
        # Cấu hình grid weights
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Top row - Stats
        top_frame = ttk.Frame(content_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        
        # Player info card
        info_card = ttk.Labelframe(top_frame, text="THÔNG TIN CỦA BẠN", bootstyle="primary")
        info_card.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ttk.Label(info_card, text=self.player_name, 
                 font=("Helvetica", 14, "bold"), bootstyle="primary").pack(pady=10)
        
        # Stats frame
        stats_card = ttk.Labelframe(top_frame, text="THỐNG KÊ", bootstyle="primary")
        stats_card.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        stats_grid = ttk.Frame(stats_card)
        stats_grid.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Tạo 2x2 grid cho stats
        for i in range(2):
            stats_grid.columnconfigure(i, weight=1)
        for i in range(2):
            stats_grid.rowconfigure(i, weight=1)
        
        self.score_label = self.create_stat_card(stats_grid, "ĐIỂM SỐ", "0", 0, 0, "primary")
        self.correct_label = self.create_stat_card(stats_grid, "CÂU ĐÚNG", "0", 0, 1, "success")
        self.total_label = self.create_stat_card(stats_grid, "TỔNG CÂU", "0", 1, 0, "warning")
        self.percent_label = self.create_stat_card(stats_grid, "TỈ LỆ", "0%", 1, 1, "danger")
        
        # Middle row - Timer và Question
        middle_frame = ttk.Frame(content_frame)
        middle_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.rowconfigure(1, weight=1)
        
        # Timer với progress bar
        timer_frame = ttk.Frame(middle_frame)
        timer_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.timer_label = ttk.Label(timer_frame, text=f"⏰ THỜI GIAN: {QUESTION_TIME_LIMIT}s", 
                                   font=("Helvetica", 14, "bold"), bootstyle="warning")
        self.timer_label.pack(pady=2)
        
        self.timer_progress = ttk.Progressbar(timer_frame, orient="horizontal", 
                                            mode="determinate", bootstyle="warning-striped")
        self.timer_progress.pack(fill="x", pady=2)
        self.timer_progress["maximum"] = QUESTION_TIME_LIMIT
        self.timer_progress["value"] = QUESTION_TIME_LIMIT
        
        # Question area - chiếm không gian còn lại
        question_card = ttk.Labelframe(middle_frame, text="CÂU HỎI", bootstyle="info-solid")
        question_card.grid(row=1, column=0, sticky="nsew")
        
        # Tạo container cho câu hỏi và đáp án
        question_container = ttk.Frame(question_card)
        question_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Frame cho câu hỏi - CĂN GIỮA
        question_text_frame = ttk.Frame(question_container)
        question_text_frame.pack(fill="x", pady=(5, 15))
        
        self.question_label = ttk.Label(question_text_frame, text="Đang chờ câu hỏi...", 
                                      wraplength=self.window_width - 100, 
                                      font=("Helvetica", 14, "bold"), 
                                      justify="center", bootstyle="default")
        self.question_label.pack(expand=True, pady=20)
        
        # Answer options - LÀM NÚT LỚN HƠN VÀ RÕ RÀNG HƠN
        self.answer_frame = ttk.Frame(question_container)
        self.answer_frame.pack(fill="both", expand=True, pady=20)
        
        # Tạo 2x2 grid cho các lựa chọn với chiều cao cố định
        for i in range(2):
            self.answer_frame.columnconfigure(i, weight=1)
        for i in range(2):
            self.answer_frame.rowconfigure(i, weight=1, minsize=80)  # Chiều cao tối thiểu 80px
        
        self.option_buttons = []

        option_styles = ["primary-solid", "danger-solid", "success-solid", "warning-solid"]

        # Tạo 4 nút đáp án LỚN HƠN với font lớn hơn
        for i in range(4):
            row = i // 2
            col = i % 2
            btn = ttk.Button(self.answer_frame, 
                           text=f"{chr(65+i)}. Đang tải...", 
                           command=lambda idx=i: self.select_answer(idx),
                           bootstyle=option_styles[i],
                           state="normal",
                           width=30,  # Độ rộng cố định
                           padding=(10, 15))  # Padding lớn hơn
            btn.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
            self.option_buttons.append(btn)
        
        # Bottom row - Submit và controls
        bottom_frame = ttk.Frame(content_frame)
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # Submit area
        submit_frame = ttk.Frame(bottom_frame)
        submit_frame.pack(fill="x", pady=10)
        
        self.selected_display = ttk.Label(submit_frame, text="CHỌN ĐÁP ÁN CỦA BẠN", 
                                        font=("Helvetica", 12), bootstyle="warning")
        self.selected_display.pack(pady=5)
        
        self.submit_btn = ttk.Button(submit_frame, text="XÁC NHẬN", 
                                   command=self.send_answer, bootstyle="success-solid",
                                   state="disabled",
                                   padding=(20, 10))  # Nút submit lớn hơn
        self.submit_btn.pack(pady=10)
        
        # Footer controls
        footer_frame = ttk.Frame(bottom_frame)
        footer_frame.pack(fill="x", pady=10)
        
        ttk.Button(footer_frame, text="BẢNG XẾP HẠNG", 
                  command=self.show_score_history, bootstyle="info-outline").pack(side="left", padx=5)
        
        ttk.Button(footer_frame, text="LÀM MỚI", 
                  command=self.restart_game, bootstyle="warning-outline").pack(side="left", padx=5)
        
        ttk.Button(footer_frame, text="THOÁT", 
                  command=self.on_close, bootstyle="danger-outline").pack(side="right", padx=5)
        
        # Bind events
        self.master.bind("<<ContinueNextQuestion>>", self.auto_advance_question)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Cập nhật layout sau khi tạo xong
        self.master.update_idletasks()

    def create_stat_card(self, parent, title, value, row, col, style):
        """Tạo card thống kê đẹp"""
        card = ttk.Frame(parent, relief="solid", borderwidth=1, padding=5)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        ttk.Label(card, text=title, font=("Helvetica", 10, "bold"), 
                  foreground="white").pack()
        
        label = ttk.Label(card, text=value, font=("Helvetica", 18, "bold"), 
                         bootstyle=style)
        label.pack(pady=5)
        
        return label

    def clear_screen(self):
        """Xóa toàn bộ widget trên màn hình"""
        for widget in self.master.winfo_children():
            widget.destroy()

    def select_answer(self, index):
        """Chọn đáp án"""
        if self.option_buttons[index]['state'] == 'disabled':
            return
        
        solid_styles = ["primary-solid", "danger-solid", "success-solid", "warning-solid"]

        # Reset style cho tất cả các nút
        for i, btn in enumerate(self.option_buttons):
            if i != index:
                btn.configure(bootstyle=solid_styles[i])
        
        # Highlight nút được chọn
        self.option_buttons[index].configure(bootstyle="info-solid")
        self.selected_answer = self.option_buttons[index].cget('text')
        
        # Hiển thị đáp án đã chọn
        answer_text = self.selected_answer
        if '. ' in self.selected_answer:
            answer_text = self.selected_answer.split('. ', 1)[1]
        self.selected_display.config(text=f"ĐÃ CHỌN: {answer_text}")
        self.submit_btn.configure(state="normal")

    def receive_data(self):
        """Nhận dữ liệu từ server"""
        while True:
            try:
                chunk = self.client_socket.recv(4096).decode()
                if not chunk:
                    break
                self.data_buffer += chunk
                self.master.after_idle(self._process_data_from_buffer)
            except:
                break

    def _process_data_from_buffer(self):
        """Xử lý dữ liệu nhận được"""
        while True:
            original_len = len(self.data_buffer)
            
            # Xử lý kết quả cuối cùng
            if "Trò chơi kết thúc!" in self.data_buffer:
                final_start = self.data_buffer.find("Trò chơi kết thúc!")
                final_msg = self.data_buffer[final_start:].strip()
                self.master.after(0, self.show_final_result, final_msg)
                self.data_buffer = ""
                return
            
            # Xử lý kết quả đáp án
            if not self.expecting_question:
                if "Đáp án đúng!" in self.data_buffer:
                    self.handle_answer_result("Đáp án đúng!")
                    continue
                elif "Đáp án sai!" in self.data_buffer:
                    self.handle_answer_result("Đáp án sai!")
                    continue
            
            # Xử lý câu hỏi mới
            if self.expecting_question and "Câu" in self.data_buffer:
                # Tìm vị trí bắt đầu và kết thúc của câu hỏi
                start_idx = self.data_buffer.find("Câu")
                end_markers = ["Nhập đáp án", "Trò chơi kết thúc!", "Đáp án đúng!", "Đáp án sai!"]
                end_idx = -1
                
                for marker in end_markers:
                    temp_idx = self.data_buffer.find(marker, start_idx)
                    if temp_idx != -1 and (end_idx == -1 or temp_idx < end_idx):
                        end_idx = temp_idx
                
                if end_idx == -1:
                    end_idx = len(self.data_buffer)
                
                question_block = self.data_buffer[start_idx:end_idx].strip()
                if question_block and any(marker in question_block for marker in ["A.", "B.", "C.", "D."]):
                    self.master.after(0, self.display_question, question_block)
                    self.data_buffer = self.data_buffer[end_idx:].strip()
                    self.expecting_question = False
                    continue
                
            if len(self.data_buffer) == original_len:
                break

    def handle_answer_result(self, result_type):
        """Xử lý kết quả đáp án"""
        idx = self.data_buffer.find(result_type)
        end_idx = self.data_buffer.find("\n\n", idx)
        if end_idx == -1:
            end_idx = len(self.data_buffer)
            
        message = self.data_buffer[idx:end_idx].strip()
        is_correct = "sai" not in message.lower()
        
        self.master.after(0, self.show_answer_feedback, message, is_correct)
        self.data_buffer = self.data_buffer[end_idx:].strip()
        self.expecting_question = True
        # Tự động chuyển câu sau 2.5 giây
        self.master.after(2500, self.master.event_generate, "<<ContinueNextQuestion>>")

    def display_question(self, data):
        """Hiển thị câu hỏi và đáp án"""
        print("Raw data received:", repr(data))  # Debug
        
        lines = data.strip().split("\n")
        question_lines = []
        options = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(("A.", "B.", "C.", "D.")):
                options.append(line)
            elif line and not line.startswith("Câu"):
                question_lines.append(line)
        
        print("Question lines:", question_lines)  # Debug
        print("Options:", options)  # Debug
        
        # Hiển thị câu hỏi
        question_text = "\n".join(question_lines)
        self.question_label.config(text=question_text)
        
        solid_styles = ["primary-solid", "danger-solid", "success-solid", "warning-solid"]

        # Hiển thị đáp án - ĐẢM BẢO HIỂN THỊ ĐẦY ĐỦ
        for i, btn in enumerate(self.option_buttons):
            btn.config(bootstyle=solid_styles[i])
            if i < len(options):
                btn_text = options[i]
                # Đảm bảo text hiển thị đầy đủ
                btn.config(text=btn_text, state="normal")
            else:
                btn.config(text=f"{chr(65+i)}. Không có đáp án", state="disabled")
        
        self.selected_answer = ""
        self.selected_display.config(text="CHỌN ĐÁP ÁN CỦA BẠN")
        self.submit_btn.configure(state="disabled")
        self.start_timer()

    def show_answer_feedback(self, message, is_correct):
        """Hiển thị phản hồi đáp án"""
        self.timer_running = False
        self.update_score(is_correct)
        
        if is_correct:
            self.show_overlay("ĐÁP ÁN CHÍNH XÁC!", "#28a745")
        else:
            correct_ans = ""
            if "Đáp án đúng là:" in message:
                correct_ans = message.split("Đáp án đúng là:")[-1].strip()
            self.show_overlay("ĐÁP ÁN SAI RỒI!", "#dc3545", correct_ans)

    def send_answer(self):
        """Gửi đáp án đến server"""
        if not self.selected_answer:
            return
            
        try:
            answer_letter = self.selected_answer[0].upper()
            self.client_socket.sendall(f"{answer_letter}\n".encode())
            self.expecting_question = False
            self.disable_answer_input()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Gửi đáp án thất bại: {e}")

    def disable_answer_input(self):
        """Vô hiệu hóa input đáp án"""
        self.submit_btn.configure(state="disabled")
        for btn in self.option_buttons:
            btn.configure(state="normal")

    def enable_answer_input(self):
        """Kích hoạt input đáp án"""
        for btn in self.option_buttons:
            btn.configure(state="normal")

    def start_timer(self):
        if self.timer_after_id is not None:
            self.master.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        """Bắt đầu đếm ngược"""
        self.time_remaining = QUESTION_TIME_LIMIT
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        """Cập nhật timer"""
        if self.timer_running and self.time_remaining > 0:
            # Cập nhật progress bar
            self.timer_progress["value"] = self.time_remaining
            
            # Đổi màu khi sắp hết giờ
            if self.time_remaining <= 5:
                self.timer_label.configure(bootstyle="danger-solid")
                self.timer_progress.configure(bootstyle="danger-striped")
            elif self.time_remaining <= 10:
                self.timer_label.configure(bootstyle="warning-solid")
                self.timer_progress.configure(bootstyle="warning-striped")
            else:
                self.timer_label.configure(bootstyle="warning-solid")
                self.timer_progress.configure(bootstyle="warning-striped")
                
            self.timer_label.config(text=f"⏰ THỜI GIAN: {self.time_remaining}s")
            self.time_remaining -= 1

            self.timer_after_id = self.master.after(1000, self.update_timer)

        elif self.timer_running:
            self.timer_running = False
            self.time_up()

    def time_up(self):
        """Xử lý khi hết giờ - TỰ ĐỘNG CHUYỂN CÂU TIẾP THEO"""
        self.show_overlay("HẾT GIỜ RỒI!", "#fd7e14")
        self.disable_answer_input()
        # Gửi đáp án rỗng để chuyển câu tiếp theo
        try:
            self.client_socket.sendall(b"\n")
        except:
            pass
        self.expecting_question = True
        self.master.after(1500, self.master.event_generate, "<<ContinueNextQuestion>>")

    def update_score(self, is_correct):
        """Cập nhật điểm số"""
        self.total_questions += 1
        if is_correct:
            self.correct_answers += 1
            self.current_score += 10
            
        self.score_label.config(text=str(self.current_score))
        self.correct_label.config(text=str(self.correct_answers))
        self.total_label.config(text=str(self.total_questions))
        
        percent = int((self.correct_answers / self.total_questions) * 100) if self.total_questions > 0 else 0
        self.percent_label.config(text=f"{percent}%")

    def show_overlay(self, message, color, sub_message=""):
        """Hiển thị overlay thông báo"""
        if hasattr(self, 'overlay') and self.overlay.winfo_exists():
            self.overlay.destroy()
            
        self.overlay = tk.Frame(self.master, bg=color)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        container = ttk.Frame(self.overlay)
        container.place(relx=0.5, rely=0.35, anchor="center")

        ttk.Label(
            container,
            text=message,
            font=("Helvetica", 30, "bold"),
            foreground="white",
            background=color
        ).pack(pady=5)
        
        if sub_message:
            ttk.Label(
                container,
                text=f"Đáp án đúng: {sub_message}",
                font=("Helvetica", 18),
                foreground="white",
                background=color
            ).pack(pady=(10, 5))

        self.master.after(1500, self.overlay.destroy)

    def auto_advance_question(self, event=None):
        """Tự động chuyển câu hỏi tiếp theo"""
        self.enable_answer_input()
        self.expecting_question = True
        self.timer_label.configure(bootstyle="warning")
        self.timer_progress.configure(bootstyle="warning-striped")
        self._process_data_from_buffer()

    def show_final_result(self, final_message):
        """Hiển thị kết quả cuối cùng"""
        total = self.total_questions
        correct = self.correct_answers
        wrong = total - correct
        percent = int((correct / total) * 100) if total > 0 else 0
        
        # Tạo cửa sổ kết quả
        result_window = ttk.Toplevel(self.master)
        result_window.title("Kết Quả Trò Chơi")
        
        # Tính toán kích thước dựa trên cửa sổ chính
        result_width = 500
        result_height = 450
        x = self.master.winfo_x() + (self.window_width - result_width) // 2
        y = self.master.winfo_y() + (self.window_height - result_height) // 2
        result_window.geometry(f"{result_width}x{result_height}+{x}+{y}")
        
        result_window.resizable(False, False)
        result_window.transient(self.master)
        result_window.grab_set()
        
        frame = ttk.Frame(result_window, padding=30)
        frame.pack(fill="both", expand=True)
        
        # Header
        ttk.Label(frame, text="CHÚC MỪNG BẠN!", font=("Helvetica", 20, "bold"), 
                 bootstyle="success").pack(pady=10)
        
        # Kết quả chi tiết
        result_card = ttk.Labelframe(frame, text="KẾT QUẢ CHI TIẾT", bootstyle="info")
        result_card.pack(fill="x", pady=15, padx=10)
        
        result_text = f"""
TÊN NGƯỜI CHƠI: {self.player_name}
ĐIỂM SỐ: {self.current_score}
SỐ CÂU ĐÚNG: {correct}/{total}
SỐ CÂU SAI: {wrong}
TỈ LỆ ĐÚNG: {percent}%
        """
        
        ttk.Label(result_card, text=result_text, font=("Helvetica", 12), 
                 justify="left", bootstyle="info").pack(pady=15, padx=10)
        
        # Nút điều khiển
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="BXH", 
                  command=lambda: [self.save_score_history(), self.show_score_history(), result_window.destroy()],
                  bootstyle="success-solid", width=15).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="CHƠI LẠI", 
                  command=lambda: [self.save_score_history(), result_window.destroy(), self.restart_game()],
                  bootstyle="warning-solid", width=15).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="THOÁT", 
                  command=lambda: [self.save_score_history(), result_window.destroy(), self.master.destroy()],
                  bootstyle="danger-solid", width=15).pack(side="left", padx=5)
        
        self.save_score_history()

    def restart_game(self):
        """Khởi động lại game"""
        try:
            # Đóng kết nối cũ
            self.client_socket.close()
            
            # Reset biến
            self.current_score = 0
            self.total_questions = 0
            self.correct_answers = 0
            self.selected_answer = ""
            self.data_buffer = ""
            self.expecting_question = True
            
            # Kết nối lại server
            self.setup_connection()
            self.create_welcome_screen()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi động lại: {e}")

    def save_score_history(self):
        """Lưu lịch sử điểm số"""
        try:
            history = []
            if os.path.exists(self.score_history_file):
                with open(self.score_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            new_score = {
                "player_name": self.player_name,
                "score": self.current_score,
                "correct_answers": self.correct_answers,
                "total_questions": self.total_questions,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            history.append(new_score)
            history.sort(key=lambda x: x["score"], reverse=True)
            
            with open(self.score_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
        except:
            pass

    def show_score_history(self):
        """Hiển thị bảng xếp hạng"""
        try:
            if not os.path.exists(self.score_history_file):
                messagebox.showinfo("Bảng Xếp Hạng", "Chưa có dữ liệu xếp hạng!")
                return
                
            with open(self.score_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            rank_window = ttk.Toplevel(self.master)
            rank_window.title("Bảng xếp hạng TOP 10")
            
            # Tính toán kích thước dựa trên cửa sổ chính
            rank_width = 600
            rank_height = 500
            x = self.master.winfo_x() + (self.window_width - rank_width) // 2
            y = self.master.winfo_y() + (self.window_height - rank_height) // 2
            rank_window.geometry(f"{rank_width}x{rank_height}+{x}+{y}")
            
            frame = ttk.Frame(rank_window, padding=20)
            frame.pack(fill="both", expand=True)
            
            ttk.Label(frame, text="BẢNG XẾP HẠNG TOP 10", 
                     font=("Helvetica", 18, "bold"), bootstyle="primary").pack(pady=10)
            
            # Tạo treeview để hiển thị bảng
            columns = ("#", "Tên", "Điểm", "Tỉ lệ", "Ngày")
            tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
            
            # Định nghĩa columns
            tree.heading("#", text="#")
            tree.heading("Tên", text="Tên Người Chơi")
            tree.heading("Điểm", text="Điểm")
            tree.heading("Tỉ lệ", text="Tỉ lệ %")
            tree.heading("Ngày", text="Ngày")
            
            tree.column("#", width=50, anchor="center")
            tree.column("Tên", width=150)
            tree.column("Điểm", width=80, anchor="center")
            tree.column("Tỉ lệ", width=80, anchor="center")
            tree.column("Ngày", width=120, anchor="center")
            
            # Thêm dữ liệu
            for i, score in enumerate(history[:10], 1):
                percent = int((score['correct_answers'] / score['total_questions']) * 100) if score['total_questions'] > 0 else 0
                tree.insert("", "end", values=(
                    i,
                    score['player_name'],
                    score['score'],
                    f"{percent}%",
                    score['date']
                ))
            
            # Thêm scrollbar
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải bảng xếp hạng: {e}")

    def on_close(self):
        """Xử lý khi đóng ứng dụng"""
        try:
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
            if self.total_questions > 0:
                self.save_score_history()
        except:
            pass
        self.master.destroy()

if __name__ == "__main__":
    # Sửa lỗi khởi tạo theme
    try:
        app = ttk.Window(themename="superhero")  # Thử theme superhero
    except:
        try:
            app = ttk.Window()  # Không dùng theme nếu lỗi
        except:
            app = tk.Tk()  # Dùng tkinter thuần nếu vẫn lỗi
            app.title("Quiz Master")
    
    ModernQuizClient(app)
    app.mainloop()