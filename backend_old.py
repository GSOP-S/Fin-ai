from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import pymysql
from pymysql.cursors import DictCursor

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 数据库连接函数
def get_db_connection():
    """创建数据库连接"""
    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'Fin'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        cursorclass=DictCursor
    )
    return conn

# 导入拆分后的模块
from routes.ai_assistant import ai_assistant_bp
from services.stock_service import generate_market_analysis, generate_stock_suggestion
from services.fund_service import generate_fund_suggestion, get_fund_list
from utils.db import get_db_connection, close_db_connection

# 注册蓝图
app.register_blueprint(ai_assistant_bp)

# 用户反馈数据存储
FEEDBACK_DATA = []

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取股票列表API - 支持分页、筛选和排序参数"""
    try:
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

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录API"""
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 查询用户
                cursor.execute("SELECT user_id, display_name FROM Users WHERE user_id = %s AND password = %s", (username, password))
                user = cursor.fetchone()

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
        finally:
            close_db_connection(conn)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '登录过程中发生错误'
        }), 500

@app.route('/api/funds', methods=['GET'])
def get_funds():
    """获取基金列表API - 使用服务层方法"""
    try:
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

@app.route('/api/bill-analysis', methods=['POST'])
def get_bill_analysis():
    """获取账单AI分析API"""
    try:
        data = request.json
        bills = data.get('bills', [])
        analysis = data.get('analysis', {})
        
        # TODO: 接入大模型API进行更智能的分析
        # 目前使用前端传来的分析数据，未来可以在后端重新计算并增强
        
        # 生成AI建议文本
        summary = analysis.get('summary', {})
        suggestions = analysis.get('suggestions', [])
        abnormal_transactions = analysis.get('abnormalTransactions', [])
        
        # 可以在这里接入大模型，生成更个性化的建议
        response_data = {
            'summary': summary,
            'suggestions': suggestions,
            'abnormalTransactions': abnormal_transactions
        }
        
        # TODO: 记录用户行为数据到数据库，用于优化建议算法
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': '获取账单分析成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取账单分析失败'
        }), 500

@app.route('/api/transfer-suggestion', methods=['POST'])
def get_transfer_suggestion():
    """获取转账智能建议API"""
    try:
        data = request.json
        recipient_account = data.get('recipientAccount', '')
        account_type = data.get('accountType', '')
        is_first_time = data.get('isFirstTimeAccount', False)
        recent_accounts = data.get('recentAccounts', [])
        
        # TODO: 接入大模型API进行风险评估和智能推荐
        # 未来可以结合用户历史转账记录、风控模型等
        
        # 生成到账时间建议
        arrival_time = '实时到账' if account_type == 'same_bank' else '预计1-2小时'
        
        # 生成安全建议
        suggestion = ''
        if is_first_time:
            suggestion = '该账户为新账户，建议仔细核实收款人姓名和账户信息，必要时可联系收款人确认。'
        elif account_type == 'other_bank':
            suggestion = '跨行转账可能产生手续费，建议选择次日到账以节省费用。'
        else:
            suggestion = '本行账户转账实时到账，无手续费。'
        
        # TODO: 从数据库查询用户历史转账记录，提供更精准的推荐
        
        response_data = {
            'recentAccounts': recent_accounts[:3],  # 返回最近3个常用账户
            'arrivalTime': arrival_time,
            'suggestion': suggestion,
            'accountType': account_type,
            'riskLevel': 'high' if is_first_time else 'low'
        }
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': '获取转账建议成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取转账建议失败'
        }), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """提交用户反馈API"""
    try:
        data = request.json
        feedback = {
            'suggestion_id': data.get('suggestionId', ''),
            'content': data.get('content', ''),
            'feedback_type': data.get('type', ''),  # 'like' or 'dislike'
            'user_comment': data.get('comment', ''),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        FEEDBACK_DATA.append(feedback)
        
        # 这里可以添加保存到数据库的代码
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
        'message': '服务运行正常'
    })

if __name__ == '__main__':
    # 在生产环境中应使用Gunicorn或uWSGI等WSGI服务器
    app.run(host='0.0.0.0', port=5000, debug=True)