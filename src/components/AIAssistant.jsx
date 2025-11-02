import React, { useState, useRef, useEffect } from 'react';
import AIChat from './ai/AIChat';
import AISuggestionBubble from './ai/AISuggestionBubble';
import './AIAssistant.css';

const AIAssistant = ({ ai, currentPage }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const dragRef = useRef(null);
  const initialOffset = useRef({ x: 0, y: 0 });

  // 初始化位置
  useEffect(() => {
    // 计算初始位置 - 左下角，确保在手机APP显示范围内
    const initialX = 20; // 左边距
    const initialY = window.innerHeight - 120; // 底部留出空间
    setPosition({ x: initialX, y: initialY });
  }, []);

  // 处理鼠标/触摸按下
  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
    const element = dragRef.current;
    if (!element) return;

    const rect = element.getBoundingClientRect();
    initialOffset.current = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  };

  // 处理触摸开始
  const handleTouchStart = (e) => {
    e.preventDefault();
    setIsDragging(true);
    const element = dragRef.current;
    if (!element) return;

    const touch = e.touches[0];
    const rect = element.getBoundingClientRect();
    initialOffset.current = {
      x: touch.clientX - rect.left,
      y: touch.clientY - rect.top
    };
  };

  // 处理移动
  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e) => {
      setPosition({
        x: e.clientX - initialOffset.current.x,
        y: e.clientY - initialOffset.current.y
      });
    };

    const handleTouchMove = (e) => {
      const touch = e.touches[0];
      setPosition({
        x: touch.clientX - initialOffset.current.x,
        y: touch.clientY - initialOffset.current.y
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('touchmove', handleTouchMove, { passive: false });

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('touchmove', handleTouchMove);
    };
  }, [isDragging]);

  // 处理释放 - 实现吸附效果
  useEffect(() => {
    const handleRelease = () => {
      if (!isDragging) return;
      setIsDragging(false);

      // 获取屏幕宽度
      const screenWidth = window.innerWidth;
      const screenHeight = window.innerHeight;
      const elementWidth = 60; // 元素宽度
      const elementHeight = 80; // 元素高度（包括标签）
      const minMargin = 10;

      // 计算吸附位置 - 吸附到最近的左右边缘
      let newX = position.x;
      let newY = position.y;

      // 水平方向吸附
      const centerPoint = screenWidth / 2;
      if (position.x + elementWidth / 2 < centerPoint) {
        newX = minMargin; // 吸附到左边
      } else {
        newX = screenWidth - elementWidth - minMargin; // 吸附到右边
      }

      // 垂直方向限制在屏幕内
      newY = Math.max(minMargin, Math.min(newY, screenHeight - elementHeight - minMargin));

      // 设置新位置
      setPosition({ x: newX, y: newY });
    };

    window.addEventListener('mouseup', handleRelease);
    window.addEventListener('touchend', handleRelease);

    return () => {
      window.removeEventListener('mouseup', handleRelease);
      window.removeEventListener('touchend', handleRelease);
    };
  }, [isDragging, position]);

  // 处理单击事件 - 打开AI聊天窗口
  const handleClick = () => {
    if (!isDragging) {
      setShowChat(!showChat);
    }
  };

  // 处理气泡打开聊天
  const handleOpenChatFromBubble = (content) => {
    setShowChat(true);
    ai.hide(); // 隐藏气泡
  };

  // 处理气泡关闭
  const handleBubbleClose = () => {
    ai.hide();
  };

  // 处理气泡反馈
  const handleBubbleFeedback = (type) => {
    console.log('Bubble feedback:', type);
    ai.hide();
  };

  return (
      <div className="ai-assistant-root">
        <div 
          className={`ai-assistant-container ${isDragging ? 'dragging' : ''}`}
          ref={dragRef}
          style={{
            left: `${position.x}px`,
            top: `${position.y}px`,
            bottom: 'auto',
            right: 'auto'
          }}
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
          onClick={handleClick}
          draggable={false}
        >
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

        {/* AI提示气泡 - 跟随图标位置 */}
        {ai.isVisible && (
          <AISuggestionBubble
            ai={ai}
            marketAnalysisShown={currentPage === 'financing'}
            onClose={handleBubbleClose}
            onOpenChat={handleOpenChatFromBubble}
            onFeedback={handleBubbleFeedback}
            style={{
              position: 'absolute',
              left: position.x + 80,
              top: position.y - 150,
              transform: position.x > window.innerWidth / 2 ? 'translateX(-100%)' : 'none',
              zIndex: 999
            }}
          />
        )}

        {/* AI聊天窗口 - 跟随图标位置 */}
        {showChat && (
          <AIChat 
            visible={showChat} 
            onClose={() => setShowChat(false)} 
            initialContent={ai.suggestionText}
            position={{ 
              x: position.x, 
              y: position.y - 320 // 向上偏移320px以显示在图标上方
            }} 
          />
        )}
      </div>
    );
};

export default AIAssistant;