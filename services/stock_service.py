"""stock_service.py
股票业务逻辑层
"""
from mapper import StockMapper
from typing import Dict, Any
from services.model_provider import ModelProvider

model = ModelProvider()


def generate_market_analysis() -> str:
    """生成市场分析和股票推荐文本，优先调用大模型，失败回退本地逻辑"""
    try:
        prompt = (
            "请基于最新A股市场表现，生成今日市场概览、3个热门板块以及3只推荐关注的股票，"
            "每条简短说明原因，中文输出。"
        )
        return model.generate(prompt, context={"type": "market_overview"})
    except Exception:
        # ------- 本地兜底示例数据 -------
        analysis = {
            "marketOverview": "今日A股三大指数小幅上涨，沪指涨0.82%，深成指涨1.25%，创业板指涨1.68%。市场成交量有所放大，北向资金净流入超50亿元。",
            "hotSectors": ["新能源", "半导体", "医药生物"],
            "recommendedStocks": [
                {"name": "贵州茅台", "code": "600519", "reason": "白酒龙头，业绩稳健，具有长期投资价值"},
                {"name": "宁德时代", "code": "300750", "reason": "新能源赛道核心标的，海外订单增长强劲"},
                {"name": "腾讯控股", "code": "0700.HK", "reason": "互联网龙头，估值处于历史低位，业绩开始回暖"},
            ],
        }

        text = (
            f"市场分析：{analysis['marketOverview']}\n\n"
            f"热门板块：{'、'.join(analysis['hotSectors'])}\n\n为您推荐以下股票：\n"
        )
        for idx, stk in enumerate(analysis["recommendedStocks"], 1):
            text += f"{idx}. {stk['name']} ({stk['code']}) - {stk['reason']}\n"
        return text


def generate_stock_suggestion(stock: Dict[str, Any]) -> str:
    """根据单只股票信息生成投资建议文本，优先使用大模型"""
    if not stock:
        return ""

    try:
        prompt = (
            "请基于以下股票信息，给出简洁的投资建议（80字以内，中文）：\n"
            f"股票名称：{stock.get('name','')}\n"
            f"股票代码：{stock.get('code','')}\n"
            f"涨跌幅：{stock.get('changePercent','')}"
        )
        return model.generate(prompt, context={"type": "stock"})
    except Exception:
        # 本地兜底
        is_up = stock.get("change", 0) >= 0
        name = stock.get("name", "")
        code = stock.get("code", "")
        change_percent = stock.get("changePercent", "")

        if is_up:
            return (
                f"{name} ({code}) 目前上涨 {change_percent}，表现强势。"
                "建议关注其成交量变化和市场热点持续性，可考虑逢低买入策略。"
            )
        else:
            return (
                f"{name} ({code}) 目前下跌 {change_percent}，可能存在短期调整。"
                "建议观察其支撑位表现，可考虑分批建仓策略。"
            )

def generate_stock_suggestion(stock: Dict[str, Any]) -> str:
    """根据单只股票信息生成投资建议文本"""
    if not stock:
        return ""

    is_up = stock.get("change", 0) >= 0
    name = stock.get("name", "")
    code = stock.get("code", "")
    change_percent = stock.get("changePercent", "")

    if is_up:
        return (
            f"{name} ({code}) 目前上涨 {change_percent}，表现强势。"
            "建议关注其成交量变化和市场热点持续性，可考虑逢低买入策略。"
        )
    else:
        return (
            f"{name} ({code}) 目前下跌 {change_percent}，可能存在短期调整。"
            "建议观察其支撑位表现，可考虑分批建仓策略。"
        )


def get_stock_details(stock_name: str):
    """通过 StockMapper 获取股票详细信息"""
    return StockMapper.get_stock_details(stock_name)


def get_stock_list(query_params: Dict[str, Any]):
    """获取股票列表，支持分页/筛选/排序

    Args:
        query_params: 包含 page, pageSize, industry, orderBy, orderDir 等键的字典
    Returns:
        {"data": [...], "pagination": {...}}
    """
    page = int(query_params.get("page", 1))
    page_size = int(query_params.get("pageSize", 20))
    industry = query_params.get("industry")
    order_by = query_params.get("orderBy", "code")
    order_dir = query_params.get("orderDir", "asc")

    return StockMapper.get_stocks(
        page=page,
        page_size=page_size,
        industry=industry,
        order_by=order_by,
        order_dir=order_dir,
    )