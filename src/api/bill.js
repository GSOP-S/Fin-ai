// src/api/bill.js
import request from './request';

export const fetchBillAnalysis = (userId) =>
  request('/api/bill-analysis', {
    method: 'POST',
    body: JSON.stringify({ userId }),
  });

export const fetchUserBills = (userId) => request(`/api/bills/${encodeURIComponent(userId)}`);