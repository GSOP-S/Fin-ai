// src/api/fund.js
import request from './request';

export const fetchFundList = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/api/funds?${qs}`);
};

export const fetchFundDetail = (code) => request(`/api/fund/${encodeURIComponent(code)}`);