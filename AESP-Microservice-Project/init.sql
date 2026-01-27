-- Đảm bảo toàn bộ hệ thống dùng bảng mã tiếng Việt chuẩn utf8mb4
SET NAMES 'utf8mb4';

-- ==========================================================
-- 1. DATABASE: user_db (Quản lý User, Mentor & Lộ trình)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS user_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE user_db;

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(100) PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    `role` VARCHAR(20) DEFAULT 'learner', -- admin, mentor, learner
    status VARCHAR(20) DEFAULT 'active',
    package_name VARCHAR(50) DEFAULT 'Free',
    user_level VARCHAR(50) DEFAULT 'A1 (Beginner)',
    
    -- Cột phục vụ chức năng DASHBOARD LEARNER (Theo đề bài)
    current_streak INT DEFAULT 0,          -- Chuỗi ngày học liên tiếp
    last_practice_date DATE NULL,          -- Ngày cuối cùng luyện nói để tính streak
    overall_accuracy FLOAT DEFAULT 0.0,    -- Điểm phát âm trung bình toàn hệ thống
    total_learning_points INT DEFAULT 0,   -- Điểm tích lũy (Leaderboard)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Admin mặc định
INSERT IGNORE INTO users (id, username, email, password, `role`, status, package_name) 
VALUES ('admin-001', 'Admin Hệ Thống', 'admin@gmail.com', '123456', 'admin', 'active', 'Pro AI');

-- BẢNG LỘ TRÌNH CÁ NHÂN HÓA (Adaptive Learning Path - Yêu cầu đề bài)
CREATE TABLE IF NOT EXISTS learning_paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    title VARCHAR(255),                    -- Ví dụ: Business English Roadmap
    `status` VARCHAR(20) DEFAULT 'in_progress', -- completed, in_progress
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- BẢNG CHI TIẾT CÁC BƯỚC TRONG LỘ TRÌNH (Path Steps)
CREATE TABLE IF NOT EXISTS path_steps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path_id INT NOT NULL,
    step_order INT,                        -- Thứ tự 1, 2, 3...
    title VARCHAR(255),                    -- Ví dụ: Greetings in Business
    content_type VARCHAR(50),              -- lesson, test, practice
    is_completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (path_id) REFERENCES learning_paths(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- BẢNG MENTORS (Đã thêm Specialty cho Admin quản lý)
CREATE TABLE IF NOT EXISTS mentors (
    id VARCHAR(100) PRIMARY KEY,
    specialty VARCHAR(100),               -- Kỹ năng: IELTS, Business, Travel...
    bio TEXT,
    experience_years INT DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 5.0,
    is_verified BOOLEAN DEFAULT FALSE,     -- Chờ Admin duyệt
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP NULL,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- BẢNG FEEDBACK (Để Admin Moderate)
CREATE TABLE IF NOT EXISTS feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    content TEXT,
    rating INT,
    target_name VARCHAR(100) DEFAULT 'System',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================================
-- 2. DATABASE: payment_db
-- ==========================================================
CREATE DATABASE IF NOT EXISTS payment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payment_db;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL, 
    amount FLOAT NOT NULL,
    package_name VARCHAR(50) NOT NULL,
    payment_method VARCHAR(20) NOT NULL, 
    status VARCHAR(20) DEFAULT 'PENDING', 
    provider_txn_id VARCHAR(100) NULL UNIQUE,
    paid_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    plan_id VARCHAR(36) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO subscription_plans (id, name, price, duration_days, badge_text, features) 
VALUES 
('free-id-001', 'Gói Miễn Phí', 0, 9999, 'Bản miễn phí', 'Cơ bản, Giới hạn AI'),
('pro-id-002', 'Gói Pro AI', 500000, 30, 'Ưu tiên AI', 'Không giới hạn, Mentor hỗ trợ');

-- ==========================================================
-- 4. DATABASE: analytics_db (Lưu kết quả AI & Thống kê)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS analytics_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE analytics_db;

-- BẢNG QUAN TRỌNG: Lưu lịch sử luyện nói AI (Để hiện Dashboard: Accuracy, Time)
CREATE TABLE IF NOT EXISTS practice_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    topic VARCHAR(100),                -- Travel, Business, Daily...
    duration_seconds INT DEFAULT 0,     -- Thời gian nói
    accuracy_score FLOAT DEFAULT 0.0,   -- Điểm phát âm AI chấm
    grammar_score FLOAT DEFAULT 0.0,    -- Điểm ngữ pháp AI chấm
    vocabulary_score FLOAT DEFAULT 0.0, -- Điểm từ vựng AI chấm
    ai_feedback TEXT,                  -- Nhận xét từ AI
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS system_stats (
    `key` VARCHAR(50) PRIMARY KEY,
    `value` BIGINT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO system_stats (`key`, `value`) VALUES 
('total_users', 1), 
('total_revenue', 0), 
('active_mentors', 0), 
('ai_sessions', 0);