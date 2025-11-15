"""资产页面服务层"""

from mapper.user_position_mapper import UserPositionMapper
from services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)


class AssetService:
    """资产页面服务类"""
    
    @staticmethod
    def get_portfolio_summary(user_id):
        """获取投资组合汇总信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 投资组合汇总数据
        """
        try:
            summary = UserPositionMapper.get_user_portfolio_summary(user_id)
            
            # 添加一些额外的计算字段
            if summary:
                overall = summary.get('overall', {})
                
                # 计算风险等级（简化处理）
                risk_level = AssetService._calculate_risk_level(summary)
                overall['risk_level'] = risk_level
                
                # 计算资产配置比例
                config_ratios = AssetService._calculate_allocation_ratios(summary)
                overall['allocation_ratios'] = config_ratios
                
                summary['overall'] = overall
            
            return summary
            
        except Exception as e:
            logger.error(f"获取投资组合汇总失败: {str(e)}")
            raise
    
    @staticmethod
    def get_fund_positions(user_id):
        """获取基金持仓列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 基金持仓列表
        """
        try:
            fund_positions = UserPositionMapper.get_user_fund_positions(user_id)
            
            # 为每个基金持仓添加额外信息
            for position in fund_positions:
                # 计算盈亏状态
                position['profit_status'] = AssetService._get_profit_status(position.get('profit_loss', 0))
                
                # 计算持有时间
                position['holding_days'] = AssetService._calculate_holding_days(position.get('purchase_date'))
                
                # 计算收益率等级
                position['return_level'] = AssetService._get_return_level(position.get('profit_loss_percent', 0))
            
            return fund_positions
            
        except Exception as e:
            logger.error(f"获取基金持仓列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_deposit_positions(user_id):
        """获取存款和储蓄持仓列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 存款/储蓄持仓列表
        """
        try:
            deposit_positions = UserPositionMapper.get_user_deposit_positions(user_id)
            
            # 为每个存款/储蓄持仓添加额外信息
            for position in deposit_positions:
                # 计算预期收益
                position['expected_interest'] = AssetService._calculate_expected_interest(
                    position.get('amount', 0),
                    position.get('annual_rate', 0),
                    position.get('purchase_date')
                )
                
                # 计算持有时间
                position['holding_days'] = AssetService._calculate_holding_days(position.get('purchase_date'))
                
                # 添加到期信息
                position['maturity_info'] = AssetService._get_maturity_info(position)
            
            return deposit_positions
            
        except Exception as e:
            logger.error(f"获取存款/储蓄持仓列表失败: {str(e)}")
            raise
    
    @staticmethod
    def generate_ai_analysis(portfolio_summary, fund_positions, deposit_positions):
        """生成资产AI分析建议
        
        Args:
            portfolio_summary: 投资组合汇总
            fund_positions: 基金持仓
            deposit_positions: 存款/储蓄持仓
            
        Returns:
            dict: AI分析结果
        """
        try:
            # 构建分析上下文
            context = {
                'portfolio_summary': portfolio_summary,
                'fund_positions': fund_positions,
                'deposit_positions': deposit_positions,
                'total_funds': len(fund_positions),
                'total_deposits': len(deposit_positions)
            }
            
            # 生成AI分析建议
            ai_service = AIService()
            analysis_result = ai_service.generate_asset_analysis(context)
            
            # 添加额外的分析维度
            analysis_result.update(AssetService._generate_additional_analysis(context))
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"生成AI资产分析失败: {str(e)}")
            # 返回基本的分析结果
            return AssetService._get_fallback_analysis()
    
    @staticmethod
    def _calculate_risk_level(summary):
        """计算投资组合风险等级"""
        try:
            if not summary:
                return "低风险"
            
            fund_data = summary.get('fund', {})
            deposit_data = summary.get('deposit', {})
            savings_data = summary.get('savings', {})
            
            total_value = fund_data.get('total_value', 0) + deposit_data.get('total_value', 0) + savings_data.get('total_value', 0)
            
            if total_value == 0:
                return "低风险"
            
            fund_ratio = fund_data.get('total_value', 0) / total_value
            deposit_ratio = deposit_data.get('total_value', 0) / total_value
            savings_ratio = savings_data.get('total_value', 0) / total_value
            
            # 简单的风险计算
            if fund_ratio > 0.7:
                return "高风险"
            elif fund_ratio > 0.4:
                return "中风险"
            else:
                return "低风险"
                
        except Exception as e:
            logger.error(f"计算风险等级失败: {str(e)}")
            return "低风险"
    
    @staticmethod
    def _calculate_allocation_ratios(summary):
        """计算资产配置比例"""
        try:
            if not summary:
                return {}
            
            allocation = {}
            overall = summary.get('overall', {})
            total_value = overall.get('total_value', 0)
            
            if total_value > 0:
                for asset_type in ['fund', 'deposit', 'savings']:
                    type_data = summary.get(asset_type, {})
                    type_value = type_data.get('total_value', 0)
                    allocation[asset_type] = round((type_value / total_value) * 100, 2)
            else:
                # 如果总价值为0，返回默认比例
                allocation = {'fund': 0, 'deposit': 0, 'savings': 0}
            
            return allocation
            
        except Exception as e:
            logger.error(f"计算资产配置比例失败: {str(e)}")
            return {'fund': 0, 'deposit': 0, 'savings': 0}
    
    @staticmethod
    def _get_profit_status(profit_loss):
        """获取盈亏状态"""
        if profit_loss > 0:
            return "盈利"
        elif profit_loss < 0:
            return "亏损"
        else:
            return "持平"
    
    @staticmethod
    def _calculate_expected_interest(amount, annual_rate, purchase_date):
        """计算预期收益"""
        try:
            if not amount or not annual_rate or not purchase_date:
                return 0
            
            from datetime import datetime, date
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            
            today = date.today()
            days = (today - purchase_date).days
            # 简单计算：本金 * 年利率 * 持有天数 / 365
            expected_interest = float(amount) * float(annual_rate) * days / 365
            return round(expected_interest, 2)
            
        except Exception as e:
            logger.error(f"计算预期收益失败: {str(e)}")
            return 0
    
    @staticmethod
    def _get_maturity_info(position):
        """获取到期信息"""
        try:
            maturity_date = position.get('maturity_date')
            if not maturity_date:
                return {"is_matured": False, "days_to_maturity": None}
            
            from datetime import datetime, date
            if isinstance(maturity_date, str):
                maturity_date = datetime.strptime(maturity_date, '%Y-%m-%d').date()
            
            today = date.today()
            days_to_maturity = (maturity_date - today).days
            
            return {
                "is_matured": days_to_maturity <= 0,
                "days_to_maturity": days_to_maturity if days_to_maturity > 0 else 0,
                "maturity_date": maturity_date.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"获取到期信息失败: {str(e)}")
            return {"is_matured": False, "days_to_maturity": None}
    
    @staticmethod
    def _generate_additional_analysis(context):
        """生成额外的分析维度"""
        try:
            portfolio_summary = context.get('portfolio_summary', {})
            fund_positions = context.get('fund_positions', [])
            deposit_positions = context.get('deposit_positions', [])
            
            # 计算投资组合多样性
            diversity_score = min(len(fund_positions) + len(deposit_positions), 10) / 10
            
            # 计算投资集中度（前三大持仓占比）
            all_positions = fund_positions + deposit_positions
            if all_positions:
                sorted_positions = sorted(all_positions, key=lambda x: x.get('current_value', 0), reverse=True)
                top3_value = sum(p.get('current_value', 0) for p in sorted_positions[:3])
                total_value = sum(p.get('current_value', 0) for p in all_positions)
                concentration = (top3_value / total_value * 100) if total_value > 0 else 0
            else:
                concentration = 0
            
            # 计算流动性评分（简化处理）
            liquidity_score = 0.7  # 基础流动性评分
            
            return {
                'diversity_score': round(diversity_score, 2),
                'concentration': round(concentration, 2),
                'liquidity_score': round(liquidity_score, 2)
            }
            
        except Exception as e:
            logger.error(f"生成额外分析失败: {str(e)}")
            return {
                'diversity_score': 0.5,
                'concentration': 0,
                'liquidity_score': 0.5
            }
    
    @staticmethod
    def _get_fallback_analysis():
        """获取备用分析结果"""
        return {
            'overall_assessment': '投资组合表现稳定，建议继续保持当前投资策略。',
            'risk_assessment': '当前投资组合风险适中。',
            'recommendations': [
                '定期检查投资组合表现',
                '考虑适当增加投资多样性',
                '保持合理的资产配置比例'
            ],
            'diversity_score': 0.5,
            'concentration': 0,
            'liquidity_score': 0.5
        }
    
    @staticmethod
    def _get_return_level(profit_loss_percent):
        """获取收益率等级"""
        if profit_loss_percent > 20:
            return "优秀"
        elif profit_loss_percent > 10:
            return "良好"
        elif profit_loss_percent > 0:
            return "一般"
        elif profit_loss_percent > -10:
            return "较差"
        else:
            return "差"
    
    @staticmethod
    def _calculate_holding_days(purchase_date):
        """计算持有天数"""
        try:
            if not purchase_date:
                return 0
            
            from datetime import datetime, date
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            
            today = date.today()
            return (today - purchase_date).days
            
        except Exception as e:
            logger.error(f"计算持有天数失败: {str(e)}")
            return 0