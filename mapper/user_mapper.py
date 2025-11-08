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
    
    @staticmethod
    def register_user(
        username: str,
        password: str,
        real_name: str,
        id_card: str,
        phone: str,
        city: str,
        occupation: str,
        risk_score: float,
        risk_level: str,
        investment_purposes: str
    ) -> int:
        """
        注册新用户（包含详细资料）
        
        Args:
            username: 用户名
            password: 密码
            real_name: 真实姓名
            id_card: 身份证号
            phone: 手机号
            city: 城市
            occupation: 职业
            risk_score: 风险评分
            risk_level: 风险等级
            investment_purposes: 投资目的（逗号分隔）
            
        Returns:
            插入的行数
        """
        query = """
            INSERT INTO Users (
                user_id, password, display_name,
                real_name, id_card, phone, city, occupation,
                risk_score, risk_level, investment_purposes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return db_execute(query, (
            username, password, real_name,
            real_name, id_card, phone, city, occupation,
            risk_score, risk_level, investment_purposes
        ))
    
    @staticmethod
    def check_username_exists(username: str) -> bool:
        """
        检查用户名是否已存在
        
        Args:
            username: 用户名
            
        Returns:
            存在返回True，否则返回False
        """
        query = "SELECT COUNT(*) as count FROM Users WHERE user_id = %s"
        result = db_query(query, (username,), fetch_one=True)
        return result['count'] > 0 if result else False

