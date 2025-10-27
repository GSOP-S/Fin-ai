"""data_service.py
统一的数据访问聚合层
负责调用各 Mapper 提供高阶数据查询接口，供业务/AI 层调用，屏蔽数据库细节。
"""
from typing import Any, Dict, Optional
from mapper import StockMapper, FundMapper, AISuggestionMapper


class DataService:
    """对接 Mapper 的聚合查询服务"""

    # --- 股票相关 ---------------------------------------------------------
    @staticmethod
    def get_stock_by_name(name: str) -> Optional[Dict[str, Any]]:
        """根据股票名称获取单条股票信息"""
        return StockMapper.get_stock_details(name)

    @staticmethod
    def list_stocks(
        page: int = 1,
        page_size: int = 20,
        industry: Optional[str] = None,
        order_by: str = "code",
        order_dir: str = "asc",
    ) -> Dict[str, Any]:
        """分页获取股票列表"""
        return StockMapper.get_stocks(page, page_size, industry, order_by, order_dir)

    # --- 基金相关 ---------------------------------------------------------
    @staticmethod
    def get_fund_by_code(code: str) -> Optional[Dict[str, Any]]:
        """根据基金代码获取基金详情"""
        return FundMapper.get_fund_details(code)

    @staticmethod
    def list_funds(
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
        order_by: str = "code",
        order_dir: str = "asc",
    ) -> Dict[str, Any]:
        """分页获取基金列表"""
        return FundMapper.get_funds(page, page_size, category, risk_level, order_by, order_dir)

    # --- AI Suggestion 相关 ----------------------------------------------
    @staticmethod
    def get_ai_suggestion(page_type: str, suggestion_type: str):
        """获取预设 AI 建议"""
        return AISuggestionMapper.get_suggestion(page_type, suggestion_type)

    @staticmethod
    def upsert_ai_suggestion(page_type: str, suggestion_type: str, content):
        """保存/更新 AI 建议"""
        return AISuggestionMapper.upsert_suggestion(page_type, suggestion_type, content)