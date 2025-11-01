import json

from services.data_service import DataService
from services.model_provider import ModelProvider


class AIService:
    """统一的AI服务层，集中管理所有AI相关功能"""
    
    def __init__(self):
        # 聚合数据服务与模型提供者
        self.data_service = DataService()
        self.model = ModelProvider()
    
    def generate_ai_response(self, prompt, context=None):
        """
        根据用户提示和上下文生成AI回复
        
        Args:
            prompt: 用户输入的提示
            context: 上下文信息，可能包含基金数据等
            
        Returns:
            生成的AI回复文本
        """
        fund_name = context.get('fundData', {}).get('name') if context else None

        # 处理基金相关查询
        if fund_name:
            return self._generate_fund_analysis(fund_name)
        
        # 通用回复逻辑
        if '基金' in prompt:
            return "您好！我是基金智能助手。请告诉我您想了解哪只基金，我可以为您提供详细分析。"
        elif '买入' in prompt or '卖出' in prompt:
            return "投资决策需要综合考虑多方面因素，建议您在做出投资决策前，充分了解相关风险。"
        else:
            return "您好！我是您的智能助手，请问有什么可以帮助您的？"

    
    def _generate_fund_analysis(self, fund_name):
        """生成基金分析报告"""
        fund_info = self.data_service.get_fund_by_code(fund_name)
        if not fund_info:
            return "未找到该基金的相关信息。"

        response = (
            f"关于{fund_info['name']}({fund_info['code']})的分析：\n"
            f"- 基金类型：{fund_info.get('category', '未知')}\n"
            f"- 基金经理：{fund_info.get('manager', '未知')}\n"
            f"- 风险等级：{fund_info.get('risk', '未知')}\n"
            f"- 当前净值：{fund_info.get('nav', '未知')}\n"
            f"- 近一年涨跌幅：{fund_info.get('changePercent', '未知')}\n\n"
        )

        # 基金类型特定建议
        fund_type_suggestions = {
            '混合型': '混合型基金风险适中，兼顾稳定性和收益性，适合大部分投资者配置。',
            '债券型': '债券型基金风险较低，收益相对稳定，适合风险承受能力较弱的投资者。',
            '货币型': '货币型基金风险最低，流动性最好，适合短期资金停泊。',
            'QDII': 'QDII基金投资海外市场，有助于分散投资风险，但需注意汇率风险。'
        }
        response += fund_type_suggestions.get(fund_info.get('category', ''), '该类型基金暂无特定分析建议。')
        return response
    
    def get_page_suggestions(self, page_type, context=None):
        """
        获取页面特定的AI建议
        
        Args:
            page_type: 页面类型，如'home', 'fund', 'bill', 'transfer', 'market'等
            context: 上下文信息，可能包含用户ID、页面数据等
            
        Returns:
            页面相关的AI建议
        """
        try:
            # 1. 优先从数据库读取预设/缓存的建议
            record = self.data_service.get_ai_suggestion(page_type, 'default')
            if record and record.get('content'):
                raw_content = record['content']
                try:
                    return json.loads(raw_content)
                except Exception:
                    return {'suggestion': raw_content}

            # 2. 如果数据库无数据，则动态生成
            if page_type == 'home':
                suggestion = self.generate_home_suggestion(context or {})
            elif page_type == 'fund':
                suggestion = self.generate_fund_suggestion((context or {}).get('fund', {}))
            elif page_type == 'bill':
                suggestion = self.generate_bill_suggestion(context or {})
            elif page_type == 'transfer':
                suggestion = self.generate_transfer_suggestion(context or {})
            elif page_type == 'market':
                suggestion = self.generate_market_analysis()
            else:
                suggestion = {'suggestion': '暂无相关建议'}

            # 3. 异步写入数据库，方便下次读取（忽略错误）
            try:
                self.data_service.upsert_ai_suggestion(page_type, 'default', json.dumps(suggestion, ensure_ascii=False))
            except Exception:
                pass

            return suggestion
        except Exception as e:
            print(f"获取AI建议失败: {str(e)}")
            return {'suggestion': '获取建议时出现错误'}
    
    def generate_market_analysis(self):
        """
        生成市场分析
        返回格式化的市场分析文本
        """
        # 模拟市场分析数据
        analysis = {
            "marketOverview": '今日基金市场整体表现良好，各类基金指数普遍上涨。市场成交量有所放大，资金净流入超50亿元。',
            "hotSectors": ['新能源', '半导体', '医药生物'],
            "recommendedFunds": [
                { "name": '易方达蓝筹精选混合', "code": '005827', "reason": '绩优混合型基金，长期表现稳健，适合长期持有' },
                { "name": '诺安成长混合', "code": '320007', "reason": '成长型基金，投资于高成长性行业，波动较大但收益潜力高' },
                { "name": '华夏回报混合A', "code": '002001', "reason": '平衡型基金，风险收益均衡，适合稳健型投资者' }
            ]
        }

        # 构建分析文本
        analysis_text = f"市场分析：{analysis['marketOverview']}\n\n热门板块：{'、'.join(analysis['hotSectors'])}\n\n"
        analysis_text += '为您推荐以下基金：\n'
        for i, fund in enumerate(analysis['recommendedFunds']):
            analysis_text += f"{i + 1}. {fund['name']} ({fund['code']}) - {fund['reason']}\n"

        return {'analysis': analysis_text, 'data': analysis}
    
    def generate_fund_suggestion(self, fund):
        """
        根据基金信息生成投资建议
        
        Args:
            fund: 包含基金信息的字典
        Returns:
            格式化的建议文本
        """
        if not fund:
            return {'suggestion': ''}
        
        name = fund.get('name', '')
        code = fund.get('code', '')
        change = fund.get('change', '')
        change_percent = fund.get('changePercent', '')
        manager = fund.get('manager', '')
        risk = fund.get('risk', '')
        
        trend = '上涨' if str(change).startswith('+') else '下跌'
        suggestion = f"基金建议：{name} ({code}) 目前{trend} {change_percent}，由{manager}管理，风险等级为{risk}。建议关注其近期表现和基金经理的投资风格。"
        
        return {'suggestion': suggestion, 'fund': fund}
    
    def generate_bill_suggestion(self, context):
        """
        生成账单分析和建议
        
        Args:
            context: 包含账单数据的上下文
        Returns:
            账单分析和建议
        """
        bill_data = context.get('billData', {})
        if not bill_data:
            return {'suggestion': '暂无账单数据，无法生成分析'}
        
        # 模拟账单分析
        suggestions = []
        
        # 储蓄率建议
        saving_rate = bill_data.get('savingRate', 0)
        if saving_rate < 20:
            suggestions.append('💰 您的储蓄率较低（低于20%），建议控制非必要开支，提高储蓄比例至30%以上。')
        elif saving_rate > 50:
            suggestions.append('👍 您的储蓄率表现优秀！可以考虑将部分储蓄用于投资理财。')
        
        # 类别支出建议
        categories = bill_data.get('categories', [])
        for cat in categories[:3]:
            if cat.get('percentage', 0) > 35:
                suggestions.append(f"⚠️ {cat.get('category', '某类别')}支出占比过高（{cat.get('percentage', 0)}%），建议适当控制该类消费。")
        
        # 异常交易建议
        abnormal = bill_data.get('abnormalItems', [])
        if len(abnormal) > 0:
            suggestions.append(f'🔍 本月检测到{len(abnormal)}笔异常大额消费，建议核实是否为本人操作。')
        
        # 消费习惯建议
        transaction_count = bill_data.get('transactionCount', 0)
        if transaction_count > 100:
            suggestions.append('📊 您的交易频次较高，建议使用预算管理工具，更好地控制日常开支。')
        
        suggestion_text = '\n'.join(suggestions[:5])  # 最多返回5条建议
        
        return {
            'suggestion': suggestion_text,
            'analysis': {
                'suggestions': suggestions[:5],
                'savingRate': saving_rate,
                'categories': categories,
                'abnormalItems': abnormal
            }
        }
    
    def generate_transfer_suggestion(self, context):
        """
        生成转账建议
        
        Args:
            context: 包含转账信息的上下文
        Returns:
            转账建议
        """
        transfer_data = context.get('transferData', {})
        if not transfer_data:
            return {'suggestion': '请输入转账信息以获取建议'}
        
        recipient_account = transfer_data.get('recipientAccount', '')
        account_type = transfer_data.get('accountType', 'other_bank')
        is_first_time = transfer_data.get('isFirstTimeAccount', True)
        recent_accounts = transfer_data.get('recentAccounts', [])
        amount = transfer_data.get('amount', 0)
        
        # 确定到账时间
        arrival_time = '实时到账' if account_type == 'same_bank' else '1-2个工作日'
        
        # 确定手续费建议
        fee_suggestion = '免手续费' if account_type == 'same_bank' else '跨行转账可能产生手续费，建议查看详细费率'
        
        # 确定风险等级
        risk_level = 'high' if is_first_time else 'low'
        if amount > 50000:
            risk_level = 'medium' if risk_level == 'low' else 'high'
        
        # 生成建议文本
        suggestion = ''
        if account_type == 'same_bank':
            suggestion = f"本行账户转账{arrival_time}，{fee_suggestion}。"
        else:
            suggestion = f"跨行转账预计{arrival_time}，{fee_suggestion}。"
        
        if is_first_time:
            suggestion += " 首次向该账户转账，请核实账户信息，注意防范诈骗风险。"
        
        if amount > 50000:
            suggestion += f" 大额转账（{amount}元）请确认无误后再操作。"
        
        return {
            'suggestion': suggestion,
            'recentAccounts': recent_accounts,
            'arrivalTime': arrival_time,
            'accountType': account_type,
            'riskLevel': risk_level,
            'feeSuggestion': fee_suggestion
        }
    
    def generate_home_suggestion(self, context):
        """
        生成首页个性化建议
        
        Args:
            context: 包含用户信息的上下文
        Returns:
            首页个性化建议
        """
        user_id = context.get('userId', '')
        if not user_id:
            return {'suggestion': '欢迎使用智能银行，请登录以获取个性化服务。'}
        
        # 模拟获取用户数据
        user_data = self._get_user_data(user_id)
        
        # 生成个性化建议
        greeting = f"您好，{user_data.get('name', '尊敬的用户')}！"
        
        suggestions = []
        
        # 账户余额提示
        balance = user_data.get('balance', 0)
        if balance > 100000:
            suggestions.append(f"您的账户余额较高（{balance}元），可考虑适当理财以提高资金收益。")
        elif balance < 1000:
            suggestions.append(f"您的账户余额较低（{balance}元），请注意及时充值以确保正常使用。")
        
        # 最近交易提示
        recent_transactions = user_data.get('recentTransactions', [])
        if recent_transactions:
            latest = recent_transactions[0]
            suggestions.append(f"您最近的交易：{latest.get('type', '')} {latest.get('amount', 0)}元 ({latest.get('time', '')})。")
        
        # 理财产品推荐
        if user_data.get('riskPreference', '') == 'conservative':
            suggestions.append("根据您的风险偏好，推荐稳健型理财产品：XX银行定期存款（年化3.5%）。")
        elif user_data.get('riskPreference', '') == 'moderate':
            suggestions.append("根据您的风险偏好，推荐平衡型基金：XX平衡混合基金（近一年收益率8.5%）。")
        else:
            suggestions.append("根据您的风险偏好，推荐进取型基金：XX科技成长基金（近一年收益率15.2%）。")
        
        # 组合建议文本
        suggestion_text = greeting + "\n" + "\n".join(suggestions)
        
        # 推荐快捷操作
        quick_actions = self._recommend_quick_actions(user_data)
        
        return {
            'suggestion': suggestion_text,
            'greeting': greeting,
            'suggestions': suggestions,
            'quickActions': quick_actions
        }
    
    def _get_user_data(self, user_id):
        """模拟获取用户数据"""
        # 实际应用中应从数据库获取
        return {
            'name': '张先生',
            'balance': 85000,
            'riskPreference': 'moderate',
            'recentTransactions': [
                {'type': '消费', 'amount': 253.5, 'time': '今天 14:30'},
                {'type': '转账', 'amount': 5000, 'time': '昨天 10:15'},
                {'type': '理财购买', 'amount': 10000, 'time': '3天前'}
            ],
            'billStats': {
                'total_count': 28,
                'total_amount': 8523.5
            },
            'transferStats': {
                'total_count': 5,
                'total_amount': 25000
            }
        }
    
    def _recommend_quick_actions(self, user_data):
        """推荐快捷操作"""
        actions = []
        
        # 根据用户行为推荐
        bill_stats = user_data.get('billStats', {})
        transfer_stats = user_data.get('transferStats', {})
        
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


# 创建单例实例
ai_service = AIService()

# 导出函数接口，便于其他模块调用
# TODO: 这些包装函数是冗余的，建议Controller直接使用 ai_service.方法名()
def generate_ai_response(prompt, context=None):
    return ai_service.generate_ai_response(prompt, context)

def get_page_suggestions(page_type, context=None):
    return ai_service.get_page_suggestions(page_type, context)

def generate_market_analysis():
    return ai_service.generate_market_analysis()

def generate_fund_suggestion(fund):
    return ai_service.generate_fund_suggestion(fund)

def generate_bill_suggestion(context):
    return ai_service.generate_bill_suggestion(context)

def generate_transfer_suggestion(context):
    return ai_service.generate_transfer_suggestion(context)

def generate_home_suggestion(context):
    return ai_service.generate_home_suggestion(context)