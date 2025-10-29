import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import AIAssistant from './components/AIAssistant';
import StockList from './components/StockList';
import Login from './components/Login';
import FundList from './components/FundList';
import HomePage from './components/HomePage';
import TransferPage from './components/TransferPage';
import BillDetail from './components/BillDetail';
import { generateAIResponse, generateAISuggestion } from './api/ai';
import { submitFeedback } from './api/feedback';
import request from './api/request';
import { useAI} from './hooks/useAI';
  // 生成市场分析和股票推荐 - 调用后端API
import { generateMarketAnalysis } from './api/stock';

function App() {
  // 统一的AI气泡管理 - 所有页面共用
  const ai = useAI();
  
  const [selectedStock, setSelectedStock] = useState(null);
  const [selectedFund, setSelectedFund] = useState(null);
  const [userActions, setUserActions] = useState([]);
  const [hasNewSuggestion, setHasNewSuggestion] = useState(false);
  const [hoveredStock, setHoveredStock] = useState(null);
  const [showAIChat, setShowAIChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home'); // 'home', 'account', 'transfer', 'financing', 'deposit', etc.
  const [financingTab, setFinancingTab] = useState('stocks'); // 'stocks' 或 'funds'
  const [marketAnalysisShown, setMarketAnalysisShown] = useState(false);
  const [currentSuggestionId, setCurrentSuggestionId] = useState('');
  const appRef = useRef(null);
  const suggestionTimeoutRef = useRef(null);
  const chatContainerRef = useRef(null);
  const marketAnalysisTimeoutRef = useRef(null);
  const currentUtteranceRef = useRef(null);

  // ===== 统一的AI建议管理系统 =====

  // ===== showAISuggestion 函数已迁移到 useAI Hook =====
  // BillDetail 和 TransferPage 现在直接使用 useAI Hook
  // 其他页面（股票、基金）仍使用旧的建议系统
  
  // 生成股票建议 - 调用后端API（保留兼容性）
  const generateStockSuggestion = async (stock) => {
    if (!stock) return '';
    const result = await generateAISuggestion('stock', { stock });
    return result?.suggestion || `${stock.name} 建议谨慎操作，注意风险控制。`;
  };

  // 处理用户点击股票的操作
  const handleStockSelect = async (stock) => {
    setSelectedStock(stock);
    const action = {
      type: 'stock_select',
      content: `查看股票: ${stock.name} (${stock.code})`,
      timestamp: new Date().toISOString(),
      stock: stock
    };
    setUserActions(prev => [...prev, action]);
    
    // 使用统一的AI气泡显示
    ai.show('stock', { stock }, {
      autoShow: true,
      autoHideDelay: 10000, // 10秒后自动隐藏
      speakEnabled: true
    });
    
    // 调用AI助手接口进行更深入分析（保留大模型接入部分）
    generateAIResponse(`分析股票 ${stock.name} (${stock.code})`, { stockData: stock });
  };

  // 处理买入/卖出操作
  const handleTradeAction = (stock, action) => {
    const actionText = `${action === 'buy' ? '买入' : '卖出'}股票: ${stock.name} (${stock.code})`;
    const newAction = {
      type: 'trade',
      content: actionText,
      timestamp: new Date().toISOString(),
      stock: stock,
      tradeType: action
    };
    setUserActions(prev => [...prev, newAction]);
    
    // 生成交易建议
    const tradeSuggestion = action === 'buy' 
      ? `买入建议：${stock.name} (${stock.code}) 当前价格 ${stock.price} 元，建议设置止盈止损，控制仓位在总资产的5-10%为宜。`
      : `卖出建议：${stock.name} (${stock.code}) 当前价格 ${stock.price} 元，建议确认卖出理由，避免情绪化交易。`;
    
    setCurrentSuggestion(tradeSuggestion);
    setShowSuggestionBubble(true);
    setHasNewSuggestion(false);
    
    // 10秒后自动隐藏气泡
    setTimeout(() => {
      setShowSuggestionBubble(false);
    }, 10000);
  };

  // 处理鼠标悬停在AI助手图标上
  const handleAIAssistantHover = () => {
    if (currentSuggestion) {
      setShowSuggestionBubble(true);
      setHasNewSuggestion(false);
    }
  };

  // 处理鼠标离开AI助手图标
  const handleAIAssistantLeave = () => {
    // 延迟隐藏，让用户有时间阅读
    setTimeout(() => {
      // 只有当不是市场分析气泡时才隐藏
      if (!marketAnalysisShown) {
        setShowSuggestionBubble(false);
      }
    }, 2000);
  };

  // 处理用户登录
  const handleLogin = (userData) => {
    setUser(userData);
  };

  // 处理选择基金
  const handleSelectFund = async (fund) => {
    setSelectedFund(fund);
    
    // 使用统一的AI气泡显示
    ai.show('fund', { fund }, {
      autoShow: true,
      autoHideDelay: 20000, // 20秒后自动隐藏
      speakEnabled: false
    });
  };
  
  // 处理鼠标悬停在股票上
  const handleStockHover = (stock) => {
    setHoveredStock(stock);
  };
  
  // 处理鼠标离开股票
  const handleStockLeave = () => {
    setHoveredStock(null);
  };
  
  // 调用AI助手接口（用于外部调用）
  const callAIAssistant = async (prompt, context = {}) => {
    try {
      const result = await generateAIResponse(prompt, context);
      return result;
    } catch (error) {
      console.error('调用AI助手失败:', error);
      return {
        success: true,
        data: {
          response: `AI分析调用失败，请稍后再试。`,
          context: context,
        },
      };
    }
  };
  
  // 语音读出建议功能
  const speakSuggestion = (text) => {
    if ('speechSynthesis' in window) {
      // 如果有正在播放的语音，先停止
      if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
        return; // 点击按钮时停止播放，不再继续
      }
      
      // 创建新的语音实例
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      utterance.rate = 0.9;
      currentUtteranceRef.current = utterance;
      speechSynthesis.speak(utterance);
    }
  };
  
  // 处理语音输入
  const handleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.lang = 'zh-CN';
      recognition.interimResults = false;
      
      recognition.onstart = () => {
        console.log('语音识别已启动');
      };
      
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
  
  // 发送消息到AI聊天
  //TODO: 使用API调用，而不是直接调用callAIAssistant
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
      const result = await callAIAssistant(userInput.trim(), {
        conversationHistory: chatMessages,
        selectedStock: selectedStock
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
    setTimeout(() => {
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
      }
    }, 100);
  };
  
  // 渲染当前内容
  const renderContent = () => {
    // 详情页优先渲染
    // 如果有选中的股票，显示股票详情
    if (selectedStock) {
      return (
        <div className="stock-detail">
          <button className="back-btn" onClick={() => {
            setSelectedStock(null);
            handleNavigate('financing');
          }}>返回</button>
          <h2>{selectedStock.name} ({selectedStock.code})</h2>
          <div className="stock-price">{selectedStock.price}元</div>
          <div className="stock-change">{selectedStock.change} ({selectedStock.changePercent})</div>
          <div className="stock-industry">行业：{selectedStock.industry}</div>
          <div className="trade-buttons">
            <button className="buy-btn" onClick={() => handleTradeAction(selectedStock, 'buy')}>买入</button>
            <button className="sell-btn" onClick={() => handleTradeAction(selectedStock, 'sell')}>卖出</button>
          </div>
        </div>
      );
    }
  
    // 如果有选中的基金，显示基金详情
    if (selectedFund) {
      return (
        <div className="fund-detail">
          <button className="back-btn" onClick={() => {
            setSelectedFund(null);
            handleNavigate('financing');
          }}>返回</button>
          <h2>{selectedFund.name} ({selectedFund.code})</h2>
          <div className="fund-nav">净值：{Number(selectedFund.nav)?.toFixed(4) || '0.0000'}元</div>
          <div className={`fund-change ${selectedFund.change.startsWith('+') ? 'positive' : 'negative'}`}>
            {selectedFund.change} ({selectedFund.changePercent})
          </div>
          <div className="fund-info">
            <div>基金经理：{selectedFund.manager}</div>
            <div>基金类型：{selectedFund.category}</div>
            <div>风险等级：{selectedFund.risk}</div>
          </div>
        </div>
      );
    }
  
    // 根据当前页面渲染不同内容
    switch (currentPage) {
      case 'home':
        return <HomePage onNavigate={handleNavigate} />;
      
      case 'financing':
        // 理财页面显示股票和基金标签
        return (
          <div className="financing-container">
            <div className="financing-tabs">
              <button 
                className={`financing-tab ${financingTab === 'stocks' ? 'active' : ''}`}
                onClick={() => setFinancingTab('stocks')}
              >
                股票
              </button>
              <button 
                className={`financing-tab ${financingTab === 'funds' ? 'active' : ''}`}
                onClick={() => setFinancingTab('funds')}
              >
                基金
              </button>
            </div>
            <div className="financing-content">
              {financingTab === 'stocks' ? (
                <StockList 
                  onSelectStock={handleStockSelect}
                  onStockHover={handleStockHover}
                  onStockLeave={handleStockLeave}
                />
              ) : (
                <FundList 
                  onSelectFund={handleSelectFund}
                />
              )}
            </div>
          </div>
        );
      
      case 'account':
        return (
          <BillDetail 
            onNavigate={handleNavigate}
            onShowAI={ai.show}
          />
        );
      
      case 'transfer':
        return (
          <TransferPage 
            onNavigate={handleNavigate}
            onShowAI={ai.show}
          />
        );
      
      case 'deposit':
        return (
          <div className="page-container">
            <button className="back-btn" onClick={() => handleNavigate('home')}>返回首页</button>
            <h1>定期存款</h1>
            <p>此处将显示定期存款产品...</p>
          </div>
        );
      
      default:
        // 其他页面暂时返回提示信息
        return (
          <div className="page-container">
            <button className="back-btn" onClick={() => handleNavigate('home')}>返回首页</button>
            <h1>{getPageTitle(currentPage)}</h1>
            <p>功能正在开发中，敬请期待...</p>
          </div>
        );
    }
  };
  
  // 获取页面标题
  const getPageTitle = (page) => {
    const titles = {
      'home': '首页',
      'account': '账户明细',
      'transfer': '转账汇款',
      'financing': '投资理财',
      'deposit': '定期存款',
      'creditCard': '信用卡',
      'insurance': '保险服务',
      'loan': '贷款服务',
      'scan': '扫一扫',
      'withdraw': '取款',
      'more': '更多服务'
    };
    return titles[page] || '功能页面';
  };
  
  // 监听financingTab的变化，确保从HomePage点击推荐产品时能正确设置标签
  useEffect(() => {
    const checkTabChange = () => {
      if (window.financingTab) {
        setFinancingTab(window.financingTab);
        // 清除全局变量
        delete window.financingTab;
      }
    };
    
    // 立即检查一次
    checkTabChange();
    
    // 添加窗口事件监听器（可选）
    window.addEventListener('tabchange', checkTabChange);
    
    return () => {
      window.removeEventListener('tabchange', checkTabChange);
    };
  }, []);
  
  // 显示市场分析气泡 - 在用户登录或切换到列表页面时触发
  useEffect(() => {
    // 只有在用户已登录且在理财页面（股票或基金列表）时才显示
    const fetchMarketAnalysis = async () => {
      if (user && currentPage === 'financing' && !selectedStock && !selectedFund && !marketAnalysisShown) {
        try {
          const analysis = await generateMarketAnalysis();
          setCurrentSuggestion(analysis);
          setShowSuggestionBubble(true);
          setMarketAnalysisShown(true);
          setCurrentSuggestionId(`market-${Date.now()}`);
          
          // 语音读出分析内容
          speakSuggestion(analysis);
          
          // 30秒后自动隐藏气泡
          marketAnalysisTimeoutRef.current = setTimeout(() => {
            setShowSuggestionBubble(false);
            setMarketAnalysisShown(false);
          }, 30000);
        } catch (error) {
          console.error('获取市场分析失败:', error);
        }
      }
    };
    
    fetchMarketAnalysis();
  
    return () => {
      if (marketAnalysisTimeoutRef.current) {
        clearTimeout(marketAnalysisTimeoutRef.current);
      }
    };
  }, [user, currentPage, selectedStock, selectedFund]);
  
  // 当返回理财列表页面时重置marketAnalysisShown状态
  useEffect(() => {
    // 当离开详情页返回到列表页时，重置marketAnalysisShown状态
    if (currentPage === 'financing' && !selectedStock && !selectedFund) {
      setMarketAnalysisShown(false);
    }
  }, [currentPage, selectedStock, selectedFund]);
  
  // 处理页面导航
  const handleNavigate = (page) => {
    // 清除详情页状态
    setSelectedStock(null);
    setSelectedFund(null);
    
    // 设置当前页面
    setCurrentPage(page);
    
    // 清除建议气泡
    setShowSuggestionBubble(false);
    setMarketAnalysisShown(false);
    
    // 延迟触发新页面的AI建议
    setTimeout(() => {
      triggerPageAISuggestion(page);
    }, 1000);
  };
  
  // 根据页面类型自动触发AI建议
  const triggerPageAISuggestion = async (page) => {
    if (!user) return; // 未登录不触发
    
    switch(page) {
      case 'home':
        // 首页显示欢迎和快捷操作建议
        showAISuggestion('home', {}, {
          autoShow: true,
          autoHideDelay: 15000,
          speakEnabled: false
        });
        break;
        
      case 'financing':
        // 理财页面显示市场分析（已有逻辑，由useEffect处理）
        break;
        
      case 'account':
        // 账单页面由BillDetail组件内部处理
        break;
        
      case 'transfer':
        // 转账页面显示常用账户推荐
        showAISuggestion('transfer', {
          recentAccounts: [
            {id: 1, name: '张三', accountNumber: '****1234'},
            {id: 2, name: '李四', accountNumber: '****5678'},
            {id: 3, name: '王五', accountNumber: '****9012'}
          ],
          suggestion: '您可以快速选择常用账户进行转账'
        }, {
          autoShow: true,
          autoHideDelay: 20000,
          speakEnabled: false
        });
        break;
        
      default:
        // 其他页面不自动触发
        break;
    }
  };
  
  // 如果用户未登录，显示登录页面
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }
  
  return (
    <div className="app" ref={appRef}>
      {/* 只有在非首页且非详情页时显示顶部导航栏 */}
      {(currentPage !== 'home' && !selectedStock && !selectedFund) && (
        <header className="app-header">
          <div className="header-content">
            <h1>{getPageTitle(currentPage)}</h1>
            <div className="user-info">
              <span className="welcome-text">欢迎，{user.displayName}</span>
            </div>
          </div>
        </header>
      )}
      
      <main className="app-content">
        {renderContent()}
      </main>
      
      {/* 底部导航栏，仅在首页和理财页显示 */}
      {(currentPage === 'home' || currentPage === 'financing') && !selectedStock && !selectedFund && (
        <nav className="bottom-nav">
          <button 
            className={`nav-item ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => handleNavigate('home')}
          >
            <span className="nav-icon">🏠</span>
            <span className="nav-text">首页</span>
          </button>
          <button 
            className={`nav-item ${currentPage === 'account' ? 'active' : ''}`}
            onClick={() => handleNavigate('account')}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-text">账户</span>
          </button>
          <button 
            className={`nav-item ${currentPage === 'financing' ? 'active' : ''}`}
            onClick={() => handleNavigate('financing')}
          >
            <span className="nav-icon">💰</span>
            <span className="nav-text">理财</span>
          </button>
          <button 
            className={`nav-item ${currentPage === 'more' ? 'active' : ''}`}
            onClick={() => handleNavigate('more')}
          >
            <span className="nav-icon">⋮⋮</span>
            <span className="nav-text">更多</span>
          </button>
        </nav>
      )}
  
      {/* 悬浮AI助手按钮 */}
      <AIAssistant 
        isVisible={true}
        onClick={() => {
          // 判断是打开还是关闭对话框
          const willOpenChat = !showAIChat;
          
          // 如果要打开对话框，且有显示的建议气泡，将其内容添加到聊天记录中
          if (willOpenChat && showSuggestionBubble && currentSuggestion) {
            // 创建AI消息
            const aiMessage = {
              type: 'ai',
              content: currentSuggestion,
              timestamp: new Date().toISOString()
            };
            setChatMessages(prev => [...prev, aiMessage]);
            
            // 停止语音播放
            if ('speechSynthesis' in window && speechSynthesis.speaking) {
              speechSynthesis.cancel();
            }
            
            // 隐藏建议气泡
            setShowSuggestionBubble(false);
            setMarketAnalysisShown(false);
          }
          
          // 切换AI聊天窗口显示状态
          setShowAIChat(willOpenChat);
          
          // 如果打开对话框，滚动到底部
          if (willOpenChat) {
            setTimeout(() => {
              if (chatContainerRef.current) {
                chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
              }
            }, 100);
          }
        }}
        onHover={handleAIAssistantHover}
        onLeave={handleAIAssistantLeave}
        hasNewSuggestion={hasNewSuggestion}
      />
  
      {/* AI侧边气泡建议 - 统一使用useAI Hook管理 */}
      {ai.isVisible && ai.suggestionText && !showAIChat && (
        <div className={`ai-suggestion-bubble ${marketAnalysisShown ? 'market-analysis' : ''}`}>
          <div className="ai-suggestion-header">
            <span className="ai-suggestion-title">
              {marketAnalysisShown ? '📊 今日市场分析' : '💡 智能建议'}
            </span>
            <button 
              className="close-bubble-btn"
              onClick={(e) => {
                e.stopPropagation();
                ai.hide();
                setMarketAnalysisShown(false);
              }}
              style={{ zIndex: 1002 }}
            >
              ×
            </button>
          </div>
          <div className="ai-suggestion-content">
            {ai.suggestionText.split('\n').map((line, index) => (
              <p key={index} className="suggestion-line">{line}</p>
            ))}
            <div className="bubble-actions">
              <div className="feedback-buttons">
                <button 
                  className="feedback-btn like-btn" 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleFeedback('like');
                  }}
                  aria-label="有用"
                >
                  👍 有用
                </button>
                <button 
                  className="feedback-btn dislike-btn" 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleFeedback('dislike');
                  }}
                  aria-label="没用"
                >
                  👎 没用
                </button>
              </div>
              <button 
                className="open-chat-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  // 将气泡内容添加到聊天记录
                  const aiMessage = {
                    type: 'ai',
                    content: ai.suggestionText,
                    timestamp: new Date().toISOString()
                  };
                  setChatMessages(prev => [...prev, aiMessage]);
                  
                  // 停止语音播放
                  ai.stopSpeaking();
                  
                  // 隐藏气泡并打开对话框
                  ai.hide();
                  setMarketAnalysisShown(false);
                  setShowAIChat(true);
                  
                  // 滚动到底部
                  setTimeout(() => {
                    if (chatContainerRef.current) {
                      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
                    }
                  }, 100);
                }}
                title="打开详细对话"
              >
                💬 详细对话
              </button>
              <button 
                className="speak-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  ai.speak(ai.suggestionText);
                }}
                title="语音播报"
              >
                🔊
              </button>
            </div>
          </div>
        </div>
      )}
  
      {/* AI聊天窗口 */}
      {showAIChat && (
        <div className="ai-chat-container">
          <div className="ai-chat-header">
            <h3>AI助手</h3>
            <button className="close-btn" onClick={() => setShowAIChat(false)}>×</button>
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
      )}
    </div>
  );
}

export default App;