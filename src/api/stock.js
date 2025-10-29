// src/api/stock.js
import request from './request';
import { generateAISuggestion } from './ai';

export const fetchStockList = (params = {}) => {
  const search = new URLSearchParams(params).toString();
  return request(`/api/stocks?${search}`);
};

export const generateMarketAnalysis = async () => {
    const result = await generateAISuggestion('market');
    return result?.analysis || '市场分析：今日市场整体平稳。建议关注新能源、半导体等热门板块。';
  };

export const fetchStockDetail = (name) => request(`/api/stock/${encodeURIComponent(name)}`);