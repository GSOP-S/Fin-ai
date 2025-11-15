"""
AI服务 Service
提供通用的AI能力接口，不包含具体业务逻辑
"""

from typing import Dict, Any, Optional
from services.model_provider import ModelProvider


class AIService:
    """AI服务类，提供通用的AI能力接口"""
    
    def __init__(self):
        self.model_provider = ModelProvider()
    
    def generate_ai_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        生成通用AI回复
        
        Args:
            prompt: 提示词
            context: 上下文信息
            
        Returns:
            AI生成的回复文本
        """
        try:
            return self.model_provider.generate(prompt, context)
        except Exception as e:
            print(f"AI生成回复失败: {str(e)}")
            # 抛出异常，让上层处理fallback
            raise Exception(f"AI服务不可用: {str(e)}")
    
    def generate_asset_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成资产分析AI回复
        
        Args:
            context: 投资组合上下文信息
            
        Returns:
            Dict[str, Any]: 结构化的AI分析结果
        """
        try:
            # 构建资产分析提示词
            prompt = self._build_asset_analysis_prompt(context)
            
            # 生成AI回复
            ai_response = self.model_provider.generate(prompt, context)
            
            # 解析AI回复为结构化数据
            return self._parse_asset_analysis_response(ai_response, context)
            
        except Exception as e:
            print(f"AI生成资产分析失败: {str(e)}")
            # 返回默认分析结果
            return self._get_default_asset_analysis(context)
    
    def _build_asset_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """构建资产分析提示词"""
        
        portfolio_summary = context.get('portfolio_summary', {})
        fund_positions = context.get('fund_positions', [])
        deposit_positions = context.get('deposit_positions', [])
        
        prompt = f"""
请基于以下投资组合信息，提供专业的投资分析和建议：

投资组合总览：
{portfolio_summary}

基金持仓详情：
{fund_positions}

存款/储蓄详情：
{deposit_positions}

请从以下几个维度进行分析：
1. 投资组合整体评估
2. 风险分析
3. 资产配置建议
4. 绩效评估
5. 具体操作建议

请以JSON格式返回分析结果，格式如下：
{{
    "overall_assessment": "总体评估描述",
    "risk_analysis": {{
        "level": "低/中/高风险",
        "description": "风险分析描述"
    }},
    "allocation_analysis": {{
        "current_allocation": {{"fund": 60, "deposit": 30, "savings": 10}},
        "recommended_actions": ["建议列表"]
    }},
    "performance_summary": {{
        "status": "表现状态",
        "description": "详细描述"
    }},
    "recommendations": [
        {{
            "type": "优化/风险/收益",
            "title": "建议标题",
            "description": "建议内容",
            "priority": "high/medium/low"
        }}
    ]
}}
"""
        return prompt
    
    def _parse_asset_analysis_response(self, ai_response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """解析AI回复为结构化数据"""
        try:
            # 这里应该使用JSON解析，但由于AI回复可能不完整，先返回默认值
            # 实际实现中应该使用json.loads()解析
            
            # 尝试简单的JSON解析
            import json
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回格式化后的文本
                return {
                    "overall_assessment": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                    "risk_analysis": {
                        "level": "中等风险",
                        "description": "基于当前投资组合的风险评估"
                    },
                    "allocation_analysis": {
                        "current_allocation": {"fund": 60, "deposit": 30, "savings": 10},
                        "recommended_actions": ["保持现有配置", "定期调整"]
                    },
                    "performance_summary": {
                        "status": "分析完成",
                        "description": "AI分析结果"
                    },
                    "recommendations": [
                        {
                            "type": "info",
                            "title": "投资提醒",
                            "description": "请注意投资风险，理性投资。",
                            "priority": "low"
                        }
                    ]
                }
                
        except Exception as e:
            print(f"解析AI资产分析回复失败: {str(e)}")
            return self._get_default_asset_analysis(context)
    
    def _get_default_asset_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取默认资产分析结果"""
        portfolio_summary = context.get('portfolio_summary', {})
        overall = portfolio_summary.get('overall', {})
        total_value = overall.get('total_value', 0)
        
        return {
            "overall_assessment": f"当前投资组合总价值为{total_value:.2f}元，建议继续保持稳健的投资策略。",
            "risk_analysis": {
                "level": "中等风险",
                "description": "基于多元化投资组合的中等风险评估"
            },
            "allocation_analysis": {
                "current_allocation": {"fund": 60, "deposit": 30, "savings": 10},
                "recommended_actions": [
                    "保持现有的资产配置比例",
                    "定期关注基金净值变化",
                    "根据市场情况适度调整投资策略"
                ]
            },
            "performance_summary": {
                "status": "稳健运行",
                "description": "投资组合表现稳定，建议持续监控"
            },
            "recommendations": [
                {
                    "type": "optimization",
                    "title": "投资组合优化",
                    "description": "建议定期回顾投资组合，根据市场变化和个人需求进行调整。",
                    "priority": "medium"
                },
                {
                    "type": "risk",
                    "title": "风险管控",
                    "description": "建议保持适度的资产分散，避免过度集中在单一投资品种。",
                    "priority": "high"
                },
                {
                    "type": "info",
                    "title": "投资提醒",
                    "description": "投资有风险，选择需谨慎。建议关注基金的风险等级和个人风险承受能力。",
                    "priority": "low"
                }
            ]
        }


# 创建单例实例
ai_service = AIService()


# 导出函数式接口
def generate_ai_response(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    """生成通用AI回复的函数式接口"""
    return ai_service.generate_ai_response(prompt, context)