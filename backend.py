from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 模拟用户数据
USER_DATA = {
    "UTSZ": {
        "password": "admin",
        "display_name": "UTSZ用户"
    }
}

# 模拟股票数据
STOCK_DATA = {
    "贵州茅台": {
        "code": "600519",
        "industry": "白酒",
        "market_cap": "2.5万亿",
        "pe": "30.5",
        "recent_performance": "连续3个月上涨",
        "volatility": "低"
    },
    "五粮液": {
        "code": "000858",
        "industry": "白酒",
        "market_cap": "9000亿",
        "pe": "25.2",
        "recent_performance": "震荡上行",
        "volatility": "中等"
    },
    "宁德时代": {
        "code": "300750",
        "industry": "新能源",
        "market_cap": "1.2万亿",
        "pe": "45.8",
        "recent_performance": "波动较大",
        "volatility": "高"
    },
    "腾讯控股": {
        "code": "00700",
        "industry": "互联网",
        "market_cap": "3万亿",
        "pe": "18.5",
        "recent_performance": "稳步回升",
        "volatility": "中等"
    },
    "阿里巴巴": {
        "code": "9988",
        "industry": "互联网",
        "market_cap": "2.8万亿",
        "pe": "15.2",
        "recent_performance": "底部企稳",
        "volatility": "中等"
    },
    "美团-W": {
        "code": "03690",
        "industry": "互联网",
        "market_cap": "8000亿",
        "pe": "-",
        "recent_performance": "持续调整",
        "volatility": "高"
    },
    "招商银行": {
        "code": "600036",
        "industry": "银行",
        "market_cap": "1.5万亿",
        "pe": "8.5",
        "recent_performance": "小幅波动",
        "volatility": "低"
    },
    "中国平安": {
        "code": "601318",
        "industry": "保险",
        "market_cap": "9000亿",
        "pe": "6.8",
        "recent_performance": "横盘整理",
        "volatility": "低"
    }
}

# 模拟基金数据
FUND_DATA = {
    "005827": {
        "name": "易方达蓝筹精选混合",
        "code": "005827",
        "nav": 2.8745,
        "changePercent": "2.13%",
        "change": "+0.0598",
        "category": "混合型",
        "risk": "中高风险",
        "manager": "张坤"
    },
    "320007": {
        "name": "诺安成长混合",
        "code": "320007",
        "nav": 1.7654,
        "changePercent": "-1.24%",
        "change": "-0.0222",
        "category": "混合型",
        "risk": "高风险",
        "manager": "蔡嵩松"
    },
    "002001": {
        "name": "华夏回报混合A",
        "code": "002001",
        "nav": 3.2456,
        "changePercent": "0.89%",
        "change": "+0.0288",
        "category": "混合型",
        "risk": "中风险",
        "manager": "王宗合"
    },
    "161005": {
        "name": "富国天惠成长混合A",
        "code": "161005",
        "nav": 4.5678,
        "changePercent": "1.56%",
        "change": "+0.0695",
        "category": "混合型",
        "risk": "中高风险",
        "manager": "朱少醒"
    },
    "163406": {
        "name": "兴全合润混合",
        "code": "163406",
        "nav": 3.8923,
        "changePercent": "1.23%",
        "change": "+0.0473",
        "category": "混合型",
        "risk": "中高风险",
        "manager": "谢治宇"
    }
}

# 模拟AI助手响应生成函数
def generate_ai_response(prompt, context):
    """生成AI助手响应"""
    stock_name = None
    
    # 从prompt中提取股票名称
    for name in STOCK_DATA.keys():
        if name in prompt:
            stock_name = name
            break
    
    # 如果有股票数据在context中
    if 'stockData' in context and context['stockData']:
        stock_name = context['stockData'].get('name', stock_name)
    
    # 生成响应
    if stock_name and stock_name in STOCK_DATA:
        stock_info = STOCK_DATA[stock_name]
        response = f"关于{stock_name}({stock_info['code']})的分析：\n"
        response += f"- 所属行业：{stock_info['industry']}\n"
        response += f"- 市值：{stock_info['market_cap']}\n"
        response += f"- PE：{stock_info['pe']}\n"
        response += f"- 近期表现：{stock_info['recent_performance']}\n"
        response += f"- 波动性：{stock_info['volatility']}\n\n"
        
        # 根据行业和表现给出建议
        if stock_info['industry'] == '白酒':
            response += "白酒行业具有较强的品牌价值和定价能力，建议关注高端白酒的长期投资价值。"
        elif stock_info['industry'] == '新能源':
            response += "新能源行业处于快速发展期，成长性强但波动较大，建议分批建仓，控制仓位。"
        elif stock_info['industry'] == '互联网':
            response += "互联网行业估值已回归合理区间，具有长期投资价值，可逢低布局龙头企业。"
        elif stock_info['industry'] == '银行' or stock_info['industry'] == '保险':
            response += "金融板块估值较低，股息率较高，适合稳健型投资者配置。"
    else:
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
    analysisText = f"市场分析：{analysis['marketOverview']}\n\n热门板块：{analysis['hotSectors'].join('、')}\n\n"
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
        
        # 构建股票列表
        stocks = []
        for name, info in STOCK_DATA.items():
            stocks.append({
                'name': name,
                'code': info['code'],
                'industry': info['industry']
            })
        
        # 过滤和排序逻辑
        filtered_stocks = stocks
        
        # 根据行业筛选
        if industry:
            filtered_stocks = [stock for stock in filtered_stocks if stock.get('industry') == industry]
        
        # 排序
        reverse = order_dir.lower() == 'desc'
        filtered_stocks.sort(key=lambda x: x.get(order_by, ''), reverse=reverse)
        
        # 分页
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_stocks = filtered_stocks[start_index:end_index]
        
        # 模拟连接外部金融数据库的接口
        # 实际实现时，这里可以替换为对真实金融数据库的查询
        
        return jsonify({
            'success': True,
            'data': paginated_stocks,
            'pagination': {
                'currentPage': page,
                'pageSize': page_size,
                'totalItems': len(filtered_stocks),
                'totalPages': (len(filtered_stocks) + page_size - 1) // page_size
            },
            'message': '获取股票数据成功'
        })
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
        
        # 验证用户名和密码
        if username in USER_DATA and USER_DATA[username]['password'] == password:
            return jsonify({
                'success': True,
                'data': {
                    'username': username,
                    'display_name': USER_DATA[username]['display_name']
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
        
        # 构建基金列表
        funds = []
        for code, info in FUND_DATA.items():
            funds.append({
                'id': code,
                'name': info['name'],
                'code': info['code'],
                'nav': info['nav'],
                'changePercent': info['changePercent'],
                'change': info['change'],
                'category': info['category'],
                'risk': info['risk'],
                'manager': info['manager']
            })
        
        # 过滤和排序逻辑
        filtered_funds = funds
        
        # 根据类别筛选
        if category:
            filtered_funds = [fund for fund in filtered_funds if fund.get('category') == category]
        
        # 根据风险等级筛选
        if risk_level:
            filtered_funds = [fund for fund in filtered_funds if fund.get('risk') == risk_level]
        
        # 排序
        reverse = order_dir.lower() == 'desc'
        filtered_funds.sort(key=lambda x: x.get(order_by, ''), reverse=reverse)
        
        # 分页
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_funds = filtered_funds[start_index:end_index]
        
        # 模拟连接外部金融数据库的接口
        # 实际实现时，这里可以替换为对真实金融数据库的查询
        
        return jsonify({
            'success': True,
            'data': paginated_funds,
            'pagination': {
                'currentPage': page,
                'pageSize': page_size,
                'totalItems': len(filtered_funds),
                'totalPages': (len(filtered_funds) + page_size - 1) // page_size
            },
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