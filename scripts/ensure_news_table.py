import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = int(os.getenv("DB_PORT", 3306))

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, charset="utf8mb4")
try:
    with conn.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS Fin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE Fin")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS News (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                summary TEXT NOT NULL,
                content TEXT,
                category VARCHAR(50) NOT NULL,
                source VARCHAR(100) NOT NULL,
                author VARCHAR(100) NOT NULL,
                publish_time DATETIME NOT NULL,
                image_url VARCHAR(500),
                tags VARCHAR(200),
                read_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_category (category),
                INDEX idx_publish_time (publish_time),
                INDEX idx_read_count (read_count)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        conn.commit()
finally:
    conn.close()