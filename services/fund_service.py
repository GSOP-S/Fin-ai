"""fund_service.py
基金业务逻辑层
"""
from typing import Dict, Any
from mapper import FundMapper


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


def get_fund_by_code(code: str):
    """根据基金代码获取基金信息"""
    return FundMapper.get_fund_by_code(code)


class FundService:
    """基金服务类，封装基金相关的业务逻辑"""
    
    def __init__(self):
        pass
    
    def get_fund_list(self, page=1, page_size=20, category=None, risk_level=None, order_by="code", order_dir="asc"):
        """获取基金列表"""
        return get_fund_list(page, page_size, category, risk_level, order_by, order_dir)
    
    def get_fund_details(self, code):
        """获取基金详情"""
        return get_fund_details(code)
    
    def get_fund_by_code(self, code):
        """根据基金代码获取基金信息"""
        return get_fund_by_code(code)
    
    def generate_fund_suggestion(self, fund):
        """生成基金建议"""
        if not fund:
            return {'suggestion': ''}
        
        # 先生成本地建议作为兜底
        fallback_suggestion = _fallback_fund_suggestion(fund)
        
        try:
            from services.model_provider import ModelProvider
            model = ModelProvider()
            prompt = (
                "请根据以下基金信息，给出简洁的投资建议（100字以内，中文）：\n"
                f"基金名称：{fund.get('name','')}\n"
                f"基金代码：{fund.get('code','')}\n"
                f"涨跌幅：{fund.get('changePercent','')}\n"
                f"基金经理：{fund.get('manager','')}\n"
                f"风险等级：{fund.get('risk','')}"
            )
            suggestion_text = model.generate(prompt, context={"type": "fund"})
            # 如果AI调用成功，返回AI结果；否则返回兜底结果
            return {'suggestion': suggestion_text if suggestion_text else fallback_suggestion, 'fund': fund}
        except Exception as exc:
            print(f"[FundService] AI 调用失败: {exc}")
            # 兜底逻辑
            return {'suggestion': fallback_suggestion, 'fund': fund}