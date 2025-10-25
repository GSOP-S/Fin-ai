"""
转账控制器 Controller
处理转账相关的HTTP请求
"""

from flask import Blueprint, request, jsonify
from services.transfer_suggestion_service import TransferSuggestionService

# 创建蓝图
transfer_bp = Blueprint('transfer', __name__, url_prefix='/api')

# 实例化服务
transfer_service = TransferSuggestionService()


@transfer_bp.route('/transfer-suggestion', methods=['POST'])
def get_transfer_suggestion():
    """
    获取转账智能建议API
    
    请求体:
        {
            "userId": "UTSZ",
            "recipientAccount": "6222123456789012",
            "accountType": "same_bank",
            "isFirstTimeAccount": false,
            "amount": 1000
        }
    
    响应:
        {
            "success": True,
            "data": {
                "recentAccounts": [...],
                "arrivalTime": "实时到账",
                "suggestion": "...",
                "accountType": "same_bank",
                "riskLevel": "low",
                "feeSuggestion": "..."
            },
            "message": "获取转账建议成功"
        }
    """
    try:
        # 获取请求数据
        data = request.json
        user_id = data.get('userId', '')
        
        # 参数验证
        if not user_id:
            return jsonify({
                'success': False,
                'error': '缺少用户ID',
                'message': '请求参数错误'
            }), 400
        
        # 构建上下文
        context = {
            'recipientAccount': data.get('recipientAccount', ''),
            'accountType': data.get('accountType', ''),
            'isFirstTimeAccount': data.get('isFirstTimeAccount', False),
            'amount': data.get('amount', 0)
        }
        
        # 调用服务层
        suggestion_result = transfer_service.generate_transfer_suggestion(user_id, context)
        
        return jsonify({
            'success': True,
            'data': suggestion_result,
            'message': '获取转账建议成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取转账建议失败'
        }), 500


@transfer_bp.route('/transfer-history/<user_id>', methods=['GET'])
def get_transfer_history(user_id):
    """
    获取用户转账历史
    
    查询参数:
        recipientAccount: 收款账户（可选）
    
    响应:
        {
            "success": True,
            "data": [...],
            "message": "获取转账历史成功"
        }
    """
    try:
        recipient_account = request.args.get('recipientAccount', None)
        
        # 从Mapper获取数据
        from mapper.transfer_mapper import TransferMapper
        history = TransferMapper.get_transfer_history(user_id, recipient_account)
        
        return jsonify({
            'success': True,
            'data': history,
            'message': '获取转账历史成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取转账历史失败'
        }), 500

