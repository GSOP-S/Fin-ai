// src/api/fund.js
import request from './request';

export const fetchFundList = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/api/funds?${qs}`);
};

export const fetchFundDetail = (code) => request(`/api/fund/${encodeURIComponent(code)}`);

// 获取基金建议
export const fetchFundSuggestion = (fundCode) => {
  const qs = new URLSearchParams({ code: fundCode }).toString();
  return request(`/api/fund-suggestion?${qs}`);
};

// 获取基金建议并显示AI气泡
export const showFundSuggestion = async (fund, aiInstance) => {
  try {
    // 使用统一的AI建议接口
    const fundData = {
      fundCode: fund.code,
      fundName: fund.name,
      fundType: fund.category,
      riskLevel: fund.risk,
      nav: fund.nav,
      change: fund.change,
      changePercent: fund.changePercent
    };
    
    // 使用aiInstance直接显示基金建议
    aiInstance.show('fund', { fundData }, {
      autoShow: true,
      autoHideDelay: 20000, // 20秒后自动隐藏
      speakEnabled: false
    });
  } catch (error) {
    console.error('获取基金建议失败:', error);
    // 显示错误提示
    aiInstance.show('fund', { fund, suggestion: '获取基金建议失败，请稍后重试' }, {
      autoShow: true,
      autoHideDelay: 20000,
      speakEnabled: false
    });
  }
};