import os
import pymysql
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = int(os.getenv('DB_PORT', '3306'))

def _connect_server():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, charset='utf8mb4')

def init_database():
    conn = _connect_server()
    try:
        with conn.cursor() as cursor:
            cursor.execute('CREATE DATABASE IF NOT EXISTS Fin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            cursor.execute('USE Fin')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id VARCHAR(50) PRIMARY KEY,
                password VARCHAR(50) NOT NULL,
                display_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS AISuggestions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                page_type VARCHAR(50) NOT NULL,
                suggestion_type VARCHAR(50) NOT NULL,
                content JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY page_type_suggestion_type (page_type, suggestion_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behavior_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id VARCHAR(64) NOT NULL UNIQUE,
                event_type VARCHAR(50) NOT NULL,
                user_id VARCHAR(50),
                session_id VARCHAR(100),
                page VARCHAR(50),
                page_url VARCHAR(255),
                referrer VARCHAR(255),
                element_type VARCHAR(50),
                element_id VARCHAR(100),
                element_text VARCHAR(200),
                element_class VARCHAR(200),
                business_data JSON,
                duration INT,
                scroll_depth INT,
                context_data JSON,
                timestamp BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_session_id (session_id),
                INDEX idx_event_type (event_type),
                INDEX idx_page (page),
                INDEX idx_timestamp (timestamp),
                INDEX idx_created_at (created_at),
                INDEX idx_user_event (user_id, event_type),
                INDEX idx_user_page (user_id, page)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserPositions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                position_type ENUM('fund', 'deposit', 'savings') NOT NULL,
                product_code VARCHAR(20) NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                shares DECIMAL(20, 4) DEFAULT 0,
                purchase_price DECIMAL(12, 4) DEFAULT 0,
                current_price DECIMAL(12, 4) DEFAULT 0,
                purchase_date DATE NOT NULL,
                current_value DECIMAL(20, 2) DEFAULT 0,
                total_investment DECIMAL(20, 2) DEFAULT 0,
                profit_loss DECIMAL(20, 2) DEFAULT 0,
                profit_loss_percent DECIMAL(8, 4) DEFAULT 0,
                status ENUM('active', 'frozen', 'liquidated') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_type (user_id, position_type),
                INDEX idx_product (product_code),
                INDEX idx_purchase_date (purchase_date),
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            cursor.execute('''
            CREATE OR REPLACE VIEW v_user_portfolio_summary AS
            SELECT 
                up.user_id,
                up.position_type,
                COUNT(*) as position_count,
                SUM(up.current_value) as total_value,
                SUM(up.total_investment) as total_investment,
                SUM(up.profit_loss) as total_profit_loss,
                CASE 
                    WHEN SUM(up.total_investment) > 0 THEN 
                        ROUND((SUM(up.profit_loss) / SUM(up.total_investment)) * 100, 2)
                    ELSE 0 
                END as total_profit_loss_percent,
                SUM(CASE WHEN up.profit_loss > 0 THEN up.profit_loss ELSE 0 END) as total_profit,
                SUM(CASE WHEN up.profit_loss < 0 THEN ABS(up.profit_loss) ELSE 0 END) as total_loss
            FROM UserPositions up
            WHERE up.status = 'active'
            GROUP BY up.user_id, up.position_type
            ''')

            try:
                cursor.execute("SET GLOBAL event_scheduler = ON")
                cursor.execute('''
                CREATE EVENT IF NOT EXISTS cleanup_old_behavior_logs
                ON SCHEDULE EVERY 1 DAY
                STARTS CURRENT_TIMESTAMP
                DO
                DELETE FROM user_behavior_logs 
                WHERE created_at < DATE_SUB(NOW(), INTERVAL 7 DAY)
                ''')
                cursor.execute('''
                CREATE PROCEDURE IF NOT EXISTS sp_cleanup_behavior_logs(IN days INT)
                BEGIN
                    DELETE FROM user_behavior_logs 
                    WHERE created_at < DATE_SUB(NOW(), INTERVAL days DAY);
                    SELECT ROW_COUNT() AS deleted_rows;
                END
                ''')
            except Exception:
                pass

            cursor.execute("""
            INSERT IGNORE INTO Users (user_id, password, display_name)
            VALUES ('UTSZ', 'admin', 'UTSZ用户')
            """)

            fund_data = [
                ('005827', '易方达蓝筹精选混合', 2.8745, '2.13%', '+0.0598', '混合型', '中高风险', '张坤'),
                ('320007', '诺安成长混合', 1.7654, '-1.24%', '-0.0222', '混合型', '高风险', '蔡嵩松'),
                ('002001', '华夏回报混合A', 3.2456, '0.89%', '+0.0288', '混合型', '中风险', '王宗合'),
                ('161005', '富国天惠成长混合A', 4.5678, '1.56%', '+0.0695', '混合型', '中高风险', '朱少醒'),
                ('163406', '兴全合润混合', 3.8923, '1.23%', '+0.0473', '混合型', '中高风险', '谢治宇')
            ]
            cursor.executemany("""
            INSERT IGNORE INTO Fundings (code, name, nav, change_percent, fund_change, category, risk, manager)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, fund_data)

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
            cursor.executemany("""
            INSERT IGNORE INTO Bills 
            (user_id, merchant, category, amount, transaction_date, transaction_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, sample_bills)

            sample_transfers = [
                ('UTSZ', '6222123456781234', '张三', 1000.00, '2023-10-15', '14:20:00'),
                ('UTSZ', '6222123456785678', '李四', 500.00, '2023-10-10', '10:35:00'),
                ('UTSZ', '6222123456789012', '王五', 2000.00, '2023-10-05', '16:45:00'),
                ('UTSZ', '6222123456781234', '张三', 800.00, '2023-09-28', '15:10:00'),
                ('UTSZ', '6222123456785678', '李四', 1500.00, '2023-09-20', '11:20:00')
            ]
            cursor.executemany("""
            INSERT IGNORE INTO TransferHistory
            (user_id, recipient_account, recipient_name, amount, transfer_date, transfer_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, sample_transfers)

            now = datetime.now()

            news_items = [
                (
                    '快4.5亿倍！量子计算，有新消息',
                    '“天衍-287”超导量子计算机完成搭建，具备量子计算优越性，特定任务较超算快4.5亿倍。',
                    """
据科技日报，11月14日，中国电信量子研究院发布消息，搭载“祖冲之三号”同款芯片的超导量子计算机“天衍-287”完成搭建。据介绍，其拥有105个数据比特和182个耦合比特，由中电信量子集团与科大国盾量子技术股份有限公司联合团队搭建和调测完成。

据悉，该量子计算系统具备“量子计算优越性”能力，处理特定问题的速度比目前最快的超级计算机快4.5亿倍，未来将接入“天衍”量子计算云平台并首次面向全球开放应用服务，标志着我国在推动量子计算实用化道路上迈出重要一步。

中电信量子集团量子计算高级研究员、测控团队负责人张鑫方介绍，此次搭建过程体现出“全国产”“AI赋能”“超量融合”三个方面技术突破。首先，搭建过程使用了全国产的超导量子计算机硬件设备和元器件，大容量稀释制冷机、测控电子学、低温元器件等关键部件全部由国内厂商研发生产，中国电信牵头国内生态厂商构建了全国产化的超导量子计算供应链体系；其次，团队自主研发了AI赋能的超导芯片参数自动校准系统，在人工智能技术赋能下，成功实现量子计算系统的高效、高精度自动校准与维护；最后，通过将这台超导量子计算机与“天翼云”超算集中部署，基于硬件直连达成高带宽的量超融合，实现量子计算和超算的低延时交互，助力算力资源的协同调度，构建“硬件—软件—云平台—生态”的全国产化量子计算全栈式工具体系。

2023年11月，中电信量子集团正式发布“天衍”量子计算云平台，实现天翼云超算能力和176量子比特超导量子计算能力的融合。目前，“天衍”量子计算云平台现访问量已突破3700万，覆盖海内外60多个国家的用户，实验任务数超过270万。
""",
                    '行业新闻', '财联社', '科技记者', (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
                    '/assets/news/News1/1.jpg', '量子计算,超导,中国电信', 0
                ),
                (
                    '10月新能源新车降价幅度超11%',
                    '新能源车10月降价力度达11.1%，纯电与插混降幅扩大，头部车企带动价格下探。',
                    """
“2025年10月份，新能源车新车降价车型的降价力度算术平均达到1.8万元，降价力度达到11.1%。”这是乘联分会秘书长崔东树近日在分析文章中透露出的一组数据。

根据崔东树的统计，今年1~10月份，新能源车新车降价车型的降价力度算术平均达到2.1万元，降价力度达到10.8%。

第一财经记者梳理发现，从纵向对比来看，这样的降价力度，仅次于2022年（13.2%）。而从今年情况来看，10月份的降价力度也超过了9月（9.8%）。

从2025年的前十月整体情况来看，新能源车的降价力度也高于整体市场。今年前十月，常规燃油车新车降价车型的降价力度算术平均达到1.4万元，降价力度达到8.4%；总体乘用车市场新车降价车型的降价力度算术平均达到1.9万元，降价力度达到10.3%。

促销力度方面，今年10月的新能源车的促销下降到9.8%的中高位，较上月微降0.4个百分点，但和去年同期相比仍然高出2.2个百分点。

此外，根据乘联分会的统计，在今年10月降价规模14款车中，纯电动车型6款，较去年同期增加了4款。纯电动车型新车降价后的均价是13.8万元，降价幅度达到1.2万元，新车降价力度达到8%。

而从细分车型来看，无论是纯电动还是插混，国央企的新车降价动作都幅度更大。

纯电动车方面，降价幅度最大的是红旗EQM纯电动车型，10月发布的最低指导价为89800元，近两年的最低价为121800元，降价幅度达到36%。东风奕派的纳米01纯电动、昊铂GT纯电动的降价幅度分别为10%和13%。懂车帝数据显示，今年1~10月，昊铂GT总销量仅有1466辆。

崔东树认为，今年10月的纯电动的降价规模总体很大，尤其是部分车型指导价的下探的降价达到10%以上，根据竞品调整，其价格下探的力度惊人。

插混车方面，新车降价后的均价是21.8万元，降价幅度达到4.2万元，新车降价力度达到19%。这主要是由于广汽传祺向往M8和长城高山的带动，这两款插混车分别降了6万元和6.4万元，降价幅度都在22%。崔东树认为，由于头部领军企业的价格很有竞争力，对应竞品需要大力调整，这样的降价是必然的趋势。

降价促销的背后，中国车企仍然需要重视盈利能力。
""",
                    '行业新闻', '第一财经', '葛慧', (now - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                    '/assets/news/News2/1.jpg', '新能源,降价,乘联会', 0
                ),
                (
                    '预言AI泡沫，机构抛售微软、英伟达、亚马逊等科技股',
                    '桥水、花旗等机构减持科技股，市场争论AI泡沫与长期潜力并存。',
                    """
北京时间11月11日，软银集团清仓英伟达股份，套现58.3亿美元，引起了市场上关于AI泡沫可能破裂的担忧。但抛售还没结束。

华尔街最大的对冲基金桥水周五公布截至今年三季度末的持仓报告。报告显示，桥水在三季度大幅减持芯片巨头英伟达，减持比例近三分之二，桥水还减持了过半的Alphabet股票、约9.6%的亚马逊股票、超35%的微软股票。在给投资者的一份报告中，桥水首席投资官Karen Karniol-Tambour等人警告称，当前的市场稳定性正面临越来越高风险。

此外，花旗最新披露的美股持仓报告显示，该机构第三季度也减持了英伟达、微软、苹果以及亚马逊这四大美国科技巨头。不过，花旗近日将英伟达目标价从每股210美元上调至220美元。

最近几周，关于AI泡沫的讨论趋于激烈。一些公司的负责人警告称，股市可能走向下跌。例如，AI公司DeepL CEO Jarek Kutylowski表示，很多市场评估都相当夸张，有迹象表明泡沫即将出现。Picsart的CEO Hovhannes Avoyan则表示，能看到很多AI公司在没有很多收入的情况下获得极高估值，这令人担忧。

知名“大空头”Michael Burry表达了对AI基础设施建设热潮的担忧，他表示，主要的人工智能基础设施和云服务提供商低估了芯片的折旧费用，像甲骨文这样的公司利润可能被严重高估，他最近还在做空Meta、英伟达。投资机构Novo Capital管理合伙人Ben Harburg则表示，大型科技公司正在讨论的投资数额可能被夸大，而数据中心建设可能已过度繁荣。

也有观点认为，抛售英伟达股票不一定意味着对英伟达不再看好，且抛售时间点不一定明智。软银清仓英伟达股票主要是为了资助其押注的人工智能项目。市场分析认为软银需要这些资金来做一些布局，包括联手OpenAI、甲骨文发起的“星际之门”项目需要大规模建设数据中心集群，软银还计划对OpenAI投资400亿美元，也在押注芯片赛道。
""",
                    '行业新闻', '第一财经', '郑栩彤', (now - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
                    '/assets/news/News3/1.jpg', 'AI,英伟达,微软,抛售', 0
                ),
                (
                    '20%涨停！医药股，爆发！',
                    'A股医药生物板块多股涨停，房地产与银行分化，港股氢能概念大涨。',
                    """
A股市场今天上午整体低位震荡，主要股指走低。盘面上，房地产板块逆势走强，荣盛发展、盈新发展、华夏幸福等多股涨停；医药股爆发，漱玉平民、康芝药业、海辰药业、金迪克20%涨停。此外，银行板块上午表现也较好。

港股市场今天上午也整体走低，多只港股科技股领跌。值得注意的是，多只和氢能相关的股票大幅上涨，其中重塑能源盘中一度大涨超过60%。

截至中午收盘，上证指数下跌0.16%，深证成指下跌1.10%，创业板指下跌1.74%。电子、通信、有色金属等板块跌幅居前。医药生物板块表现活跃，多只个股涨停。
""",
                    '市场行情', '证券时报', '胡华雄', (now - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
                    '/assets/news/News4/1.jpg', '医药,涨停,A股,港股,氢能', 0
                ),
                (
                    '习近平：因地制宜发展新质生产力',
                    '强调科技创新引领产业升级，因地制宜培育新兴与未来产业，推进绿色低碳发展。',
                    """
要以科技创新引领产业全面振兴。要立足现有产业基础，扎实推进先进制造业高质量发展，加快推动传统制造业升级，发挥科技创新的增量器作用。

新质生产力是创新起主导作用，具有高科技、高效能、高质量特征，符合新发展理念的先进生产力质态。它由技术革命性突破、生产要素创新性配置、产业深度转型升级而催生。

要加强科技创新特别是原创性、颠覆性科技创新，加快实现高水平科技自立自强。要以关键共性技术、前沿引领技术、现代工程技术、颠覆性技术创新为突破口，打好关键核心技术攻坚战。

绿色发展是高质量发展的底色，新质生产力本身就是绿色生产力。要加快绿色科技创新和先进绿色技术推广应用，做强绿色制造业，壮大绿色能源产业，构建绿色低碳循环经济体系。

要牢牢把握高质量发展这个首要任务，因地制宜加快发展新质生产力。要根据本地的资源禀赋、产业基础、科研条件等，有选择地推动新产业、新模式、新动能发展，用新技术改造提升传统产业。
""",
                    '政策解读', '新华社', '记者', (now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
                    '/assets/news/News5/1.jpg', '新质生产力,科技创新,绿色发展', 0
                )
            ]
            cursor.executemany("""
            INSERT IGNORE INTO News
            (title, summary, content, category, source, author, publish_time, image_url, tags, read_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, news_items)

            sample_positions = [
                ('UTSZ', 'fund', '005827', '易方达蓝筹精选混合', 1000.0000, 2.5000, 2.8745, '2023-08-15', 2874.50, 2500.00, 374.50, 14.98),
                ('UTSZ', 'fund', '320007', '诺安成长混合', 500.0000, 1.8000, 1.7654, '2023-09-01', 882.70, 900.00, -17.30, -1.92),
                ('UTSZ', 'fund', '002001', '华夏回报混合A', 300.0000, 3.0000, 3.2456, '2023-07-20', 973.68, 900.00, 73.68, 8.19),
                ('UTSZ', 'deposit', 'D001', '定期存款-3个月', 50000.0000, 1.0000, 1.0000, '2023-10-01', 50000.00, 50000.00, 0.00, 0.00),
                ('UTSZ', 'deposit', 'D002', '大额存单-1年', 200000.0000, 1.0000, 1.0000, '2023-06-15', 200000.00, 200000.00, 0.00, 0.00),
                ('UTSZ', 'savings', 'S001', '活期储蓄', 28563.4500, 1.0000, 1.0000, '2023-01-01', 28563.45, 28563.45, 0.00, 0.00)
            ]
            cursor.executemany("""
            INSERT IGNORE INTO UserPositions 
            (user_id, position_type, product_code, product_name, shares, purchase_price, current_price, purchase_date, 
             current_value, total_investment, profit_loss, profit_loss_percent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, sample_positions)

        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    pass