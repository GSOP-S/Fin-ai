"""
Mock日志分析服务
模拟大模型分析用户行为日志并返回固定响应
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from utils.db import get_db_connection, close_db_connection


class MockLogAnalysisService:
    
    def __init__(self):
        # 预定义的mock响应模板
        self.mock_responses = [
            {
                "suggestion": "根据您最近的浏览记录，您可能对以下基金感兴趣：混合型基金和债券基金可以作为您投资组合的稳定器。",
                "command": "bubble",
                "confidence": 0.85
            },
            {
                "suggestion": "我们注意到您最近查看了多只科技类基金，建议您关注一下新能源主题基金，该领域近期表现亮眼。",
                "command": "highlight",
                "fund_id": "FUND123456",
                "confidence": 0.92
            },
            {
                "suggestion": "您的投资组合目前偏重于股票型基金，建议适当增加一些债券型基金以平衡风险。",
                "command": "bubble",
                "confidence": 0.78
            },
            {
                "suggestion": "基于您的交易历史，我们发现您在市场波动时容易做出情绪化决策，建议设置定投计划以平摊成本。",
                "command": "bubble",
                "confidence": 0.88
            },
            {
                "suggestion": "您最近关注的FUND789012基金表现优异，基金经理经验丰富，建议您考虑纳入观察列表。",
                "command": "highlight",
                "fund_id": "FUND789012",
                "confidence": 0.90
            }
        ]
    
    def analyze_user_logs(self, user_id: str, page_type: Optional[str] = None) -> Dict[str, Any]:

        try:
            # 获取用户近7天的行为日志
            logs = self._get_recent_user_logs(user_id, days=7)
            
            # 根据日志数量和内容选择合适的mock响应
            if not logs:
                # 如果没有日志数据，返回默认响应
                response = {
                    "suggestion": "欢迎回来！建议您先浏览一下热门基金，了解当前市场趋势。",
                    "command": "bubble",
                    "confidence": 0.75
                }
            else:
                # 根据日志数量选择不同的mock响应
                log_count = len(logs)
                response_index = min(log_count % len(self.mock_responses), len(self.mock_responses) - 1)
                response = self.mock_responses[response_index].copy()
                
                # 添加日志统计信息
                response["analysis_summary"] = {
                    "log_count": log_count,
                    "days_analyzed": 7,
                    "most_active_page": self._get_most_active_page(logs),
                    "last_activity": self._format_timestamp(logs[0]["timestamp"]) if logs else None
                }
            
            # 添加元数据
            response["mock_mode"] = True
            response["timestamp"] = int(time.time())
            response["user_id"] = user_id
            
            return response
            
        except Exception as e:
            print(f"分析用户日志失败: {str(e)}")
            # 返回错误响应
            return {
                "suggestion": "抱歉，暂时无法提供个性化建议，请稍后再试。",
                "command": "bubble",
                "confidence": 0.5,
                "mock_mode": True,
                "error": str(e)
            }
    
    def _get_recent_user_logs(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 计算时间范围（最近7天）
            end_time = int(time.time() * 1000)  # 当前时间戳（毫秒）
            start_time = end_time - (days * 24 * 60 * 60 * 1000)  # 7天前的时间戳
            
            query_sql = """
            SELECT 
                id, event_id, event_type, user_id, session_id,
                page, page_url, referrer,
                element_type, element_id, element_text, element_class,
                business_data, duration, scroll_depth,
                context_data, timestamp, created_at
            FROM user_behavior_logs
            WHERE user_id = %s AND timestamp >= %s AND timestamp <= %s
            ORDER BY timestamp DESC
            LIMIT 100
            """
            
            cursor.execute(query_sql, (user_id, start_time, end_time))
            results = cursor.fetchall()
            
            # 解析JSON字段
            for row in results:
                if row.get('business_data'):
                    try:
                        row['business_data'] = json.loads(row['business_data'])
                    except:
                        pass
                
                if row.get('context_data'):
                    try:
                        row['context_data'] = json.loads(row['context_data'])
                    except:
                        pass
            
            return results
            
        except Exception as e:
            print(f"获取用户行为日志失败: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            close_db_connection(conn)
    
    def _get_most_active_page(self, logs: List[Dict[str, Any]]) -> str:

        if not logs:
            return "无"
        
        page_counts = {}
        for log in logs:
            page = log.get('page', 'unknown')
            page_counts[page] = page_counts.get(page, 0) + 1
        
        return max(page_counts.items(), key=lambda x: x[1])[0]
    
    def _format_timestamp(self, timestamp: int) -> str:

        try:
            dt = datetime.fromtimestamp(timestamp / 1000)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "未知时间"


mock_log_analysis_service = MockLogAnalysisService()

def analyze_user_logs(user_id: str, page_type: Optional[str] = None) -> Dict[str, Any]:
    """分析用户行为日志的函数式接口"""
    return mock_log_analysis_service.analyze_user_logs(user_id, page_type)