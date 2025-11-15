import React, { useState, useRef, useEffect } from 'react';
import { generateAISuggestion } from '../../api/ai';

const AIChat = ({ visible, onClose, position = { x: 0, y: 0 }, initialContent }) => {
  const [chatMessages, setChatMessages] = useState([]);

  // 初始内容处理
  useEffect(() => {
    if (initialContent && chatMessages.length === 0) {
      setChatMessages([{
        id: Date.now().toString(),
        content: initialContent,
        sender: 'ai',
        timestamp: new Date().toISOString()
      }]);
    }
  }, [initialContent]);
  const [userInput, setUserInput] = useState('');
  const chatContainerRef = useRef(null);
  const currentUtteranceRef = useRef(null);

  // 发送消息到AI聊天
  const sendToAIAssistant = async () => {
    if (!userInput.trim()) return;

    // 添加用户消息
    const userMessage = {
      type: 'user',
      content: userInput.trim(),
      timestamp: new Date().toISOString()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setUserInput('');

    // 显示加载状态
    const loadingMessage = {
      type: 'ai',
      content: '思考中...',
      timestamp: new Date().toISOString(),
      loading: true
    };
    setChatMessages(prev => [...prev, loadingMessage]);

    try {
      // 调用AI助手接口
      const result = await generateAISuggestion(userInput.trim(), {
        conversationHistory: chatMessages
      });

      // 更新消息，移除加载状态并添加AI回复
      setChatMessages(prev => prev.filter(msg => !msg.loading));
      if (result.success) {
        const aiMessage = {
          type: 'ai',
          content: result.data.response,
          timestamp: new Date().toISOString()
        };
        setChatMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      // 处理错误
      setChatMessages(prev => prev.filter(msg => !msg.loading));
      const errorMessage = {
        type: 'ai',
        content: '抱歉，我暂时无法回答，请稍后再试。',
        timestamp: new Date().toISOString()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }

    // 滚动到底部
    scrollToBottom();
  };

  // 语音输入功能
  const handleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();

      recognition.lang = 'zh-CN';
      recognition.interimResults = false;

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setUserInput(transcript);
      };

      recognition.onerror = (event) => {
        console.error('语音识别错误:', event.error);
      };

      recognition.start();
    } else {
      console.log('您的浏览器不支持语音识别功能');
    }
  };

  // 滚动到底部
  const scrollToBottom = () => {
    setTimeout(() => {
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
      }
    }, 100);
  };

  // 监听可见性变化，需要时滚动到底部
  useEffect(() => {
    if (visible) {
      scrollToBottom();
    }
  }, [visible, chatMessages]);

  return (
    <div className="ai-chat-container" style={{
      left: `${position.x}px`,
      top: `${position.y}px`,
      position: 'absolute',
      zIndex: 1000
    }}>
      <div className="ai-chat-header">
        <h3>AI助手</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="ai-chat-messages" ref={chatContainerRef}>
        {chatMessages.length === 0 ? (
          <div className="ai-chat-placeholder">
            你好！我是您的智能助手，请问有什么可以帮助你的？
          </div>
        ) : (
          chatMessages.map((message, index) => (
            <div 
              key={index} 
              className={`message ${message.type === 'user' ? 'user-message' : 'ai-message'}`}
            >
              <div className="message-content">{message.content}</div>
            </div>
          ))
        )}
      </div>

      <div className="ai-chat-input">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendToAIAssistant()}
          placeholder="输入您的问题..."
        />
        <button 
          className="voice-input-btn" 
          onClick={handleVoiceInput}
          title="语音输入"
        >
          🎤
        </button>
        <button 
          className="send-btn" 
          onClick={sendToAIAssistant}
          disabled={!userInput.trim()}
        >
          发送
        </button>
      </div>
    </div>
  );
};

export default AIChat;