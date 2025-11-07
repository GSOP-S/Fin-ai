"""
快速查看用户行为日志
"""
from mapper.behavior_mapper import behavior_mapper
import json

# 查询最近的日志
print("=" * 60)
print("最近20条用户行为日志：")
print("=" * 60)

try:
    conn = None
    from utils.db import get_db_connection, close_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_sql = """
    SELECT 
        event_type, 
        page, 
        element_id, 
        element_text,
        business_data,
        created_at
    FROM user_behavior_logs 
    ORDER BY created_at DESC 
    LIMIT 20
    """
    
    cursor.execute(query_sql)
    results = cursor.fetchall()
    
    if not results:
        print("\n暂无日志数据")
        print("\n提示：请在浏览器中点击几个按钮，然后再运行此脚本")
    else:
        for i, row in enumerate(results, 1):
            print(f"\n[{i}] {row['created_at']}")
            print(f"  事件类型: {row['event_type']}")
            print(f"  页面: {row['page']}")
            print(f"  元素ID: {row['element_id']}")
            print(f"  元素文本: {row['element_text']}")
            if row['business_data']:
                try:
                    business = json.loads(row['business_data'])
                    print(f"  业务数据: {business}")
                except:
                    pass
    
    print("\n" + "=" * 60)
    print(f"总计: {len(results)} 条日志")
    print("=" * 60)
    
except Exception as e:
    print(f"查询失败: {str(e)}")
finally:
    if cursor:
        cursor.close()
    if conn:
        close_db_connection(conn)

