// src/api/ai.js
import request from './request';
import { API_ENDPOINTS } from '../config/api.config';

export const generateAIResponse = (prompt, context = {}) =>
  request(API_ENDPOINTS.ai.interact, {
    method: 'POST',
    body: JSON.stringify({ prompt, context }),
  });

export const generateAISuggestion = async (pageType, context = {}) => {
    try {
      const result = await request(API_ENDPOINTS.ai.suggestion, {
        method: 'POST',
        body: JSON.stringify({ pageType, context }),
      });
      
      // 确保AI返回有效数据
      if (result.success && result.data) {
        return result.data;
      } else {
        console.error(`获取${pageType}建议失败:`, result.error);
        return null;
      }
    } catch (error) {
      console.error(`AI建议API调用失败(${pageType}):`, error);
      return null;
    }
  };
