"""快速测试数据库连接"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("测试 Railway 数据库连接")
print("=" * 60)

host = os.getenv('MYSQL_HOST')
port = os.getenv('MYSQL_PORT', '3306')
user = os.getenv('MYSQL_USER')
database = os.getenv('MYSQL_DATABASE')
password = os.getenv('MYSQL_PASSWORD', '')

print(f"\n配置信息:")
print(f"  Host: {host}")
print(f"  Port: {port}")
print(f"  User: {user}")
print(f"  Database: {database}")
print(f"  Password: {'*' * len(password) if password else '(empty)'}")

if not all([host, port, user, password, database]):
    print("\n[ERROR] 缺少必需的配置！")
    exit(1)

print(f"\n正在连接到 {host}:{port}...")

try:
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port),
        connect_timeout=10,
        charset='utf8mb4'
    )
    
    print("[SUCCESS] 连接成功！\n")
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MySQL 版本: {version[0]}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"数据库表数: {len(tables)}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("[OK] Railway 数据库配置正确！")
    print("=" * 60)
    
    if len(tables) == 0:
        print("\n下一步: python init_db.py")
    else:
        print("\n下一步: python app.py")
    
except Exception as e:
    print(f"\n[FAILED] 连接失败: {e}")
    print("\n请检查:")
    print("1. Railway 是否已启用公网访问")
    print("2. .env 中的地址是否为公网地址")
    print("3. 端口号是否正确")
    exit(1)

