import socket
import threading
import mysql.connector

class QuizServer:
    def __init__(self):
        self.setup_database()
        
    def setup_database(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="quiz_game",
                autocommit=True
            )
            self.cursor = self.db.cursor(dictionary=True)
            print("Database connected successfully")
        except mysql.connector.Error as e:
            print(f"Database connection error: {e}")
            exit(1)

    def get_questions(self):
        try:
            self.cursor.execute("""
                SELECT q.id, t.name AS topic, q.question, q.option_a, q.option_b, 
                       q.option_c, q.option_d, q.correct_option 
                FROM questions q 
                JOIN topics t ON q.topic_id = t.id 
                ORDER BY RAND() LIMIT 10
            """)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error getting questions: {e}")
            return []

    def get_or_create_user(self, name):
        try:
            self.cursor.execute("SELECT id, score FROM users WHERE name = %s", (name,))
            row = self.cursor.fetchone()
            if row:
                return row["id"], row["score"]
            else:
                self.cursor.execute("INSERT INTO users (name, score) VALUES (%s, 0)", (name,))
                return self.cursor.lastrowid, 0
        except mysql.connector.Error as e:
            print(f"Error with user: {e}")
            return None, 0

    def update_score(self, user_id, score):
        try:
            self.cursor.execute("UPDATE users SET score = score + %s WHERE id = %s", (score, user_id))
        except mysql.connector.Error as e:
            print(f"Error updating score: {e}")

    def handle_client(self, client_socket, addr):
        try:
            client_socket.sendall("Chào mừng đến với trò chơi trắc nghiệm!\nXin mời nhập tên của bạn:\n".encode())
            
            name = client_socket.recv(1024).decode().strip()
            if not name:
                client_socket.sendall("Tên không hợp lệ!\n".encode())
                return

            user_id, current_score = self.get_or_create_user(name)
            if user_id is None:
                client_socket.sendall("Lỗi hệ thống! Không thể tạo người chơi.\n".encode())
                return

            client_socket.sendall(f"Xin chào {name}! Để bắt đầu trò chơi, nhấn phím 0 và Enter:\n".encode())
            
            # Chờ tín hiệu bắt đầu
            start_attempts = 0
            while start_attempts < 3:
                start_signal = client_socket.recv(1024).decode().strip()
                if start_signal == '0':
                    break
                else:
                    start_attempts += 1
                    if start_attempts < 3:
                        client_socket.sendall("Vui lòng nhấn phím 0 để bắt đầu:\n".encode())
                    else:
                        client_socket.sendall("Quá nhiều lần thử. Kết thúc kết nối.\n".encode())
                        return

            # Bắt đầu trò chơi
            questions = self.get_questions()
            if not questions:
                client_socket.sendall("Hiện không có câu hỏi nào. Vui lòng thử lại sau!\n".encode())
                return

            score = 0
            for i, q in enumerate(questions, 1):
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
                
                if answer in ['A', 'B', 'C', 'D']:
                    if answer == q['correct_option'].upper():
                        client_socket.sendall("Đáp án đúng!\n\n".encode())
                        score += 1
                    else:
                        client_socket.sendall(f"Đáp án sai! Đáp án đúng là: {q['correct_option']}\n\n".encode())
                else:
                    client_socket.sendall(f"Đáp án không hợp lệ! Đáp án đúng là: {q['correct_option']}\n\n".encode())

            # Cập nhật điểm và hiển thị kết quả
            self.update_score(user_id, score)
            
            result_text = f"Trò chơi kết thúc! Điểm của bạn: {score}/10\n"
            result_text += f"Cảm ơn bạn {name} đã chơi!\n"

            client_socket.sendall(result_text.encode())
            
        except socket.error as e:
            print(f"Socket error with client {addr}: {e}")
        except Exception as e:
            print(f"Unexpected error with client {addr}: {e}")
        finally:
            client_socket.close()
            print(f"Client {addr} disconnected")

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind(('0.0.0.0', 9999))
            server.listen(5)
            print("Server started. Waiting for connections...")

            while True:
                client_sock, addr = server.accept()
                print(f"Client {addr} connected")
                threading.Thread(target=self.handle_client, args=(client_sock, addr), daemon=True).start()
                
        except KeyboardInterrupt:
            print("\nShutting down server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server.close()
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'db'):
                self.db.close()

if __name__ == "__main__":
    quiz_server = QuizServer()
    quiz_server.start_server()