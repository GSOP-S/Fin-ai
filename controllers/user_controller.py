"""
用户控制器 Controller
处理用户相关的HTTP请求
"""

from flask import Blueprint, request, jsonify
from mapper.user_mapper import UserMapper

# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/api')

# 实例化Mapper
user_mapper = UserMapper()


@user_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录API
    
    请求体:
        {
            "username": "UTSZ",
            "password": "admin"
        }
    
    响应:
        {
            "success": True,
            "data": {
                "username": "UTSZ",
                "display_name": "UTSZ用户"
            },
            "message": "登录成功"
        }
    """
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        # 参数验证
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '请输入用户名和密码',
                'message': '参数错误'
            }), 400
        
        # 调用Mapper验证登录
        user = user_mapper.verify_user_login(username, password)
        
        if user:
            return jsonify({
                'success': True,
                'data': {
                    'username': user['user_id'],
                    'display_name': user['display_name']
                },
                'message': '登录成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '用户名或密码错误',
                'message': '登录失败'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '登录过程中发生错误'
        }), 500


@user_bp.route('/user/<user_id>', methods=['GET'])
def get_user_info(user_id):
    """
    获取用户信息API
    
    响应:
        {
            "success": True,
            "data": {
                "user_id": "UTSZ",
                "display_name": "UTSZ用户",
                "created_at": "2023-01-01 00:00:00"
            },
            "message": "获取用户信息成功"
        }
    """
    try:
        user = user_mapper.get_user_by_id(user_id)
        
        if user:
            return jsonify({
                'success': True,
                'data': user,
                'message': '获取用户信息成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'message': '获取用户信息失败'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取用户信息失败'
        }), 500

