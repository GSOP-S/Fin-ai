"""用户持仓数据访问层"""

from utils.db import db_query, db_execute


class UserPositionMapper:
    """用户持仓数据映射器"""
    
    @staticmethod
    def get_user_positions_by_type(user_id, position_type=None):
        """获取用户持仓列表
        
        Args:
            user_id: 用户ID
            position_type: 持仓类型 (fund/deposit/savings), None表示获取所有类型
            
        Returns:
            list: 持仓列表
        """
        if position_type:
            sql = """
            SELECT 
                up.id,
                up.user_id,
                up.position_type,
                up.product_code,
                up.product_name,
                up.shares,
                up.purchase_price,
                up.current_price,
                up.purchase_date,
                up.current_value,
                up.total_investment,
                up.profit_loss,
                up.profit_loss_percent,
                up.status,
                up.created_at,
                up.updated_at
            FROM UserPositions up
            WHERE up.user_id = %s AND up.position_type = %s AND up.status = 'active'
            ORDER BY up.updated_at DESC
            """
            return db_query(sql, (user_id, position_type))
        else:
            sql = """
            SELECT 
                up.id,
                up.user_id,
                up.position_type,
                up.product_code,
                up.product_name,
                up.shares,
                up.purchase_price,
                up.current_price,
                up.purchase_date,
                up.current_value,
                up.total_investment,
                up.profit_loss,
                up.profit_loss_percent,
                up.status,
                up.created_at,
                up.updated_at
            FROM UserPositions up
            WHERE up.user_id = %s AND up.status = 'active'
            ORDER BY up.updated_at DESC
            """
            return db_query(sql, (user_id,))
    
    @staticmethod
    def get_user_portfolio_summary(user_id):
        """获取用户投资组合汇总
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 投资组合汇总信息
        """
        sql = """
        SELECT 
            position_type,
            COUNT(*) as position_count,
            ROUND(SUM(current_value), 2) as total_value,
            ROUND(SUM(total_investment), 2) as total_investment,
            ROUND(SUM(profit_loss), 2) as total_profit_loss,
            CASE 
                WHEN SUM(total_investment) > 0 THEN 
                    ROUND((SUM(profit_loss) / SUM(total_investment)) * 100, 2)
                ELSE 0 
            END as total_profit_loss_percent,
            ROUND(SUM(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END), 2) as total_profit,
            ROUND(SUM(CASE WHEN profit_loss < 0 THEN ABS(profit_loss) ELSE 0 END), 2) as total_loss
        FROM UserPositions
        WHERE user_id = %s AND status = 'active'
        GROUP BY position_type
        """
        results = db_query(sql, (user_id,))
        
        # 转换为字典格式，便于前端使用
        summary = {}
        total_value = 0
        total_investment = 0
        total_profit_loss = 0
        
        for result in results:
            position_type = result['position_type']
            summary[position_type] = {
                'position_count': result['position_count'],
                'total_value': float(result['total_value'] or 0),
                'total_investment': float(result['total_investment'] or 0),
                'total_profit_loss': float(result['total_profit_loss'] or 0),
                'total_profit_loss_percent': float(result['total_profit_loss_percent'] or 0),
                'total_profit': float(result['total_profit'] or 0),
                'total_loss': float(result['total_loss'] or 0)
            }
            
            total_value += float(result['total_value'] or 0)
            total_investment += float(result['total_investment'] or 0)
            total_profit_loss += float(result['total_profit_loss'] or 0)
        
        # 添加总体汇总
        summary['overall'] = {
            'total_value': round(total_value, 2),
            'total_investment': round(total_investment, 2),
            'total_profit_loss': round(total_profit_loss, 2),
            'total_profit_loss_percent': round((total_profit_loss / total_investment * 100) if total_investment > 0 else 0, 2),
            'position_count': sum(result['position_count'] for result in results)
        }
        
        return summary
    
    @staticmethod
    def get_user_fund_positions(user_id):
        """获取用户基金持仓列表（包含基金详情信息）
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 基金持仓列表（包含基金基础信息）
        """
        sql = """
        SELECT 
            up.id as position_id,
            up.user_id,
            up.shares,
            up.purchase_price,
            up.current_price as current_nav,
            up.purchase_date,
            up.current_value,
            up.total_investment,
            up.profit_loss,
            up.profit_loss_percent,
            f.code as fund_code,
            f.name as fund_name,
            f.nav as fund_nav,
            f.change_percent as fund_change_percent,
            f.fund_change as fund_change,
            f.category as fund_category,
            f.risk as fund_risk,
            f.manager as fund_manager
        FROM UserPositions up
        LEFT JOIN Fundings f ON up.product_code = f.code
        WHERE up.user_id = %s AND up.position_type = 'fund' AND up.status = 'active'
        ORDER BY up.updated_at DESC
        """
        results = db_query(sql, (user_id,))
        
        # 处理数据，确保数值类型正确
        processed_results = []
        for result in results:
            processed_result = dict(result)
            # 转换数值字段
            numeric_fields = [
                'shares', 'purchase_price', 'current_nav', 'current_value', 
                'total_investment', 'profit_loss', 'profit_loss_percent',
                'fund_nav'
            ]
            for field in numeric_fields:
                if field in processed_result and processed_result[field] is not None:
                    processed_result[field] = float(processed_result[field])
            
            processed_results.append(processed_result)
        
        return processed_results
    
    @staticmethod
    def get_user_deposit_positions(user_id):
        """获取用户存款/储蓄持仓列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 存款/储蓄持仓列表
        """
        sql = """
        SELECT 
            up.id as position_id,
            up.user_id,
            up.product_code,
            up.product_name,
            up.shares as amount,
            up.purchase_price,
            up.purchase_date,
            up.current_value,
            up.total_investment,
            up.status,
            CASE 
                WHEN up.position_type = 'deposit' THEN '定期存款'
                WHEN up.position_type = 'savings' THEN '储蓄账户'
                ELSE up.product_name
            END as deposit_type,
            CASE 
                WHEN up.position_type = 'deposit' THEN 3.25
                WHEN up.position_type = 'savings' THEN 0.35
                ELSE 0
            END as annual_rate
        FROM UserPositions up
        WHERE up.user_id = %s AND up.position_type IN ('deposit', 'savings') AND up.status = 'active'
        ORDER BY up.updated_at DESC
        """
        results = db_query(sql, (user_id,))
        
        # 处理数据，确保数值类型正确
        processed_results = []
        for result in results:
            processed_result = dict(result)
            # 转换数值字段
            numeric_fields = ['amount', 'purchase_price', 'current_value', 'total_investment', 'annual_rate']
            for field in numeric_fields:
                if field in processed_result and processed_result[field] is not None:
                    processed_result[field] = float(processed_result[field])
            
            processed_results.append(processed_result)
        
        return processed_results
    
    @staticmethod
    def create_user_position(user_id, position_type, product_code, product_name, shares, purchase_price, purchase_date):
        """创建用户持仓记录
        
        Args:
            user_id: 用户ID
            position_type: 持仓类型
            product_code: 产品代码
            product_name: 产品名称
            shares: 持有份额/金额
            purchase_price: 买入价格
            purchase_date: 买入日期
            
        Returns:
            int: 新记录ID
        """
        # 计算当前市值（简化处理，实际中需要根据最新价格计算）
        current_price = purchase_price
        current_value = shares * current_price
        total_investment = shares * purchase_price
        profit_loss = current_value - total_investment
        profit_loss_percent = (profit_loss / total_investment * 100) if total_investment > 0 else 0
        
        sql = """
        INSERT INTO UserPositions 
        (user_id, position_type, product_code, product_name, shares, purchase_price, current_price, 
         purchase_date, current_value, total_investment, profit_loss, profit_loss_percent)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id, position_type, product_code, product_name, shares, purchase_price, 
            current_price, purchase_date, current_value, total_investment, profit_loss, profit_loss_percent
        )
        
        conn = None
        try:
            from utils.db import get_db_connection, close_db_connection
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor.lastrowid
        finally:
            if conn:
                close_db_connection(conn)
    
    @staticmethod
    def update_user_position(position_id, shares=None, current_price=None):
        """更新用户持仓记录
        
        Args:
            position_id: 持仓记录ID
            shares: 新的持有份额（可选）
            current_price: 当前价格（可选）
            
        Returns:
            int: 影响的行数
        """
        update_fields = []
        params = []
        
        if shares is not None:
            update_fields.append("shares = %s")
            params.append(shares)
        
        if current_price is not None:
            update_fields.append("current_price = %s")
            params.append(current_price)
        
        if not update_fields:
            return 0
        
        # 添加市值和盈亏计算
        update_fields.append("current_value = shares * current_price")
        update_fields.append("total_investment = shares * purchase_price")
        update_fields.append("profit_loss = current_value - total_investment")
        update_fields.append("profit_loss_percent = CASE WHEN total_investment > 0 THEN (profit_loss / total_investment) * 100 ELSE 0 END")
        
        sql = f"UPDATE UserPositions SET {', '.join(update_fields)} WHERE id = %s"
        params.append(position_id)
        
        return db_execute(sql, params)