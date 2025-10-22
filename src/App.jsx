import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import AIAssistant from './components/AIAssistant';
import StockList from './components/StockList';
import Login from './components/Login';
import FundList from './components/FundList';

function App() {
  const [selectedStock, setSelectedStock] = useState(null);
  const [selectedFund, setSelectedFund] = useState(null);
  const [userActions, setUserActions] = useState([]);
  const [showSuggestionBubble, setShowSuggestionBubble] = useState(false);
  const [currentSuggestion, setCurrentSuggestion] = useState('');
  const [hasNewSuggestion, setHasNewSuggestion] = useState(false);
  const [hoveredStock, setHoveredStock] = useState(null);
  const [showAIChat, setShowAIChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('stocks'); // 'stocks' 或 'funds'
  const [marketAnalysisShown, setMarketAnalysisShown] = useState(false);
  const [currentSuggestionId, setCurrentSuggestionId] = useState('');
  const appRef = useRef(null);
  const suggestionTimeoutRef = useRef(null);
  const chatContainerRef = useRef(null);
  const marketAnalysisTimeoutRef = useRef(null);
  const currentUtteranceRef = useRef(null);

  // 生成市场分析和股票推荐 - 调用后端API
  const generateMarketAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/market-analysis');
      const data = await response.json();
      if (data.success) {
        return data.data.analysis;
      } else {
        console.error('获取市场分析失败:', data.error);
        // 生成备用分析（模拟数据，实际应用中可替换为大模型API调用）
        return '市场分析：今日市场整体平稳。建议关注新能源、半导体等热门板块。';
      }
    } catch (error) {
      console.error('市场分析API调用失败:', error);
      // 生成备用分析（模拟数据，实际应用中可替换为大模型API调用）
      return '市场分析：今日市场整体平稳。建议关注新能源、半导体等热门板块。';
    }
  };

  // 生成股票建议 - 调用后端API
  const generateStockSuggestion = async (stock) => {
    if (!stock) return '';
    
    try {
      const response = await fetch('http://localhost:5000/api/stock-suggestion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ stock })
      });
      const data = await response.json();
      if (data.success) {
        return data.data.suggestion;
      } else {
        console.error('获取股票建议失败:', data.error);
        // 备用逻辑（可替换为大模型API调用）
        return stock.change >= 0 ? 
          `${stock.name} 表现良好，可考虑关注。` : 
          `${stock.name} 有所调整，建议观望。`;
      }
    } catch (error) {
      console.error('股票建议API调用失败:', error);
      // 备用逻辑（可替换为大模型API调用）
      return stock.change >= 0 ? 
        `${stock.name} 表现良好，可考虑关注。` : 
        `${stock.name} 有所调整，建议观望。`;
    }
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
    
    // 生成并显示建议
    const suggestion = await generateStockSuggestion(stock);
    setCurrentSuggestion(suggestion);
    setHasNewSuggestion(true);
    setCurrentSuggestionId(`stock-${stock.code}-${Date.now()}`);
    
    // 语音读出建议
    speakSuggestion(suggestion);
    
    // 清除之前的定时器
    if (suggestionTimeoutRef.current) {
      clearTimeout(suggestionTimeoutRef.current);
    }
    
    // 3秒后自动显示气泡建议
    suggestionTimeoutRef.current = setTimeout(() => {
      setShowSuggestionBubble(true);
      // 10秒后自动隐藏气泡
      setTimeout(() => {
        setShowSuggestionBubble(false);
        setHasNewSuggestion(false);
      }, 10000);
    }, 1000);
    
    // 调用AI助手接口进行更深入分析（保留大模型接入部分）
    callAIAssistant(`分析股票 ${stock.name} (${stock.code})`, { stockData: stock });
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
    
    // 调用后端API生成基金建议
    try {
      const response = await fetch('http://localhost:5000/api/fund-suggestion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ fund })
      });
      const data = await response.json();
      
      let suggestion;
      if (data.success) {
        suggestion = data.data.suggestion;
      } else {
        console.error('获取基金建议失败:', data.error);
        // 备用逻辑（可替换为大模型API调用）
        suggestion = `基金建议：${fund.name} 可作为您投资组合的一个选择。`;
      }
      
      setCurrentSuggestion(suggestion);
      setShowSuggestionBubble(true);
      setHasNewSuggestion(false);
      setCurrentSuggestionId(`fund-${fund.code}-${Date.now()}`);
      
      // 10秒后自动隐藏气泡
      setTimeout(() => {
        setShowSuggestionBubble(false);
      }, 10000);
    } catch (error) {
      console.error('基金建议API调用失败:', error);
      // 备用建议
      const suggestion = `基金建议：${fund.name} 可作为您投资组合的一个选择。`;
      setCurrentSuggestion(suggestion);
      setShowSuggestionBubble(true);
      setHasNewSuggestion(false);
      setCurrentSuggestionId(`fund-${fund.code}-${Date.now()}`);
      
      // 10秒后自动隐藏气泡
      setTimeout(() => {
        setShowSuggestionBubble(false);
      }, 10000);
    }
  };

  // 处理用户反馈
  const handleFeedback = async (type, comment = '') => {
    if (!currentSuggestionId || !currentSuggestion) return;
    
    try {
      const response = await fetch('http://localhost:5000/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          suggestionId: currentSuggestionId,
          content: currentSuggestion,
          type,
          comment
        })
      });
      
      const data = await response.json();
      if (data.success) {
        console.log('反馈提交成功');
        // 显示感谢信息
        alert('感谢您的反馈！');
        // 关闭建议气泡
        setShowSuggestionBubble(false);
      } else {
        console.error('反馈提交失败:', data.error);
      }
    } catch (error) {
      console.error('反馈API调用失败:', error);
    }
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
    // 这里是接入大模型的接口
    try {
      // 实际应用中会调用真实的大模型API或后端接口
      const response = await fetch('http://localhost:5000/api/ai-assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt, context })
      });
      
      if (!response.ok) {
        throw new Error('网络响应错误');
      }
      
      return await response.json();
    } catch (error) {
      console.error('调用AI助手失败:', error);
      // 模拟AI处理过程作为备用
      return {
        success: true,
        data: {
          response: `AI分析调用失败，请稍后再试。`,
          context: context
        }
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
    // 如果有选中的股票，显示股票详情
    if (selectedStock) {
      return (
        <div className="stock-detail">
          <button className="back-btn" onClick={() => setSelectedStock(null)}>返回</button>
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
          <button className="back-btn" onClick={() => setSelectedFund(null)}>返回</button>
          <h2>{selectedFund.name} ({selectedFund.code})</h2>
          <div className="fund-nav">净值：{selectedFund.nav.toFixed(4)}元</div>
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

    // 根据当前选中的标签显示对应内容
    if (activeTab === 'stocks') {
      return (
        <StockList 
          onSelectStock={handleStockSelect}
          onStockHover={handleStockHover}
          onStockLeave={handleStockLeave}
        />
      );
    } else {
      return (
        <FundList 
          onSelectFund={handleSelectFund}
        />
      );
    }
  };

  // 显示市场分析气泡 - 在用户登录或切换到列表页面时触发
  useEffect(() => {
    // 只有在用户已登录且在列表页面时才显示
    const fetchMarketAnalysis = async () => {
      if (user && !selectedStock && !selectedFund && !marketAnalysisShown) {
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
  }, [user, selectedStock, selectedFund]);
  
  // 当返回列表页面时重置marketAnalysisShown状态，以便再次显示市场分析
  useEffect(() => {
    // 当离开详情页返回到列表页时，重置marketAnalysisShown状态
    if (!selectedStock && !selectedFund) {
      setMarketAnalysisShown(false);
    }
  }, [selectedStock, selectedFund]);

  // 如果用户未登录，显示登录页面
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app" ref={appRef}>
      <header className="app-header">
        <div className="header-content">
          <h1>金融理财APP</h1>
          <div className="user-info">
            <span className="welcome-text">欢迎，{user.displayName}</span>
          </div>
        </div>
        
        {/* 导航标签 */}
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'stocks' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('stocks');
              // 如果在详情页，切换标签时需要清除选中状态
              setSelectedStock(null);
              setSelectedFund(null);
            }}
          >
            股票
          </button>
          <button 
            className={`nav-tab ${activeTab === 'funds' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('funds');
              // 如果在详情页，切换标签时需要清除选中状态
              setSelectedStock(null);
              setSelectedFund(null);
            }}
          >
            基金
          </button>
        </div>
      </header>
      
      <main className="app-content">
        {renderContent()}
      </main>

      {/* 悬浮AI助手按钮 */}
      <AIAssistant 
        isVisible={true}
        onClick={() => {
          // 如果有显示的建议气泡，将其内容添加到聊天记录中
          if (showSuggestionBubble && currentSuggestion) {
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
          setShowAIChat(!showAIChat);
          
          // 滚动聊天窗口到底部
          setTimeout(() => {
            if (chatContainerRef.current) {
              chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
            }
          }, 100);
        }}
        onHover={handleAIAssistantHover}
        onLeave={handleAIAssistantLeave}
        hasNewSuggestion={hasNewSuggestion}
      />

      {/* AI侧边气泡建议 */}
      {showSuggestionBubble && currentSuggestion && (
        <div className={`ai-suggestion-bubble ${marketAnalysisShown ? 'market-analysis' : ''}`}>
          <div className="ai-suggestion-header">
            <span className="ai-suggestion-title">
              {marketAnalysisShown ? '📊 今日市场分析' : '💡 智能建议'}
            </span>
            <button 
              className="close-bubble-btn"
              onClick={(e) => {
                e.stopPropagation();
                // 停止语音播放
                if ('speechSynthesis' in window && speechSynthesis.speaking) {
                  speechSynthesis.cancel();
                }
                setShowSuggestionBubble(false);
                setMarketAnalysisShown(false);
              }}
              style={{ zIndex: 1002 }}
            >
              ×
            </button>
          </div>
          <div className="ai-suggestion-content">
            {currentSuggestion.split('\n').map((line, index) => (
              <p key={index} className="suggestion-line">{line}</p>
            ))}
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
              className="speak-btn"
              onClick={(e) => {
                e.stopPropagation();
                speakSuggestion(currentSuggestion);
              }}
            >
              🔊
            </button>
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
                你好！我是股票智能助手，请问有什么可以帮助你的？
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