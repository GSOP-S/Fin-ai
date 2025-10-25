"""
转账数据访问层 Mapper
负责转账历史相关的数据库操作
"""

from utils.db import db_query, db_execute
from typing import List, Dict, Optional


class TransferMapper:
    """转账数据访问类"""
    
    @staticmethod
    def get_recent_accounts(user_id: str, limit: int = 5) -> List[Dict]:
        """
        获取用户最近转账的账户列表
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            最近转账账户列表
        """
        query = """
            SELECT 
                recipient_account,
                recipient_name,
                COUNT(*) as transfer_count,
                MAX(transfer_date) as last_transfer_date,
                SUM(amount) as total_amount
            FROM TransferHistory
            WHERE user_id = %s
            GROUP BY recipient_account, recipient_name
            ORDER BY last_transfer_date DESC
            LIMIT %s
        """
        return db_query(query, (user_id, limit))
    
    @staticmethod
    def get_transfer_history(user_id: str, recipient_account: Optional[str] = None) -> List[Dict]:
        """
        获取用户转账历史
        
        Args:
            user_id: 用户ID
            recipient_account: 收款账户（可选）
            
        Returns:
            转账历史列表
        """
        if recipient_account:
            query = """
                SELECT id, user_id, recipient_account, recipient_name, amount, 
                       transfer_date, transfer_time, status, created_at
                FROM TransferHistory
                WHERE user_id = %s AND recipient_account = %s
                ORDER BY transfer_date DESC, transfer_time DESC
                LIMIT 20
            """
            return db_query(query, (user_id, recipient_account))
        else:
            query = """
                SELECT id, user_id, recipient_account, recipient_name, amount, 
                       transfer_date, transfer_time, status, created_at
                FROM TransferHistory
                WHERE user_id = %s
                ORDER BY transfer_date DESC, transfer_time DESC
                LIMIT 50
            """
            return db_query(query, (user_id,))
    
    @staticmethod
    def check_account_exists(user_id: str, recipient_account: str) -> bool:
        """
        检查用户是否曾向该账户转账
        
        Args:
            user_id: 用户ID
            recipient_account: 收款账户
            
        Returns:
            True表示存在历史记录，False表示首次转账
        """
        query = """
            SELECT COUNT(*) as count
            FROM TransferHistory
            WHERE user_id = %s AND recipient_account = %s
        """
        result = db_query(query, (user_id, recipient_account), fetch_one=True)
        return result['count'] > 0 if result else False
    
    @staticmethod
    def insert_transfer(user_id: str, recipient_account: str, recipient_name: str,
                       amount: float, transfer_date: str, transfer_time: str = '00:00:00',
                       status: str = 'completed') -> int:
        """
        插入一条转账记录
        
        Args:
            user_id: 用户ID
            recipient_account: 收款账户
            recipient_name: 收款人姓名
            amount: 转账金额
            transfer_date: 转账日期
            transfer_time: 转账时间
            status: 状态
            
        Returns:
            插入的行数
        """
        query = """
            INSERT INTO TransferHistory
            (user_id, recipient_account, recipient_name, amount, 
             transfer_date, transfer_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return db_execute(query, (user_id, recipient_account, recipient_name, 
                                  amount, transfer_date, transfer_time, status))
    
    @staticmethod
    def get_transfer_statistics(user_id: str, days: int = 30) -> Dict:
        """
        获取用户最近N天的转账统计
        
        Args:
            user_id: 用户ID
            days: 统计天数
            
        Returns:
            统计数据字典
        """
        query = """
            SELECT 
                COUNT(*) as total_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                COUNT(DISTINCT recipient_account) as recipient_count
            FROM TransferHistory
            WHERE user_id = %s 
              AND transfer_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        """
        result = db_query(query, (user_id, days), fetch_one=True)
        return result or {
            'total_count': 0,
            'total_amount': 0,
            'avg_amount': 0,
            'recipient_count': 0
        }

