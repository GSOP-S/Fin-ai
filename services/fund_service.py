"""fund_service.py
基金业务逻辑层
"""
from typing import Dict, Any
from mapper import FundMapper
from services.model_provider import ModelProvider


model = ModelProvider()


def _fallback_fund_suggestion(fund: Dict[str, Any]) -> str:
    """本地兜底文案"""
    if not fund:
        return ""
    name = fund.get("name", "")
    code = fund.get("code", "")
    change = str(fund.get("change", ""))
    change_percent = fund.get("changePercent", "")
    manager = fund.get("manager", "")
    risk = fund.get("risk", "")

    trend = "上涨" if change.startswith("+") else "下跌"
    return (
        f"基金建议：{name} ({code}) 目前{trend} {change_percent}，"
        f"由{manager}管理，风险等级为{risk}。建议关注其近期表现和基金经理的投资风格。"
    )


def generate_fund_suggestion(fund: Dict[str, Any]) -> str:
    """根据基金信息生成投资建议，优先调用大模型，失败则回退本地算法"""
    try:
        prompt = (
            "请根据以下基金信息，给出简洁的投资建议（100字以内，中文）：\n"
            f"基金名称：{fund.get('name','')}\n"
            f"基金代码：{fund.get('code','')}\n"
            f"涨跌幅：{fund.get('changePercent','')}\n"
            f"基金经理：{fund.get('manager','')}\n"
            f"风险等级：{fund.get('risk','')}"
        )
        return model.generate(prompt, context={"type": "fund"})
    except Exception:
        # 兜底逻辑
        return _fallback_fund_suggestion(fund)


def get_fund_list(
    page: int = 1,
    page_size: int = 20,
    category: str | None = None,
    risk_level: str | None = None,
    order_by: str = "code",
    order_dir: str = "asc",
):
    """通过 FundMapper 获取基金列表"""
    return FundMapper.get_funds(
        page=page,
        page_size=page_size,
        category=category,
        risk_level=risk_level,
        order_by=order_by,
        order_dir=order_dir,
    )


def get_fund_details(code: str):
    """获取基金详情"""
    return FundMapper.get_fund_details(code)