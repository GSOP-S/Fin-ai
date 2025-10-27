"""
账单控制器 Controller
处理账单相关的HTTP请求
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.bill_analysis_service import BillAnalysisService

# 创建蓝图
bill_bp = Blueprint('bill', __name__, url_prefix='/api')

# 实例化服务
bill_service = BillAnalysisService()


@bill_bp.route('/bill-analysis', methods=['POST'])
@handle_exceptions
def get_bill_analysis():
    data = request.json or {}
    user_id = data.get('userId', '')
    bills = data.get('bills', [])
    month = data.get('month', '')

    if not user_id:
        return error_response(error='缺少用户ID', message='请求参数错误', status_code=400)

    analysis_result = bill_service.analyze_bills(user_id, bills, month)

    return success_response(analysis_result, message='获取账单分析成功')


@bill_bp.route('/bills/<user_id>', methods=['GET'])
@handle_exceptions
def get_user_bills(user_id):
    month = request.args.get('month', None)

    from mapper.bill_mapper import BillMapper
    bills = BillMapper.get_bills_by_user(user_id, month)

    return success_response(bills, message='获取账单列表成功')

