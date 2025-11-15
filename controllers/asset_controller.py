"""资产页面API控制器"""

from flask import Blueprint, request, jsonify
from mapper.user_position_mapper import UserPositionMapper
from services.asset_service import AssetService
from utils.response import success_response, error_response
import logging

# 创建蓝图
asset_bp = Blueprint('asset', __name__)
logger = logging.getLogger(__name__)

@asset_bp.route('/api/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """获取投资组合汇总信息"""
    try:
        # 获取用户ID，这里暂时使用默认值"UTSZ"，实际应该从session获取
        user_id = request.args.get('user_id', 'UTSZ')
        
        portfolio_summary = AssetService.get_portfolio_summary(user_id)
        return success_response(portfolio_summary)
        
    except Exception as e:
        logger.error(f"获取投资组合汇总失败: {str(e)}")
        return error_response(f"获取投资组合汇总失败: {str(e)}")


@asset_bp.route('/api/fund-positions', methods=['GET'])
def get_fund_positions():
    """获取基金持仓列表"""
    try:
        # 获取用户ID，这里暂时使用默认值"UTSZ"，实际应该从session获取
        user_id = request.args.get('user_id', 'UTSZ')
        
        fund_positions = AssetService.get_fund_positions(user_id)
        return success_response(fund_positions)
        
    except Exception as e:
        logger.error(f"获取基金持仓失败: {str(e)}")
        return error_response(f"获取基金持仓失败: {str(e)}")


@asset_bp.route('/api/deposit-positions', methods=['GET'])
def get_deposit_positions():
    """获取存款和储蓄持仓列表"""
    try:
        # 获取用户ID，这里暂时使用默认值"UTSZ"，实际应该从session获取
        user_id = request.args.get('user_id', 'UTSZ')
        
        deposit_positions = AssetService.get_deposit_positions(user_id)
        return success_response(deposit_positions)
        
    except Exception as e:
        logger.error(f"获取存款/储蓄持仓失败: {str(e)}")
        return error_response(f"获取存款/储蓄持仓失败: {str(e)}")


@asset_bp.route('/api/all-positions', methods=['GET'])
def get_all_positions():
    """获取所有持仓列表"""
    try:
        # 获取用户ID，这里暂时使用默认值"UTSZ"，实际应该从session获取
        user_id = request.args.get('user_id', 'UTSZ')
        position_type = request.args.get('position_type', None)
        
        all_positions = UserPositionMapper.get_user_positions_by_type(user_id, position_type)
        return success_response(all_positions)
        
    except Exception as e:
        logger.error(f"获取持仓列表失败: {str(e)}")
        return error_response(f"获取持仓列表失败: {str(e)}")


@asset_bp.route('/api/asset/ai-analysis', methods=['POST'])
def get_asset_ai_analysis():
    """获取资产AI分析建议"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'UTSZ')
        
        # 获取用户持仓数据进行分析
        fund_positions = AssetService.get_fund_positions(user_id)
        deposit_positions = AssetService.get_deposit_positions(user_id)
        portfolio_summary = AssetService.get_portfolio_summary(user_id)
        
        # 生成AI分析建议
        analysis_result = AssetService.generate_ai_analysis(
            portfolio_summary, fund_positions, deposit_positions
        )
        
        return success_response(analysis_result)
        
    except Exception as e:
        logger.error(f"获取资产AI分析失败: {str(e)}")
        return error_response(f"获取资产AI分析失败: {str(e)}")


@asset_bp.route('/api/positions/<int:position_id>', methods=['PUT'])
def update_position(position_id):
    """更新持仓记录"""
    try:
        data = request.get_json()
        shares = data.get('shares')
        current_price = data.get('current_price')
        
        result = UserPositionMapper.update_user_position(
            position_id, shares=shares, current_price=current_price
        )
        
        if result > 0:
            return success_response({"message": "持仓记录更新成功"})
        else:
            return error_response("持仓记录更新失败")
            
    except Exception as e:
        logger.error(f"更新持仓记录失败: {str(e)}")
        return error_response(f"更新持仓记录失败: {str(e)}")


@asset_bp.route('/api/positions', methods=['POST'])
def create_position():
    """创建新的持仓记录"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id', 'UTSZ')
        position_type = data.get('position_type')
        product_code = data.get('product_code')
        product_name = data.get('product_name')
        shares = data.get('shares')
        purchase_price = data.get('purchase_price')
        purchase_date = data.get('purchase_date')
        
        # 参数验证
        if not all([position_type, product_code, product_name, shares, purchase_price, purchase_date]):
            return error_response("缺少必要参数")
        
        position_id = UserPositionMapper.create_user_position(
            user_id=user_id,
            position_type=position_type,
            product_code=product_code,
            product_name=product_name,
            shares=float(shares),
            purchase_price=float(purchase_price),
            purchase_date=purchase_date
        )
        
        return success_response({"position_id": position_id, "message": "持仓记录创建成功"})
        
    except Exception as e:
        logger.error(f"创建持仓记录失败: {str(e)}")
        return error_response(f"创建持仓记录失败: {str(e)}")


@asset_bp.route('/api/positions/<int:position_id>', methods=['DELETE'])
def delete_position(position_id):
    """删除持仓记录（软删除）"""
    try:
        from mapper.user_position_mapper import UserPositionMapper
        result = UserPositionMapper.update_user_position(position_id, status='deleted')
        
        if result > 0:
            return success_response({"message": "持仓记录删除成功"})
        else:
            return error_response("持仓记录删除失败")
            
    except Exception as e:
        logger.error(f"删除持仓记录失败: {str(e)}")
        return error_response(f"删除持仓记录失败: {str(e)}")