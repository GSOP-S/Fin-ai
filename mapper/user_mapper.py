"""
用户数据访问层 Mapper
负责用户相关的数据库操作
"""

from utils.db import db_query, db_execute
from typing import Optional, Dict


class UserMapper:
    """用户数据访问类"""
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """
        根据用户ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典，不存在时返回None
        """
        query = """
            SELECT user_id, display_name, created_at
            FROM Users
            WHERE user_id = %s
        """
        return db_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def verify_user_login(user_id: str, password: str) -> Optional[Dict]:
        """
        验证用户登录
        
        Args:
            user_id: 用户ID
            password: 密码
            
        Returns:
            验证通过返回用户信息，否则返回None
        """
        query = """
            SELECT user_id, display_name
            FROM Users
            WHERE user_id = %s AND password = %s
        """
        return db_query(query, (user_id, password), fetch_one=True)
    
    @staticmethod
    def insert_user(user_id: str, password: str, display_name: str) -> int:
        """
        创建新用户
        
        Args:
            user_id: 用户ID
            password: 密码
            display_name: 显示名称
            
        Returns:
            插入的行数
        """
        query = """
            INSERT INTO Users (user_id, password, display_name)
            VALUES (%s, %s, %s)
        """
        return db_execute(query, (user_id, password, display_name))
    
    @staticmethod
    def update_user_info(user_id: str, display_name: str) -> int:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            display_name: 新的显示名称
            
        Returns:
            更新的行数
        """
        query = """
            UPDATE Users
            SET display_name = %s
            WHERE user_id = %s
        """
        return db_execute(query, (display_name, user_id))

