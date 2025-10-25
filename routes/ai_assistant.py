from flask import Blueprint, request, jsonify
import pymysql
from pymysql.cursors import DictCursor
import os
import json
from dotenv import load_dotenv
from utils.db import get_db_connection, close_db_connection

# 初始化Blueprint
ai_assistant_bp = Blueprint('ai_assistant', __name__)
load_dotenv()

# AI响应生成函数
def generate_ai_response(prompt, context):
    stock_name = context.get('stockData', {}).get('name') if context else None
    
    if stock_name:
        conn = None
        try:
            conn = pymysql.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=os.getenv('MYSQL_DATABASE', 'Fin'),
                port=int(os.getenv('MYSQL_PORT', '3306')),
                cursorclass=DictCursor
            )
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
                    
                    # 行业特定建议
                    industry_suggestions = {
                        '白酒': '白酒行业具有较强的品牌价值和定价能力，建议关注高端白酒的长期投资价值。',
                        '新能源': '新能源行业处于快速发展期，成长性强但波动较大，建议分批建仓，控制仓位。',
                        '互联网': '互联网行业估值已回归合理区间，具有长期投资价值，可逢低布局龙头企业。',
                        '银行': '金融板块估值较低，股息率较高，适合稳健型投资者配置。',
                        '保险': '金融板块估值较低，股息率较高，适合稳健型投资者配置。'
                    }
                    response += industry_suggestions.get(stock_info['industry'], '该行业当前暂无特定分析建议。')
                    return response
        except Exception as e:
            return f"数据查询错误：{str(e)}"
        finally:
            if conn:
                conn.close()
    
    # 通用回复逻辑
    if '股票' in prompt or '行情' in prompt:
        return "您好！我是股票智能助手。请告诉我您想了解哪只股票，我可以为您提供详细分析。"
    elif '买入' in prompt or '卖出' in prompt:
        return "投资决策需要综合考虑多方面因素，建议您在做出投资决策前，充分了解相关风险。"
    else:
        return "您好！我是您的智能助手，请问有什么可以帮助您的？"

# 获取特定页面的AI建议
@ai_assistant_bp.route('/api/ai-suggestions/<page_type>', methods=['GET'])
def get_ai_suggestions(page_type):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 查询该页面所有类型的建议
            cursor.execute(
                "SELECT suggestion_type, content FROM AISuggestions WHERE page_type = %s",
                (page_type,)
            )
            results = cursor.fetchall()
            
            # 格式化结果为字典
            suggestions = {}
            for row in results:
                suggestions[row['suggestion_type']] = json.loads(row['content'])
            
            return jsonify({
                'success': True,
                'data': suggestions
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取AI建议失败: {str(e)}'
        }), 500
    finally:
        close_db_connection(conn)

# AI助手对话接口
@ai_assistant_bp.route('/api/ai-assistant', methods=['POST'])
def ai_assistant_api():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        context = data.get('context', {})
        response_text = generate_ai_response(prompt, context)
        
        # 记录用户交互（后续可扩展到大模型调用）
        if context.get('userId'):
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO UserAIActions (user_id, page_type, action_type) VALUES (%s, %s, %s)",
                        (context['userId'], context.get('pageType', 'unknown'), 'query')
                    )
                    conn.commit()
            except Exception as e:
                print(f'记录用户交互失败: {str(e)}')
                conn.rollback()
            finally:
                close_db_connection(conn)
        
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