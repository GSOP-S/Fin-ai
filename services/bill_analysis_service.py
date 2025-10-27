"""
账单分析服务 Service
提供账单智能分析的业务逻辑
"""

from mapper.bill_mapper import BillMapper
from typing import Dict, List
import os


class BillAnalysisService:
    """账单分析服务类"""
    
    def __init__(self):
        self.bill_mapper = BillMapper()
    
    def analyze_bills(self, user_id: str, bills: List[Dict], month: str) -> Dict:
        """
        分析用户账单，生成AI建议
        
        Args:
            user_id: 用户ID
            bills: 账单列表（前端传来或从数据库查询）
            month: 分析月份
            
        Returns:
            分析结果字典
        """
        # 如果bills为空，从数据库查询
        if not bills:
            bills = self.bill_mapper.get_bills_by_user(user_id, month)
        
        # 1. 基础统计分析
        summary = self._calculate_summary(bills)
        
        # 2. 类别支出分析
        category_distribution = self._analyze_categories(bills, summary['totalExpense'])
        
        # 3. 异常交易检测
        abnormal_transactions = self._detect_abnormal_transactions(bills, summary['totalExpense'])
        
        # 4. 生成优化建议
        suggestions = self._generate_suggestions(summary, category_distribution, abnormal_transactions)
        
        # TODO: 接入大模型API，生成更智能的分析
        # ai_insights = self._call_ai_model(summary, category_distribution, bills)
        ai_insights = self._call_ai_model(summary, category_distribution, bills)
        if ai_insights:
            suggestions = ai_insights
        
        return {
            'summary': summary,
            'categoryDistribution': category_distribution,
            'abnormalTransactions': abnormal_transactions,
            'suggestions': suggestions
        }
    
    def _calculate_summary(self, bills: List[Dict]) -> Dict:
        """计算账单汇总数据"""
        total_income = sum(bill['amount'] for bill in bills if bill['amount'] > 0)
        total_expense = sum(abs(bill['amount']) for bill in bills if bill['amount'] < 0)
        
        saving_rate = 0
        if total_income > 0:
            saving_rate = round((total_income - total_expense) / total_income * 100, 1)
        
        return {
            'totalIncome': round(total_income, 2),
            'totalExpense': round(total_expense, 2),
            'savingRate': saving_rate,
            'transactionCount': len(bills)
        }
    
    def _analyze_categories(self, bills: List[Dict], total_expense: float) -> List[Dict]:
        """分析各类别支出"""
        category_expenses = {}
        
        for bill in bills:
            if bill['amount'] < 0:
                category = bill.get('category', '其他')
                amount = abs(bill['amount'])
                category_expenses[category] = category_expenses.get(category, 0) + amount
        
        # 排序并计算百分比
        sorted_categories = sorted(
            category_expenses.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # 取前5个类别
        
        result = []
        for category, amount in sorted_categories:
            percentage = round(amount / total_expense * 100, 1) if total_expense > 0 else 0
            result.append({
                'category': category,
                'amount': round(amount, 2),
                'percentage': percentage
            })
        
        return result
    
    def _detect_abnormal_transactions(self, bills: List[Dict], total_expense: float) -> List[Dict]:
        """检测异常交易"""
        abnormal = []
        threshold = total_expense * 0.3  # 超过总支出30%视为异常
        
        for bill in bills:
            if bill['amount'] < 0:
                amount = abs(bill['amount'])
                reason = None
                
                # 检测规则
                if amount > threshold:
                    reason = f'超过月总支出{round(amount/total_expense*100, 1)}%'
                elif bill.get('category') == '餐饮' and amount > 200:
                    reason = '单次餐饮消费过高'
                elif bill.get('category') == '购物' and amount > 1000:
                    reason = '单次购物消费过高'
                
                if reason:
                    abnormal.append({
                        'id': bill.get('id'),
                        'merchant': bill.get('merchant', '未知商户'),
                        'amount': -amount,  # 保持负数显示
                        'date': bill.get('transaction_date', bill.get('date', '')),
                        'reason': reason
                    })
        
        return sorted(abnormal, key=lambda x: abs(x['amount']), reverse=True)[:5]
    
    def _generate_suggestions(self, summary: Dict, categories: List[Dict], 
                             abnormal: List[Dict]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 储蓄率建议
        if summary['savingRate'] < 20:
            suggestions.append('💰 您的储蓄率较低（低于20%），建议控制非必要开支，提高储蓄比例至30%以上。')
        elif summary['savingRate'] > 50:
            suggestions.append('👍 您的储蓄率表现优秀！可以考虑将部分储蓄用于投资理财。')
        
        # 类别支出建议
        for cat in categories[:3]:
            if cat['percentage'] > 35:
                suggestions.append(f'⚠️ {cat["category"]}支出占比过高（{cat["percentage"]}%），建议适当控制该类消费。')
        
        # 异常交易建议
        if len(abnormal) > 0:
            suggestions.append(f'🔍 本月检测到{len(abnormal)}笔异常大额消费，建议核实是否为本人操作。')
        
        # 消费习惯建议
        if summary['transactionCount'] > 100:
            suggestions.append('📊 您的交易频次较高，建议使用预算管理工具，更好地控制日常开支。')
        
        return suggestions[:5]  # 最多返回5条建议
    
    def _call_ai_model(self, summary: Dict, categories: List[Dict], bills: List[Dict]) -> str:
        """
        调用大模型API生成智能分析，失败时返回 None
        """
        try:
            from services.model_provider import ModelProvider  # 延迟导入避免循环
            model = ModelProvider()
            prompt = (
                "请根据以下账单摘要与分类，给出3条专业的理财建议（每条不超过40字，中文）：\n"
                f"摘要：收入 {summary.get('totalIncome')} 元，支出 {summary.get('totalExpense')} 元，"\
                f"节余率 {summary.get('savingRate')}%，交易笔数 {summary.get('transactionCount')}。\n"\
                f"主要支出类别：{[c.get('category') for c in categories]}"
            )
            return model.generate(prompt, context={"type": "bill"})
        except Exception as exc:
            print(f"[BillAnalysisService] AI 调用失败: {exc}")
            return None

