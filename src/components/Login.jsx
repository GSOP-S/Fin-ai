import React, { useState } from 'react';
import './Login.css';
import { loginUser } from '../api/user';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 简单的验证逻辑
    if (!username || !password) {
      setError('请输入用户名和密码');
      return;
    }

    try {
      const result = await loginUser({ username, password });
      if (result.success) {
        const user = {
          username: result.data.username,
          displayName: result.data.display_name,
        };
        onLogin(user);
        setError('');
      }
    } catch (error) {
      console.error('登录失败:', error);
      setError(error.message || '登录过程中发生错误，请稍后重试');
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>欢迎登录</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">用户名</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入用户名"
              autoFocus
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="login-btn">登录</button>
        </form>
      </div>
    </div>
  );
};

export default Login;