import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_db_connection():
    """创建并返回数据库连接对象
    自动读取环境变量配置，使用DictCursor以便返回字典格式结果
    """
    try:
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'Fin'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            cursorclass=DictCursor,
            charset='utf8mb4',
            connect_timeout=10
        )
        return conn
    except pymysql.MySQLError as e:
        print(f"数据库连接失败: {str(e)}")
        raise

def close_db_connection(conn):
    """安全关闭数据库连接
    忽略已关闭连接的异常
    """
    if conn:
        try:
            if not conn._closed:
                conn.close()
        except pymysql.MySQLError:
            pass

def db_query(sql, params=None, fetch_one=False):
    """执行查询并自动处理连接
    Args:
        sql: SQL查询语句
        params: 查询参数
        fetch_one: 是否只返回单条结果
    Returns:
        查询结果列表或单条结果
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    finally:
        close_db_connection(conn)

def db_execute(sql, params=None):
    """执行写操作(INSERT/UPDATE/DELETE)并自动提交
    Returns:
        影响行数
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            affected_rows = cursor.execute(sql, params or ())
            conn.commit()
            return affected_rows
    except pymysql.MySQLError as e:
        if conn:
            conn.rollback()
        raise
    finally:
        close_db_connection(conn)