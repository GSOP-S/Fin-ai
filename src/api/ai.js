// src/api/ai.js
import request from './request';
import { API_ENDPOINTS } from '../config/api.config';

export const generateAIResponse = (prompt, context = {}) =>
  request(API_ENDPOINTS.ai.interact, {
    method: 'POST',
    body: JSON.stringify({ prompt, context }),
  });


 const getFallbackSuggestion = (pageType, context = {}) => {
    const fallbacks = {
      'home': { 
        suggestion: `欢迎回来！。\n\n💡 今日建议：\n• 查看账单分析，了解本月消费情况\n• 关注理财产品，把握投资机会\n• 定期存款利率优惠中`
      },
      'market': { analysis: '市场分析：今日市场整体平稳。建议关注新能源、半导体等热门板块。' },
      'bill': { 
        summary: '本月总支出较上月有所增加，建议控制非必要支出。',
        suggestions: ['餐饮支出占较高，建议适当减少外出就餐', '储蓄率偏低，建议增加储蓄比例']
      },
      'transfer': {
        recentAccounts: context.recentAccounts || [],
        arrivalTime: '预计2小时内到账',
        suggestion: context.suggestion || '建议核实收款人信息后再转账'
      },
      'stock': { suggestion: `${context.stock?.name || '该股票'} 建议谨慎操作，注意风险控制。` },
      'fund': { suggestion: `${context.fund?.name || '该基金'} 建议长期持有，注意市场波动。` }
    };
    return fallbacks[pageType] || { suggestion: '暂无建议' };
  };

export const generateAISuggestion = async (pageType, context = {}) => {
    try {
      const result = await generateAIResponse(pageType, context);
      // 确保AI返回有效数据才使用，否则使用备用建议
      if (result.success && result.data) {
        return result.data;
      } else {
        console.error(`获取${pageType}建议失败:`, result.error);
        try {
          return getFallbackSuggestion(pageType, context);
        } catch (fallbackError) {
          console.error('备用建议生成失败:', fallbackError);
          return { suggestion: '暂无建议' };
        }
      }
    } catch (error) {
      console.error(`AI建议API调用失败(${pageType}):`, error);
      try {
        return getFallbackSuggestion(pageType, context);
      } catch (fallbackError) {
        console.error('备用建议生成失败:', fallbackError);
        return { suggestion: '暂无建议' };
      }
    }
  };
