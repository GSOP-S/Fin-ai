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
    const response = await request.get(API_ENDPOINTS.news.list, { params });
    
    if (response.success) {
      return response.data || [];
    } else {
      console.error('获取资讯列表失败:', response.message);
      return [];
    }
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
    const response = await request.get(API_ENDPOINTS.news.search, {
      params: {
        keyword,
        ...params
      }
    });
    
    if (response.success) {
      return response.data || [];
    } else {
      console.error('搜索资讯失败:', response.message);
      return [];
    }
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
    const response = await request.get(url);
    
    if (response.success) {
      return response.data;
    } else {
      console.error('获取资讯详情失败:', response.message);
      return null;
    }
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
    const response = await request.post(url);
    
    return response.success;
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
    const response = await request.get(API_ENDPOINTS.news.hot, {
      params: { limit }
    });
    
    if (response.success) {
      return response.data || [];
    } else {
      console.error('获取热门资讯失败:', response.message);
      return [];
    }
  } catch (error) {
    console.error('获取热门资讯异常:', error);
    return [];
  }
};

