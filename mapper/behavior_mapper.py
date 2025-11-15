"""
用户行为日志 Mapper
负责用户行为日志的数据库操作
"""

import json
from typing import List, Dict, Any, Optional
from utils.db import get_db_connection, close_db_connection


class BehaviorMapper:
    """用户行为日志数据访问对象"""
    
    @staticmethod
    def batch_insert_logs(events: List[Dict[str, Any]]) -> int:
        """
        批量插入行为日志
        
        Args:
            events: 事件列表
            
        Returns:
            成功插入的行数
        """
        if not events:
            return 0
        
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 批量插入SQL
            insert_sql = """
            INSERT INTO user_behavior_logs (
                event_id, event_type, user_id, session_id,
                page, page_url, referrer,
                element_type, element_id, element_text, element_class,
                business_data, duration, scroll_depth,
                context_data, timestamp
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s
            ) ON DUPLICATE KEY UPDATE 
                event_id = event_id  -- 避免重复插入
            """
            
            # 准备批量数据
            values_list = []
            for event in events:
                # 提取业务数据和上下文数据
                business_data = {}
                context_data = event.get('context', {})
                
                # 将除核心字段外的所有字段放入business_data
                core_fields = {
                    'event_id', 'event_type', 'user_id', 'session_id',
                    'page', 'page_url', 'referrer',
                    'element_type', 'element_id', 'element_text', 'element_class',
                    'duration', 'scroll_depth', 'timestamp', 'context'
                }
                
                for key, value in event.items():
                    if key not in core_fields and value is not None:
                        business_data[key] = value
                
                values = (
                    event.get('event_id'),
                    event.get('event_type'),
                    event.get('user_id'),
                    event.get('session_id'),
                    event.get('page'),
                    event.get('page_url'),
                    event.get('referrer'),
                    event.get('element_type'),
                    event.get('element_id'),
                    event.get('element_text'),
                    event.get('element_class'),
                    json.dumps(business_data, ensure_ascii=False) if business_data else None,
                    event.get('duration'),
                    event.get('scroll_depth'),
                    json.dumps(context_data, ensure_ascii=False) if context_data else None,
                    event.get('timestamp')
                )
                values_list.append(values)
            
            # 批量执行
            affected_rows = cursor.executemany(insert_sql, values_list)
            conn.commit()
            
            return affected_rows
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"批量插入行为日志失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            close_db_connection(conn)
    
    @staticmethod
    def get_user_behaviors(
        user_id: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        event_type: Optional[str] = None,
        page: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        查询用户行为日志
        
        Args:
            user_id: 用户ID
            start_time: 开始时间戳
            end_time: 结束时间戳
            event_type: 事件类型
            page: 页面
            limit: 限制条数
            
        Returns:
            行为日志列表
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 构建查询条件
            conditions = ["user_id = %s"]
            params = [user_id]
            
            if start_time:
                conditions.append("timestamp >= %s")
                params.append(start_time)
            
            if end_time:
                conditions.append("timestamp <= %s")
                params.append(end_time)
            
            if event_type:
                conditions.append("event_type = %s")
                params.append(event_type)
            
            if page:
                conditions.append("page = %s")
                params.append(page)
            
            where_clause = " AND ".join(conditions)
            params.append(limit)
            
            query_sql = f"""
            SELECT 
                id, event_id, event_type, user_id, session_id,
                page, page_url, referrer,
                element_type, element_id, element_text, element_class,
                business_data, duration, scroll_depth,
                context_data, timestamp, created_at
            FROM user_behavior_logs
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s
            """
            
            cursor.execute(query_sql, params)
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
            raise Exception(f"查询用户行为日志失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            close_db_connection(conn)
    
    @staticmethod
    def get_user_behavior_stats(user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        获取用户行为统计
        
        Args:
            user_id: 用户ID
            days: 统计天数
            
        Returns:
            统计结果
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            stats_sql = """
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(DISTINCT page) as total_pages,
                COUNT(DISTINCT event_type) as total_event_types,
                event_type,
                page,
                COUNT(*) as event_count
            FROM user_behavior_logs
            WHERE user_id = %s 
                AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY event_type, page
            ORDER BY event_count DESC
            """
            
            cursor.execute(stats_sql, (user_id, days))
            results = cursor.fetchall()
            
            # 统计按事件类型和页面分组
            event_type_stats = {}
            page_stats = {}
            
            total_events = 0
            total_sessions = 0
            total_pages = 0
            
            for row in results:
                event_type = row['event_type']
                page = row['page']
                count = row['event_count']
                
                total_events += count
                
                if event_type not in event_type_stats:
                    event_type_stats[event_type] = 0
                event_type_stats[event_type] += count
                
                if page not in page_stats:
                    page_stats[page] = 0
                page_stats[page] += count
            
            return {
                'total_events': total_events,
                'event_type_stats': event_type_stats,
                'page_stats': page_stats,
                'days': days
            }
            
        except Exception as e:
            raise Exception(f"获取用户行为统计失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            close_db_connection(conn)
    
    @staticmethod
    def get_recent_user_path(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户最近的页面访问路径
        
        Args:
            user_id: 用户ID
            limit: 限制条数
            
        Returns:
            页面访问路径
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query_sql = """
            SELECT page, timestamp, event_type
            FROM user_behavior_logs
            WHERE user_id = %s 
                AND event_type IN ('page_view', 'page_leave')
            ORDER BY timestamp DESC
            LIMIT %s
            """
            
            cursor.execute(query_sql, (user_id, limit))
            results = cursor.fetchall()
            
            return results
            
        except Exception as e:
            raise Exception(f"获取用户访问路径失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            close_db_connection(conn)


# 创建单例
behavior_mapper = BehaviorMapper()

