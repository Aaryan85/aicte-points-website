-- =============================================================================
-- AICTE Activity & Points Management System
-- MySQL Database Schema
-- =============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS aicte_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aicte_db;

-- =============================================================================
-- USERS TABLE
-- Stores students, clubs, and admins in a single table with role differentiation
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'club', 'admin') NOT NULL DEFAULT 'student',
    full_name VARCHAR(150) NOT NULL,
    department VARCHAR(100) DEFAULT NULL,       -- For students
    roll_number VARCHAR(50) DEFAULT NULL,       -- For students
    club_name VARCHAR(150) DEFAULT NULL,        -- For clubs
    club_description TEXT DEFAULT NULL,          -- For clubs
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_email (email)
) ENGINE=InnoDB;

-- =============================================================================
-- EVENTS TABLE
-- Stores all events created by clubs, with approval workflow
-- =============================================================================
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category ENUM('technical', 'cultural', 'social', 'sports') NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME NOT NULL,
    venue VARCHAR(200) NOT NULL,
    points INT NOT NULL CHECK (points > 0 AND points <= 20),
    max_participants INT NOT NULL CHECK (max_participants > 0),
    club_id INT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    qr_token VARCHAR(100) DEFAULT NULL,         -- Unique token for QR-based attendance
    qr_code_path VARCHAR(255) DEFAULT NULL,     -- Path to generated QR image
    rejection_reason TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_category (category),
    INDEX idx_status (status),
    INDEX idx_club (club_id),
    INDEX idx_date (event_date)
) ENGINE=InnoDB;

-- =============================================================================
-- REGISTRATIONS TABLE
-- Many-to-many relationship between students and events
-- Tracks attendance and points awarded
-- =============================================================================
CREATE TABLE IF NOT EXISTS registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    event_id INT NOT NULL,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    attended TINYINT(1) DEFAULT 0,
    points_awarded INT DEFAULT 0,
    attendance_marked_at DATETIME DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE KEY unique_registration (student_id, event_id),
    INDEX idx_student (student_id),
    INDEX idx_event (event_id),
    INDEX idx_attended (attended)
) ENGINE=InnoDB;


-- =============================================================================
-- SAMPLE DATA
-- =============================================================================

-- Admin account (password: admin123)
INSERT INTO users (username, email, password_hash, role, full_name)
VALUES ('admin', 'admin@aicte.edu', '$2b$12$LJ3m4ys3Kkl0wGfOHg0dO.3KQx8JH9fGZ3VBE6YXeMVmFJprADsm6', 'admin', 'System Administrator');

-- Club accounts (password: club123)
INSERT INTO users (username, email, password_hash, role, full_name, club_name, club_description)
VALUES 
('techclub', 'tech@college.edu', '$2b$12$LJ3m4ys3Kkl0wGfOHg0dO.3KQx8JH9fGZ3VBE6YXeMVmFJprADsm6', 'club', 'Tech Club Lead', 'Technical Club', 'Promoting technology and innovation among students'),
('artclub', 'arts@college.edu', '$2b$12$LJ3m4ys3Kkl0wGfOHg0dO.3KQx8JH9fGZ3VBE6YXeMVmFJprADsm6', 'club', 'Arts Club Lead', 'Cultural Arts Club', 'Celebrating art, music, and cultural diversity'),
('sportsclub', 'sports@college.edu', '$2b$12$LJ3m4ys3Kkl0wGfOHg0dO.3KQx8JH9fGZ3VBE6YXeMVmFJprADsm6', 'club', 'Sports Club Lead', 'Sports Club', 'Encouraging physical fitness and sportsmanship');

-- Student accounts (password: student123)
INSERT INTO users (username, email, password_hash, role, full_name, department, roll_number)
VALUES 
('rahul', 'rahul@student.edu', '$2b$12$LJ3m4ys3Kkl0wGfOHg0dO.3KQx8JH9fGZ3VBE6YXeMVmFJprADsm6', 'student', 'Rahul Sharma', 'Computer Science', 'CS2024001'),
('priya', 'priya@student.edu', '$2b$12$LJ3m4ys3Kkl0wGfOHg0dO.3KQx8JH9fGZ3VBE6YXeMVmFJprADsm6', 'student', 'Priya Patel', 'Electronics', 'EC2024002'),
('amit', 'amit@student.edu', '$2b$12$LJ3m4ys3Kkl0wGfOHg0dO.3KQx8JH9fGZ3VBE6YXeMVmFJprADsm6', 'student', 'Amit Kumar', 'Mechanical', 'ME2024003');

-- Sample events (some approved, some pending)
INSERT INTO events (title, description, category, event_date, event_time, venue, points, max_participants, club_id, status, qr_token)
VALUES 
('Hackathon 2026', 'Annual 24-hour coding hackathon with exciting prizes and mentorship from industry experts.', 'technical', '2026-04-15', '09:00:00', 'Main Auditorium', 15, 100, 2, 'approved', 'hack2026token'),
('Cultural Fest', 'A grand celebration of music, dance, and art featuring performances from various colleges.', 'cultural', '2026-04-20', '10:00:00', 'Open Air Theatre', 10, 200, 3, 'approved', 'cultfest2026'),
('Code Sprint', 'Competitive programming contest testing algorithmic skills and problem-solving.', 'technical', '2026-04-25', '14:00:00', 'Computer Lab 1', 10, 50, 2, 'approved', 'codesprint2026'),
('Sports Day', 'Inter-department sports competition featuring cricket, football, and athletics.', 'sports', '2026-05-01', '08:00:00', 'College Ground', 10, 150, 4, 'pending', 'sports2026'),
('Social Awareness Drive', 'Community outreach program focusing on environmental sustainability and social responsibility.', 'social', '2026-05-05', '09:00:00', 'College Campus', 5, 80, 3, 'pending', 'social2026');

-- Sample registrations
INSERT INTO registrations (student_id, event_id, attended, points_awarded)
VALUES 
(5, 1, 1, 15),    -- Rahul attended Hackathon
(5, 2, 1, 10),    -- Rahul attended Cultural Fest
(5, 3, 0, 0),     -- Rahul registered for Code Sprint
(6, 1, 1, 15),    -- Priya attended Hackathon
(6, 2, 0, 0),     -- Priya registered for Cultural Fest
(7, 2, 1, 10);    -- Amit attended Cultural Fest
