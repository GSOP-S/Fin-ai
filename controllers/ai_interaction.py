
"""
AI交互控制器
提供统一的AI交互接口，支持多种交互模式和上下文处理
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.ai_service import AIService
from services.home_suggestion_service import HomeSuggestionService
from services.fund_service import FundService
from services.bill_analysis_service import BillAnalysisService
from services.transfer_suggestion_service import TransferSuggestionService
from services.market_analysis_service import market_analysis_service

ai_interaction_bp = Blueprint('ai_interaction', __name__)

ai_service = AIService()

# 统一AI交互接口
@ai_interaction_bp.route('/api/ai/interact', methods=['POST'])
@handle_exceptions
def ai_interact():
    data = request.json or {}
    if not data:
        return error_response(error='请求数据不能为空', status_code=400)

    interaction_type = data.get('interaction_type')
    page_context = data.get('page_context', {})

    if interaction_type == 'chat' or data.get('prompt') is not None:
        message = data.get('message') or data.get('prompt', '')
        context = data.get('context', {}) or page_context.get('data', {})
        response_txt = ai_service.generate_ai_response(message, context)
        return success_response({'response': response_txt, 'interaction_type': 'chat'})

    if interaction_type == 'suggestion':
        page_type = page_context.get('page_type') or data.get('pageType')
        context = {'userId': page_context.get('user_id'), **page_context.get('data', {}), **data.get('context', {})}
        if not page_type:
            return error_response(error='缺少页面类型参数', status_code=400)
        if page_type == 'home':
            result = HomeSuggestionService().generate_home_suggestion_from_context(context)
        elif page_type == 'fund':
            fund_data = context.get('fundData', {})
            fund = {
                'name': fund_data.get('fundName', ''),
                'code': fund_data.get('fundCode', ''),
                'category': fund_data.get('fundType', ''),
                'risk': fund_data.get('riskLevel', ''),
                'nav': fund_data.get('nav', 0),
                'change': fund_data.get('change', ''),
                'changePercent': fund_data.get('changePercent', ''),
                'manager': fund_data.get('manager', '未知基金经理')
            }
            result = FundService().generate_fund_suggestion(fund)
        elif page_type == 'bill':
            result = BillAnalysisService().generate_bill_suggestion(context)
        elif page_type == 'transfer':
            result = TransferSuggestionService().generate_transfer_suggestion_from_context(context)
        elif page_type == 'market':
            result = market_analysis_service.generate_market_suggestion_from_context(context)
        else:
            return error_response(error=f'不支持的页面类型: {page_type}', status_code=400)
        return success_response({'suggestion': result, 'interaction_type': 'suggestion', 'page_type': page_type})

    if interaction_type == 'analysis':
        page_type = page_context.get('page_type') or data.get('pageType')
        context = page_context.get('data', {}) or data.get('context', {})
        if not page_type:
            return error_response(error='缺少页面类型参数', status_code=400)
        if page_type == 'market':
            analysis = market_analysis_service.get_market_overview()
        elif page_type == 'fund':
            fund = context.get('fund', {})
            analysis = FundService().generate_fund_suggestion(fund)
        elif page_type == 'bill':
            analysis = BillAnalysisService().generate_bill_suggestion({'billData': context})
        elif page_type == 'transfer':
            analysis = TransferSuggestionService().generate_transfer_suggestion_from_context(context)
        elif page_type == 'home':
            analysis = HomeSuggestionService().generate_home_suggestion_from_context({'userId': page_context.get('user_id', '')})
        else:
            return error_response(error=f'不支持的页面类型: {page_type}', status_code=400)
        return success_response({'analysis': analysis, 'interaction_type': 'analysis', 'page_type': page_type})

    return error_response(error=f'不支持的交互类型: {interaction_type}', status_code=400)

# AI反馈接口
@ai_interaction_bp.route('/api/ai/feedback', methods=['POST'])
@handle_exceptions
def ai_feedback():
    data = request.json or {}
    if not data:
        return error_response(error='请求数据不能为空', status_code=400)
    # TODO: store feedback
    return success_response(message='感谢您的反馈')

# AI设置接口
@ai_interaction_bp.route('/api/ai/settings', methods=['GET', 'POST'])
@handle_exceptions
def ai_settings():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            return error_response(error='缺少用户ID参数', status_code=400)
        # TODO: retrieve settings
        return success_response({
            'enable_voice': True,
            'auto_suggestions': True,
            'suggestion_frequency': 'medium',
            'preferred_analysis_type': 'summary'
        })
    else:
        data = request.json or {}
        if not data:
            return error_response(error='请求数据不能为空', status_code=400)
        user_id = data.get('user_id')
        settings = data.get('settings', {})
        if not user_id:
            return error_response(error='缺少用户ID参数', status_code=400)
        # TODO: update settings in db
        return success_response(settings, message='设置已更新')