"""
转账建议服务 Service
提供转账智能建议的业务逻辑
"""

from mapper.transfer_mapper import TransferMapper
from typing import Dict, List


class TransferSuggestionService:
    """转账建议服务类"""
    
    def __init__(self):
        self.transfer_mapper = TransferMapper()
    
    def generate_transfer_suggestion(self, user_id: str, context: Dict) -> Dict:
        """
        生成转账智能建议
        
        Args:
            user_id: 用户ID
            context: 转账上下文信息
                - recipientAccount: 收款账户
                - accountType: 账户类型（'same_bank' | 'other_bank'）
                - isFirstTimeAccount: 是否首次转账
                - amount: 转账金额（可选）
                
        Returns:
            建议结果字典
        """
        recipient_account = context.get('recipientAccount', '')
        account_type = context.get('accountType', '')
        is_first_time = context.get('isFirstTimeAccount', False)
        amount = context.get('amount', 0)
        
        # 1. 获取最近转账账户
        recent_accounts = self._get_recent_accounts_formatted(user_id)
        
        # 2. 评估风险等级
        risk_level = self._assess_risk(user_id, recipient_account, is_first_time, amount)
        
        # 3. 计算到账时间
        arrival_time = self._calculate_arrival_time(account_type, amount)
        
        # 4. 生成建议文本
        suggestion = self._generate_suggestion_text(
            account_type, is_first_time, risk_level, amount
        )
        
        # 5. 手续费建议
        fee_suggestion = self._get_fee_suggestion(account_type, amount)
        
        # TODO: 接入大模型API，生成更个性化的建议
        # ai_suggestion = self._call_ai_model(user_id, context, risk_level)
        ai_suggestion = self._call_ai_model(user_id, context, risk_level)
        if ai_suggestion:
            suggestion = ai_suggestion
        
        return {
            'recentAccounts': recent_accounts,
            'arrivalTime': arrival_time,
            'suggestion': suggestion,
            'accountType': account_type,
            'riskLevel': risk_level,
            'feeSuggestion': fee_suggestion
        }
    
    def _get_recent_accounts_formatted(self, user_id: str) -> List[Dict]:
        """获取格式化的最近转账账户"""
        accounts = self.transfer_mapper.get_recent_accounts(user_id, limit=5)
        
        result = []
        for acc in accounts:
            result.append({
                'id': acc.get('recipient_account'),
                'name': acc.get('recipient_name', '未知'),
                'accountNumber': self._mask_account_number(acc.get('recipient_account', '')),
                'lastTransfer': str(acc.get('last_transfer_date', '')),
                'transferCount': acc.get('transfer_count', 0)
            })
        
        return result
    
    def _mask_account_number(self, account: str) -> str:
        """脱敏账号"""
        if len(account) <= 8:
            return account
        return account[:4] + '****' + account[-4:]
    
    def _assess_risk(self, user_id: str, recipient_account: str, 
                    is_first_time: bool, amount: float) -> str:
        """
        评估转账风险等级
        
        Returns:
            'low' | 'medium' | 'high'
        """
        # 检查历史记录
        has_history = self.transfer_mapper.check_account_exists(user_id, recipient_account)
        
        # 风险评分
        risk_score = 0
        
        if is_first_time or not has_history:
            risk_score += 3  # 首次转账风险高
        
        if amount > 10000:
            risk_score += 2  # 大额转账风险较高
        elif amount > 5000:
            risk_score += 1
        
        # 根据评分返回风险等级
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_arrival_time(self, account_type: str, amount: float) -> str:
        """计算到账时间"""
        if account_type == 'same_bank':
            return '实时到账'
        else:
            # 跨行转账
            if amount > 50000:
                return '预计2-4小时'
            else:
                return '预计1-2小时'
    
    def _generate_suggestion_text(self, account_type: str, is_first_time: bool,
                                  risk_level: str, amount: float) -> str:
        """生成建议文本"""
        suggestions = []
        
        # 风险提示
        if risk_level == 'high':
            suggestions.append('⚠️ 该笔转账存在一定风险')
            if is_first_time:
                suggestions.append('该账户为新账户，建议仔细核实收款人姓名和账户信息')
        
        # 账户类型建议
        if account_type == 'same_bank':
            suggestions.append('✅ 本行账户转账实时到账，无手续费')
        else:
            suggestions.append('💡 跨行转账可能产生手续费')
            suggestions.append('建议选择次日到账以节省手续费')
        
        # 金额建议
        if amount > 50000:
            suggestions.append('💰 大额转账建议分批操作，降低风险')
        
        return '\n'.join(suggestions) if suggestions else '建议核实收款人信息后转账'
    
    def _get_fee_suggestion(self, account_type: str, amount: float) -> str:
        """获取手续费建议"""
        if account_type == 'same_bank':
            return '本行转账免手续费'
        else:
            if amount < 5000:
                return '建议选择实时到账，手续费约2元'
            elif amount < 50000:
                return '建议选择次日到账，可免手续费'
            else:
                return '大额跨行转账建议咨询客服获取最优方案'
    
    def _call_ai_model(self, user_id: str, context: Dict, risk_level: str) -> str:
        """
        调用大模型API生成智能建议，失败时返回 None
        """
        try:
            from services.model_provider import ModelProvider
            model = ModelProvider()
            prompt = (
                "你是一名资深金融理财助手，请根据以下转账场景给出3条精炼的转账建议（每条不超过40字，中文）：\n"\
                f"收款账户: {context.get('recipientAccount')}，账户类型: {context.get('accountType')}，"\
                f"首次转账: {context.get('isFirstTimeAccount')}，金额: {context.get('amount')} 元，风险等级: {risk_level}。"
            )
            return model.generate(prompt, context={"type": "transfer"})
        except Exception as exc:
            print(f"[TransferSuggestionService] AI 调用失败: {exc}")
            return None

