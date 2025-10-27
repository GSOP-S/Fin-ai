// src/api/user.js
import request from './request';

export const loginUser = ({ username, password }) =>
  request('/api/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });

export const fetchUserInfo = (userId) => request(`/api/user/${encodeURIComponent(userId)}`);