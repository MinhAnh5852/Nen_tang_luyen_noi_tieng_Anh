-- Đảm bảo toàn bộ hệ thống dùng bảng mã tiếng Việt chuẩn utf8mb4
SET NAMES 'utf8mb4';
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- ==========================================================
-- 1. DATABASE: user_db (Dùng cho User-Service & Mentor-Service)
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
    -- Tên gói hiển thị trên giao diện
    package_name VARCHAR(50) DEFAULT 'Gói Miễn Phí', 
    -- ID gói dùng để React so sánh logic (Khớp với subscription_db.subscription_plans.id)
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

-- Bảng Mentors: Hồ sơ chuyên sâu của cố vấn
CREATE TABLE IF NOT EXISTS mentors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    bio TEXT,
    skills_json TEXT, 
    status VARCHAR(20) DEFAULT 'PENDING',
    rating FLOAT DEFAULT 5.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Bảng learning_sessions: Lưu tiến độ học tập
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

-- Bảng feedbacks
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

-- Các bảng bổ trợ Mentor (Tasks, Submissions, Messages, Resources, Topics)
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
    title VARCHAR(200) NOT NULL,
    link VARCHAR(500),
    skill_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_name VARCHAR(200) NOT NULL,
    level VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS topic_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    learner_id VARCHAR(100),
    learner_name VARCHAR(100),
    topic_name VARCHAR(200),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learner_id) REFERENCES users(id) ON DELETE CASCADE
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

-- ==========================================================
-- 2. DATABASE: payment_db (Dùng cho Payment-Service)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS payment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payment_db;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL, 
    amount FLOAT NOT NULL,
    -- Tên gói hiển thị (Gói Cơ Bản, Gói Pro AI)
    package_name VARCHAR(50) NOT NULL,
    -- BỔ SUNG: ID gói để khớp với logic React và User-Service (free-id-001, pro-id-002)
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

-- Khởi tạo các gói dịch vụ (ID phải khớp với package_id trong user_db và transactions)
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
-- Bảng nhận dữ liệu đồng bộ từ RabbitMQ để phục vụ Dashboard
CREATE TABLE IF NOT EXISTS practice_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL, 
    topic VARCHAR(100),
    duration_seconds INT DEFAULT 0,
    accuracy_score FLOAT DEFAULT 0.0,
    grammar_score FLOAT DEFAULT 0.0,
    vocabulary_score FLOAT DEFAULT 0.0,
    ai_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (user_id) -- Giúp Dashboard tải dữ liệu nhanh hơn
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

-- Bảng kết quả luyện tập AI (Dùng cho Learner Dashboard)
CREATE TABLE IF NOT EXISTS practice_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    topic VARCHAR(100),
    duration_seconds INT DEFAULT 0,    -- Thời gian luyện tập
    accuracy_score FLOAT DEFAULT 0.0,
    grammar_score FLOAT DEFAULT 0.0,   -- Điểm ngữ pháp
    vocabulary_score FLOAT DEFAULT 0.0, -- Điểm từ vựng
    ai_feedback TEXT,                  -- Nhận xét chi tiết từ AI
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

COMMIT;