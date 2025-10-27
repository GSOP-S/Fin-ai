// src/api/feedback.js
// 用户反馈相关 API 封装
import request from './request';

/**
 * 提交用户对智能建议的反馈
 * @param {Object} params
 * @param {string} params.suggestionId - 建议的唯一 ID
 * @param {string} params.content - 建议内容
 * @param {string} params.type - 反馈类型，例如 'like' | 'dislike' | 'comment'
 * @param {string} [params.comment] - 额外评论内容，可选
 * @returns {Promise<{success: boolean, data?: any, error?: string}>}
 */
export const submitFeedback = ({ suggestionId, content, type, comment = '' }) =>
  request('/api/feedback', {
    method: 'POST',
    body: JSON.stringify({ suggestionId, content, type, comment }),
  });