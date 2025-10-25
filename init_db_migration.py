"""
数据库迁移脚本
添加Bills和TransferHistory表
"""

import pymysql
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 数据库连接信息
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
DB_PORT = int(os.getenv('MYSQL_PORT', 3306))
DB_NAME = os.getenv('MYSQL_DATABASE', 'Fin')

# 连接到MySQL数据库
try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        database=DB_NAME,
        charset='utf8mb4'
    )
    
    print(f"✅ 成功连接到数据库: {DB_NAME}")
    
    with conn.cursor() as cursor:
        # 创建Bills表（账单表）
        print("\n📊 创建Bills表...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            merchant VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            amount DECIMAL(12, 2) NOT NULL,
            transaction_date DATE NOT NULL,
            transaction_time TIME DEFAULT '00:00:00',
            status VARCHAR(20) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_date (user_id, transaction_date),
            INDEX idx_category (category),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ Bills表创建成功")
        
        # 创建TransferHistory表（转账历史表）
        print("\n💸 创建TransferHistory表...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TransferHistory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            recipient_account VARCHAR(20) NOT NULL,
            recipient_name VARCHAR(100) NOT NULL,
            amount DECIMAL(12, 2) NOT NULL,
            transfer_date DATE NOT NULL,
            transfer_time TIME DEFAULT '00:00:00',
            status VARCHAR(20) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_recipient (user_id, recipient_account),
            INDEX idx_transfer_date (transfer_date),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ TransferHistory表创建成功")
        
        # 插入示例账单数据
        print("\n📝 插入示例账单数据...")
        sample_bills = [
            ('UTSZ', '星巴克咖啡', '餐饮', -45.00, '2023-10-28', '09:25:00'),
            ('UTSZ', '沃尔玛超市', '购物', -189.50, '2023-10-27', '18:42:00'),
            ('UTSZ', '滴滴出行', '交通', -28.60, '2023-10-27', '08:15:00'),
            ('UTSZ', '工资入账', '收入', 12500.00, '2023-10-25', '10:30:00'),
            ('UTSZ', '电影票', '娱乐', -98.00, '2023-10-24', '19:00:00'),
            ('UTSZ', '房租支出', '住房', -3500.00, '2023-10-01', '00:00:00'),
        ]
        
        for bill in sample_bills:
            try:
                cursor.execute('''
                INSERT IGNORE INTO Bills 
                (user_id, merchant, category, amount, transaction_date, transaction_time)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''', bill)
            except Exception as e:
                print(f"⚠️  插入账单数据失败: {e}")
        
        print("✅ 示例账单数据插入完成")
        
        # 插入示例转账历史数据
        print("\n📝 插入示例转账历史数据...")
        sample_transfers = [
            ('UTSZ', '6222123456781234', '张三', 1000.00, '2023-10-15', '14:20:00'),
            ('UTSZ', '6222123456785678', '李四', 500.00, '2023-10-10', '10:35:00'),
            ('UTSZ', '6222123456789012', '王五', 2000.00, '2023-10-05', '16:45:00'),
        ]
        
        for transfer in sample_transfers:
            try:
                cursor.execute('''
                INSERT IGNORE INTO TransferHistory
                (user_id, recipient_account, recipient_name, amount, transfer_date, transfer_time)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''', transfer)
            except Exception as e:
                print(f"⚠️  插入转账数据失败: {e}")
        
        print("✅ 示例转账历史数据插入完成")
        
    # 提交事务
    conn.commit()
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ✅ 数据库迁移完成！                                     ║
║                                                           ║
║   新增表：                                               ║
║   • Bills - 账单表                                        ║
║   • TransferHistory - 转账历史表                         ║
║                                                           ║
║   示例数据已插入，可以开始测试了！                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
except Exception as e:
    print(f"❌ 数据库迁移失败: {e}")
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'conn' in locals():
        conn.close()
        print("🔌 数据库连接已关闭")

