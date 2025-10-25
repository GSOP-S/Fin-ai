from utils.db import db_query


def generate_market_analysis():
    """生成市场分析和股票推荐
    返回格式化的市场分析文本
    """
    # 模拟市场分析数据
    analysis = {
        "marketOverview": '今日A股三大指数小幅上涨，沪指涨0.82%，深成指涨1.25%，创业板指涨1.68%。市场成交量有所放大，北向资金净流入超50亿元。',
        "hotSectors": ['新能源', '半导体', '医药生物'],
        "recommendedStocks": [
            { "name": '贵州茅台', "code": '600519', "reason": '白酒龙头，业绩稳健，具有长期投资价值' },
            { "name": '宁德时代', "code": '300750', "reason": '新能源赛道核心标的，海外订单增长强劲' },
            { "name": '腾讯控股', "code": '0700.HK', "reason": '互联网龙头，估值处于历史低位，业绩开始回暖' }
        ]
    }

    # 构建分析文本
    analysis_text = f"市场分析：{analysis['marketOverview']}\n\n热门板块：{'、'.join(analysis['hotSectors'])}\n\n"
    analysis_text += '为您推荐以下股票：\n'
    for i, stock in enumerate(analysis['recommendedStocks']):
        analysis_text += f"{i + 1}. {stock['name']} ({stock['code']}) - {stock['reason']}\n"

    return analysis_text

def generate_stock_suggestion(stock):
    """根据股票信息生成投资建议
    Args:
        stock: 包含股票信息的字典
    Returns:
        格式化的建议文本
    """
    if not stock:
        return ""
    
    is_up = stock.get('change', 0) >= 0
    name = stock.get('name', '')
    code = stock.get('code', '')
    change_percent = stock.get('changePercent', '')
    
    if is_up:
        return f"{name} ({code}) 目前上涨 {change_percent}，表现强势。建议关注其成交量变化和市场热点持续性，可考虑逢低买入策略。"
    else:
        return f"{name} ({code}) 目前下跌 {change_percent}，可能存在短期调整。建议观察其支撑位表现，可考虑分批建仓策略。"

def get_stock_details(stock_name):
    """从数据库获取股票详细信息
    Args:
        stock_name: 股票名称
    Returns:
        股票详细信息字典
    """
    if not stock_name:
        return None
    
    query = "SELECT name, code, industry, market_cap, pe, recent_performance, volatility FROM Stocks WHERE name = %s"
    return db_query(query, (stock_name,), fetch_one=True)