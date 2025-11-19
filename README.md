# 🎮 Hệ Thống Trò Chơi Trắc Nghiệm Online 

Một ứng dụng trò chơi trắc nghiệm thời gian thực (Real-time Quiz Game) được xây dựng dựa trên mô hình Client-Server sử dụng **Python Socket** và cơ sở dữ liệu **MySQL**.

---

## 🌟 Tính năng nổi bật

### 🖥️ Server (Máy chủ)
- **Đa luồng (Multi-threading)**: Hỗ trợ nhiều người chơi kết nối và chơi cùng một lúc.
- **Quản lý dữ liệu**: Kết nối MySQL để lưu trữ câu hỏi, chủ đề và thông tin người chơi.
- **Logic game**: Tự động trộn câu hỏi (Random), chấm điểm và gửi phản hồi tức thì cho Client.
- **Bảo toàn dữ liệu**: Lưu trữ điểm số tích lũy của người chơi vào Database.

### 📱 Client (Người chơi)
- **Giao diện hiện đại**: Sử dụng thư viện `ttkbootstrap` (Theme Superhero) cho giao diện đẹp mắt, thân thiện.
- **Tương tác thời gian thực**: Nhận câu hỏi và hiển thị kết quả ngay lập tức từ Server.
- **Đồng hồ đếm ngược**: Giới hạn 30 giây cho mỗi câu hỏi với thanh hiển thị trực quan.
- **Lịch sử đấu (Local)**: Tự động lưu và hiển thị bảng xếp hạng thành tích cá nhân ngay trên máy Client.

---

## 🛠️ Yêu cầu hệ thống & Cài đặt

### 1. Phần mềm cần thiết
- Python 3.x
- MySQL Server (XAMPP, WAMP hoặc MySQL Installer)

### 2. Cài đặt thư viện Python
Mở Terminal hoặc Command Prompt và chạy:

```bash
pip install mysql-connector-python ttkbootstrap
