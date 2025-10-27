"""
首页控制器 Controller
处理首页相关的HTTP请求
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.home_suggestion_service import HomeSuggestionService

# 创建蓝图
home_bp = Blueprint('home', __name__, url_prefix='/api')

# 实例化服务
home_service = HomeSuggestionService()


@home_bp.route('/home-suggestion', methods=['POST'])
@handle_exceptions
def get_home_suggestion():
    """
    获取首页智能建议API
    
    请求体:
        {
            "userId": "UTSZ"
        }
    
    响应:
        {
            "success": True,
            "data": {
                "greeting": "欢迎回来，UTSZ用户！",
                "suggestion": "...",
                "quickActions": [...],
                "billStats": {...},
                "transferStats": {...}
            },
            "message": "获取首页建议成功"
        }
    """
    data = request.json or {}
    user_id = data.get('userId', '')
    if not user_id:
        return error_response('缺少用户ID', message='请求参数错误', status_code=400)
    suggestion_result = home_service.generate_home_suggestion(user_id)
    return success_response(suggestion_result, message='获取首页建议成功')

