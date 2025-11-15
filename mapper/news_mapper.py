"""
资讯数据访问层（Mapper）
负责资讯数据的数据库操作
"""

from utils.db import get_db_connection


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
        with conn.cursor() as cursor:
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
                    'id': row[0],
                    'title': row[1],
                    'summary': row[2],
                    'content': row[3],
                    'category': row[4],
                    'source': row[5],
                    'author': row[6],
                    'publish_time': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
                    'image_url': row[8],
                    'tags': row[9],
                    'read_count': row[10],
                    'created_at': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else None
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
        with conn.cursor() as cursor:
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
                    'id': row[0],
                    'title': row[1],
                    'summary': row[2],
                    'content': row[3],
                    'category': row[4],
                    'source': row[5],
                    'author': row[6],
                    'publish_time': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
                    'image_url': row[8],
                    'tags': row[9],
                    'read_count': row[10],
                    'created_at': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else None
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
        with conn.cursor() as cursor:
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
                    'id': row[0],
                    'title': row[1],
                    'summary': row[2],
                    'content': row[3],
                    'category': row[4],
                    'source': row[5],
                    'author': row[6],
                    'publish_time': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
                    'image_url': row[8],
                    'tags': row[9],
                    'read_count': row[10],
                    'created_at': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else None
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
        with conn.cursor() as cursor:
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
                    'id': row[0],
                    'title': row[1],
                    'summary': row[2],
                    'content': row[3],
                    'category': row[4],
                    'source': row[5],
                    'author': row[6],
                    'publish_time': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
                    'image_url': row[8],
                    'tags': row[9],
                    'read_count': row[10],
                    'created_at': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else None
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
        with conn.cursor() as cursor:
            if category:
                sql = 'SELECT COUNT(*) FROM News WHERE category = %s'
                cursor.execute(sql, [category])
            else:
                sql = 'SELECT COUNT(*) FROM News'
                cursor.execute(sql)
            
            result = cursor.fetchone()
            return result[0] if result else 0
    finally:
        conn.close()

