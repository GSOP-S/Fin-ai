"""
用户控制器 Controller
处理用户相关的HTTP请求
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from mapper.user_mapper import UserMapper

# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/api')

# 实例化Mapper
user_mapper = UserMapper()


@user_bp.route('/register', methods=['POST'])
@handle_exceptions
def register():
    """
    用户注册API
    
    请求体:
        {
            "username": "user123",
            "password": "password",
            "realName": "张三",
            "idCard": "110101199001011234",
            "phone": "13800138000",
            "city": "北京",
            "occupation": "企业职工",
            "riskScore": 3.25,
            "riskLevel": "平衡型",
            "investmentPurposes": "purpose_1,purpose_2"
        }
    
    响应:
        {
            "success": True,
            "message": "注册成功"
        }
    """
    data = request.json or {}
    
    # 必填字段验证
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    real_name = data.get('realName', '').strip()
    id_card = data.get('idCard', '').strip()
    phone = data.get('phone', '').strip()
    
    if not all([username, password, real_name, id_card, phone]):
        return error_response('请完整填写必填信息', status_code=400)
    
    # 检查用户名是否已存在
    if user_mapper.check_username_exists(username):
        return error_response('用户名已存在', status_code=400)
    
    # 可选字段
    city = data.get('city', '')
    occupation = data.get('occupation', '')
    risk_score = data.get('riskScore', 0)
    risk_level = data.get('riskLevel', '')
    investment_purposes = data.get('investmentPurposes', '')
    
    # 插入用户
    try:
        user_mapper.register_user(
            username=username,
            password=password,
            real_name=real_name,
            id_card=id_card,
            phone=phone,
            city=city,
            occupation=occupation,
            risk_score=risk_score,
            risk_level=risk_level,
            investment_purposes=investment_purposes
        )
        return success_response(None, message='注册成功')
    except Exception as e:
        return error_response(f'注册失败: {str(e)}', status_code=500)


@user_bp.route('/login', methods=['POST'])
@handle_exceptions
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
    data = request.json or {}
    username = data.get('username', '')
    password = data.get('password', '')
    if not username or not password:
        return error_response('请输入用户名和密码', message='参数错误', status_code=400)
    user = user_mapper.verify_user_login(username, password)
    if user:
        return success_response({'username': user['user_id'], 'display_name': user['display_name']}, message='登录成功')
    return error_response('用户名或密码错误', message='登录失败', status_code=401)


@user_bp.route('/user/<user_id>', methods=['GET'])
@handle_exceptions
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
            return success_response(user, message='获取用户信息成功')
        return error_response('用户不存在', message='获取用户信息失败', status_code=404)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取用户信息失败'
        }), 500

