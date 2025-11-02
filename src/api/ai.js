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
    // 添加用户信息日志
    if (context.userId) {
      console.log(`[API] 发送用户ID: ${context.userId} 用于${pageType}页面建议`);
    } else {
      console.log(`[API] 警告: 没有用户ID用于${pageType}页面建议`);
    }
    
    // 使用统一的AI建议接口
    const result = await request(API_ENDPOINTS.ai.suggestion, {
      method: 'POST',
      body: JSON.stringify({ pageType, context }),
    });
    
    // 确保AI返回有效数据
    if (result.success && result.data) {
      return result.data;
    } else {
      console.error(`获取${pageType}建议失败:`, result.error);
      // 返回备用建议而不是null
      return getFallbackSuggestion(pageType);
    }
  } catch (error) {
    console.error(`AI建议API调用失败(${pageType}):`, error);
    // 返回备用建议而不是null
    return getFallbackSuggestion(pageType);
  }
};
  
  // 备用建议函数
  function getFallbackSuggestion(pageType) {
    const fallbackSuggestions = {
      home: { suggestion: '欢迎使用智能银行系统！建议您定期查看账户明细，合理规划理财投资。' },
      fund: { suggestion: '基金投资有风险，建议根据自身风险承受能力选择合适的基金产品。' },
      bill: { suggestion: '建议您定期查看账单明细，合理控制支出，提高储蓄率。' },
      transfer: { suggestion: '转账时请仔细核对收款人信息，大额转账建议分批进行。' },
      market: { suggestion: '市场有风险，投资需谨慎。建议分散投资，降低风险。' },
    };
    return fallbackSuggestions[pageType] || { suggestion: '暂无相关建议' };
  }
