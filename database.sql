-- DROP USER IF EXISTS 'newuser' @'localhost';
-- CREATE USER 'newuser' @'localhost' IDENTIFIED BY '123456789';
-- GRANT ALL PRIVILEGES ON quiz_game.* TO 'newuser' @'localhost';
-- FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS quiz_game;
USE quiz_game;
-- Bảng người chơi
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Bảng chủ đề
CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);
-- Bảng câu hỏi
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT,
    question TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_option ENUM('A', 'B', 'C', 'D') NOT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);


INSERT IGNORE INTO topics (name)
VALUES ('Độ khó 1'),
    ('Độ khó 2'),
    ('Độ khó 3'),
    ('Độ khó 4'),
    ('Độ khó 5');


INSERT INTO questions (
        topic_id,
        question,
        option_a,
        option_b,
        option_c,
        option_d,
        correct_option
    )
VALUES (
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'cái gì cầm càng nhiều càng dễ mất?',
        'cầm bút',
        'cầm đồ',
        'cầm lòng ',
        'cầm tay',
        'B'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Vịt nào đi bằng 2 chân',
        'Vịt Donald',
        'vịt bầu',
        'Vịt xiêm',
        'tất cả các con vịt',
        'D'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Biển nào nhỏ nhất',
        'Biển Đông',
        'Biển số xe',
        'Biển đen',
        'Biển hồ',
        'B'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Loại củ nào khiến bạn rơi nước mắt?',
        'Khoai tây',
        'Ớt chuông',
        'Cà rốt',
        'Củ Hành',
        'D'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Cái gì càng trắng càng bẩn',
        'Cái Khăn',
        'Cái gối',
        'Cái bảng',
        'Cái áo',
        'C'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Đầu dê, mình ốc là con gì?',
        'Con rốc',
        'Con dốc',
        'Con dê',
        'Con ốc',
        'B'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Kiến gì không bao giờ thức',
        'Kiến càng',
        'Kiến lửa',
        'Kiến thức',
        'Kiến đen',
        'C'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Càng cất càng thấy?',
        'Cất quần',
        'cất nhà',
        'Cất sách',
        'Cất áo',
        'B'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Bánh gì đã thấy đau?',
        'Bánh tét',
        'Bánh đau',
        'Bánh bao',
        'Bánh tráng',
        'A'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 1'
        ),
        'Chữ gì mất đầu là hỏi, mất đuôi là trả lời',
        'Tay',
        'Tại',
        'Tai',
        'Tài',
        'C'
    );


INSERT INTO questions (
        topic_id,
        question,
        option_a,
        option_b,
        option_c,
        option_d,
        correct_option
    )
VALUES(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'Con gì biết đi nhưng người ta vẫn nói nó không biết đi?',
        'Con bò',
        'Con cua',
        'Con kiến',
        'Con vịt',
        'A'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'Mua để ăn nhưng không bao giờ ăn ',
        'Muối',
        'Bánh mì',
        'Bát đũa',
        'Kẹo',
        'C'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'Thứ gì đập liên tục mà không bao giờ vỡ',
        'Quả Bóng ',
        'Trái tim',
        'Cái trống',
        'Cái dùi',
        'B'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'Âm thầm trôi qua, không ai gữi lại được,cũng chẳng bao giờ quay đầu',
        'Năm tháng',
        'Thang cuốn',
        'Con lắc',
        'Xe hơi',
        'A'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'Môn thể thao người đấu càng lùi càng thắng',
        'Cờ vua',
        'Đấu vật',
        'Bóng bầu dục',
        'Kéo co',
        'D'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'làm thế nào để 1 tay che kín bầu trời?',
        'Lấy tay che mắt',
        'Dùng tay che mặt trời',
        'Dùng tay che trán ',
        'không thể che',
        'A'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'khi còn giữ thì có giá trị nhưng một khi nói ra thì không còn nguyên vẹn',
        'tiền bạc',
        'Quyền lực',
        'Bí mật ',
        'Bánh',
        'B'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'Trong một cuộc đua, bạn vượt qua người thứ hai. Vậy bạn đang ở vị trí thứ mấy?',
        'Thứ nhất',
        'Thứ hai',
        'Thứ ba',
        'Thứ tư',
        'B'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'Cái gì không đào mà sâu',
        'Giếng',
        'Hồ nước',
        'Hang động',
        'Biển',
        'D'
    ),
(
        (
            SELECT id
            FROM topics
            WHERE name = 'Độ khó 2'
        ),
        'Bệnh gì bác sĩ bó tay?',
        'Viêm họng',
        'Cảm lạnh',
        'Đau đầu',
        'Gãy tay',
        'D'
    );


INSERT INTO questions (
        topic_id,
        question,
        option_a,
        option_b,
        option_c,
        option_d,
        correct_option
    )
VALUES (
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Cái gì càng đưa lên cao thì càng nhỏ lại?',
    'Máy bay',
    'Bóng đèn',
    'Ngọn lửa',
    'Cái bóng',
    'D'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Con gì không bao giờ ngủ?',
    'Con cá',
    'Con muỗi',
    'Con mắt',
    'Con kiến',
    'C'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Thứ gì bạn càng lấy đi thì nó càng lớn?',
    'Cái lỗ',
    'Đám mây',
    'Cái bóng',
    'Cây bút chì',
    'A'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Cái gì càng đánh càng nhỏ?',
    'Cục đá',
    'Viên nước đá',
    'Cái trống',
    'Xà phòng',
    'B'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Cái gì có răng nhưng không cắn?',
    'Con cá',
    'Cái lược',
    'Cưa',
    'Ủng đất',
    'B'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Cái gì ướt khi làm khô thứ khác?',
    'Giấy',
    'Vải',
    'Khăn tắm',
    'Không khí',
    'C'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Thứ gì đi khắp thế giới mà vẫn nằm nguyên một chỗ?',
    'Bản đồ',
    'Dấu chân',
    'Con tem',
    'Cái bóng',
    'C'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Thứ gì càng nhiều chân thì đi càng chậm?',
    'Bàn',
    'Kiến',
    'Rết',
    'Ghế',
    'A'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Con gì càng tắm càng bẩn?',
    'Con cá',
    'Con heo',
    'Cái khăn',
    'Bọt biển',
    'C'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 3'
    ),
    'Cái gì có mặt nhưng không bao giờ nhìn thấy?',
    'Con mèo',
    'Mặt trời',
    'Mặt trăng',
    'Mặt bàn',
    'D'
);



INSERT INTO questions (
        topic_id,
        question,
        option_a,
        option_b,
        option_c,
        option_d,
        correct_option
    )
VALUES(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Cái gì có nhiều lỗ nhưng vẫn chứa được nước?',
    'Cái rổ',
    'Miếng bọt biển',
    'Cái chai',
    'Cái thùng rỗng',
    'B'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Thứ gì bạn có thể giữ nhưng không thể chạm vào?',
    'Hơi thở',
    'Lời hứa',
    'Cái bóng',
    'Thời gian',
    'B'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Cái gì càng nhiều thì càng ít thấy?',
    'Sương mù',
    'Khói',
    'Bóng tối',
    'Mưa',
    'C'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Con gì biết bay mà không có cánh?',
    'Bóng bay',
    'Máy bay',
    'Thời gian',
    'Giấc mơ',
    'D'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Thứ gì chạy mà không bao giờ biết mệt?',
    'Nước',
    'Gió',
    'Dòng thời gian',
    'Bánh xe',
    'C'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Cái gì mở ra được nhưng không đóng lại được?',
    'Cửa sổ',
    'Miệng',
    'Thời gian',
    'Lời nói đã lỡ',
    'D'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Cái gì bị bẻ thì không bao giờ lành lại?',
    'Gương',
    'Xương',
    'Lời hứa',
    'Chiếc lá',
    'C'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Thứ gì có thể đi qua thủy tinh mà không làm vỡ nó?',
    'Hơi nước',
    'Ánh sáng',
    'Bóng tối',
    'Âm thanh',
    'B'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Cái gì có một mắt nhưng không nhìn được?',
    'Kim đồng hồ',
    'Cây kim',
    'Bão',
    'Con cá',
    'C'
),

(
    (
        SELECT id FROM topics WHERE name = 'Độ khó 4'
    ),
    'Cái gì nặng hơn 1kg nhưng nhẹ hơn 1g?',
    'Bóng đèn',
    'Một ý tưởng',
    'Bóng bay',
    'Âm thanh',
    'B'
);

INSERT INTO questions (
        topic_id,
        question,
        option_a,
        option_b,
        option_c,
        option_d,
        correct_option
    )
VALUES (
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì có nhiều răng nhưng không cắn được?',
    'Cái cưa',
    'Cái bẫy',
    'Cái lược',
    'Bánh răng',
    'C'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Con gì càng chạy nhanh càng đứng yên?',
    'Con gió',
    'Con sông',
    'Con quay',
    'Đồng hồ',
    'B'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì càng lấy đi nhiều thì nó càng lớn?',
    'Cái hố',
    'Cái bóng',
    'Cái vết thương',
    'Cái lỗ hổng',
    'A'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì không chân, không đuôi, không thân mà lại nhiều đầu?',
    'Cái chổi',
    'Cầu truyền hình',
    'Bộ dây cáp',
    'Ổ điện',
    'B'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Con gì đi thì nằm, đứng cũng nằm, ngồi vẫn nằm?',
    'Con sâu',
    'Con tằm',
    'Con nhộng',
    'Con ốc sên',
    'B'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Quần gì không ai mặc?',
    'Quần thể',
    'Quần vợt',
    'Quần đảo',
    'Quần chúng',
    'C'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Con gì chỉ ăn mà không uống?',
    'Con mực',
    'Con giun',
    'Con tằm',
    'Con kiến',
    'C'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Bông gì không mọc trên cây?',
    'Bông hoa đá',
    'Bông tuyết',
    'Bông băng',
    'Bông cát',
    'B'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Xe gì không bao giờ giảm tốc độ?',
    'Xe cứu thương',
    'Xe tăng',
    'Xe lửa đồ chơi',
    'Xe chỉ',
    'D'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Mắt gì không dùng để nhìn?',
    'Mắt cá',
    'Mắt bão',
    'Mắt lưới',
    'Mắt kim',
    'A'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cầu nào không bắc qua sông?',
    'Cầu thang',
    'Cầu giấy',
    'Cầu hôn',
    'Cầu vòng',
    'C'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì có mắt nhưng không nhìn thấy?',
    'Cây kim',
    'Cối xay',
    'Trái tim',
    'Hột gạo',
    'A'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Chân nào không đi?',
    'Chân bàn',
    'Chân đèn',
    'Chân ghế',
    'Chân kiềng',
    'A'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Miệng nào không ăn?',
    'Miệng hang',
    'Miệng núi lửa',
    'Miệng cống',
    'Miệng giếng',
    'B'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Độc gì càng trúng càng thích?',
    'Độc đắc',
    'Độc đáo',
    'Độc chiêu',
    'Độc ca',
    'A'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì luôn đi lên mà không bao giờ đi xuống?',
    'Mực nước',
    'Tuổi tác',
    'Khí nóng',
    'Con diều',
    'B'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì có một đầu nhưng không có chân?',
    'Cái kim',
    'Cái búa',
    'Cái nón',
    'Cái que',
    'A'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì có cổ nhưng không có đầu?',
    'Chai nước',
    'Áo sơ mi',
    'Lọ hoa',
    'Bình cắm',
    'A'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì có một cái mà ai cũng có?',
    'Ngày sinh',
    'Tên',
    'Bóng',
    'Giọng nói',
    'B'
),
(
    (SELECT id FROM topics WHERE name = 'Độ khó 5'),
    'Cái gì có hai mặt nhưng chỉ có một mặt?',
    'Tờ tiền',
    'Cái đĩa',
    'Cái ví',
    'Cái gương',
    'C'
);
