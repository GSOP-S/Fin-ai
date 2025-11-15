"""
资讯控制器（Controller）
处理资讯相关的HTTP请求
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.news_service import (
    get_news_list,
    get_news_detail,
    search_news,
    get_hot_news,
    record_news_read,
    get_news_by_category_summary,
    create_news
)

# 创建Blueprint
news_bp = Blueprint('news', __name__, url_prefix='/api')


@news_bp.route('/news', methods=['GET'])
@handle_exceptions
def get_news():
    """
    获取资讯列表
    
    Query参数:
        - category: 分类筛选（可选）
        - page: 页码（可选，默认1）
        - page_size: 每页数量（可选，默认20）
    
    Returns:
        JSON响应，包含资讯列表和分页信息
    """
    # 获取查询参数
    category = request.args.get('category')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    
    # 参数验证
    if page < 1:
        return error_response('页码必须大于0', status_code=400)
    
    if page_size < 1 or page_size > 100:
        return error_response('每页数量必须在1-100之间', status_code=400)
    
    # 获取资讯列表
    result = get_news_list(category=category, page=page, page_size=page_size)
    
    # 构造响应数据
    response_data = {
        'list': result['list'],
        'pagination': result['pagination']
    }
    
    return success_response(response_data, message='获取资讯列表成功')


@news_bp.route('/news/<int:news_id>', methods=['GET'])
@handle_exceptions
def get_news_by_id(news_id):
    """
    获取资讯详情
    
    Path参数:
        - news_id: 资讯ID
    
    Returns:
        JSON响应，包含资讯详情
    """
    news = get_news_detail(news_id)
    
    if news:
        return success_response(news, message='获取资讯详情成功')
    else:
        return error_response('资讯不存在', status_code=404)


@news_bp.route('/news/search', methods=['GET'])
@handle_exceptions
def search():
    """
    搜索资讯
    
    Query参数:
        - keyword: 搜索关键词
    
    Returns:
        JSON响应，包含匹配的资讯列表
    """
    keyword = request.args.get('keyword', '').strip()
    
    if not keyword:
        return error_response('搜索关键词不能为空', status_code=400)
    
    news_list = search_news(keyword)
    
    return success_response(news_list, message=f'找到{len(news_list)}条相关资讯')


@news_bp.route('/news/hot', methods=['GET'])
@handle_exceptions
def get_hot():
    """
    获取热门资讯
    
    Query参数:
        - limit: 返回数量（可选，默认10）
    
    Returns:
        JSON响应，包含热门资讯列表
    """
    limit = int(request.args.get('limit', 10))
    
    if limit < 1 or limit > 50:
        return error_response('返回数量必须在1-50之间', status_code=400)
    
    news_list = get_hot_news(limit)
    
    return success_response(news_list, message='获取热门资讯成功')


@news_bp.route('/news/<int:news_id>/read', methods=['POST'])
@handle_exceptions
def mark_as_read(news_id):
    """
    标记资讯为已读（增加阅读量）
    
    Path参数:
        - news_id: 资讯ID
    
    Returns:
        JSON响应
    """
    result = record_news_read(news_id)
    
    if result:
        return success_response(None, message='记录成功')
    else:
        return error_response('资讯不存在或记录失败', status_code=404)


@news_bp.route('/news/stats', methods=['GET'])
@handle_exceptions
def get_stats():
    """
    获取资讯统计信息
    
    Returns:
        JSON响应，包含各分类的资讯数量
    """
    summary = get_news_by_category_summary()
    
    return success_response(summary, message='获取统计信息成功')

def _classify(category_label, title, content):
    label = category_label or ''
    text = f"{title}\n{content}" if content else title
    if label in ['财经新闻', '市场行情', '政策解读', '理财知识']:
        return label
    kw_market = ['涨停', '股', '指数', '降价', '销量', '行情', '盘中', '收盘']
    if any(k in text for k in kw_market):
        return '市场行情'
    kw_policy = ['政策', '讲话', '会议', '指导意见', '总书记']
    if any(k in text for k in kw_policy):
        return '政策解读'
    kw_edu = ['科普', '入门', '理财', '指南']
    if any(k in text for k in kw_edu):
        return '理财知识'
    return '财经新闻'


@news_bp.route('/news', methods=['POST'])
@handle_exceptions
def create_news_item():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    summary = data.get('summary', '').strip()
    content = data.get('content', '').strip()
    category_label = data.get('category', '').strip()
    source = data.get('source', '').strip()
    author = data.get('author', '').strip()
    image_rel = data.get('image', '').strip()
    tags = data.get('tags', '').strip() or None
    from datetime import datetime
    publish_time = data.get('publish_time') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not title or not summary:
        return error_response('缺少标题或摘要', status_code=400)
    category = _classify(category_label, title, content)
    image_url = f"/assets/news/{image_rel}" if image_rel else None
    news_id = create_news(title, summary, content, category, source or '来源不详', author or '作者不详', publish_time, image_url, tags, 0)
    if not news_id:
        return error_response('创建失败', status_code=500)
    return success_response({'id': news_id}, message='创建资讯成功')

