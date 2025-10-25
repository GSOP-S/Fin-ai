"""
首页建议服务 Service
提供首页智能建议的业务逻辑
"""

from mapper.bill_mapper import BillMapper
from mapper.transfer_mapper import TransferMapper
from mapper.user_mapper import UserMapper
from typing import Dict
from datetime import datetime, timedelta


class HomeSuggestionService:
    """首页建议服务类"""
    
    def __init__(self):
        self.bill_mapper = BillMapper()
        self.transfer_mapper = TransferMapper()
        self.user_mapper = UserMapper()
    
    def generate_home_suggestion(self, user_id: str) -> Dict:
        """
        生成首页智能建议
        
        Args:
            user_id: 用户ID
            
        Returns:
            建议结果字典
        """
        # 1. 获取用户信息
        user = self.user_mapper.get_user_by_id(user_id)
        display_name = user['display_name'] if user else '用户'
        
        # 2. 获取本月账单统计
        current_month = datetime.now().strftime('%Y-%m')
        bill_stats = self.bill_mapper.get_bill_statistics(user_id, current_month)
        
        # 3. 获取最近转账统计
        transfer_stats = self.transfer_mapper.get_transfer_statistics(user_id, days=30)
        
        # 4. 生成个性化建议
        suggestions = self._generate_personalized_suggestions(
            bill_stats, transfer_stats, display_name
        )
        
        # 5. 生成快捷操作推荐
        quick_actions = self._recommend_quick_actions(bill_stats, transfer_stats)
        
        # TODO: 接入大模型API，生成更智能的首页建议
        # ai_greeting = self._call_ai_model(user_id, bill_stats, transfer_stats)
        
        return {
            'greeting': f'欢迎回来，{display_name}！',
            'suggestion': suggestions,
            'quickActions': quick_actions,
            'billStats': {
                'totalExpense': bill_stats.get('total_expense', 0),
                'transactionCount': bill_stats.get('total_count', 0)
            },
            'transferStats': {
                'totalAmount': transfer_stats.get('total_amount', 0),
                'transferCount': transfer_stats.get('total_count', 0)
            }
        }
    
    def _generate_personalized_suggestions(self, bill_stats: Dict, 
                                          transfer_stats: Dict,
                                          display_name: str) -> str:
        """生成个性化建议文本"""
        suggestions = []
        
        # 问候语
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = '早上好'
        elif 12 <= hour < 18:
            greeting = '下午好'
        else:
            greeting = '晚上好'
        
        suggestions.append(f'{greeting}，{display_name}！')
        
        # 账单相关建议
        expense = bill_stats.get('total_expense', 0)
        if expense > 5000:
            suggestions.append(f'\n📊 本月已消费 {expense:.2f} 元，建议查看账单明细，合理规划支出')
        elif expense > 0:
            suggestions.append(f'\n💰 本月消费 {expense:.2f} 元，消费合理，请继续保持')
        else:
            suggestions.append('\n💡 本月暂无消费记录，开启理财之旅吧')
        
        # 转账相关建议
        transfer_count = transfer_stats.get('total_count', 0)
        if transfer_count > 10:
            suggestions.append('\n📤 本月转账频繁，建议使用常用账户功能快速转账')
        
        # 理财建议
        suggestions.append('\n🎯 今日推荐：定期存款利率优惠中，点击理财页面查看详情')
        
        return ''.join(suggestions)
    
    def _recommend_quick_actions(self, bill_stats: Dict, transfer_stats: Dict) -> list:
        """推荐快捷操作"""
        actions = []
        
        # 根据用户行为推荐
        if bill_stats.get('total_count', 0) > 0:
            actions.append({
                'title': '查看账单分析',
                'icon': '📊',
                'page': 'account',
                'priority': 1
            })
        
        if transfer_stats.get('total_count', 0) > 0:
            actions.append({
                'title': '快速转账',
                'icon': '💸',
                'page': 'transfer',
                'priority': 2
            })
        
        actions.append({
            'title': '投资理财',
            'icon': '💰',
            'page': 'financing',
            'priority': 3
        })
        
        # 按优先级排序
        actions.sort(key=lambda x: x['priority'])
        
        return actions[:3]
    
    def _call_ai_model(self, user_id: str, bill_stats: Dict, transfer_stats: Dict) -> str:
        """
        调用大模型API生成智能问候
        
        TODO: 接入大模型
        """
        # 预留接口
        return None

