"""
资讯业务逻辑层（Service）
处理资讯相关的业务逻辑
"""

from mapper.news_mapper import (
    get_all_news,
    get_news_by_id,
    search_news as mapper_search_news,
    get_hot_news as mapper_get_hot_news,
    increase_read_count as mapper_increase_read_count,
    get_news_count
)


def get_news_list(category=None, page=1, page_size=20):
    """
    获取资讯列表（支持分页）
    
    Args:
        category: 分类筛选（可选）
        page: 页码（从1开始）
        page_size: 每页数量
    
    Returns:
        dict: 包含资讯列表和分页信息
    """
    try:
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取资讯列表
        news_list = get_all_news(category=category, limit=page_size, offset=offset)
        
        # 获取总数
        total = get_news_count(category=category)
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return {
            'list': news_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages
            }
        }
    except Exception as e:
        print(f'获取资讯列表失败: {e}')
        return {
            'list': [],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': 0,
                'total_pages': 0
            }
        }


def get_news_detail(news_id):
    """
    获取资讯详情
    
    Args:
        news_id: 资讯ID
    
    Returns:
        dict: 资讯详情，不存在返回None
    """
    try:
        return get_news_by_id(news_id)
    except Exception as e:
        print(f'获取资讯详情失败: {e}')
        return None


def search_news(keyword):
    """
    搜索资讯
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        list: 匹配的资讯列表
    """
    try:
        if not keyword or not keyword.strip():
            return []
        
        return mapper_search_news(keyword.strip())
    except Exception as e:
        print(f'搜索资讯失败: {e}')
        return []


def get_hot_news(limit=10):
    """
    获取热门资讯
    
    Args:
        limit: 返回数量
    
    Returns:
        list: 热门资讯列表
    """
    try:
        return mapper_get_hot_news(limit)
    except Exception as e:
        print(f'获取热门资讯失败: {e}')
        return []


def record_news_read(news_id):
    """
    记录资讯阅读
    
    Args:
        news_id: 资讯ID
    
    Returns:
        bool: 是否成功
    """
    try:
        return mapper_increase_read_count(news_id)
    except Exception as e:
        print(f'记录资讯阅读失败: {e}')
        return False


def get_news_by_category_summary():
    """
    获取各分类的资讯摘要统计
    
    Returns:
        dict: 各分类的资讯数量
    """
    try:
        categories = ['财经新闻', '市场行情', '政策解读', '理财知识']
        summary = {}
        
        for category in categories:
            count = get_news_count(category=category)
            summary[category] = count
        
        return summary
    except Exception as e:
        print(f'获取资讯分类统计失败: {e}')
        return {}

