/**
 * API配置文件
 * 统一管理所有API相关配置
 */

// 根据环境变量决定BaseURL
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  timeout: 10000,
  retryTimes: 3,
};

// API端点定义
export const API_ENDPOINTS = {
  // AI相关接口
  ai: {
    interact: '/api/ai/interact',
    suggestion: '/api/ai/suggestion',
    feedback: '/api/ai/feedback',
    settings: '/api/ai/settings',
  },
  
  // 账单相关接口
  bill: {
    list: '/api/bills',
    detail: '/api/bills/:id',
    analysis: '/api/bill-analysis',
  },
  
  // 转账相关接口
  transfer: {
    list: '/api/transfers',
    create: '/api/transfers',
    suggestion: '/api/transfer-suggestion',
  },
  
  
  
  // 基金相关接口
  fund: {
    list: '/api/funds',
    detail: '/api/fund/:code',
    suggestion: '/api/fund-suggestion',
  },
  
  // 用户相关接口
  user: {
    login: '/api/login',
    logout: '/api/logout',
    profile: '/api/user/profile',
  },
};

/**
 * 获取完整URL
 * @param {string} endpoint - 端点路径
 * @param {object} params - 路径参数 {id: '123'}
 * @returns {string} 完整URL
 */
export const getFullURL = (endpoint, params = {}) => {
  let url = endpoint;
  Object.keys(params).forEach(key => {
    url = url.replace(`:${key}`, params[key]);
  });
  return url;
};

