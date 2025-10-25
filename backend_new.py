"""
Flask应用入口文件
负责应用初始化、蓝图注册和启动
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 注册蓝图 - Controller层
from controllers.bill_controller import bill_bp
from controllers.transfer_controller import transfer_bp
from controllers.home_controller import home_bp
from controllers.user_controller import user_bp

app.register_blueprint(bill_bp)
app.register_blueprint(transfer_bp)
app.register_blueprint(home_bp)
app.register_blueprint(user_bp)

# 保留原有的股票和基金相关接口（从routes目录）
from routes.ai_assistant import ai_assistant_bp
from services.stock_service import generate_market_analysis, generate_stock_suggestion
from services.fund_service import generate_fund_suggestion, get_fund_list
from utils.db import get_db_connection, close_db_connection

app.register_blueprint(ai_assistant_bp)


# ==================== 原有接口保留 ====================

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取股票列表API - 支持分页、筛选和排序参数"""
    try:
        from flask import request
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        industry = request.args.get('industry', None)
        order_by = request.args.get('orderBy', 'code')
        order_dir = request.args.get('orderDir', 'asc')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 构建查询SQL，获取更多股票信息
                base_query = "SELECT name, code, industry, market_cap, pe, recent_performance FROM Stocks"
                count_query = "SELECT COUNT(*) as total FROM Stocks"
                params = []
                conditions = []

                # 行业筛选
                if industry:
                    conditions.append("industry = %s")
                    params.append(industry)
                
                # 添加WHERE子句
                if conditions:
                    where_clause = " WHERE " + " AND ".join(conditions)
                    base_query += where_clause
                    count_query += where_clause

                # 排序
                valid_order_by = {'code', 'name', 'industry', 'market_cap', 'pe'}
                if order_by not in valid_order_by:
                    order_by = 'code'
                order_dir_sql = 'DESC' if order_dir.lower() == 'desc' else 'ASC'
                order_clause = f" ORDER BY {order_by} {order_dir_sql}"
                
                # 总数查询
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']
                
                # 最终查询（包含排序和分页）
                query = base_query + order_clause
                query += " LIMIT %s OFFSET %s"
                params.extend([page_size, (page - 1) * page_size])

                cursor.execute(query, params)
                paginated_stocks = cursor.fetchall()

                return jsonify({
                    'success': True,
                    'data': paginated_stocks,
                    'pagination': {
                        'currentPage': page,
                        'pageSize': page_size,
                        'totalItems': total,
                        'totalPages': (total + page_size - 1) // page_size
                    },
                    'message': '获取股票数据成功'
                })
        finally:
            close_db_connection(conn)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/funds', methods=['GET'])
def get_funds():
    """获取基金列表API - 使用服务层方法"""
    try:
        from flask import request
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        category = request.args.get('category', None)
        risk_level = request.args.get('riskLevel', None)
        order_by = request.args.get('orderBy', 'code')
        order_dir = request.args.get('orderDir', 'asc')
        
        result = get_fund_list(page, page_size, category, risk_level, order_by, order_dir)
        return jsonify({
            'success': True,
            'data': result['data'],
            'pagination': result['pagination'],
            'message': '获取基金数据成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/market-analysis', methods=['GET'])
def get_market_analysis():
    """获取市场分析和股票推荐API"""
    try:
        analysis = generate_market_analysis()
        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock-suggestion', methods=['POST'])
def get_stock_suggestion():
    """获取股票建议API"""
    try:
        from flask import request
        data = request.json
        stock = data.get('stock', {})
        suggestion = generate_stock_suggestion(stock)
        return jsonify({
            'success': True,
            'data': {
                'suggestion': suggestion
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fund-suggestion', methods=['POST'])
def get_fund_suggestion():
    """获取基金建议API"""
    try:
        from flask import request
        data = request.json
        fund = data.get('fund', {})
        suggestion = generate_fund_suggestion(fund)
        return jsonify({
            'success': True,
            'data': {
                'suggestion': suggestion
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """提交用户反馈API"""
    try:
        from flask import request
        import datetime
        
        data = request.json
        feedback = {
            'suggestion_id': data.get('suggestionId', ''),
            'content': data.get('content', ''),
            'feedback_type': data.get('type', ''),
            'user_comment': data.get('comment', ''),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # TODO: 保存到数据库
        print(f"收到反馈: {feedback}")
        
        return jsonify({
            'success': True,
            'message': '反馈提交成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '反馈提交失败'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '服务运行正常',
        'version': '2.0 - 分层架构'
    })


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': '接口不存在',
        'message': 'Not Found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'message': 'Internal Server Error'
    }), 500


# ==================== 应用启动 ====================

if __name__ == '__main__':
    # 开发环境启动
    # 生产环境应使用 Gunicorn 或 uWSGI
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 Fin-AI 银行后端服务 v2.0                           ║
║   📍 运行地址: http://localhost:{port}                    ║
║   🏗️  架构: Mapper → Service → Controller               ║
║   📚 API文档: http://localhost:{port}/health             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)

