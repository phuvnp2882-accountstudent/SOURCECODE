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

            # 3. Xử lý câu hỏi (chỉ khi đang đợi câu hỏi)
            if self.expecting_question:
                if "Câu" in self.data_buffer and "Nhập đáp án (A/B/C/D):" in self.data_buffer:
                    question_start_idx = self.data_buffer.find("Câu")
                    question_end_idx = self.data_buffer.find("Nhập đáp án (A/B/C/D):") + len("Nhập đáp án (A/B/C/D):")
                    
                    if question_start_idx != -1 and question_end_idx != -1 and question_end_idx > question_start_idx:
                        question_block = self.data_buffer[question_start_idx:question_end_idx].strip()
                        self.master.after(0, self.parse_and_show_question, question_block)
                        self.data_buffer = self.data_buffer[question_end_idx:].strip() # Cắt bỏ phần câu hỏi đã xử lý
                        self.expecting_question = False # Đã nhận câu hỏi, giờ đợi đáp án
                        continue # Quay lại đầu vòng lặp để kiểm tra xem có kết quả hoặc thông báo khác ngay sau câu hỏi không
            
            # Nếu không có gì được xử lý trong vòng lặp này, thoát ra để chờ thêm dữ liệu
            if len(self.data_buffer) == original_buffer_len_in_loop:
                break # Không có gì mới để xử lý trong buffer hiện tại
            
    def parse_and_show_question(self, data):
        """Cập nhật giao diện với câu hỏi mới và các lựa chọn."""
        lines = data.strip().split("\n")
    
        question_text_lines = []
        options = []
    
        # Tách câu hỏi và các lựa chọn
        for line in lines:
            line_strip = line.strip()
            if line_strip.startswith(("A.", "B.", "C.", "D.")):
               options.append(line_strip)
            else:
                # Đảm bảo chỉ thêm các dòng có nội dung vào phần câu hỏi
                if line_strip:  # Không thêm dòng trống
                   question_text_lines.append(line_strip)

        self.question_label.config(text="\n".join(question_text_lines))

        # Cập nhật nút đáp án
        for i in range(4):
            if i < len(options):
                self.option_buttons[i].config(text=options[i], state=NORMAL)
            else:
                self.option_buttons[i].config(text=f"Đáp án {chr(65+i)}. (Trống)", state=DISABLED)

        self.selected_answer = ""
        self.drop_area.config(text="⬇️ Chọn đáp án của bạn")
    
        # Bắt đầu đếm ngược thời gian cho câu hỏi mới
        self.start_timer()

    def show_answer_result(self, message):
        """Hiển thị thông báo đúng/sai kiểu Ai là triệu phú."""
        self.timer_running = False
        is_correct = "sai" not in message.lower() and "incorrect" not in message.lower()
        self.update_score(is_correct)
        if is_correct:
           self.show_overlay("🎉 CHÍNH XÁC!", "#28a745")  # Xanh lá
        else:
            # Tách đáp án đúng nếu có
            correct_ans = ""
            if "Đáp án đúng là:" in message:
                correct_ans = message.split("Đáp án đúng là:")[-1].strip()
            self.show_overlay("❌ SAI RỒI!", "#dc3545", f"Đáp án đúng: {correct_ans}")

    def send_answer(self):
        """Gửi đáp án đã chọn đến server."""
        if not self.selected_answer:
            messagebox.showwarning("Thông báo", "Vui lòng chọn một đáp án trước khi gửi!")
            return
    
        try:
            # Lấy ký tự đáp án (A, B, C, D) từ chuỗi đầy đủ (ví dụ "A. 3" -> "A")
            answer_letter = self.selected_answer[0].upper()
        
            self.client_socket.sendall(f"{answer_letter}\n".encode())  # Thêm \n để server dễ đọc
        
            self.expecting_question = False  # Đã gửi đáp án, giờ đợi kết quả từ server
            self.disable_answer_submission()  # Vô hiệu hóa nút gửi và lựa chọn ngay lập tức

        except Exception as e:
            messagebox.showerror("Lỗi", f"Gửi dữ liệu thất bại: {e}")

    def auto_advance_question(self, event=None):
        """
        Hàm này được gọi bởi sự kiện <<ContinueNextQuestion>> sau khi hiển thị kết quả và chờ.
        Nó sẽ kích hoạt lại quá trình xử lý buffer để hiển thị câu hỏi tiếp theo.
        """
        self.response_label.config(text="")  # Xóa thông báo kết quả cũ sau độ trễ
        self.enable_answer_submission()  # Kích hoạt lại các nút và ô nhập liệu
        self.expecting_question = True  # Đặt lại trạng thái để _process_data_from_buffer tìm câu hỏi
        self._process_data_from_buffer()  # Kích hoạt lại việc xử lý buffer để tìm câu hỏi mới (nếu đã có trong buffer)

    def disable_answer_submission(self):
        """Vô hiệu hóa nút gửi đáp án và các lựa chọn."""
        self.submit_btn.config(state=DISABLED)
        for btn in self.option_buttons:
            btn.config(state=DISABLED)

    def enable_answer_submission(self):
        """Kích hoạt lại nút gửi đáp án và các lựa chọn."""
        self.submit_btn.config(state=NORMAL)
        for btn in self.option_buttons:
            btn.config(state=NORMAL)

    def start_timer(self):
    """Bắt đầu đếm ngược thời gian cho câu hỏi."""
    self.timer_running = False  # Dừng timer cũ nếu còn
    self.time_remaining = QUESTION_TIME_LIMIT
    self.timer_running = True
    self.update_timer()

    def update_timer(self):
        """Cập nhật đồng hồ đếm ngược trên UI."""
        if self.timer_running and self.time_remaining > 0:
           self.timer_label.config(text=f"⏰ Thời gian: {self.time_remaining}s")
           self.time_remaining -= 1
           self.master.after(1000, self.update_timer)
        elif self.timer_running:
            self.timer_running = False
            self.time_up()

    def time_up(self):
        """Xử lý khi hết thời gian."""
        self.show_overlay("⏰ HẾT GIỜ!", "#fd7e14")
        self.disable_answer_submission()
        self.master.after(2500, self.master.event_generate, "<<ContinueNextQuestion>>")

    def update_score(self, is_correct):
        """Cập nhật điểm số và thống kê trên UI."""
        self.total_questions += 1
        if is_correct:
           self.correct_answers += 1
           self.current_score += 10
        # Cập nhật các label thống kê
        self.score_label.config(text=f"Điểm: {self.current_score}")
        self.correct_label.config(text=f"Đúng: {self.correct_answers}")
        self.total_label.config(text=f"Tổng: {self.total_questions}")
        percent = int((self.correct_answers / self.total_questions) * 100) if self.total_questions > 0 else 0
        self.percent_label.config(text=f"Tỉ lệ: {percent}%")

    def save_score_history(self):
        """Lưu lịch sử điểm số vào file JSON."""
        try:
            # Đọc lịch sử điểm số hiện tại
            history = []
            if os.path.exists(self.score_history_file):
                with open(self.score_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

            # Thêm điểm số mới
            new_score = {
                "player_name": self.player_name,
                "score": self.current_score,
                "correct_answers": self.correct_answers,
                "total_questions": self.total_questions,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            history.append(new_score)

            # Sắp xếp theo điểm số cao nhất
            history.sort(key=lambda x: x["score"], reverse=True)

            # Lưu lại vào file
            with open(self.score_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=4)

        except Exception as e:
            pass

    def show_score_history(self):
        """Hiển thị lịch sử điểm số."""
        try:
            if not os.path.exists(self.score_history_file):
                messagebox.showinfo("Lịch sử điểm số", "Chưa có lịch sử điểm số!")
                return

            with open(self.score_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # Tạo cửa sổ mới để hiển thị lịch sử
            history_window = ttk.Toplevel(self.master)
            history_window.title("Lịch sử điểm số")
            history_window.geometry("400x500")

            # Tạo frame với scrollbar
            frame = ttk.Frame(history_window)
            frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Tạo text widget với scrollbar
            text_widget = tk.Text(frame, wrap=tk.WORD, width=40, height=20)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            # Pack widgets
            scrollbar.pack(side="right", fill="y")
            text_widget.pack(side="left", fill="both", expand=True)

            # Hiển thị lịch sử
            text_widget.insert("end", "=== BẢNG XẾP HẠNG ===\n\n")
            for i, score in enumerate(history[:10], 1):  # Chỉ hiển thị top 10
                text_widget.insert("end", f"{i}. {score['player_name']}\n")
                text_widget.insert("end", f"   Điểm: {score['score']} ({score['correct_answers']}/{score['total_questions']})\n")
                text_widget.insert("end", f"   Ngày: {score['date']}\n\n")

            text_widget.config(state="disabled")  # Không cho phép chỉnh sửa

        except Exception as e:
            pass

  




    