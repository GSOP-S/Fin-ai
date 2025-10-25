"""
账单数据访问层 Mapper
负责账单相关的数据库操作
"""

from utils.db import db_query, db_execute
from typing import List, Dict, Optional
from datetime import datetime


class BillMapper:
    """账单数据访问类"""
    
    @staticmethod
    def get_bills_by_user(user_id: str, month: Optional[str] = None) -> List[Dict]:
        """
        根据用户ID获取账单列表
        
        Args:
            user_id: 用户ID
            month: 月份，格式：YYYY-MM，为None时获取所有账单
            
        Returns:
            账单列表
        """
        if month:
            # 获取指定月份的账单
            query = """
                SELECT id, user_id, merchant, category, amount, 
                       transaction_date, transaction_time, status, created_at
                FROM Bills
                WHERE user_id = %s AND DATE_FORMAT(transaction_date, '%Y-%m') = %s
                ORDER BY transaction_date DESC, transaction_time DESC
            """
            return db_query(query, (user_id, month))
        else:
            # 获取所有账单
            query = """
                SELECT id, user_id, merchant, category, amount, 
                       transaction_date, transaction_time, status, created_at
                FROM Bills
                WHERE user_id = %s
                ORDER BY transaction_date DESC, transaction_time DESC
                LIMIT 100
            """
            return db_query(query, (user_id,))
    
    @staticmethod
    def get_bill_statistics(user_id: str, month: str) -> Dict:
        """
        获取用户指定月份的账单统计数据
        
        Args:
            user_id: 用户ID
            month: 月份，格式：YYYY-MM
            
        Returns:
            统计数据字典
        """
        query = """
            SELECT 
                COUNT(*) as total_count,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_expense,
                AVG(CASE WHEN amount < 0 THEN ABS(amount) ELSE NULL END) as avg_expense
            FROM Bills
            WHERE user_id = %s AND DATE_FORMAT(transaction_date, '%Y-%m') = %s
        """
        result = db_query(query, (user_id, month), fetch_one=True)
        return result or {
            'total_count': 0,
            'total_income': 0,
            'total_expense': 0,
            'avg_expense': 0
        }
    
    @staticmethod
    def get_category_expenses(user_id: str, month: str) -> List[Dict]:
        """
        获取用户指定月份各类别的支出统计
        
        Args:
            user_id: 用户ID
            month: 月份，格式：YYYY-MM
            
        Returns:
            类别支出列表，每项包含 category 和 total_amount
        """
        query = """
            SELECT 
                category,
                SUM(ABS(amount)) as total_amount,
                COUNT(*) as transaction_count
            FROM Bills
            WHERE user_id = %s 
              AND DATE_FORMAT(transaction_date, '%Y-%m') = %s
              AND amount < 0
            GROUP BY category
            ORDER BY total_amount DESC
        """
        return db_query(query, (user_id, month))
    
    @staticmethod
    def insert_bill(user_id: str, merchant: str, category: str, 
                   amount: float, transaction_date: str, 
                   transaction_time: str = '00:00:00', 
                   status: str = 'completed') -> int:
        """
        插入一条账单记录
        
        Args:
            user_id: 用户ID
            merchant: 商户名称
            category: 类别
            amount: 金额（正数为收入，负数为支出）
            transaction_date: 交易日期
            transaction_time: 交易时间
            status: 状态
            
        Returns:
            插入的行数
        """
        query = """
            INSERT INTO Bills 
            (user_id, merchant, category, amount, transaction_date, transaction_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return db_execute(query, (user_id, merchant, category, amount, 
                                  transaction_date, transaction_time, status))
    
    @staticmethod
    def get_abnormal_transactions(user_id: str, month: str, threshold: float) -> List[Dict]:
        """
        获取异常交易（大额消费）
        
        Args:
            user_id: 用户ID
            month: 月份
            threshold: 异常金额阈值
            
        Returns:
            异常交易列表
        """
        query = """
            SELECT id, merchant, category, amount, transaction_date
            FROM Bills
            WHERE user_id = %s 
              AND DATE_FORMAT(transaction_date, '%Y-%m') = %s
              AND amount < 0
              AND ABS(amount) > %s
            ORDER BY ABS(amount) DESC
        """
        return db_query(query, (user_id, month, threshold))

