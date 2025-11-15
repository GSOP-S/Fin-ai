// src/api/bill.js
import request from './request';
import { API_ENDPOINTS } from '../config/api.config';

// 获取账单分析（使用统一的AI建议接口）
export const fetchBillAnalysis = (userId, bills = [], month = null) =>
  request(API_ENDPOINTS.ai.suggestion, {
    method: 'POST',
    body: JSON.stringify({ 
      pageType: 'bill', 
      userId, 
      timeRange: month || '本月',
      context: { bills }
    }),
  });

// 获取用户账单列表
export const fetchUserBills = (userId, month = null) => {
  const url = month ? `/api/bills/${encodeURIComponent(userId)}?month=${encodeURIComponent(month)}` : `/api/bills/${encodeURIComponent(userId)}`;
  return request(url);
};