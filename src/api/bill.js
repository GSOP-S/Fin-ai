// src/api/bill.js
import request from './request';
import { generateAISuggestion } from './ai';

// 生成账单AI分析
 export const generateBillAnalysis = (transactions) => {
  // 计算总支出和收入
  const totalIncome = transactions
    .filter(t => t.amount > 0)
    .reduce((sum, t) => sum + t.amount, 0);

  const totalExpense = transactions
    .filter(t => t.amount < 0)
    .reduce((sum, t) => sum + Math.abs(t.amount), 0);

  // 按类别统计支出
  const categoryExpenses = {};
  transactions
    .filter(t => t.amount < 0 && t.category !== '收入')
    .forEach(t => {
      const absAmount = Math.abs(t.amount);
      categoryExpenses[t.category] = (categoryExpenses[t.category] || 0) + absAmount;
    });

  // 找出主要支出类别
  const mainCategories = Object.entries(categoryExpenses)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  // 检测异常消费
  const abnormalTransactions = transactions
    .filter(t => t.amount < 0)
    .filter(t => Math.abs(t.amount) > totalExpense * 0.3 || 
                (t.category === '餐饮' && t.amount < -200) || 
                (t.category === '购物' && t.amount < -1000));

  // 生成优化建议（调用ai.js中的AI服务）
  const suggestions = generateAISuggestion('bill_analysis', {
    totalIncome,
    totalExpense,
    categoryExpenses,
    abnormalTransactions
  });

  return {
    summary: {
      totalIncome,
      totalExpense,
      savingRate: totalIncome > 0 ? ((totalIncome - totalExpense) / totalIncome * 100).toFixed(1) : 0
    },
    categoryDistribution: mainCategories.map(([category, amount]) => ({
      category,
      amount,
      percentage: (amount / totalExpense * 100).toFixed(1)
    })),
    abnormalTransactions: abnormalTransactions.map(t => ({
      id: t.id,
      merchant: t.merchant,
      amount: t.amount,
      date: t.date,
      reason: Math.abs(t.amount) > totalExpense * 0.3 ? '超过月总支出30%' : 
             t.category === '餐饮' ? '单次餐饮消费过高' : '单次购物消费过高'
    })),
    suggestions
  };
}

export const fetchBillAnalysis = (userId) =>
  request('/api/bill-analysis', {
    method: 'POST',
    body: JSON.stringify({ userId }),
  });

export const fetchUserBills = (userId) => request(`/api/bills/${encodeURIComponent(userId)}`);