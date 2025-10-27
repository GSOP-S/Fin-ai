"""
股票控制器 Controller
处理股票相关的HTTP请求
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.stock_service import get_stock_list, get_stock_details

# 创建蓝图 统一前缀 /api
stock_bp = Blueprint('stock', __name__, url_prefix='/api')


@stock_bp.route('/stocks', methods=['GET'])
@handle_exceptions
def stocks_list_api():
    """股票列表接口
    查询参数:
        page: 当前页码(默认1)
        pageSize: 每页条数(默认20)
        industry: 行业筛选
        orderBy: 排序字段(code|name|market_cap|pe)
        orderDir: 排序方向(asc|desc)
    """
    try:
        query_params = {
            'page': request.args.get('page', 1),
            'pageSize': request.args.get('pageSize', 20),
            'industry': request.args.get('industry'),
            'orderBy': request.args.get('orderBy', 'code'),
            'orderDir': request.args.get('orderDir', 'asc'),
        }
        result = get_stock_list(query_params)
        return success_response({ 'data': result['data'], 'pagination': result['pagination'] }, message='获取股票列表成功')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'message': '获取股票列表失败'}), 500


@stock_bp.route('/stock/<string:stock_name>', methods=['GET'])
@handle_exceptions
def stock_detail_api(stock_name):
    """股票详情接口
    Path 参数:
        stock_name: 股票名称
    """
    try:
        detail = get_stock_details(stock_name)
        if not detail:
            return error_response('NOT_FOUND', message='未找到对应股票', status_code=404)
        return success_response(detail, message='获取股票详情成功')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'message': '获取股票详情失败'}), 500