"""
扩展Users表，添加用户详细资料字段
"""

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def extend_users_table():
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
            # 逐个添加字段（避免IF NOT EXISTS语法问题）
            columns_to_add = [
                ("real_name", "VARCHAR(50)", "真实姓名"),
                ("id_card", "VARCHAR(18)", "身份证号"),
                ("phone", "VARCHAR(11)", "手机号"),
                ("city", "VARCHAR(50)", "城市"),
                ("occupation", "VARCHAR(50)", "职业"),
                ("risk_score", "DECIMAL(4,2)", "风险评分"),
                ("risk_level", "VARCHAR(20)", "风险等级"),
                ("investment_purposes", "TEXT", "投资目的"),
            ]
            
            for col_name, col_type, comment in columns_to_add:
                try:
                    alter_sql = f"ALTER TABLE Users ADD COLUMN {col_name} {col_type} COMMENT '{comment}'"
                    cursor.execute(alter_sql)
                    print(f"[OK] 添加字段: {col_name}")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print(f"[INFO] 字段已存在: {col_name}")
                    else:
                        print(f"[WARN] 添加{col_name}失败: {str(e)}")
            
        conn.commit()
        print("[SUCCESS] 数据库扩展完成")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 错误: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("开始扩展Users表...")
    extend_users_table()

