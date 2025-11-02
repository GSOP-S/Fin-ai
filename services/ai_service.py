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


# 创建单例实例
ai_service = AIService()


# 导出函数式接口
def generate_ai_response(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    """生成通用AI回复的函数式接口"""
    return ai_service.generate_ai_response(prompt, context)