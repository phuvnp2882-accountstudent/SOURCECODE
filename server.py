import socket
import threading
import random
import mysql.connector

# Kết nối database với biến db
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="quiz_game"
)
cursor = db.cursor(dictionary=True)

# Lấy 10 câu hỏi random
def get_questions():
    cursor.execute("SELECT q.id, t.name AS topic, q.question, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_option "
                   "FROM questions q JOIN topics t ON q.topic_id = t.id ORDER BY RAND() LIMIT 10")
    return cursor.fetchall()

# Lấy hoặc tạo người chơi, trả về id người chơi
def get_or_create_user(name):
    cursor.execute("SELECT id, score FROM users WHERE name = %s", (name,))
    row = cursor.fetchone()
    if row:
        return row["id"], row["score"]
    else:
        cursor.execute("INSERT INTO users (name, score) VALUES (%s, 0)", (name,))
        db.commit()
        return cursor.lastrowid, 0

# Cập nhật điểm người chơi
def update_score(user_id, score):
    cursor.execute("UPDATE users SET score = score + %s WHERE id = %s", (score, user_id))
    db.commit()

# Lấy bảng xếp hạng top 5
def get_leaderboard():
    cursor.execute("SELECT name, score FROM users ORDER BY score DESC LIMIT 5")
    return cursor.fetchall()

# Hàm xử lý client
def handle_client(client_socket, addr):
    try:
        client_socket.sendall("Chào mừng đến với trò chơi trắc nghiệm!\nXin mời nhập tên của bạn:\n".encode())
        name = client_socket.recv(1024).decode().strip()
        user_id, current_score = get_or_create_user(name)

        client_socket.sendall(f"Xin chào {name}! Để bắt đầu trò chơi, nhấn phím 0 và Enter:\n".encode())
        while True:
            start_signal = client_socket.recv(1024).decode().strip()
            if start_signal == '0':
                break
            else:
                client_socket.sendall("Vui lòng nhấn phím 0 để bắt đầu:\n".encode())

        questions = get_questions()
        score = 0

        for i, q in enumerate(questions, 1):
            # Gửi câu hỏi
            question_text = (f"Câu {i}:\n"
                             f"Chủ đề: {q['topic']}\n"
                             f"{q['question']}\n"
                             f"A. {q['option_a']}\n"
                             f"B. {q['option_b']}\n"
                             f"C. {q['option_c']}\n"
                             f"D. {q['option_d']}\n"
                             f"Nhập đáp án (A/B/C/D):\n")
            client_socket.sendall(question_text.encode())

            answer = client_socket.recv(1024).decode().strip().upper()

            if answer == q['correct_option'].upper():
                client_socket.sendall("Đáp án đúng!\n\n".encode())
                score += 1
            else:
                client_socket.sendall(f"Đáp án sai! Đáp án đúng là: {q['correct_option']}\n\n".encode())

        # Cập nhật điểm số vào database
        update_score(user_id, score)

        # Gửi điểm và bảng xếp hạng
        leaderboard = get_leaderboard()
        result_text = f"Trò chơi kết thúc! Điểm của bạn: {score}/10\n\n=== BẢNG XẾP HẠNG TOP 5 ===\n"
        for rank, player in enumerate(leaderboard, 1):
            result_text += f"{rank}. {player['name']} - {player['score']} điểm\n"
        result_text += "\nCảm ơn bạn đã chơi!\n"

        client_socket.sendall(result_text.encode())
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        client_socket.close()