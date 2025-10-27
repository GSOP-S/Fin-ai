from flask import Blueprint, request
from services.ai_service import AIService
from utils.response import success_response, error_response, handle_exceptions

# 移除旧的 utils.db 和 generate_* 函数导入
from services.ai_service import (
    generate_ai_response, 
    get_page_suggestions,
    generate_market_analysis,
    generate_stock_suggestion,
    generate_fund_suggestion,
    generate_bill_suggestion,
    generate_transfer_suggestion,
    generate_home_suggestion
)
from utils.db import get_db_connection, close_db_connection

# 初始化Blueprint
ai_bp = Blueprint('ai', __name__)

ai_service = AIService()

# 兼容旧路径：AI助手对话接口
@ai_bp.route('/api/ai-assistant', methods=['POST'])
@ai_bp.route('/api/ai/interact', methods=['POST'])  # 新路径，供前端统一使用
@handle_exceptions
def ai_assistant_api():
    data = request.json or {}
    prompt = data.get('prompt', '')
    context = data.get('context', {})
    response_text = ai_service.generate_ai_response(prompt, context)
    return success_response(response_text)

# 获取特定页面的AI建议（GET 旧版本，POST 新版本）
@ai_bp.route('/api/ai-suggestions/<page_type>', methods=['GET'])  # 旧路径，兼容
@ai_bp.route('/api/ai/suggestion', methods=['POST'])  # 新路径，前端传入 pageType
@handle_exceptions
def get_ai_suggestions(page_type=None):
    if request.method == 'GET':
        # 保持旧接口：/api/ai-suggestions/<page_type>
        context = {}
        target_page = page_type
    else:
        # 新接口：/api/ai/suggestion
        data = request.json or {}
        target_page = data.get('pageType')
        context = data.get('context', {}) or {}

    if not target_page:
        return error_response('缺少 pageType 参数', status_code=400)

    suggestions = ai_service.get_page_suggestions(target_page, context)
    return success_response(suggestions)

# 市场分析接口
@ai_bp.route('/api/market-analysis', methods=['GET'])
@handle_exceptions
def market_analysis_api():
    analysis = ai_service.generate_market_analysis()
    return success_response(analysis)

# 股票建议接口
@ai_bp.route('/api/stock-suggestion', methods=['GET'])
@handle_exceptions
def stock_suggestion_api():
    stock_code = request.args.get('code')
    if not stock_code:
        return error_response('缺少股票代码参数', status_code=400)
    suggestion = ai_service.generate_stock_suggestion(stock_code)
    return success_response(suggestion)

# 基金建议接口
@ai_bp.route('/api/fund-suggestion', methods=['GET'])
@handle_exceptions
def fund_suggestion_api():
    fund_code = request.args.get('code')
    if not fund_code:
        return error_response('缺少基金代码参数', status_code=400)
    suggestion = ai_service.generate_fund_suggestion(fund_code)
    return success_response(suggestion)

# 账单分析接口
@ai_bp.route('/api/bill-analysis', methods=['GET'])
@handle_exceptions
def bill_analysis_api():
    user_id = request.args.get('userId')
    if not user_id:
        return error_response('缺少用户ID参数', status_code=400)
    analysis = ai_service.generate_bill_suggestion({'userId': user_id})
    return success_response(analysis)

# 转账建议接口
@ai_bp.route('/api/transfer-suggestion', methods=['GET'])
@handle_exceptions
def transfer_suggestion_api():
    user_id = request.args.get('userId')
    if not user_id:
        return error_response('缺少用户ID参数', status_code=400)
    suggestion = ai_service.generate_transfer_suggestion({'userId': user_id})
    return success_response(suggestion)

# 首页建议接口
@ai_bp.route('/api/home-suggestion', methods=['GET'])
@handle_exceptions
def home_suggestion_api():
    user_id = request.args.get('userId')
    if not user_id:
        return error_response('缺少用户ID参数', status_code=400)
    suggestion = ai_service.generate_home_suggestion({'userId': user_id})
    return success_response(suggestion)