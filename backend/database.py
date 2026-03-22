from datetime import datetime

import mysql.connector
from mysql.connector import Error

from config import Config


def get_server_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
    )


def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
    )


def initialize_database():
    server_conn = None
    cursor = None
    try:
        server_conn = get_server_connection()
        cursor = server_conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        server_conn.commit()
    finally:
        if cursor:
            cursor.close()
        if server_conn:
            server_conn.close()

    db_conn = None
    db_cursor = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()

        db_cursor.execute(
            """
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
            )
            """
        )

        db_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                alert_type VARCHAR(50) NOT NULL,
                user_phone VARCHAR(20) NULL,
                latitude DECIMAL(10, 7) NOT NULL,
                longitude DECIMAL(10, 7) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) NOT NULL DEFAULT 'OPEN'
            )
            """
        )

        db_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_phone VARCHAR(20) NULL,
                latitude DECIMAL(10, 7) NOT NULL,
                longitude DECIMAL(10, 7) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        db_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS geofence_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_phone VARCHAR(20) NOT NULL UNIQUE,
                center_latitude DECIMAL(10, 7) NOT NULL,
                center_longitude DECIMAL(10, 7) NOT NULL,
                radius_meters DECIMAL(10, 2) NOT NULL DEFAULT 500,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )

        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'notification_enabled'")
        if not db_cursor.fetchone():
            db_cursor.execute(
                "ALTER TABLE users ADD COLUMN notification_enabled TINYINT(1) NOT NULL DEFAULT 1"
            )
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'linked_user_phone'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN linked_user_phone VARCHAR(20) NULL")
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'address'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN address VARCHAR(255) NULL")
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'parent_name'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN parent_name VARCHAR(100) NULL")
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'warden_name'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN warden_name VARCHAR(100) NULL")
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'date_of_birth'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth DATE NULL")
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'college_address'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN college_address VARCHAR(255) NULL")
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'home_address'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN home_address VARCHAR(255) NULL")
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'preferred_language'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN preferred_language VARCHAR(40) NULL")
        db_cursor.execute("SHOW COLUMNS FROM users LIKE 'profile_photo'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE users ADD COLUMN profile_photo VARCHAR(255) NULL")
        db_cursor.execute("SHOW COLUMNS FROM alerts LIKE 'user_phone'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE alerts ADD COLUMN user_phone VARCHAR(20) NULL")
        db_cursor.execute("SHOW COLUMNS FROM locations LIKE 'user_phone'")
        if not db_cursor.fetchone():
            db_cursor.execute("ALTER TABLE locations ADD COLUMN user_phone VARCHAR(20) NULL")

        db_cursor.execute("SELECT COUNT(*) FROM users")
        existing_users = db_cursor.fetchone()[0]
        if existing_users == 0:
            db_cursor.executemany(
                "INSERT INTO users (name, phone, role, notification_enabled, linked_user_phone) VALUES (%s, %s, %s, %s, %s)",
                [
                    ("Admin User", "+910000000000", "admin", 0, None),
                ],
            )

        db_cursor.execute(
            "UPDATE users SET notification_enabled = 0 WHERE role = 'admin'"
        )

        db_conn.commit()
        print(
            f"[{datetime.now()}] Database initialized successfully: {Config.MYSQL_DATABASE}"
        )
    except Error as exc:
        print(f"[{datetime.now()}] Database initialization error: {exc}")
        raise
    finally:
        if db_cursor:
            db_cursor.close()
        if db_conn:
            db_conn.close()
