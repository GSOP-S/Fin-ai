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

// 获取基金建议的专用API，不显示气泡
export const getFundSuggestionOnly = async (fund) => {
  try {
    const fundData = {
      fundCode: fund.code,
      fundName: fund.name,
      fundType: fund.category,
      riskLevel: fund.risk,
      nav: fund.nav,
      change: fund.change,
      changePercent: fund.changePercent
    };
    
    const response = await fetch('/api/ai/suggestion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pageType: 'fund',
        context: { fundData }
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取基金建议失败:', error);
    return {
      success: false,
      data: {
        suggestion: '基金投资有风险，建议根据自身风险承受能力选择合适的基金产品。'
      }
    };
  }
};

// 带缓存的获取基金建议
const suggestionCache = new Map();
const CACHE_EXPIRY = 5 * 60 * 1000; // 5分钟缓存

export const getCachedFundSuggestion = async (fund) => {
  const cacheKey = fund.code;
  const cached = suggestionCache.get(cacheKey);
  
  // 检查缓存是否有效
  if (cached && Date.now() - cached.timestamp < CACHE_EXPIRY) {
    console.log(`使用缓存的基金建议: ${fund.code}`);
    return cached.data;
  }
  
  // 获取新建议
  const result = await getFundSuggestionOnly(fund);
  
  // 更新缓存
  suggestionCache.set(cacheKey, {
    data: result,
    timestamp: Date.now()
  });
  
  return result;
};