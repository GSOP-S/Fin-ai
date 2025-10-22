import React from 'react';
import './AIAssistant.css';

const AIAssistant = ({ isVisible = true, onClick, onHover, onLeave, hasNewSuggestion }) => {
  if (!isVisible) return null;

  return (
    <div 
      className={`ai-assistant-container ${hasNewSuggestion ? 'has-suggestion' : ''}`}
      onClick={onClick}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
    >
      <div className="ai-assistant-icon">
        {/* 使用指定的图标 */}
        <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
          <rect x="2" y="2" width="20" height="20" rx="10" fill="#28a745"/>
          <circle cx="8" cy="12" r="2" fill="white"/>
          <circle cx="16" cy="12" r="2" fill="white"/>
        </svg>
      </div>
      <span className="ai-assistant-label">AI助手</span>
      {hasNewSuggestion && <div className="notification-dot"></div>}
    </div>
  );
};

export default AIAssistant;