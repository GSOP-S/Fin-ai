import React, { useState, useEffect, useRef } from 'react';
import './AIAssistantDialog.css';

const AIAssistantDialog = ({ isOpen, onClose, onSendMessage, initialMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // 初始化消息
  useEffect(() => {
    if (isOpen && initialMessage) {
      setMessages([{
        type: 'ai',
        content: initialMessage,
        timestamp: new Date().toISOString()
      }]);
    } else if (isOpen) {
      setMessages([{
        type: 'ai',
        content: '你好！我是您的智能金融助手，请问有什么可以帮助您的？',
        timestamp: new Date().toISOString()
      }]);
    }
  }, [isOpen, initialMessage]);

  // 滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    };

    // 添加用户消息
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // 调用父组件传递的发送消息函数
      const aiResponse = await onSendMessage(inputValue.trim());
      
      const aiMessage = {
        type: 'ai',
        content: aiResponse,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'ai',
        content: '抱歉，我遇到了一些问题，请稍后再试。',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="ai-assistant-dialog-overlay" onClick={onClose}>
      <div className="ai-assistant-dialog" onClick={e => e.stopPropagation()}>
        <div className="ai-assistant-dialog-header">
          <h3>智能金融助手</h3>
          <button className="ai-dialog-close" onClick={onClose}>×</button>
        </div>
        
        <div className="ai-assistant-dialog-messages">
          {messages.map((message, index) => (
            <div key={index} className={`ai-message ${message.type}`}>
              <div className="ai-message-content">
                {message.content}
              </div>
              <div className="ai-message-time">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="ai-message ai">
              <div className="ai-message-content">
                <div className="ai-loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="ai-assistant-dialog-input">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="请输入您的问题..."
            disabled={isLoading}
          />
          <button 
            className="ai-send-button" 
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
          >
            发送
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIAssistantDialog;