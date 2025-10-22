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

# 模拟AI助手响应生成函数
def generate_ai_response(prompt, context):
    """生成AI助手响应"""
    stock_name = None
    
    # 从context中获取股票数据
    if 'stockData' in context and context['stockData']:
        stock_name = context['stockData'].get('name', None)
    
    # 从数据库查询股票信息
    if stock_name:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Stocks WHERE name = %s", (stock_name,))
                stock_info = cursor.fetchone()
                
                if stock_info:
                    response = f"关于{stock_info['name']}({stock_info['code']})的分析：\n"
                    response += f"- 所属行业：{stock_info['industry']}\n"
                    response += f"- 市值：{stock_info['market_cap']}\n"
                    response += f"- PE：{stock_info['pe']}\n"
                    response += f"- 近期表现：{stock_info['recent_performance']}\n"
                    response += f"- 波动性：{stock_info['volatility']}\n\n"
                    
                    # 根据行业给出建议
                    if stock_info['industry'] == '白酒':
                        response += "白酒行业具有较强的品牌价值和定价能力，建议关注高端白酒的长期投资价值。"
                    elif stock_info['industry'] == '新能源':
                        response += "新能源行业处于快速发展期，成长性强但波动较大，建议分批建仓，控制仓位。"
                    elif stock_info['industry'] == '互联网':
                        response += "互联网行业估值已回归合理区间，具有长期投资价值，可逢低布局龙头企业。"
                    elif stock_info['industry'] == '银行' or stock_info['industry'] == '保险':
                        response += "金融板块估值较低，股息率较高，适合稳健型投资者配置。"
                    return response
        finally:
            conn.close()
    
    # 通用回复
    if '股票' in prompt or '行情' in prompt:
        response = "您好！我是股票智能助手。请告诉我您想了解哪只股票，我可以为您提供详细分析。"
    elif '买入' in prompt or '卖出' in prompt:
        response = "投资决策需要综合考虑多方面因素，包括公司基本面、行业前景、技术面和宏观经济环境。建议您在做出投资决策前，充分了解相关风险。"
    else:
        response = "您好！我是您的股票智能助手，请问有什么可以帮助您的？"
    
    return response

# 生成市场分析和股票推荐
def generate_market_analysis():
    """生成市场分析和股票推荐"""
    # 模拟市场分析数据
    analysis = {
        "marketOverview": '今日A股三大指数小幅上涨，沪指涨0.82%，深成指涨1.25%，创业板指涨1.68%。市场成交量有所放大，北向资金净流入超50亿元。',
        "hotSectors": ['新能源', '半导体', '医药生物'],
        "recommendedStocks": [
            { "name": '贵州茅台', "code": '600519', "reason": '白酒龙头，业绩稳健，具有长期投资价值' },
            { "name": '宁德时代', "code": '300750', "reason": '新能源赛道核心标的，海外订单增长强劲' },
            { "name": '腾讯控股', "code": '0700.HK', "reason": '互联网龙头，估值处于历史低位，业绩开始回暖' }
        ]
    }

    # 构建分析文本
    analysisText = f"市场分析：{analysis['marketOverview']}\n\n热门板块：{'、'.join(analysis['hotSectors'])}\n\n"
    analysisText += '为您推荐以下股票：\n'
    for i, stock in enumerate(analysis['recommendedStocks']):
        analysisText += f"{i + 1}. {stock['name']} ({stock['code']}) - {stock['reason']}\n"

    return analysisText

# 生成股票建议
def generate_stock_suggestion(stock):
    """根据股票信息生成建议"""
    if not stock:
        return ""
    
    # 根据股票涨跌状态生成不同的建议
    isUp = stock.get('change', 0) >= 0
    name = stock.get('name', '')
    code = stock.get('code', '')
    changePercent = stock.get('changePercent', '')
    
    if isUp:
        suggestion = f"{name} ({code}) 目前上涨 {changePercent}，表现强势。建议关注其成交量变化和市场热点持续性，可考虑逢低买入策略。"
    else:
        suggestion = f"{name} ({code}) 目前下跌 {changePercent}，可能存在短期调整。建议观察其支撑位表现，可考虑分批建仓策略。"
    
    return suggestion

# 生成基金建议
def generate_fund_suggestion(fund):
    """根据基金信息生成建议"""
    if not fund:
        return ""
    
    name = fund.get('name', '')
    code = fund.get('code', '')
    change = fund.get('change', '')
    changePercent = fund.get('changePercent', '')
    manager = fund.get('manager', '')
    risk = fund.get('risk', '')
    
    suggestion = f"基金建议：{name} ({code}) 目前{'上涨' if change.startswith('+') else '下跌'} {changePercent}，{manager}管理，{risk}。建议关注其近期表现和基金经理的投资风格。"
    
    return suggestion

# 用户反馈数据存储
FEEDBACK_DATA = []

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant_api():
    """AI助手API接口"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        context = data.get('context', {})
        
        # 生成AI响应
        response_text = generate_ai_response(prompt, context)
        
        return jsonify({
            'success': True,
            'data': {
                'response': response_text,
                'context': context
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
                # 构建查询SQL
                query = "SELECT name, code, industry FROM Stocks"
                params = []
                conditions = []

                # 行业筛选
                if industry:
                    conditions.append("industry = %s")
                    params.append(industry)

                # 添加WHERE子句
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                # 排序
                valid_order_by = {'code', 'name', 'industry'}
                if order_by not in valid_order_by:
                    order_by = 'code'
                order_dir_sql = 'DESC' if order_dir.lower() == 'desc' else 'ASC'
                query += f" ORDER BY {order_by} {order_dir_sql}"

                # 总数查询
                count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                # 分页
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
            conn.close()
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
            conn.close()
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '登录过程中发生错误'
        }), 500

@app.route('/api/funds', methods=['GET'])
def get_funds():
    """获取基金列表API - 支持分页、筛选和排序参数"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        category = request.args.get('category', None)
        risk_level = request.args.get('riskLevel', None)
        order_by = request.args.get('orderBy', 'code')
        order_dir = request.args.get('orderDir', 'asc')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 构建查询SQL
                query = "SELECT name, code, nav, change_percent as changePercent, fund_change as change, category, risk, manager FROM Fundings"
                params = []
                conditions = []

                # 根据类别筛选
                if category:
                    conditions.append("category = %s")
                    params.append(category)

                # 根据风险等级筛选
                if risk_level:
                    conditions.append("risk = %s")
                    params.append(risk_level)

                # 添加WHERE子句
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                # 排序
                valid_order_by = {'code', 'name', 'nav', 'change_percent'}
                if order_by not in valid_order_by:
                    order_by = 'code'
                order_dir_sql = 'DESC' if order_dir.lower() == 'desc' else 'ASC'
                # 总数查询
                count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                # 排序
                valid_order_by = {'code', 'name', 'nav', 'change_percent'}
                if order_by not in valid_order_by:
                    order_by = 'code'
                order_dir_sql = 'DESC' if order_dir.lower() == 'desc' else 'ASC'
                query += f" ORDER BY {order_by} {order_dir_sql}"

                # 分页
                query += " LIMIT %s OFFSET %s"
                params.extend([page_size, (page - 1) * page_size])

                cursor.execute(query, params)
                paginated_funds = cursor.fetchall()

                return jsonify({
                    'success': True,
                    'data': paginated_funds,
                    'pagination': {
                        'currentPage': page,
                        'pageSize': page_size,
                        'totalItems': total,
                        'totalPages': (total + page_size - 1) // page_size
                    },
                    'message': '获取基金数据成功'
                })
        finally:
            conn.close()
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
            'timestamp': datetime.now().isoformat()
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