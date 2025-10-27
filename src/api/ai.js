// src/api/ai.js
import request from './request';

export const generateAIResponse = (prompt, context = {}) =>
  request('/api/ai/interact', {
    method: 'POST',
    body: JSON.stringify({ prompt, context }),
  });

export const getPageSuggestion = (pageType, context = {}) =>
  request('/api/ai/suggestion', {
    method: 'POST',
    body: JSON.stringify({ pageType, context }),
  });