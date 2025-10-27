"""
转账控制器 Controller
处理转账相关的HTTP请求
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.transfer_suggestion_service import TransferSuggestionService

# 创建蓝图
transfer_bp = Blueprint('transfer', __name__, url_prefix='/api')

# 实例化服务
transfer_service = TransferSuggestionService()


@transfer_bp.route('/transfer-suggestion', methods=['POST'])
@handle_exceptions
def get_transfer_suggestion():
    # 获取请求数据
    data = request.json or {}
    user_id = data.get('userId', '')

    # 参数验证
    if not user_id:
        return error_response(error='缺少用户ID', message='请求参数错误', status_code=400)

    # 构建上下文
    context = {
        'recipientAccount': data.get('recipientAccount', ''),
        'accountType': data.get('accountType', ''),
        'isFirstTimeAccount': data.get('isFirstTimeAccount', False),
        'amount': data.get('amount', 0)
    }

    # 调用服务层
    suggestion_result = transfer_service.generate_transfer_suggestion(user_id, context)

    return success_response(suggestion_result, message='获取转账建议成功')


@transfer_bp.route('/transfer-history/<user_id>', methods=['GET'])
@handle_exceptions
def get_transfer_history(user_id):
    recipient_account = request.args.get('recipientAccount', None)

    from mapper.transfer_mapper import TransferMapper
    history = TransferMapper.get_transfer_history(user_id, recipient_account)

    return success_response(history, message='获取转账历史成功')

