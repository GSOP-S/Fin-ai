"""基金控制器 Controller
处理基金相关API请求"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.fund_service import get_fund_list, get_fund_details, FundService

fund_bp = Blueprint('fund', __name__, url_prefix='/api')

@fund_bp.route('/funds', methods=['GET'])
@handle_exceptions
def funds_list_api():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 20))
    category = request.args.get('category')
    risk_level = request.args.get('riskLevel')
    order_by = request.args.get('orderBy', 'code')
    order_dir = request.args.get('orderDir', 'asc')

    result = get_fund_list(page, page_size, category, risk_level, order_by, order_dir)
    # 直接将 service 返回结果作为 data，内含列表与分页信息
    return success_response(result, message='获取基金列表成功')


@fund_bp.route('/fund/<string:fund_code>', methods=['GET'])
@handle_exceptions
def fund_detail_api(fund_code):
    detail = get_fund_details(fund_code)
    if not detail:
        return error_response(error='NOT_FOUND', message='未找到对应基金', status_code=404)
    return success_response(detail, message='获取基金详情成功')


@fund_bp.route('/fund-suggestion', methods=['GET'])
@handle_exceptions
def fund_suggestion_api():
    """获取基金建议API"""
    fund_code = request.args.get('code')
    if not fund_code:
        return error_response(error='INVALID_PARAMS', message='缺少基金代码参数', status_code=400)
    
    # 获取基金详情
    fund = get_fund_details(fund_code)
    if not fund:
        return error_response(error='NOT_FOUND', message='未找到对应基金', status_code=404)
    
    # 生成基金建议
    fund_service = FundService()
    suggestion = fund_service.generate_fund_suggestion(fund)
    
    return success_response(suggestion, message='获取基金建议成功')