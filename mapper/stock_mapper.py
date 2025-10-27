"""
股票数据访问层 Mapper
负责股票相关的数据库操作
"""

from typing import List, Dict, Optional

from utils.db import db_query, db_execute


class StockMapper:
    """股票数据访问类"""

    @staticmethod
    def get_stock_details(stock_name: str) -> Optional[Dict]:
        """根据股票名称获取股票详细信息

        Args:
            stock_name: 股票名称
        Returns:
            股票信息字典，若不存在返回 None
        """
        if not stock_name:
            return None

        query = (
            "SELECT name, code, industry, market_cap, pe, "
            "recent_performance, volatility FROM Stocks WHERE name = %s"
        )
        return db_query(query, (stock_name,), fetch_one=True)

    @staticmethod
    def get_stocks(
        page: int = 1,
        page_size: int = 20,
        industry: Optional[str] = None,
        order_by: str = "code",
        order_dir: str = "asc",
    ) -> Dict:
        """分页获取股票列表，可按行业筛选并排序

        Args:
            page: 当前页码
            page_size: 每页条数
            industry: 行业筛选
            order_by: 排序字段
            order_dir: 排序方向（asc/desc）
        Returns:
            包含 `data` 和 `pagination` 的字典
        """
        params = []
        conditions = []

        if industry:
            conditions.append("industry = %s")
            params.append(industry)

        base_query = (
            "SELECT id, name, code, industry, market_cap, pe, "
            "recent_performance, volatility FROM Stocks"
        )
        count_query = "SELECT COUNT(*) as total FROM Stocks"

        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            base_query += where_clause
            count_query += where_clause

        valid_order_by = {"code", "name", "market_cap", "pe"}
        if order_by not in valid_order_by:
            order_by = "code"
        order_dir_sql = "DESC" if order_dir.lower() == "desc" else "ASC"

        base_query += f" ORDER BY {order_by} {order_dir_sql}"

        total = db_query(count_query, params, fetch_one=True)["total"]
        offset = (page - 1) * page_size
        query = f"{base_query} LIMIT %s OFFSET %s"
        params_with_pagination = params + [page_size, offset]

        stocks = db_query(query, params_with_pagination)

        return {
            "data": stocks,
            "pagination": {
                "currentPage": page,
                "pageSize": page_size,
                "totalItems": total,
                "totalPages": (total + page_size - 1) // page_size,
            },
        }

    @staticmethod
    def create_stock(data: Dict) -> int:
        """新增股票记录，返回影响行数"""
        columns = [
            "name",
            "code",
            "industry",
            "market_cap",
            "pe",
            "recent_performance",
            "volatility",
        ]
        cols_sql = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        values = tuple(data.get(col) for col in columns)
        query = f"INSERT INTO Stocks ({cols_sql}) VALUES ({placeholders})"
        return db_execute(query, values)

    @staticmethod
    def update_stock(code: str, updates: Dict) -> int:
        """根据股票代码更新股票信息，返回影响行数"""
        if not updates:
            return 0
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        params = list(updates.values()) + [code]
        query = f"UPDATE Stocks SET {set_clause} WHERE code = %s"
        return db_execute(query, tuple(params))

    @staticmethod
    def delete_stock(code: str) -> int:
        """根据股票代码删除股票记录"""
        query = "DELETE FROM Stocks WHERE code = %s"
        return db_execute(query, (code,))