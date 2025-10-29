import React from 'react';
import './AIAssistant.css';

const AIAssistant = () => {
  return (
    <div className="ai-assistant-root">
      {/* AI助手图标 - 机器人（装饰用，无交互） */}
      <div className="ai-assistant-container ai-assistant-decorative">
        <div className="ai-assistant-icon">
          {/* 机器人SVG图标 */}
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            {/* 头部 */}
            <rect x="6" y="7" width="12" height="10" rx="2" fill="url(#robotGradient)" stroke="#fff" strokeWidth="0.5"/>
            {/* 眼睛 */}
            <circle cx="9" cy="11" r="1.5" fill="#fff"/>
            <circle cx="15" cy="11" r="1.5" fill="#fff"/>
            {/* 嘴巴 */}
            <path d="M 9 14 Q 12 15.5 15 14" stroke="#fff" strokeWidth="1" strokeLinecap="round" fill="none"/>
            {/* 天线 */}
            <line x1="12" y1="7" x2="12" y2="4" stroke="#fff" strokeWidth="1"/>
            <circle cx="12" cy="3.5" r="1" fill="#ffd700"/>
            {/* 身体 */}
            <rect x="8" y="17" width="8" height="4" rx="1" fill="url(#robotGradient)" stroke="#fff" strokeWidth="0.5"/>
            {/* 手臂 */}
            <rect x="4" y="8" width="2" height="6" rx="1" fill="url(#robotGradient)"/>
            <rect x="18" y="8" width="2" height="6" rx="1" fill="url(#robotGradient)"/>
            {/* 渐变定义 */}
            <defs>
              <linearGradient id="robotGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#667eea"/>
                <stop offset="100%" stopColor="#764ba2"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span className="ai-assistant-label">AI助手</span>
        
      </div>

    </div>
  );
};

export default AIAssistant;