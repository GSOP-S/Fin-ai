from utils.db import db_query


def generate_fund_suggestion(fund):
    """根据基金信息生成投资建议
    Args:
        fund: 包含基金信息的字典
    Returns:
        格式化的建议文本
    """
    if not fund:
        return ""
    
    name = fund.get('name', '')
    code = fund.get('code', '')
    change = fund.get('change', '')
    change_percent = fund.get('changePercent', '')
    manager = fund.get('manager', '')
    risk = fund.get('risk', '')
    
    trend = '上涨' if str(change).startswith('+') else '下跌'
    return f"基金建议：{name} ({code}) 目前{trend} {change_percent}，由{manager}管理，风险等级为{risk}。建议关注其近期表现和基金经理的投资风格。"

def get_fund_list(page=1, page_size=20, category=None, risk_level=None, order_by='code', order_dir='asc'):
    """获取基金列表，支持分页、筛选和排序
    Args:
        page: 当前页码
        page_size: 每页条数
        category: 基金类别筛选
        risk_level: 风险等级筛选
        order_by: 排序字段
        order_dir: 排序方向
    Returns:
        分页后的基金列表和分页信息
    """
    # 构建查询条件
    params = []
    conditions = []
    
    if category:
        conditions.append("category = %s")
        params.append(category)
    
    if risk_level:
        conditions.append("risk = %s")
        params.append(risk_level)
    
    # 基础查询SQL
    base_query = "SELECT name, code, nav, change_percent as changePercent, fund_change as `change`, category, risk, manager FROM Fundings"
    count_query = "SELECT COUNT(*) as total FROM Fundings"
    
    # 添加WHERE子句
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
        base_query += where_clause
        count_query += where_clause
    
    # 验证排序字段
    valid_order_by = {'code', 'name', 'nav', 'change_percent'}
    if order_by not in valid_order_by:
        order_by = 'code'
    
    order_dir_sql = 'DESC' if order_dir.lower() == 'desc' else 'ASC'
    order_clause = f" ORDER BY {order_by} {order_dir_sql}"
    
    # 获取总数
    total = db_query(count_query, params, fetch_one=True)['total']
    
    # 分页处理
    offset = (page - 1) * page_size
    query = f"{base_query}{order_clause} LIMIT %s OFFSET %s"
    params.extend([page_size, offset])
    
    funds = db_query(query, params)
    
    return {
        'data': funds,
        'pagination': {
            'currentPage': page,
            'pageSize': page_size,
            'totalItems': total,
            'totalPages': (total + page_size - 1) // page_size
        }
    }