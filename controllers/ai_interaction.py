
"""
AI交互控制器
提供统一的AI交互接口，支持多种交互模式和上下文处理
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.ai_service import AIService

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

    if interaction_type == 'chat':
        message = data.get('message', '')
        history = data.get('history', [])  # 未使用但保留
        context = page_context.get('data', {})
        response_txt = ai_service.generate_ai_response(message, context)
        return success_response({
            'response': response_txt,
            'interaction_type': 'chat'
        })

    elif interaction_type == 'suggestion':
        page_type = page_context.get('page_type')
        context = {
            'userId': page_context.get('user_id'),
            **page_context.get('data', {})
        }
        if not page_type:
            return error_response(error='缺少页面类型参数', status_code=400)
        suggestion = ai_service.get_page_suggestions(page_type, context)
        return success_response({
            'suggestion': suggestion,
            'interaction_type': 'suggestion',
            'page_type': page_type
        })

    elif interaction_type == 'analysis':
        page_type = page_context.get('page_type')
        context = page_context.get('data', {})
        if not page_type:
            return error_response(error='缺少页面类型参数', status_code=400)
        if page_type == 'market':
            analysis = ai_service.generate_market_analysis()
        
        elif page_type == 'fund':
            analysis = ai_service.generate_fund_suggestion(context.get('fund', {}))
        elif page_type == 'bill':
            analysis = ai_service.generate_bill_suggestion({'billData': context})
        elif page_type == 'transfer':
            analysis = ai_service.generate_transfer_suggestion({'transferData': context})
        elif page_type == 'home':
            analysis = ai_service.generate_home_suggestion({'userId': page_context.get('user_id', '')})
        else:
            return error_response(error=f'不支持的页面类型: {page_type}', status_code=400)
        return success_response({
            'analysis': analysis,
            'interaction_type': 'analysis',
            'page_type': page_type
        })
    else:
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