"""
初始化用户行为日志表
创建 user_behavior_logs 表，并设置7天自动清理机制
"""

import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_behavior_logs_table():
    """创建用户行为日志表"""
    
    # 连接数据库
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'Fin'),
        port=int(os.getenv('DB_PORT', '3306')),
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor() as cursor:
            # 创建用户行为日志表
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_behavior_logs (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
                event_id VARCHAR(64) NOT NULL UNIQUE COMMENT '事件唯一ID',
                event_type VARCHAR(50) NOT NULL COMMENT '事件类型',
                
                -- 用户信息
                user_id VARCHAR(50) COMMENT '用户ID',
                session_id VARCHAR(100) COMMENT '会话ID',
                
                -- 页面信息
                page VARCHAR(50) COMMENT '当前页面',
                page_url VARCHAR(255) COMMENT '页面URL',
                referrer VARCHAR(255) COMMENT '来源页面',
                
                -- 元素信息
                element_type VARCHAR(50) COMMENT '元素类型',
                element_id VARCHAR(100) COMMENT '元素ID',
                element_text VARCHAR(200) COMMENT '元素文本',
                element_class VARCHAR(200) COMMENT '元素class',
                
                -- 业务数据 (JSON格式，灵活存储)
                business_data JSON COMMENT '业务上下文数据',
                
                -- 行为数据
                duration INT COMMENT '持续时长(ms)',
                scroll_depth INT COMMENT '滚动深度(%)',
                
                -- 上下文信息 (JSON格式)
                context_data JSON COMMENT '设备和环境信息',
                
                -- 时间戳
                timestamp BIGINT NOT NULL COMMENT '事件时间戳(ms)',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                
                -- 索引
                INDEX idx_user_id (user_id),
                INDEX idx_session_id (session_id),
                INDEX idx_event_type (event_type),
                INDEX idx_page (page),
                INDEX idx_timestamp (timestamp),
                INDEX idx_created_at (created_at),
                INDEX idx_user_event (user_id, event_type),
                INDEX idx_user_page (user_id, page)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户行为日志表';
            """
            
            cursor.execute(create_table_sql)
            print("[OK] 用户行为日志表创建成功")
            
            # 创建自动清理旧数据的事件（7天）
            # 首先启用事件调度器
            cursor.execute("SET GLOBAL event_scheduler = ON;")
            print("[OK] 启用MySQL事件调度器")
            
            # 创建定时清理事件
            create_event_sql = """
            CREATE EVENT IF NOT EXISTS cleanup_old_behavior_logs
            ON SCHEDULE EVERY 1 DAY
            STARTS CURRENT_TIMESTAMP
            DO
            DELETE FROM user_behavior_logs 
            WHERE created_at < DATE_SUB(NOW(), INTERVAL 7 DAY);
            """
            
            cursor.execute(create_event_sql)
            print("[OK] 自动清理事件创建成功（每天清理7天前的数据）")
            
            # 创建手动清理存储过程
            create_procedure_sql = """
            CREATE PROCEDURE IF NOT EXISTS sp_cleanup_behavior_logs(IN days INT)
            BEGIN
                DELETE FROM user_behavior_logs 
                WHERE created_at < DATE_SUB(NOW(), INTERVAL days DAY);
                SELECT ROW_COUNT() AS deleted_rows;
            END;
            """
            
            cursor.execute(create_procedure_sql)
            print("[OK] 手动清理存储过程创建成功")
            
        conn.commit()
        print("\n[SUCCESS] 数据库初始化完成！")
        print("\n[INFO] 表结构说明：")
        print("  - 表名：user_behavior_logs")
        print("  - 保留期：7天（自动清理）")
        print("  - 预计容量：10万条/天 x 7天 = 70万条")
        print("  - 索引：已优化查询性能")
        print("\n[INFO] 手动清理方法：")
        print("  CALL sp_cleanup_behavior_logs(7);  -- 清理7天前的数据")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 错误: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("开始初始化用户行为日志表...")
    create_behavior_logs_table()

