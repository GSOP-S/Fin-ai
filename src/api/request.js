// src/api/request.js
// 通用 HTTP 请求封装，基于浏览器 fetch API
// 使用示例：
// import request from './request';
// const data = await request('/api/stocks');

const BASE_URL = '' // 同源，若需要可替换为后端服务地址，如 'http://localhost:5000'

/**
 * 统一请求封装
 * @param {string} url 请求地址（相对 / 绝对）
 * @param {object} options 其余 fetch 选项
 * @returns {Promise<any>} data 字段
 * @throws Error 当 success false 或网络失败
 */
export default async function request(url, options = {}) {
  const response = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    credentials: 'include',
    ...options,
  });

  // HTTP 层错误
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text}`);
  }

  const result = await response.json();

  // 业务层统一 success 字段判断
  if (!result.success) {
    const msg = result.message || 'Request failed';
    throw new Error(msg);
  }

  return result; // 返回完整结果，包含 data / pagination 等
}