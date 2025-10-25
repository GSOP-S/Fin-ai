"""
账单控制器 Controller
处理账单相关的HTTP请求
"""

from flask import Blueprint, request, jsonify
from services.bill_analysis_service import BillAnalysisService

# 创建蓝图
bill_bp = Blueprint('bill', __name__, url_prefix='/api')

# 实例化服务
bill_service = BillAnalysisService()


@bill_bp.route('/bill-analysis', methods=['POST'])
def get_bill_analysis():
    """
    获取账单AI分析API
    
    请求体:
        {
            "userId": "UTSZ",
            "bills": [...],
            "month": "2023-10"
        }
    
    响应:
        {
            "success": True,
            "data": {
                "summary": {...},
                "categoryDistribution": [...],
                "abnormalTransactions": [...],
                "suggestions": [...]
            },
            "message": "获取账单分析成功"
        }
    """
    try:
        # 获取请求数据
        data = request.json
        user_id = data.get('userId', '')
        bills = data.get('bills', [])
        month = data.get('month', '')
        
        # 参数验证
        if not user_id:
            return jsonify({
                'success': False,
                'error': '缺少用户ID',
                'message': '请求参数错误'
            }), 400
        
        # 调用服务层
        analysis_result = bill_service.analyze_bills(user_id, bills, month)
        
        return jsonify({
            'success': True,
            'data': analysis_result,
            'message': '获取账单分析成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取账单分析失败'
        }), 500


@bill_bp.route('/bills/<user_id>', methods=['GET'])
def get_user_bills(user_id):
    """
    获取用户账单列表
    
    查询参数:
        month: 月份（可选），格式：YYYY-MM
    
    响应:
        {
            "success": True,
            "data": [...],
            "message": "获取账单列表成功"
        }
    """
    try:
        month = request.args.get('month', None)
        
        # 从Mapper获取数据
        from mapper.bill_mapper import BillMapper
        bills = BillMapper.get_bills_by_user(user_id, month)
        
        return jsonify({
            'success': True,
            'data': bills,
            'message': '获取账单列表成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取账单列表失败'
        }), 500

