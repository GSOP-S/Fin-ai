import pymysql
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 数据库连接信息
DB_HOST = os.getenv('MYSQL_HOST')
DB_USER = os.getenv('MYSQL_USER')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD')
DB_PORT = int(os.getenv('MYSQL_PORT', 3306))

# 连接到MySQL服务器
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT,
    charset='utf8mb4'
)

try:
    with conn.cursor() as cursor:
        # 创建数据库
        cursor.execute('CREATE DATABASE IF NOT EXISTS Fin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        cursor.execute('USE Fin')

        # 创建Users表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id VARCHAR(50) PRIMARY KEY,
            password VARCHAR(50) NOT NULL,
            display_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 创建Stocks表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Stocks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(20) NOT NULL UNIQUE,
            industry VARCHAR(50) NOT NULL,
            market_cap VARCHAR(50) NOT NULL,
            pe VARCHAR(20) NOT NULL,
            recent_performance VARCHAR(100) NOT NULL,
            volatility VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 创建Fundings表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Fundings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            nav DECIMAL(10, 4) NOT NULL,
            change_percent VARCHAR(20) NOT NULL,
            fund_change VARCHAR(20) NOT NULL,
            category VARCHAR(50) NOT NULL,
            risk VARCHAR(20) NOT NULL,
            manager VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 插入初始用户数据
        cursor.execute('''
        INSERT IGNORE INTO Users (user_id, password, display_name) VALUES
        ('UTSZ', 'admin', 'UTSZ用户')
        ''')

        # 插入初始股票数据
        stock_data = [
            ('贵州茅台', '600519', '白酒', '2.5万亿', '30.5', '连续3个月上涨', '低'),
            ('五粮液', '000858', '白酒', '9000亿', '25.2', '震荡上行', '中等'),
            ('宁德时代', '300750', '新能源', '1.2万亿', '45.8', '波动较大', '高'),
            ('腾讯控股', '00700', '互联网', '3万亿', '18.5', '稳步回升', '中等'),
            ('阿里巴巴', '9988', '互联网', '2.8万亿', '15.2', '底部企稳', '中等'),
            ('美团-W', '03690', '互联网', '8000亿', '-', '持续调整', '高'),
            ('招商银行', '600036', '银行', '1.5万亿', '8.5', '小幅波动', '低'),
            ('中国平安', '601318', '保险', '9000亿', '6.8', '横盘整理', '低')
        ]
        cursor.executemany('''
        INSERT IGNORE INTO Stocks (name, code, industry, market_cap, pe, recent_performance, volatility)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', stock_data)

        # 插入初始基金数据
        fund_data = [
            ('005827', '易方达蓝筹精选混合', 2.8745, '2.13%', '+0.0598', '混合型', '中高风险', '张坤'),
            ('320007', '诺安成长混合', 1.7654, '-1.24%', '-0.0222', '混合型', '高风险', '蔡嵩松'),
            ('002001', '华夏回报混合A', 3.2456, '0.89%', '+0.0288', '混合型', '中风险', '王宗合'),
            ('161005', '富国天惠成长混合A', 4.5678, '1.56%', '+0.0695', '混合型', '中高风险', '朱少醒'),
            ('163406', '兴全合润混合', 3.8923, '1.23%', '+0.0473', '混合型', '中高风险', '谢治宇')
        ]
        cursor.executemany('''
        INSERT IGNORE INTO Fundings (code, name, nav, change_percent, fund_change, category, risk, manager)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', fund_data)

    conn.commit()
    print('数据库和表创建成功，并插入初始数据')

except Exception as e:
    print(f'创建数据库和表失败: {e}')
    conn.rollback()
finally:
    conn.close()