/**
 * 资讯相关API
 */

import request from './request';
import { API_ENDPOINTS } from '../config/api.config';

/**
 * 获取资讯列表
 * @param {Object} params - 查询参数
 * @param {string} params.category - 分类（可选）
 * @param {number} params.page - 页码（可选）
 * @param {number} params.pageSize - 每页数量（可选）
 * @returns {Promise<Array>} 资讯列表
 */
export const getNewsList = async (params = {}) => {
  try {
    const url = API_ENDPOINTS.news.list;
    const query = new URLSearchParams(params).toString();
    const resp = await request(`${url}${query ? `?${query}` : ''}`);
    if (resp.success) {
      const data = resp.data || {};
      return data.list || [];
    }
    console.error('获取资讯列表失败:', resp.message);
    return [];
  } catch (error) {
    console.error('获取资讯列表异常:', error);
    return [];
  }
};

/**
 * 搜索资讯
 * @param {string} keyword - 搜索关键词
 * @param {Object} params - 其他查询参数
 * @returns {Promise<Array>} 资讯列表
 */
export const searchNews = async (keyword, params = {}) => {
  try {
    const url = API_ENDPOINTS.news.search;
    const query = new URLSearchParams({ keyword, ...params }).toString();
    const resp = await request(`${url}?${query}`);
    if (resp.success) {
      const data = resp.data || {};
      return data.list || [];
    }
    console.error('搜索资讯失败:', resp.message);
    return [];
  } catch (error) {
    console.error('搜索资讯异常:', error);
    return [];
  }
};

/**
 * 获取资讯详情
 * @param {number} id - 资讯ID
 * @returns {Promise<Object|null>} 资讯详情
 */
export const getNewsDetail = async (id) => {
  try {
    const url = API_ENDPOINTS.news.detail.replace(':id', id);
    const resp = await request(url);
    if (resp.success) {
      return resp;
    }
    console.error('获取资讯详情失败:', resp.message);
    return null;
  } catch (error) {
    console.error('获取资讯详情异常:', error);
    return null;
  }
};

/**
 * 增加资讯阅读量
 * @param {number} id - 资讯ID
 * @returns {Promise<boolean>} 是否成功
 */
export const increaseReadCount = async (id) => {
  try {
    const url = API_ENDPOINTS.news.read.replace(':id', id);
    const resp = await request(url, { method: 'POST' });
    return !!resp.success;
  } catch (error) {
    console.error('增加阅读量失败:', error);
    return false;
  }
};

/**
 * 获取热门资讯
 * @param {number} limit - 数量限制（默认10）
 * @returns {Promise<Array>} 热门资讯列表
 */
export const getHotNews = async (limit = 10) => {
  try {
    const url = API_ENDPOINTS.news.hot;
    const query = new URLSearchParams({ limit }).toString();
    const resp = await request(`${url}?${query}`);
    if (resp.success) {
      const data = resp.data || {};
      return data.list || [];
    }
    console.error('获取热门资讯失败:', resp.message);
    return [];
  } catch (error) {
    console.error('获取热门资讯异常:', error);
    return [];
  }
};

