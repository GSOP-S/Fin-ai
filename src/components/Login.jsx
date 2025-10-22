import React, { useState } from 'react';
import './Login.css';

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
      // 调用后端登录API
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // 登录成功，调用父组件的onLogin方法
        const user = {
          username: data.data.username,
          displayName: data.data.display_name
        };
        onLogin(user);
        setError('');
      } else {
        // 登录失败，显示错误信息
        setError(data.message || '用户名或密码错误');
      }
    } catch (error) {
      // 网络错误或其他异常
      console.error('登录失败:', error);
      setError('登录过程中发生错误，请稍后重试');
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