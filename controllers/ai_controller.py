"""
AI控制器 Controller
处理所有AI相关的HTTP请求，直接调用各个专门的服务
"""

from flask import request, jsonify
from services.home_suggestion_service import HomeSuggestionService
from services.fund_service import FundService
from services.bill_analysis_service import BillAnalysisService
from services.transfer_suggestion_service import TransferSuggestionService
from services.ai_service import AIService


# 创建服务实例
home_suggestion_service = HomeSuggestionService()
fund_service = FundService()
bill_analysis_service = BillAnalysisService()
transfer_suggestion_service = TransferSuggestionService()
ai_service = AIService()


def register_ai_routes(app):
    """注册AI相关的路由"""
    
    @app.route('/api/ai-assistant', methods=['POST'])
    def ai_assistant():
        """AI助手接口，处理通用AI对话"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求数据不能为空'}), 400
            
            prompt = data.get('prompt', '')
            context = data.get('context', {})
            
            if not prompt:
                return jsonify({'error': '提示词不能为空'}), 400
            
            # 使用通用AI服务生成回复
            response = ai_service.generate_ai_response(prompt, context)
            
            return jsonify({
                'success': True,
                'response': response
            })
        except Exception as e:
            print(f"AI助手处理失败: {str(e)}")
            return jsonify({'error': 'AI助手处理失败，请稍后再试'}), 500
    
    @app.route('/api/ai/suggestion', methods=['POST'])
    def get_ai_suggestions():
        """获取页面特定的AI建议"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求数据不能为空'}), 400
            
            page_type = data.get('pageType', '')
            context = data.get('context', {})
            
            if not page_type:
                return jsonify({'error': '页面类型不能为空'}), 400
            
            # 根据页面类型调用相应的服务
            if page_type == 'home':
                user_id = context.get('userId', '')
                result = home_suggestion_service.generate_home_suggestion_from_context(context) if user_id else {"suggestion": "请提供用户ID"}
            elif page_type == 'fund':
                fund_data = context.get('fundData', {})
                if not fund_data:
                    result = {"suggestion": "请提供基金数据"}
                else:
                    result = fund_service.generate_fund_suggestion(fund_data)
            elif page_type == 'bill':
                try:
                    result = bill_analysis_service.generate_bill_suggestion(context)
                except Exception as e:
                    print(f"账单AI建议生成失败，使用fallback: {str(e)}")
                    # 账单分析fallback
                    result = {"suggestion": "暂无账单数据，无法生成分析"}
            elif page_type == 'transfer':
                result = transfer_suggestion_service.generate_transfer_suggestion_from_context(context)
            elif page_type == 'market':
                # 市场分析暂时使用通用AI服务
                market_data = context.get('marketData', {})
                try:
                    prompt = (
                        f"当前市场趋势：{market_data.get('trend', '平稳')}\n"
                        f"热门板块：{', '.join(market_data.get('hotSectors', []))}\n"
                        "请给出简要的市场分析建议（100字以内，中文）"
                    )
                    suggestion = ai_service.generate_ai_response(prompt, context={"type": "market"})
                    result = {"suggestion": suggestion}
                except Exception as e:
                    print(f"市场AI建议生成失败，使用fallback: {str(e)}")
                    # 市场分析fallback
                    result = {"suggestion": "当前市场整体表现平稳，建议投资者保持理性，关注优质蓝筹股和债券配置，控制风险。"}
            else:
                result = {"suggestion": "暂无相关建议"}
            
            return jsonify({
                'success': True,
                'data': result
            })
        except Exception as e:
            print(f"获取AI建议失败: {str(e)}")
            return jsonify({'error': '获取AI建议失败，请稍后再试'}), 500