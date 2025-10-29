import React, { useState, useEffect, useRef } from 'react';
import './AIAssistant.css';
import { useLocation } from 'react-router-dom';
import { getPageSuggestion } from '../api/ai';


const AIAssistant = ({ onAction, user, showBubble, suggestion, suggestionId, onCloseBubble }) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [currentSuggestionId, setCurrentSuggestionId] = useState(null);
  const [showSuggestionBubble, setShowSuggestionBubble] = useState(false);
  const [currentSuggestion, setCurrentSuggestion] = useState('');
  const [suggestionData, setSuggestionData] = useState({});
  const [loading, setLoading] = useState(false);
  const [hasNewSuggestion, setHasNewSuggestion] = useState(false);
  const location = useLocation();
  const currentPage = location.pathname.split('/')[1] || 'home';
  const suggestionTimeoutRef = useRef(null);


  // 备用建议生成（离线模式）
  const getFallbackSuggestion = (pageType, context = {}) => {
    const fallbacks = {
      'home': { 
        suggestion: `欢迎回来！💡 今日建议：\n• 查看账单分析，了解本月消费情况\n• 关注理财产品，把握投资机会\n• 定期存款利率优惠中`
      },
      'transfer': {
        suggestion: `转账建议：\n• 建议核实收款人信息后再转账\n• 跨行转账可能会有手续费\n• 大额转账建议选择工作时间操作`
      },
      'financing': {
        suggestion: `理财建议：\n• 分散投资，降低风险\n• 根据个人风险承受能力选择产品\n• 定期关注市场动态，及时调整投资策略`
      },
      'bill': { 
        suggestion: `账单分析：\n• 本月消费情况概览\n• 建议控制非必要支出\n• 提高储蓄率，为未来做准备`
      }
    };
    return fallbacks[pageType] || { suggestion: '您好！有什么可以帮助您的吗？' };
  };

  // 监听建议变化显示气泡
  useEffect(() => {
    if (showBubble && suggestion && suggestionId) {
      setCurrentSuggestion(suggestion);
      setCurrentSuggestionId(suggestionId);
      showSuggestionAutomatically();
    } else if (!showBubble) {
      setShowSuggestionBubble(false);
    }
  }, [showBubble, suggestion, suggestionId]);

  // 清除定时器
  useEffect(() => {
    return () => {
      if (suggestionTimeoutRef.current) {
        clearTimeout(suggestionTimeoutRef.current);
      }
    };
  }, []);

  // 根据当前页面获取AI建议
  useEffect(() => {
    const fetchAISuggestions = async () => {
      // 未登录用户不显示建议
      if (!user) {
        setCurrentSuggestion('');
        setShowSuggestionBubble(false);
        setHasNewSuggestion(false);
        return;
      }
      
      setLoading(true);
      try {
        // 调用后端API获取建议
        const pageType = getCurrentPage();
        const result = await getPageSuggestion(pageType, {}, user.id);
        
        let suggestionData;
        if (result && result.success) {
          suggestionData = result.data;
        } else {
          // 使用备用建议
          suggestionData = getFallbackSuggestion(pageType);
        }
        
        setSuggestionData(suggestionData);
        
        // 提取建议文本
        let suggestionText = '';
        if (typeof suggestionData === 'string') {
          suggestionText = suggestionData;
        } else if (suggestionData.suggestion) {
          suggestionText = suggestionData.suggestion;
        } else if (suggestionData.analysis) {
          suggestionText = suggestionData.analysis;
        }
        
        if (suggestionText) {
          setCurrentSuggestion(suggestionText);
          setHasNewSuggestion(true);
          
          // 自动显示气泡建议
          showSuggestionAutomatically(suggestionText);
        }
      } catch (error) {
        console.error('获取AI建议失败:', error);
        // 使用备用建议
        const fallback = getFallbackSuggestion(getCurrentPage());
        setSuggestionData(fallback);
        setCurrentSuggestion(fallback.suggestion);
        setHasNewSuggestion(true);
        
        // 显示备用建议气泡
        showSuggestionAutomatically(fallback.suggestion);
      } finally {
        setLoading(false);
      }
    };

    // 页面切换时获取建议
    fetchAISuggestions();
    
    // 清除定时器
    return () => {
      if (suggestionTimeoutRef.current) {
        clearTimeout(suggestionTimeoutRef.current);
      }
    };
  }, [currentPage]);

  // 自动显示建议气泡
  const isMouseOverBubble = useRef(false);

  const showSuggestionAutomatically = () => {
    if (!user || !currentSuggestion) return;
    
    // 清除之前的定时器
    if (suggestionTimeoutRef.current) {
      clearTimeout(suggestionTimeoutRef.current);
    }

    // 设置新的定时器显示气泡
    suggestionTimeoutRef.current = setTimeout(() => {
      setShowSuggestionBubble(true);
      // 5秒后自动隐藏
      suggestionTimeoutRef.current = setTimeout(() => {
        if (!isMouseOverBubble.current) {
          setShowSuggestionBubble(false);
          onCloseBubble?.();
        }
      }, 5000);
    }, 800);
  }
    // 清除之前的定时器
    if (suggestionTimeoutRef.current) {
      clearTimeout(suggestionTimeoutRef.current);
    }
    
    // 延迟1秒显示气泡
    setTimeout(() => {
      if (hasNewSuggestion) {
        setShowSuggestionBubble(true);
        
        // 15秒后自动隐藏气泡
        suggestionTimeoutRef.current = setTimeout(() => {
          setShowSuggestionBubble(false);
          setHasNewSuggestion(false);
        }, 15000);
      }
    }, 1000);
  };



  // 处理点击AI助手图标
  const handleAssistantClick = () => {
    if (showSuggestionBubble) {
      // 如果气泡已显示，则关闭气泡并打开对话框
      setShowSuggestionBubble(false);
      setIsDialogOpen(true);
      onCloseBubble?.();
    } else if (!isDialogOpen) {
      // 如果都未显示，则直接打开对话框
      // 如果没有当前建议，使用默认欢迎语
      if (!currentSuggestion) {
        const defaultSuggestion = '您好！我是您的智能金融助手，有什么可以帮助您的吗？';
        setCurrentSuggestion(defaultSuggestion);
        setSuggestionData({ suggestion: defaultSuggestion });
      }
      setIsDialogOpen(true);
    } else {
      // 如果对话框已打开，则关闭
      setIsDialogOpen(false);
    }
    setHasNewSuggestion(false);
    
    // 调用父组件的回调
    if (onAction) {
      onAction('show_dialog', { page: getCurrentPage() });
    }
  }

  // 处理点击外部关闭弹窗
  useEffect(() => {
    const handleClickOutside = (event) => {
      const aiContainer = document.querySelector('.ai-assistant-container');
      const aiDialog = document.querySelector('.ai-dialog');
      const aiBubble = document.querySelector('.ai-suggestion-bubble');
      
      if (aiContainer && 
          !aiContainer.contains(event.target) && 
          (!aiDialog || !aiDialog.contains(event.target)) &&
          (!aiBubble || !aiBubble.contains(event.target))) {
        
        // 点击外部只关闭对话框，不关闭气泡（气泡有自己的自动关闭逻辑）
        setIsDialogOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 确定当前页面
  const getCurrentPage = () => {
    switch(currentPage) {
      case 'transfer': return 'transfer';
      case 'financing': return 'financing';
      case 'account': return 'bill';
      default: return 'home';
    }
  };

  // 关闭气泡
  const closeSuggestionBubble = () => {
    setShowSuggestionBubble(false);
    setHasNewSuggestion(false);
    onCloseBubble?.();
  }

  // 关闭对话框
  const closeDialog = () => {
    setIsDialogOpen(false);
  };

  // 从气泡打开对话框
  const openDialogFromBubble = () => {
    setShowSuggestionBubble(false);
    setIsDialogOpen(true);
    setHasNewSuggestion(false);
  };

  return (
    <div className="ai-assistant-root">
      {/* AI助手图标 - 机器人（手机端优化尺寸） */}
      <div 
        className={`ai-assistant-container ${hasNewSuggestion ? 'has-suggestion' : ''}`}
        onClick={handleAssistantClick}
        aria-label="智能金融助手"
      >
        <div className="ai-assistant-icon">
          {/* 机器人SVG图标 - 优化尺寸适合手机端 */}
          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
            {/* 渐变定义 */}
            <defs>
              <linearGradient id="robotGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#667eea"/>
                <stop offset="100%" stopColor="#764ba2"/>
              </linearGradient>
            </defs>
          </svg>
          {hasNewSuggestion && <div className="notification-dot"></div>}
        </div>
      </div>

      {/* AI建议气泡 - 自动显示 */}
      {showSuggestionBubble && currentSuggestion && (
        <div className="ai-suggestion-bubble" onClick={openDialogFromBubble}>
          <div className="ai-suggestion-header">
            <span className="ai-bubble-title">💡 智能建议</span>
            <button className="ai-bubble-close" onClick={(e) => {
              e.stopPropagation();
              closeSuggestionBubble();
            }}>×</button>
          </div>
          <div className="ai-suggestion-content">
            {currentSuggestion.split('\n').map((line, index) => (
              <React.Fragment key={index}>
                {line}
                <br />
              </React.Fragment>
            ))}
          </div>
          <div className="ai-bubble-actions">

            <button className="bubble-action-btn primary" onClick={openDialogFromBubble}>查看详情</button>
          </div>
        </div>
      )}

      {/* AI对话框 - 点击图标打开 */}
      {isDialogOpen && (
        <div className="ai-dialog-overlay" onClick={closeDialog}>
          <div 
            className="ai-dialog"
            onMouseDown={(e) => e.stopPropagation()}
          >
            <div className="ai-dialog-header">
              <h2>🤖 智能金融助手</h2>
              <button className="ai-dialog-close" onClick={closeDialog}>×</button>
            </div>
            <div className="ai-dialog-content">
              {/* 显示气泡中的相同建议内容 */}
              <div className="dialog-message">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  {currentSuggestion.split('\n').map((line, index) => (
                    <React.Fragment key={index}>
                      {line}
                      <br />
                    </React.Fragment>
                  ))}
                </div>
              </div>
              
              {/* 可以在这里添加更多对话记录或其他内容 */}
            </div>
            <div className="ai-dialog-footer">
              <input 
                type="text" 
                className="message-input" 
                placeholder="有什么可以帮助您的？"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    // 这里可以添加发送消息的逻辑
                    console.log('发送消息:', e.target.value);
                    e.target.value = '';
                  }
                }}
              />
              <button className="send-button" onClick={() => {
                const input = document.querySelector('.message-input');
                if (input && input.value.trim()) {
                  // 这里可以添加发送消息的逻辑
                  console.log('发送消息:', input.value);
                  input.value = '';
                }
              }}>发送</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;