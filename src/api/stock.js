// src/api/stock.js
import request from './request';

export const fetchStockList = (params = {}) => {
  const search = new URLSearchParams(params).toString();
  return request(`/api/stocks?${search}`);
};

export const fetchStockDetail = (name) => request(`/api/stock/${encodeURIComponent(name)}`);