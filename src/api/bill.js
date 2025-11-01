// src/api/bill.js
import request from './request';

// 获取账单分析（使用后端API）
export const fetchBillAnalysis = (userId, bills = [], month = null) =>
  request('/api/bill-analysis', {
    method: 'POST',
    body: JSON.stringify({ userId, bills, month }),
  });

// 获取用户账单列表
export const fetchUserBills = (userId, month = null) => {
  const url = month ? `/api/bills/${encodeURIComponent(userId)}?month=${encodeURIComponent(month)}` : `/api/bills/${encodeURIComponent(userId)}`;
  return request(url);
};