"""
数据库连接测试脚本
用于验证 Railway MySQL 数据库连接是否正常
"""

import pymysql
from dotenv import load_dotenv
import os
import sys

# 加载环境变量
load_dotenv()

def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("Railway MySQL 数据库连接测试")
    print("=" * 60)
    
    # 获取环境变量
    host = os.getenv('MYSQL_HOST')
    port = int(os.getenv('MYSQL_PORT', 3306))
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    database = os.getenv('MYSQL_DATABASE')
    
    # 显示连接信息（隐藏密码）
    print(f"\n连接信息:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  User: {user}")
    print(f"  Password: {'*' * len(password) if password else 'None'}")
    print(f"  Database: {database}")
    print()
    
    # 检查必需的环境变量
    if not all([host, user, password, database]):
        print("❌ 错误: 缺少必需的环境变量")
        print("请确保 .env 文件包含以下变量:")
        print("  - MYSQL_HOST")
        print("  - MYSQL_PORT")
        print("  - MYSQL_USER")
        print("  - MYSQL_PASSWORD")
        print("  - MYSQL_DATABASE")
        return False
    
    try:
        print("正在连接数据库...")
        
        # 尝试连接
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ 数据库连接成功!")
        
        # 测试查询
        with conn.cursor() as cursor:
            # 获取数据库版本
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"\n数据库版本: {version}")
            
            # 获取所有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"\n数据库中的表 ({len(tables)} 个):")
                for table in tables:
                    table_name = table[0]
                    
                    # 获取表的行数
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    count = cursor.fetchone()[0]
                    
                    print(f"  - {table_name}: {count} 行")
            else:
                print("\n⚠️  数据库中没有表")
                print("请运行 'python init_db.py' 初始化数据库")
        
        conn.close()
        print("\n" + "=" * 60)
        print("✅ 测试完成 - 数据库连接正常")
        print("=" * 60)
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ 数据库连接失败!")
        print(f"错误信息: {str(e)}")
        print("\n可能的原因:")
        print("  1. Railway MySQL 服务未启动")
        print("  2. 连接信息不正确")
        print("  3. 网络连接问题")
        print("  4. 防火墙阻止连接")
        print("\n解决方案:")
        print("  1. 检查 Railway 控制台，确认 MySQL 服务状态为 Active")
        print("  2. 验证 .env 文件中的连接信息")
        print("  3. 确保已启用 TCP Proxy (Settings → Networking)")
        print("=" * 60)
        return False
        
    except Exception as e:
        print(f"\n❌ 未知错误: {str(e)}")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
