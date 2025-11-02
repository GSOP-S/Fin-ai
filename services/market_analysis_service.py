"""
市场分析服务
提供市场趋势分析、热门板块推荐等功能
"""

from typing import Dict, Any, List
from datetime import datetime


class MarketAnalysisService:
    """市场分析服务类"""
    
    def __init__(self):
        self.market_trends = {
            "bull": "牛市",
            "bear": "熊市", 
            "sideways": "震荡市",
            "volatile": "高波动"
        }
        
        self.hot_sectors = [
            "新能源", "半导体", "医药生物", "消费电子", 
            "金融科技", "人工智能", "高端制造", "新材料"
        ]
    
    def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        import random
        
        # 模拟市场数据
        trend = random.choice(list(self.market_trends.keys()))
        hot_sectors = random.sample(self.hot_sectors, k=min(3, len(self.hot_sectors)))
        
        return {
            "trend": trend,
            "trend_name": self.market_trends[trend],
            "hotSectors": hot_sectors,
            "market_sentiment": random.choice(["乐观", "谨慎", "中性"]),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_market_suggestion(self, market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成市场分析建议"""
        if not market_data:
            market_data = self.get_market_overview()
        
        # 先生成本地建议作为兜底
        fallback_suggestion = self._fallback_market_suggestion(market_data)
        
        # 立即返回兜底建议，不等待AI调用
        import threading
        
        def call_ai_async():
            try:
                from services.model_provider import ModelProvider  # 延迟导入避免循环
                model = ModelProvider()
                prompt = (
                    f"当前市场趋势：{market_data.get('trend_name', '平稳')}\n"
                    f"热门板块：{', '.join(market_data.get('hotSectors', []))}\n"
                    f"市场情绪：{market_data.get('market_sentiment', '中性')}\n"
                    "请给出简要的市场分析建议（100字以内，中文）"
                )
                suggestion_text = model.generate(prompt, context={"type": "market"})
                # 这里可以更新缓存，但不影响已返回的兜底建议
                print(f"[MarketAnalysisService] AI建议已生成: {suggestion_text[:50]}...")
            except Exception as exc:
                print(f"[MarketAnalysisService] AI 调用失败: {exc}")
        
        # 启动后台线程调用AI，不阻塞主流程
        ai_thread = threading.Thread(target=call_ai_async, daemon=True)
        ai_thread.start()
        
        # 立即返回兜底建议
        return {"suggestion": fallback_suggestion, "market_data": market_data}
    
    def generate_market_suggestion_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """从上下文生成市场分析建议"""
        market_data = context.get('marketData', {})
        return self.generate_market_suggestion(market_data)
    
    def _fallback_market_suggestion(self, market_data: Dict[str, Any]) -> str:
        """生成市场分析的兜底建议"""
        trend = market_data.get('trend_name', '平稳')
        hot_sectors = market_data.get('hotSectors', [])
        
        if trend == "牛市":
            return f"当前市场处于{trend}，建议适当增加权益类资产配置，关注{hot_sectors[0] if hot_sectors else '优质板块'}等热门板块，注意控制仓位。"
        elif trend == "熊市":
            return f"当前市场处于{trend}，建议保持谨慎，适当增加债券等防御性资产配置，等待市场企稳后再加大权益类资产投入。"
        elif trend == "震荡市":
            return f"当前市场处于{trend}，建议采取均衡配置策略，可关注{hot_sectors[0] if hot_sectors else '优质板块'}等板块机会，注意分散投资风险。"
        else:  # 高波动
            return f"当前市场{trend}，建议控制仓位，关注基本面良好的优质资产，避免追涨杀跌，保持长期投资视角。"


# 创建服务实例
market_analysis_service = MarketAnalysisService()