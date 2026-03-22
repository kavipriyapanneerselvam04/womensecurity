CREATE DATABASE IF NOT EXISTS women_safety_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE women_safety_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'guardian',
    notification_enabled TINYINT(1) NOT NULL DEFAULT 1,
    linked_user_phone VARCHAR(20) NULL,
    address VARCHAR(255) NULL,
    parent_name VARCHAR(100) NULL,
    warden_name VARCHAR(100) NULL,
    date_of_birth DATE NULL,
    college_address VARCHAR(255) NULL,
    home_address VARCHAR(255) NULL,
    preferred_language VARCHAR(40) NULL,
    profile_photo VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    user_phone VARCHAR(20) NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN'
);

CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_phone VARCHAR(20) NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS geofence_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_phone VARCHAR(20) NOT NULL UNIQUE,
    center_latitude DECIMAL(10, 7) NOT NULL,
    center_longitude DECIMAL(10, 7) NOT NULL,
    radius_meters DECIMAL(10, 2) NOT NULL DEFAULT 500,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
