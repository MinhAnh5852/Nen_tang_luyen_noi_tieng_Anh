-- Đảm bảo toàn bộ hệ thống dùng bảng mã tiếng Việt chuẩn utf8mb4
SET NAMES 'utf8mb4';

-- ==========================================================
-- 1. DATABASE: user_db (Quản lý User & Mentor)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS user_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE user_db;

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(100) PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    `role` VARCHAR(20) DEFAULT 'learner',
    status VARCHAR(20) DEFAULT 'active',
    package_name VARCHAR(50) DEFAULT 'Free',
    user_level VARCHAR(50) DEFAULT 'A1 (Beginner)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Admin mặc định (Email: admin@gmail.com | Pass: 123456)
INSERT IGNORE INTO users (id, username, email, password, `role`, status, package_name) 
VALUES ('admin-001', 'Admin Hệ Thống', 'admin@gmail.com', '123456', 'admin', 'active', 'Pro AI');

-- BẢNG MENTORS: Logic Duyệt nằm ở cột is_verified
CREATE TABLE IF NOT EXISTS mentors (
    id VARCHAR(100) PRIMARY KEY,
    specialty VARCHAR(100),
    bio TEXT,
    experience_years INT DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 5.0,
    is_verified BOOLEAN DEFAULT FALSE, -- MẶC ĐỊNH LÀ FALSE (Chờ Admin duyệt)
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP NULL,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
-- 2. DATABASE: payment_db (Đã đồng bộ với transaction.py)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS payment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payment_db;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Khớp với String(36) bên Python
    user_id VARCHAR(36) NOT NULL, 
    
    -- Khớp với db.Float
    amount FLOAT NOT NULL,
    
    package_name VARCHAR(50) NOT NULL,
    
    -- Khớp với biến payment_method trong Python
    payment_method VARCHAR(20) NOT NULL, 
    
    -- QUAN TRỌNG: Khớp với 'PENDING', 'SUCCESS', 'FAILED' (Viết HOA)
    status VARCHAR(20) DEFAULT 'PENDING', 
    
    provider_txn_id VARCHAR(100) NULL UNIQUE,
    paid_at DATETIME NULL,
    
    -- Dùng DATETIME thay vì TIMESTAMP để khớp với datetime.utcnow của Python
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================================
-- 3. DATABASE: subscription_db (Gói dịch vụ)
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
-- 4. DATABASE: analytics_db (Thống kê Dashboard)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS analytics_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE analytics_db;

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