"""
用户行为追踪 Controller
处理前端行为日志上报请求
"""

from flask import Blueprint, request, jsonify
from mapper.behavior_mapper import behavior_mapper
from utils.response import success_response, error_response
from datetime import datetime

# 创建蓝图
behavior_bp = Blueprint('behavior', __name__, url_prefix='/api/behavior')


@behavior_bp.route('/track', methods=['POST'])
def track_behaviors():
    """
    接收并存储用户行为日志
    
    请求体格式：
    {
        "events": [...],
        "meta": {
            "client_time": 1234567890,
            "version": "1.0.0"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response('请求数据不能为空', 400)
        
        events = data.get('events', [])
        meta = data.get('meta', {})
        
        if not events:
            return error_response('事件列表不能为空', 400)
        
        if len(events) > 100:
            return error_response('单次上报事件数量不能超过100条', 400)
        
        # 数据验证
        valid_events = []
        user_id = None
        
        for event in events:
            if validate_event(event):
                valid_events.append(event)
                # 获取用户ID用于后续分析
                if not user_id and event.get('user_id'):
                    user_id = event.get('user_id')
        
        if not valid_events:
            return error_response('没有有效的事件数据', 400)
        
        # 批量插入数据库
        affected_rows = behavior_mapper.batch_insert_logs(valid_events)
        
        # 如果有用户ID，调用mock服务分析用户日志
        ai_suggestion = None
        if user_id:
            try:
                from services.mock import analyze_user_logs
                ai_suggestion = analyze_user_logs(user_id)
                print(f"[behavior_controller] 已为用户 {user_id} 生成AI建议")
            except Exception as e:
                print(f"[behavior_controller] 生成AI建议失败: {str(e)}")
        
        response_data = {
            'received': len(events),
            'valid': len(valid_events),
            'inserted': affected_rows,
            'server_time': int(datetime.now().timestamp() * 1000)
        }
        
        # 如果有AI建议，添加到响应中
        if ai_suggestion:
            response_data['ai_suggestion'] = ai_suggestion
        
        return success_response(response_data, '行为日志上报成功')
        
    except Exception as e:
        print(f"[behavior_controller] 上报失败: {str(e)}")
        return error_response(f'服务器错误: {str(e)}', 500)


@behavior_bp.route('/query', methods=['POST'])
def query_behaviors():
    """
    查询用户行为日志
    
    请求体格式：
    {
        "user_id": "12345",
        "start_time": 1234567890,
        "end_time": 1234567890,
        "event_type": "click",
        "page": "home",
        "limit": 100
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('user_id'):
            return error_response('user_id不能为空', 400)
        
        user_id = data.get('user_id')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        event_type = data.get('event_type')
        page = data.get('page')
        limit = data.get('limit', 100)
        
        # 查询数据
        behaviors = behavior_mapper.get_user_behaviors(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            event_type=event_type,
            page=page,
            limit=limit
        )
        
        return success_response({
            'behaviors': behaviors,
            'count': len(behaviors)
        })
        
    except Exception as e:
        print(f"[behavior_controller] 查询失败: {str(e)}")
        return error_response(f'查询失败: {str(e)}', 500)


@behavior_bp.route('/stats', methods=['POST'])
def get_behavior_stats():
    """
    获取用户行为统计
    
    请求体格式：
    {
        "user_id": "12345",
        "days": 7
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('user_id'):
            return error_response('user_id不能为空', 400)
        
        user_id = data.get('user_id')
        days = data.get('days', 7)
        
        # 获取统计数据
        stats = behavior_mapper.get_user_behavior_stats(user_id, days)
        
        return success_response(stats)
        
    except Exception as e:
        print(f"[behavior_controller] 统计失败: {str(e)}")
        return error_response(f'统计失败: {str(e)}', 500)


@behavior_bp.route('/path', methods=['POST'])
def get_user_path():
    """
    获取用户最近的页面访问路径
    
    请求体格式：
    {
        "user_id": "12345",
        "limit": 20
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('user_id'):
            return error_response('user_id不能为空', 400)
        
        user_id = data.get('user_id')
        limit = data.get('limit', 20)
        
        # 获取路径数据
        path = behavior_mapper.get_recent_user_path(user_id, limit)
        
        return success_response({
            'path': path,
            'count': len(path)
        })
        
    except Exception as e:
        print(f"[behavior_controller] 获取路径失败: {str(e)}")
        return error_response(f'获取路径失败: {str(e)}', 500)


def validate_event(event: dict) -> bool:
    """
    验证事件数据的有效性
    
    Args:
        event: 事件数据
        
    Returns:
        是否有效
    """
    # 必填字段
    required_fields = ['event_id', 'event_type', 'timestamp']
    
    for field in required_fields:
        if field not in event or event[field] is None:
            print(f"[validate_event] 缺少必填字段: {field}")
            return False
    
    # 字段长度验证
    if len(str(event.get('event_id', ''))) > 64:
        return False
    
    if len(str(event.get('event_type', ''))) > 50:
        return False
    
    # 时间戳合法性
    try:
        timestamp = int(event.get('timestamp', 0))
        # 时间戳应该在合理范围内（2020年-2030年）
        if timestamp < 1577836800000 or timestamp > 1893456000000:
            return False
    except:
        return False
    
    return True

