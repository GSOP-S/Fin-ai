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

        # 创建用户持仓表
        print('创建UserPositions表（用户持仓表）...')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserPositions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            position_type ENUM('fund', 'deposit', 'savings') NOT NULL COMMENT '持仓类型：fund-基金, deposit-存款, savings-储蓄',
            product_code VARCHAR(20) NOT NULL COMMENT '产品代码（基金代码、存款类型等）',
            product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
            shares DECIMAL(20, 4) DEFAULT 0 COMMENT '持有份额/金额',
            purchase_price DECIMAL(12, 4) DEFAULT 0 COMMENT '买入价格',
            current_price DECIMAL(12, 4) DEFAULT 0 COMMENT '当前价格',
            purchase_date DATE NOT NULL COMMENT '买入日期',
            current_value DECIMAL(20, 2) DEFAULT 0 COMMENT '当前市值',
            total_investment DECIMAL(20, 2) DEFAULT 0 COMMENT '总投资金额',
            profit_loss DECIMAL(20, 2) DEFAULT 0 COMMENT '盈亏金额',
            profit_loss_percent DECIMAL(8, 4) DEFAULT 0 COMMENT '盈亏百分比',
            status ENUM('active', 'frozen', 'liquidated') DEFAULT 'active' COMMENT '持仓状态',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_type (user_id, position_type),
            INDEX idx_product (product_code),
            INDEX idx_purchase_date (purchase_date),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print('✓ UserPositions表创建成功')

        # 为测试用户插入示例持仓数据
        print('插入示例持仓数据...')
        sample_positions = [
            # 基金持仓
            ('UTSZ', 'fund', '005827', '易方达蓝筹精选混合', 1000.0000, 2.5000, 2.8745, '2023-08-15', 2874.50, 2500.00, 374.50, 14.98),
            ('UTSZ', 'fund', '320007', '诺安成长混合', 500.0000, 1.8000, 1.7654, '2023-09-01', 882.70, 900.00, -17.30, -1.92),
            ('UTSZ', 'fund', '002001', '华夏回报混合A', 300.0000, 3.0000, 3.2456, '2023-07-20', 973.68, 900.00, 73.68, 8.19),
            
            # 存款持仓
            ('UTSZ', 'deposit', 'D001', '定期存款-3个月', 50000.0000, 1.0000, 1.0000, '2023-10-01', 50000.00, 50000.00, 0.00, 0.00),
            ('UTSZ', 'deposit', 'D002', '大额存单-1年', 200000.0000, 1.0000, 1.0000, '2023-06-15', 200000.00, 200000.00, 0.00, 0.00),
            
            # 储蓄持仓
            ('UTSZ', 'savings', 'S001', '活期储蓄', 28563.4500, 1.0000, 1.0000, '2023-01-01', 28563.45, 28563.45, 0.00, 0.00),
        ]
        cursor.executemany('''
        INSERT INTO UserPositions 
        (user_id, position_type, product_code, product_name, shares, purchase_price, current_price, purchase_date, 
         current_value, total_investment, profit_loss, profit_loss_percent)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', sample_positions)
        print('✓ 示例持仓数据插入完成')

        # 创建视图：用户持仓汇总
        print('创建用户持仓汇总视图...')
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
        print('✓ 用户持仓汇总视图创建成功')

    conn.commit()
    print('''
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ✅ 用户持仓表初始化完成！                               ║
║                                                           ║
║   创建的表：                                             ║
║   • UserPositions - 用户持仓表                            ║
║                                                           ║
║   创建的视图：                                           ║
║   • v_user_portfolio_summary - 用户持仓汇总视图          ║
║                                                           ║
║   插入的示例数据：                                       ║
║   • 3条基金持仓记录                                      ║
║   • 2条存款记录                                         ║
║   • 1条储蓄记录                                         ║
║                                                           ║
║   数据特点：                                             ║
║   • 支持基金、存款、储蓄等多种持仓类型                   ║
║   • 记录买入日期、份额、价格等详细信息                   ║
║   • 自动计算当前市值、盈亏情况                           ║
║   • 支持持仓状态管理（正常、冻结、已清算）               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    ''')

except Exception as e:
    print(f'❌ 创建用户持仓表失败: {e}')
    conn.rollback()
finally:
    conn.close()
    print('🔌 数据库连接已关闭')