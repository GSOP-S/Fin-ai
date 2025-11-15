"""
资讯数据访问层（Mapper）
负责资讯数据的数据库操作
"""

from utils.db import get_db_connection
from pymysql.cursors import DictCursor


def get_all_news(category=None, limit=None, offset=0):
    """
    获取资讯列表
    
    Args:
        category: 分类筛选（可选）
        limit: 返回数量限制（可选）
        offset: 偏移量
    
    Returns:
        list: 资讯列表
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor=DictCursor) as cursor:
            if category:
                sql = '''
                SELECT id, title, summary, content, category, source, author, 
                       publish_time, image_url, tags, read_count, created_at
                FROM News 
                WHERE category = %s
                ORDER BY publish_time DESC
                '''
                params = [category]
            else:
                sql = '''
                SELECT id, title, summary, content, category, source, author, 
                       publish_time, image_url, tags, read_count, created_at
                FROM News 
                ORDER BY publish_time DESC
                '''
                params = []
            
            # 添加分页
            if limit:
                sql += ' LIMIT %s OFFSET %s'
                params.extend([limit, offset])
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            news_list = []
            for row in results:
                news_list.append({
                    'id': row['id'],
                    'title': row['title'],
                    'summary': row['summary'],
                    'content': row['content'],
                    'category': row['category'],
                    'source': row['source'],
                    'author': row['author'],
                    'publish_time': row['publish_time'].strftime('%Y-%m-%d %H:%M:%S') if row['publish_time'] else None,
                    'image_url': row['image_url'],
                    'tags': row['tags'],
                    'read_count': row['read_count'],
                    'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else None
                })
            
            return news_list
    finally:
        conn.close()


def get_news_by_id(news_id):
    """
    根据ID获取资讯详情
    
    Args:
        news_id: 资讯ID
    
    Returns:
        dict: 资讯详情，不存在返回None
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor=DictCursor) as cursor:
            sql = '''
            SELECT id, title, summary, content, category, source, author, 
                   publish_time, image_url, tags, read_count, created_at
            FROM News 
            WHERE id = %s
            '''
            cursor.execute(sql, [news_id])
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'title': row['title'],
                    'summary': row['summary'],
                    'content': row['content'],
                    'category': row['category'],
                    'source': row['source'],
                    'author': row['author'],
                    'publish_time': row['publish_time'].strftime('%Y-%m-%d %H:%M:%S') if row['publish_time'] else None,
                    'image_url': row['image_url'],
                    'tags': row['tags'],
                    'read_count': row['read_count'],
                    'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else None
                }
            return None
    finally:
        conn.close()


def search_news(keyword):
    """
    搜索资讯
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        list: 匹配的资讯列表
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor=DictCursor) as cursor:
            sql = '''
            SELECT id, title, summary, content, category, source, author, 
                   publish_time, image_url, tags, read_count, created_at
            FROM News 
            WHERE title LIKE %s OR summary LIKE %s OR content LIKE %s
            ORDER BY publish_time DESC
            '''
            search_pattern = f'%{keyword}%'
            cursor.execute(sql, [search_pattern, search_pattern, search_pattern])
            results = cursor.fetchall()
            
            news_list = []
            for row in results:
                news_list.append({
                    'id': row['id'],
                    'title': row['title'],
                    'summary': row['summary'],
                    'content': row['content'],
                    'category': row['category'],
                    'source': row['source'],
                    'author': row['author'],
                    'publish_time': row['publish_time'].strftime('%Y-%m-%d %H:%M:%S') if row['publish_time'] else None,
                    'image_url': row['image_url'],
                    'tags': row['tags'],
                    'read_count': row['read_count'],
                    'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else None
                })
            
            return news_list
    finally:
        conn.close()


def get_hot_news(limit=10):
    """
    获取热门资讯（按阅读量排序）
    
    Args:
        limit: 返回数量
    
    Returns:
        list: 热门资讯列表
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor=DictCursor) as cursor:
            sql = '''
            SELECT id, title, summary, content, category, source, author, 
                   publish_time, image_url, tags, read_count, created_at
            FROM News 
            ORDER BY read_count DESC, publish_time DESC
            LIMIT %s
            '''
            cursor.execute(sql, [limit])
            results = cursor.fetchall()
            
            news_list = []
            for row in results:
                news_list.append({
                    'id': row['id'],
                    'title': row['title'],
                    'summary': row['summary'],
                    'content': row['content'],
                    'category': row['category'],
                    'source': row['source'],
                    'author': row['author'],
                    'publish_time': row['publish_time'].strftime('%Y-%m-%d %H:%M:%S') if row['publish_time'] else None,
                    'image_url': row['image_url'],
                    'tags': row['tags'],
                    'read_count': row['read_count'],
                    'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else None
                })
            
            return news_list
    finally:
        conn.close()


def increase_read_count(news_id):
    """
    增加资讯阅读量
    
    Args:
        news_id: 资讯ID
    
    Returns:
        bool: 是否成功
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = 'UPDATE News SET read_count = read_count + 1 WHERE id = %s'
            cursor.execute(sql, [news_id])
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_news_count(category=None):
    """
    获取资讯总数
    
    Args:
        category: 分类筛选（可选）
    
    Returns:
        int: 资讯总数
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor=DictCursor) as cursor:
            if category:
                sql = 'SELECT COUNT(*) as count FROM News WHERE category = %s'
                cursor.execute(sql, [category])
            else:
                sql = 'SELECT COUNT(*) as count FROM News'
                cursor.execute(sql)
            
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()


def insert_news_item(title, summary, content, category, source, author, publish_time, image_url=None, tags=None, read_count=0):
    """
    插入一条资讯记录（若标题已存在则忽略）
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 检查是否已存在同标题记录
            check_sql = 'SELECT id FROM News WHERE title = %s LIMIT 1'
            cursor.execute(check_sql, [title])
            exists = cursor.fetchone()
            if exists:
                return exists[0]

            insert_sql = '''
            INSERT INTO News (title, summary, content, category, source, author, publish_time, image_url, tags, read_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_sql, [title, summary, content, category, source, author, publish_time, image_url, tags, read_count])
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

