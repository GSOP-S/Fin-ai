#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试演示页面功能
"""

import requests
import json
import time

def test_demo_page():
    """测试演示页面"""
    base_url = "http://localhost:5000"
    
    print("=== 测试演示页面功能 ===")
    
    # 1. 测试页面访问
    print("\n1. 测试页面访问")
    try:
        response = requests.get(f"{base_url}/mock_demo.html")
        if response.status_code == 200:
            print("✓ 演示页面访问成功")
        else:
            print(f"✗ 演示页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 页面访问异常: {e}")
    
    # 2. 测试API接口
    print("\n2. 测试API接口")
    test_cases = [
        {
            "name": "基金详情页面测试",
            "data": {
                "userId": "demo_user_1",
                "pageType": "fund_detail",
                "pageUrl": "/fund/000001",
                "pageTitle": "华夏成长混合",
                "userBehaviorLogs": [
                    {"action": "view", "timestamp": "2025-11-07 10:00:00"},
                    {"action": "click", "element": "buy_button", "timestamp": "2025-11-07 10:01:00"},
                    {"action": "scroll", "position": "middle", "timestamp": "2025-11-07 10:02:00"}
                ]
            }
        },
        {
            "name": "自选页面测试",
            "data": {
                "userId": "demo_user_2",
                "pageType": "favorites",
                "pageUrl": "/favorites",
                "pageTitle": "我的自选",
                "userBehaviorLogs": [
                    {"action": "view", "timestamp": "2025-11-07 09:00:00"},
                    {"action": "click", "element": "fund_item", "fund_id": "000001", "timestamp": "2025-11-07 09:01:00"},
                    {"action": "click", "element": "fund_item", "fund_id": "000002", "timestamp": "2025-11-07 09:02:00"}
                ]
            }
        },
        {
            "name": "错误处理测试",
            "data": {
                "pageType": "fund_detail",
                "userBehaviorLogs": []
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  测试用例 {i}: {test_case['name']}")
        try:
            response = requests.post(
                f"{base_url}/api/ai/analyze-logs",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ 请求成功，状态码: {response.status_code}")
                
                # 检查响应结构
                if "data" in result and "command" in result["data"]:
                    print(f"  ✓ 命令类型: {result['data']['command']}")
                else:
                    print("  ✗ 响应中缺少command字段")
                
                if "data" in result and "suggestion" in result["data"]:
                    print(f"  ✓ 包含分析结果: {result['data']['suggestion'][:50]}...")
                else:
                    print("  ✗ 响应中缺少suggestion字段")
                
                # 检查命令格式
                command = result.get("data", {}).get("command")
                if command in ["bubble", "highlight"]:
                    print("  ✓ 命令格式正确")
                else:
                    print(f"  ✗ 无效的命令格式: {command}")
                    
            else:
                print(f"  ✗ 请求失败，状态码: {response.status_code}")
                print(f"  错误信息: {response.text}")
                
        except Exception as e:
            print(f"  ✗ 请求异常: {e}")
    
    print("\n=== 测试完成 ===")
    print("请访问 http://localhost:5000/mock_demo.html 查看演示页面")

if __name__ == "__main__":
    test_demo_page()