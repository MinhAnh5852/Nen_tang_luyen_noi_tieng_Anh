SET NAMES 'utf8mb4';
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- ==========================================================
-- 1. DATABASE: user_db (Dùng cho User, Mentor & Điều phối bài tập)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS user_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE user_db;

-- Bảng Users: Quản lý thông tin tài khoản và phân quyền
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(100) PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    `role` VARCHAR(20) DEFAULT 'learner',
    status VARCHAR(20) DEFAULT 'active',
    package_name VARCHAR(50) DEFAULT 'Gói Miễn Phí', 
    package_id VARCHAR(50) DEFAULT 'free-id-001',   
    user_level VARCHAR(50) DEFAULT 'A1 (Beginner)',
    current_streak INT DEFAULT 0,
    last_practice_date DATE NULL,
    overall_accuracy FLOAT DEFAULT 0.0,
    total_learning_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Chèn dữ liệu Admin mẫu
INSERT IGNORE INTO users (id, username, email, password, `role`, status, package_name, package_id) 
VALUES ('admin-001', 'Admin Hệ Thống', 'admin@gmail.com', '123456', 'admin', 'active', 'Gói Pro AI', 'pro-id-002');

-- Bảng Mentors: Lưu thông tin chuyên gia
CREATE TABLE IF NOT EXISTS mentors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(100), 
    email VARCHAR(100),    
    full_name VARCHAR(100),
    bio TEXT,
    skills TEXT, 
    status VARCHAR(20) DEFAULT 'pending',
    rating FLOAT DEFAULT 5.0,
    max_learners INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ==========================================================
-- BỔ SUNG: QUẢN LÝ CHỦ ĐỀ VÀ GIAO BÀI (TOPICS & ASSIGNMENTS)
-- Đáp ứng yêu cầu: Mentor cung cấp chủ đề thực tế & gợi ý từ vựng
-- ==========================================================

-- 1. Bảng topics: Thư viện các tình huống hội thoại (Do Mentor hoặc Admin tạo)
CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mentor_id VARCHAR(100),               -- ID người tạo (NULL nếu là mặc định hệ thống)
    topic_name VARCHAR(200) NOT NULL,
    level VARCHAR(50),                    -- A1, A2, B1, B2...
    description TEXT,                     -- Mô tả tình huống
    suggested_vocabulary TEXT,            -- TỪ VỰNG GỢI Ý (AI hiển thị lên màn hình cho học viên)
    scenario_context TEXT,                -- NGỮ CẢNH AI (Trang trọng, công sở, du lịch...)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 2. Bảng topic_assignments: Quản lý việc Mentor giao bài cụ thể cho học viên
CREATE TABLE IF NOT EXISTS topic_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mentor_id VARCHAR(100) NOT NULL,
    learner_id VARCHAR(100) NOT NULL,
    topic_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending', -- Pending (Chờ), In_Progress (Đang làm), Completed (Xong)
    due_date DATETIME,                   -- Hạn chót
    mentor_feedback TEXT,                -- Phản hồi riêng của Mentor sau khi học viên làm xong bài này
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (mentor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (learner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Chèn dữ liệu mẫu cho Chủ đề để hệ thống có sẵn dữ liệu test
INSERT IGNORE INTO topics (topic_name, level, description, suggested_vocabulary, scenario_context) 
VALUES 
('Job Interview', 'B2', 'Phỏng vấn xin việc vị trí Marketing Manager', 'Professional, candidate, experience, strengths', 'Business'),
('Booking a Hotel', 'A2', 'Đặt phòng khách sạn qua điện thoại', 'Reservation, check-in, availability, double room', 'Travel'),
('Daily Routine', 'A1', 'Kể về các hoạt động hàng ngày', 'Breakfast, shower, workplace, exercise', 'General');

-- Các bảng bổ trợ khác
CREATE TABLE IF NOT EXISTS learning_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    learner_id VARCHAR(100) NOT NULL,
    lesson_name VARCHAR(255),
    skill_type VARCHAR(50), 
    score FLOAT DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learner_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    ai_comment TEXT, 
    sentiment VARCHAR(20),
    target_name VARCHAR(100) DEFAULT 'System',
    rating INT DEFAULT 5,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mentor_id VARCHAR(100) DEFAULT 'Current_Mentor',
    learner_id VARCHAR(100) NOT NULL,
    learner_name VARCHAR(100),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline DATETIME,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (learner_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    learner_id VARCHAR(100) NOT NULL,
    learner_name VARCHAR(100),
    task_title VARCHAR(200),
    audio_link VARCHAR(500),
    score FLOAT DEFAULT 0.0,
    feedback TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learner_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id VARCHAR(100),
    receiver_id VARCHAR(100),
    receiver_name VARCHAR(100),
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mentor_id VARCHAR(100),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    link VARCHAR(500) NOT NULL,      -- Link tải file (Cloudinary/S3/Local)
    file_type VARCHAR(20),           -- PDF, Video, Word...
    skill_type VARCHAR(50),          -- Vocabulary, Grammar...
    file_size VARCHAR(50),           -- Dung lượng file (VD: 2MB)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mentor_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    theme VARCHAR(20) DEFAULT 'Light',
    language VARCHAR(20) DEFAULT 'Vietnamese',
    reminder_enabled TINYINT(1) DEFAULT 0,
    reminder_time VARCHAR(20) DEFAULT '08:00',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Bảng Mentor_Selections: Lưu vết việc Learner chọn Mentor nào để theo học
CREATE TABLE IF NOT EXISTS mentor_selections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    learner_id VARCHAR(100) NOT NULL,
    mentor_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_assignment (learner_id, mentor_id),
    FOREIGN KEY (learner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (mentor_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ==========================================================
-- 2. DATABASE: payment_db
-- ==========================================================
CREATE DATABASE IF NOT EXISTS payment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payment_db;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL, 
    amount FLOAT NOT NULL,
    package_name VARCHAR(50) NOT NULL,
    package_id VARCHAR(50) NOT NULL, 
    payment_method VARCHAR(20) NOT NULL, 
    status VARCHAR(20) DEFAULT 'PENDING', 
    provider_txn_id VARCHAR(100) NULL UNIQUE,
    paid_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
) ENGINE=InnoDB;

-- ==========================================================
-- 3. DATABASE: subscription_db
-- ==========================================================
CREATE DATABASE IF NOT EXISTS subscription_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE subscription_db;

CREATE TABLE IF NOT EXISTS subscription_plans (
    id VARCHAR(36) PRIMARY KEY, 
    name VARCHAR(100) NOT NULL,
    price FLOAT DEFAULT 0.0,
    duration_days INT DEFAULT 30,
    badge_text VARCHAR(50),
    features TEXT,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

INSERT IGNORE INTO subscription_plans (id, name, price, duration_days, badge_text, features) 
VALUES 
('free-id-001', 'Gói Miễn Phí', 0, 9999, 'Bản miễn phí', 'Cơ bản, Giới hạn AI'),
('plan-basic-001', 'Gói Cơ Bản', 149000, 30, 'Bản Cơ Bản', 'Cơ bản, Nâng cao giới hạn AI'),
('pro-id-002', 'Gói Pro AI', 500000, 30, 'Ưu tiên AI', 'Không giới hạn, Mentor hỗ trợ');

-- ==========================================================
-- 4. DATABASE: analytics_db
-- ==========================================================
CREATE DATABASE IF NOT EXISTS analytics_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE analytics_db;

CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS system_stats (
    `key` VARCHAR(50) PRIMARY KEY,
    `value` FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS system_feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100),
    user_email VARCHAR(150),
    subject VARCHAR(255), 
    message TEXT,
    status VARCHAR(20) DEFAULT 'new', 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT IGNORE INTO system_stats (`key`, `value`) VALUES ('total_users', 1), ('active_mentors', 0), ('total_revenue', 0.0);

CREATE TABLE IF NOT EXISTS practice_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL, 
    topic VARCHAR(100),
    duration_seconds INT DEFAULT 0,
    accuracy_score FLOAT DEFAULT 0.0,
    grammar_score FLOAT DEFAULT 0.0,
    vocabulary_score FLOAT DEFAULT 0.0,
    ai_feedback TEXT,
    audio_url VARCHAR(500),              -- CỘT MỚI: Link để Mentor nghe lại bài nói
    mentor_score FLOAT DEFAULT NULL,      -- CỘT MỚI: Điểm Mentor chấm
    mentor_feedback TEXT DEFAULT NULL,   -- CỘT MỚI: Nhận xét của Mentor
    status VARCHAR(20) DEFAULT 'Pending', -- CỘT MỚI: Trạng thái (Pending/Graded)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==========================================================
-- 5. DATABASE: xdpm (Dành riêng cho AI-core-service)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS xdpm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE xdpm;

CREATE TABLE IF NOT EXISTS chat_histories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    role VARCHAR(10) NOT NULL, 
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS practice_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL, 
    topic VARCHAR(100),
    duration_seconds INT DEFAULT 0,
    accuracy_score FLOAT DEFAULT 0.0,
    grammar_score FLOAT DEFAULT 0.0,
    vocabulary_score FLOAT DEFAULT 0.0,
    ai_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

COMMIT;