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

        # 创建AI建议表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS AISuggestions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            page_type VARCHAR(50) NOT NULL,
            suggestion_type VARCHAR(50) NOT NULL,
            content JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY page_type_suggestion_type (page_type, suggestion_type)
        )
        ''')

        # 创建用户AI交互记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserAIActions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            page_type VARCHAR(50) NOT NULL,
            action_type VARCHAR(50) NOT NULL,
            suggestion_id INT,
            action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (suggestion_id) REFERENCES AISuggestions(id)
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

        # 插入初始AI建议数据
        ai_suggestions = [
            # 转账页面智能账户推荐
            ('transfer', 'recent_accounts', '''{
                "recentAccounts": [
                    {"id": 1, "name": "张三", "accountNumber": "6222 **** **** 5678", "avatar": "👤"},
                    {"id": 2, "name": "李四", "accountNumber": "6222 **** **** 1234", "avatar": "👤"},
                    {"id": 3, "name": "王五", "accountNumber": "6222 **** **** 9012", "avatar": "👤"}
                ]
            }'''),
            # 转账页面到账时间预估
            ('transfer', 'arrival_time', '''{
                "same_bank": "实时到账",
                "other_bank": "预计1-2小时",
                "peak_suggestion": "当前高峰，建议次日到账免手续费"
            }'''),
            # 账单页面消费结构分析
            ('bill', 'category_analysis', '''{
                "categoryAnalysis": [
                    {"name": "餐饮美食", "percentage": 35},
                    {"name": "购物消费", "percentage": 25},
                    {"name": "交通出行", "percentage": 15},
                    {"name": "休闲娱乐", "percentage": 10},
                    {"name": "其他支出", "percentage": 15}
                ],
                "abnormalItems": [
                    {"merchant": "XX奢侈品店", "amount": "+5800元"},
                    {"merchant": "XX游戏充值", "amount": "+1200元"}
                ]
            }'''),
            # 理财页面产品适配度分析
            ('financing', 'product_match', '''{
                "matchIndex": 75,
                "riskLevel": "中等",
                "paramExplanations": [
                    {"name": "夏普比率", "explanation": "该基金夏普比率为1.8，高于同类平均水平，风险调整后收益表现良好"},
                    {"name": "最大回撤", "explanation": "近一年最大回撤为15%，处于同类中等水平"},
                    {"name": "年化收益率", "explanation": "近一年年化收益率为12.5%，符合您的风险偏好"}
                ]
            }''')
        ]
        cursor.executemany('''
        INSERT IGNORE INTO AISuggestions (page_type, suggestion_type, content)
        VALUES (%s, %s, %s)
        ''', ai_suggestions)

    conn.commit()
    print('数据库和表创建成功，并插入初始数据')

except Exception as e:
    print(f'创建数据库和表失败: {e}')
    conn.rollback()
finally:
    conn.close()