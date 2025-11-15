import pymysql
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 数据库连接信息
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = int(os.getenv('DB_PORT', 3306))

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
        
        # 创建Bills表（账单表）
        print('创建Bills表...')
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
        print('✓ Bills表创建成功')
        
        # 创建TransferHistory表（转账历史表）
        print('创建TransferHistory表...')
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
        print('✓ TransferHistory表创建成功')
        
        # 创建News表（资讯表）
        print('创建News表...')
        cursor.execute('''
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
        ''')
        print('✓ News表创建成功')

        # 插入初始用户数据
        cursor.execute('''
        INSERT IGNORE INTO Users (user_id, password, display_name) VALUES
        ('UTSZ', 'admin', 'UTSZ用户')
        ''')

        

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

        # 插入示例账单数据
        print('插入示例账单数据...')
        sample_bills = [
            ('UTSZ', '星巴克咖啡', '餐饮', -45.00, '2023-10-28', '09:25:00'),
            ('UTSZ', '沃尔玛超市', '购物', -189.50, '2023-10-27', '18:42:00'),
            ('UTSZ', '滴滴出行', '交通', -28.60, '2023-10-27', '08:15:00'),
            ('UTSZ', '工资入账', '收入', 12500.00, '2023-10-25', '10:30:00'),
            ('UTSZ', '电影票', '娱乐', -98.00, '2023-10-24', '19:00:00'),
            ('UTSZ', '房租支出', '住房', -3500.00, '2023-10-01', '00:00:00'),
            ('UTSZ', '必胜客晚餐', '餐饮', -156.00, '2023-10-20', '19:30:00'),
            ('UTSZ', '地铁充值', '交通', -100.00, '2023-10-18', '08:00:00'),
            ('UTSZ', '京东购物', '购物', -568.00, '2023-10-15', '20:15:00'),
            ('UTSZ', '健身房会费', '健身', -299.00, '2023-10-12', '10:00:00')
        ]
        cursor.executemany('''
        INSERT IGNORE INTO Bills 
        (user_id, merchant, category, amount, transaction_date, transaction_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', sample_bills)
        print('✓ 示例账单数据插入完成')
        
        # 插入示例转账历史数据
        print('插入示例转账历史数据...')
        sample_transfers = [
            ('UTSZ', '6222123456781234', '张三', 1000.00, '2023-10-15', '14:20:00'),
            ('UTSZ', '6222123456785678', '李四', 500.00, '2023-10-10', '10:35:00'),
            ('UTSZ', '6222123456789012', '王五', 2000.00, '2023-10-05', '16:45:00'),
            ('UTSZ', '6222123456781234', '张三', 800.00, '2023-09-28', '15:10:00'),
            ('UTSZ', '6222123456785678', '李四', 1500.00, '2023-09-20', '11:20:00')
        ]
        cursor.executemany('''
        INSERT IGNORE INTO TransferHistory
        (user_id, recipient_account, recipient_name, amount, transfer_date, transfer_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', sample_transfers)
        print('✓ 示例转账历史数据插入完成')
        
        # 插入示例资讯数据
        print('插入示例资讯数据...')
        from datetime import datetime, timedelta
        now = datetime.now()
        sample_news = [
            ('央行降准0.5个百分点，释放长期资金约1万亿元', 
             '中国人民银行宣布下调金融机构存款准备金率0.5个百分点，预计释放长期资金约1万亿元，支持实体经济发展。',
             '中国人民银行今日宣布，将于近期下调金融机构存款准备金率0.5个百分点。此次降准将释放长期资金约1万亿元，有助于降低社会融资成本，支持实体经济发展。专家分析认为，此举体现了稳健货币政策的精准发力，为经济恢复提供有力支持。',
             '财经新闻', '中国人民银行', '金融时报', (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=1', '央行,降准,货币政策', 1523),
            
            ('A股三大指数集体收涨，科技股表现强势', 
             '今日A股市场延续强势，沪指涨1.2%，创业板指涨2.3%，科技板块领涨。',
             '今日A股市场延续强势，沪指收涨1.2%，深成指涨1.8%，创业板指涨2.3%。科技板块表现强势，半导体、人工智能、云计算等概念股纷纷走强。分析师指出，政策利好叠加业绩预期改善，科技股有望继续领涨市场。',
             '市场行情', '东方财富网', '市场研究员', (now - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=2', 'A股,科技股,市场行情', 2856),
            
            ('新版金融监管政策出台，助力实体经济发展', 
             '金融监管部门发布新版监管政策，强化金融服务实体经济导向，优化融资结构。',
             '金融监管部门近日发布新版监管政策，强调金融机构要坚持服务实体经济本源，优化融资结构，提升金融服务质效。政策要求加大对制造业、小微企业、科技创新等领域的支持力度，同时防范化解金融风险。',
             '政策解读', '金融监管总局', '政策分析师', (now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=3', '金融监管,政策,实体经济', 1845),
            
            ('基金投资入门：如何选择适合自己的基金产品', 
             '本文详细介绍了基金投资的基础知识，包括基金类型、风险评估、投资策略等内容。',
             '基金投资是理财的重要方式之一。首先要了解不同类型基金的特点：货币基金风险低流动性好，债券基金收益稳定，股票基金潜在收益高但波动大，混合基金平衡风险与收益。投资者应根据自身风险承受能力、投资期限和收益预期选择合适的产品。建议采用定投方式分散风险，长期持有获取复利效应。',
             '理财知识', '金融学堂', '理财专家', (now - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=4', '基金,理财,投资入门', 3421),
            
            ('人民币汇率稳中有升，外汇市场运行平稳', 
             '近期人民币对美元汇率保持稳定并略有上升，反映了我国经济基本面向好。',
             '近期人民币对美元汇率保持稳定并略有上升，反映了我国经济基本面向好和国际收支平衡的良好态势。专家认为，随着我国经济持续恢复，人民币汇率将在合理均衡水平上保持基本稳定。外汇局表示，将继续深化外汇领域改革开放，维护外汇市场平稳运行。',
             '市场行情', '外汇管理局', '汇率分析师', (now - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=5', '人民币,汇率,外汇', 1234),
            
            ('银行理财产品收益率回升，投资者信心增强', 
             '近期银行理财产品平均收益率有所回升，吸引更多投资者关注。',
             '数据显示，近期银行理财产品平均收益率有所回升，部分产品年化收益率达到4%以上。业内人士分析，这与债券市场收益率波动、银行优化资产配置等因素有关。建议投资者根据自身需求选择合适期限和风险等级的产品，注意产品说明书中的风险提示。',
             '理财知识', '银行资讯', '理财顾问', (now - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=6', '银行理财,收益率,投资', 2167),
            
            ('数字人民币试点范围扩大，应用场景日益丰富', 
             '数字人民币试点范围进一步扩大，在零售、交通、政务等领域应用不断深化。',
             '数字人民币试点范围进一步扩大，已覆盖多个省市。应用场景不断丰富，在零售消费、公共交通、政务服务、税收缴纳等领域的应用持续深化。数字人民币具有法定货币地位、支付便捷、安全可靠等特点，为公众提供了更多支付选择。',
             '财经新闻', '数字货币研究所', '科技记者', (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=7', '数字人民币,支付,科技金融', 3892),
            
            ('保险行业加大创新力度，推出多款惠民保险产品', 
             '保险公司推出多款创新型惠民保险产品，覆盖医疗、养老、意外等多个领域。',
             '保险行业持续加大创新力度，推出多款惠民保险产品。这些产品覆盖医疗、养老、意外伤害等多个领域，保费亲民，保障全面。例如城市定制型商业医疗保险，保费低至几十元，保额可达数百万。专家建议，消费者应根据自身需求合理配置保险，构建完善的保障体系。',
             '理财知识', '保险协会', '保险专家', (now - timedelta(days=1, hours=2)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=8', '保险,惠民,医疗保障', 1678),
            
            ('资本市场改革持续深化，注册制改革稳步推进', 
             '资本市场改革持续深化，全面注册制改革平稳落地，市场生态不断优化。',
             '资本市场改革持续深化，全面注册制改革平稳落地。这标志着资本市场进入新的发展阶段，有助于提升市场包容性和适应性，更好服务实体经济。监管部门表示，将继续完善基础制度，加强市场监管，保护投资者合法权益，促进资本市场高质量发展。',
             '政策解读', '证监会', '市场观察员', (now - timedelta(days=1, hours=6)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=9', '资本市场,注册制,改革', 2543),
            
            ('金融科技赋能普惠金融，小微企业融资更便利', 
             '金融科技创新应用不断深化，为小微企业提供更加便捷高效的融资服务。',
             '金融科技创新应用不断深化，通过大数据、人工智能等技术，金融机构能够更精准地评估企业信用，为小微企业提供便捷高效的融资服务。数据显示，普惠小微贷款余额持续增长，平均利率稳中有降，有效缓解了小微企业融资难、融资贵问题。',
             '财经新闻', '金融科技协会', '科技观察员', (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=10', '金融科技,普惠金融,小微企业', 1956),
            
            ('养老金融产品创新发展，助力构建多层次养老保障体系', 
             '养老金融产品创新发展，个人养老金制度稳步实施，为养老保障提供有力支持。',
             '养老金融产品创新发展，个人养老金制度稳步实施。银行、保险、基金等机构纷纷推出各类养老金融产品，为居民提供多样化的养老储备选择。专家建议，应尽早规划养老财务，通过多种方式积累养老资金，构建完善的养老保障体系。',
             '理财知识', '养老金融研究院', '养老规划师', (now - timedelta(days=2, hours=4)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=11', '养老,个人养老金,保障', 2234),
            
            ('绿色金融快速发展，支持经济社会绿色转型', 
             '绿色金融快速发展，绿色信贷、绿色债券规模持续增长，助力实现"双碳"目标。',
             '绿色金融快速发展，绿色信贷、绿色债券规模持续增长。金融机构积极支持清洁能源、节能环保等绿色产业发展，助力实现碳达峰、碳中和目标。监管部门不断完善绿色金融标准体系，引导更多资金投向绿色低碳领域，促进经济社会绿色转型。',
             '政策解读', '绿色金融委员会', '环境金融专家', (now - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 
             'https://picsum.photos/400/240?random=12', '绿色金融,碳中和,可持续发展', 1823)
        ]
        cursor.executemany('''
        INSERT IGNORE INTO News
        (title, summary, content, category, source, author, publish_time, image_url, tags, read_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', sample_news)
        print('✓ 示例资讯数据插入完成')
        
        # 插入初始AI建议数据
        print('插入AI建议数据...')
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
        print('✓ AI建议数据插入完成')

    conn.commit()
    print('''
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ✅ 数据库初始化完成！                                   ║
║                                                           ║
║   创建的表：                                             ║
║   • Users - 用户表                                        ║
║   • Fundings - 基金表                                     ║
║   • Bills - 账单表                                        ║
║   • TransferHistory - 转账历史表                         ║
║   • News - 资讯表                                         ║
║   • AISuggestions - AI建议表                             ║
║   • UserAIActions - 用户AI交互表                         ║
║                                                           ║
║   插入的数据：                                           ║
║   • 1个测试用户 (UTSZ/admin)                             ║
║   • 5条基金数据                                          ║
║   • 10条账单数据                                         ║
║   • 5条转账历史数据                                      ║
║   • 12条资讯数据                                         ║
║   • AI建议配置数据                                       ║
║                                                           ║
║   🚀 现在可以启动应用了！                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    ''')

except Exception as e:
    print(f'❌ 创建数据库和表失败: {e}')
    conn.rollback()
finally:
    conn.close()
    print('🔌 数据库连接已关闭')