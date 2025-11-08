#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试API响应格式
"""

import requests
import json

def test_api_response():
    """测试API响应格式"""
    url = "http://localhost:5000/api/ai/analyze-logs"
    data = {
        "userId": "test_user",
        "pageType": "fund_detail",
        "pageUrl": "/fund/000001",
        "pageTitle": "测试基金",
        "userBehaviorLogs": [
            {"action": "view", "timestamp": "2025-11-07 10:00:00"},
            {"action": "click", "element": "buy_button", "timestamp": "2025-11-07 10:01:00"}
        ]
    }
    
    print("发送请求到API...")
    response = requests.post(url, json=data)
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"解析后的JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except:
            print("无法解析JSON响应")

if __name__ == "__main__":
    test_api_response()