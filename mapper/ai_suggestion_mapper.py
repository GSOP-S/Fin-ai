"""
AI建议数据访问层 Mapper
"""

from typing import List, Dict, Optional

from utils.db import db_query, db_execute


class AISuggestionMapper:
    """AI 建议数据表访问类"""

    @staticmethod
    def get_suggestion(page_type: str, suggestion_type: str) -> Optional[Dict]:
        """根据页面类型和建议类型获取建议内容"""
        query = (
            "SELECT id, page_type, suggestion_type, content, created_at "
            "FROM AISuggestions WHERE page_type = %s AND suggestion_type = %s"
        )
        return db_query(query, (page_type, suggestion_type), fetch_one=True)

    @staticmethod
    def upsert_suggestion(page_type: str, suggestion_type: str, content: Dict) -> int:
        """插入或更新建议
        使用 INSERT ... ON DUPLICATE KEY UPDATE
        """
        query = (
            "INSERT INTO AISuggestions (page_type, suggestion_type, content) "
            "VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE content = VALUES(content)"
        )
        return db_execute(query, (page_type, suggestion_type, content))