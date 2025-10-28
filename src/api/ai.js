// src/api/ai.js
import request from './request';
import { API_ENDPOINTS } from '../config/api.config';

export const generateAIResponse = (prompt, context = {}) =>
  request(API_ENDPOINTS.ai.interact, {
    method: 'POST',
    body: JSON.stringify({ prompt, context }),
  });

export const getPageSuggestion = (pageType, context = {}) =>
  request(API_ENDPOINTS.ai.suggestion, {
    method: 'POST',
    body: JSON.stringify({ pageType, context }),
  });