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