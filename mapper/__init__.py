"""
Mapper层 - 数据访问层
负责与数据库交互，执行CRUD操作
"""

from .bill_mapper import BillMapper
from .transfer_mapper import TransferMapper
from .user_mapper import UserMapper

from .fund_mapper import FundMapper
from .ai_suggestion_mapper import AISuggestionMapper

__all__ = ['BillMapper', 'TransferMapper', 'UserMapper', 'FundMapper', 'AISuggestionMapper']

