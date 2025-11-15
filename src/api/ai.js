// src/api/ai.js
import request from './request';
import { API_ENDPOINTS } from '../config/api.config';

export const generateAIResponse = (prompt, context = {}) =>
  request(API_ENDPOINTS.ai.interact, {
    method: 'POST',
    body: JSON.stringify({ prompt, context }),
  });

export const generateAISuggestion = async (pageType, context = {}) => {
  // 添加用户信息日志
  if (context.userId) {
    console.log(`[API] 发送用户ID: ${context.userId} 用于${pageType}页面建议`);
  } else {
    console.log(`[API] 警告: 没有用户ID用于${pageType}页面建议`);
  }
  
  // 使用统一的AI建议接口，后端已实现完整的fallback机制
  const result = await request(API_ENDPOINTS.ai.suggestion, {
    method: 'POST',
    body: JSON.stringify({ pageType, context }),
  });
  
  // 确保AI返回有效数据
  if (result.success && result.data) {
    return result.data;
  } else {
    console.error(`获取${pageType}建议失败:`, result.error);
    throw new Error(`获取${pageType}建议失败: ${result.error}`);
  }
};

export const analyzeUserLogs = async (userId, pageType = '') => {
  // 添加用户信息日志
  console.log(`[API] 分析用户行为日志: ${userId} 用于${pageType || '所有'}页面`);
  
  // 使用新的日志分析接口
  const result = await request(API_ENDPOINTS.ai.analyzeLogs, {
    method: 'POST',
    body: JSON.stringify({ userId, pageType }),
  });
  
  // 确保API返回有效数据
  if (result.success && result.data) {
    return result.data;
  } else {
    console.error(`分析用户日志失败:`, result.error);
    throw new Error(`分析用户日志失败: ${result.error}`);
  }
};
