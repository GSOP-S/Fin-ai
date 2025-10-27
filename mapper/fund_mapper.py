"""
基金数据访问层 Mapper
负责基金相关的数据库操作
"""

from typing import List, Dict, Optional

from utils.db import db_query, db_execute


class FundMapper:
    """基金数据访问类"""

    @staticmethod
    def get_fund_details(fund_code: str) -> Optional[Dict]:
        """根据基金代码获取基金详细信息

        Args:
            fund_code: 基金代码
        Returns:
            基金信息字典，若不存在返回 None
        """
        if not fund_code:
            return None

        query = (
            "SELECT code, name, nav, change_percent AS changePercent, "
            "fund_change AS `change`, category, risk, manager "
            "FROM Fundings WHERE code = %s"
        )
        return db_query(query, (fund_code,), fetch_one=True)

    @staticmethod
    def get_funds(
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
        order_by: str = "code",
        order_dir: str = "asc",
    ) -> Dict:
        """分页获取基金列表，支持筛选和排序

        Args:
            page: 当前页码
            page_size: 每页条数
            category: 基金类别筛选
            risk_level: 风险等级筛选
            order_by: 排序字段（code|name|nav|change_percent）
            order_dir: 排序方向 asc/desc
        Returns:
            包含 `data` 和 `pagination` 的字典
        """
        params = []
        conditions = []

        if category:
            conditions.append("category = %s")
            params.append(category)
        if risk_level:
            conditions.append("risk = %s")
            params.append(risk_level)

        base_query = (
            "SELECT code, name, nav, change_percent AS changePercent, "
            "fund_change AS `change`, category, risk, manager FROM Fundings"
        )
        count_query = "SELECT COUNT(*) as total FROM Fundings"

        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            base_query += where_clause
            count_query += where_clause

        valid_order_by = {"code", "name", "nav", "change_percent"}
        if order_by not in valid_order_by:
            order_by = "code"
        order_dir_sql = "DESC" if order_dir.lower() == "desc" else "ASC"

        base_query += f" ORDER BY {order_by} {order_dir_sql}"

        total = db_query(count_query, params, fetch_one=True)["total"]
        offset = (page - 1) * page_size
        query = f"{base_query} LIMIT %s OFFSET %s"
        params_with_pagination = params + [page_size, offset]

        funds = db_query(query, params_with_pagination)

        return {
            "data": funds,
            "pagination": {
                "currentPage": page,
                "pageSize": page_size,
                "totalItems": total,
                "totalPages": (total + page_size - 1) // page_size,
            },
        }

    @staticmethod
    def create_fund(data: Dict) -> int:
        """新增基金记录，返回影响行数"""
        columns = [
            "code",
            "name",
            "nav",
            "change_percent",
            "fund_change",
            "category",
            "risk",
            "manager",
        ]
        cols_sql = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        values = tuple(data.get(col) for col in columns)
        query = f"INSERT INTO Fundings ({cols_sql}) VALUES ({placeholders})"
        return db_execute(query, values)

    @staticmethod
    def update_fund(code: str, updates: Dict) -> int:
        """根据基金代码更新基金信息"""
        if not updates:
            return 0
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        params = list(updates.values()) + [code]
        query = f"UPDATE Fundings SET {set_clause} WHERE code = %s"
        return db_execute(query, tuple(params))

    @staticmethod
    def delete_fund(code: str) -> int:
        """删除基金记录"""
        query = "DELETE FROM Fundings WHERE code = %s"
        return db_execute(query, (code,))