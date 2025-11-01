import React from 'react';
import './AISuggestionBubble.css';

const AISuggestionBubble = ({ ai, marketAnalysisShown, onClose, onOpenChat }) => {
  // 如果AI不可见，不渲染组件
  if (!ai || !ai.isVisible) {
    return null;
  }

  return (
    <div className={`ai-suggestion-bubble ${marketAnalysisShown ? 'market-analysis' : ''}`}>
      <div className="ai-suggestion-header">
        <span>
          {marketAnalysisShown ? '📊 今日市场分析' : '💡 智能建议'}
        </span>
        <button 
          className="close-bubble-btn"
          onClick={(e) => {
            e.stopPropagation();
            onClose();
          }}
          style={{ zIndex: 1002 }}
        >
          ×
        </button>
      </div>
      <div className="ai-suggestion-content">
        {ai.suggestionText && ai.suggestionText.split('\n').map((line, index) => (
          <p key={index} className="suggestion-line">{line}</p>
        ))}
        <div className="bubble-actions">
          <div className="feedback-buttons">
            {/* Feedback buttons will be added here */}
          </div>
          <button 
            className="speak-btn"
            onClick={(e) => {
              e.stopPropagation();
              ai.toggleSpeech(ai.suggestionText);
            }}
            title="语音播报"
          >
            🔊
          </button>
          <button 
            className="open-chat-btn"
            onClick={(e) => {
              e.stopPropagation();
              onOpenChat(ai.suggestionText);
            }}
          >
            详细对话
          </button>
        </div>
      </div>
    </div>
  );
};

export default AISuggestionBubble;