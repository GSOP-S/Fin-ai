import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import AIAssistant from './components/AIAssistant';
import AISuggestionBubble from './components/ai/AISuggestionBubble';
import Login from './components/Login';
import FundList from './components/FundList';
import FundDetail from './components/FundDetail';
import HomePage from './components/HomePage';
import TransferPage from './components/TransferPage';
import AssetPage from './components/AssetPage';
import BillDetail from './components/BillDetail';
import NewsPage from './components/NewsPage';
import { generateAIResponse, generateAISuggestion } from './api/ai';
import { submitFeedback } from './api/feedback';
import { showFundSuggestion } from './api/fund';
import request from './api/request';
import { useAI} from './hooks/useAI';
import { BehaviorTracker } from './utils/BehaviorTracker';


function App() {
  // 统一的AI气泡管理 - 所有页面共用
  const ai = useAI();
  
  // ===== 监听行为追踪触发的AI建议（核心逻辑）=====
  useEffect(() => {
    const handleBehaviorAISuggestion = (event) => {
      console.log('[App] 收到行为追踪AI建议:', event.detail);
      
      const { suggestion, command, confidence, fund_id } = event.detail;
      
      // 处理高亮命令
      if (command === 'highlight' && fund_id) {
        console.log('[App] 处理高亮命令, fund_id:', fund_id);
        
        // 解析fund_id（可能是单个或多个，逗号分隔）
        const fundIds = typeof fund_id === 'string' 
          ? fund_id.split(',').map(id => id.trim())
          : Array.isArray(fund_id) ? fund_id : [fund_id];
        
        // 设置高亮基金ID
        setHighlightedFundIds(fundIds);
        
        // 触发滚动事件（让FundList滚动到高亮基金）
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('scroll-to-fund', {
            detail: { fundCodes: fundIds }
          }));
        }, 100);
        
        // 显示弹窗（使用简化版的setAIContent）
        ai.setAIContent({
          suggestion,
          command: 'bubble',
          confidence: confidence
        }, {
          autoShow: true,
          autoHideDelay: 15000,
          speakEnabled: false
        });
        
        // 15秒后清除高亮（与弹窗同步）
        setTimeout(() => {
          setHighlightedFundIds([]);
        }, 15000);
        
      } else {
        // 普通弹窗（无高亮）
        ai.setAIContent({
          suggestion,
          command: 'bubble',
          confidence: confidence
        }, {
          autoShow: true,
          autoHideDelay: 15000,
          speakEnabled: false
        });
      }
    };
    
    // 添加监听器
    window.addEventListener('ai-suggestion-received', handleBehaviorAISuggestion);
    
    // 清理监听器
    return () => {
      window.removeEventListener('ai-suggestion-received', handleBehaviorAISuggestion);
    };
  }, [ai]);
    

  const [selectedFund, setSelectedFund] = useState(null);
  const [userActions, setUserActions] = useState([]);
  const [hasNewSuggestion, setHasNewSuggestion] = useState(false);
  const [showSuggestionBubble, setShowSuggestionBubble] = useState(false);
  const [currentSuggestion, setCurrentSuggestion] = useState('');

  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home'); // 'home', 'account', 'transfer', 'financing', 'deposit', etc.
  const [financingTab, setFinancingTab] = useState('funds'); // 仅保留基金页
  
  // 高亮基金ID列表（用于AI推荐高亮）
  const [highlightedFundIds, setHighlightedFundIds] = useState([]);

  const [currentSuggestionId, setCurrentSuggestionId] = useState('');
  const appRef = useRef(null);
  const suggestionTimeoutRef = useRef(null);
  const chatContainerRef = useRef(null);

  const currentUtteranceRef = useRef(null);

  // ===== 统一的AI建议管理系统 =====
  
 
  


  // 处理用户登录
  const handleLogin = (userData) => {
    console.log('[App] 用户登录:', userData);
    setUser(userData);
    
    // 初始化行为追踪器
    if (userData && userData.id) {
      BehaviorTracker.init(userData.id);
      console.log('[App] 已初始化行为追踪器，用户ID:', userData.id);
      
      // 记录登录事件
      BehaviorTracker.track('LOGIN', {
        user_id: userData.id,
        user_name: userData.displayName,
        timestamp: Date.now()
      }, { realtime: true });
      
      // 记录页面访问事件
      BehaviorTracker.track('PAGE_VIEW', {
        page: 'home',
        page_url: window.location.pathname,
        timestamp: Date.now()
      }, { realtime: true });
    }
  };

  // 处理选择基金
  const handleSelectFund = async (fund) => {
    // 确保基金数据格式一致，处理资产页面传递的fund_name和fund_code字段
    const normalizedFund = {
      ...fund,
      // 如果有fund_name和fund_code字段，则转换为name和code字段
      name: fund.name || fund.fund_name,
      code: fund.code || fund.fund_code
    };
    
    setSelectedFund(normalizedFund);
    
    // 使用fund.js中的showFundSuggestion函数处理基金建议的显示
    showFundSuggestion(normalizedFund, ai);
  };

  

  
  // 语音读出建议功能已迁移至useAI Hook中的toggleSpeech方法
  // 语音输入和消息发送功能已迁移至AIChat组件  
  // 渲染当前内容
  const renderContent = () => {
    // 详情页优先渲染
    // 如果有选中的基金，显示基金详情
    if (selectedFund) {
      return (
        <FundDetail 
          fund={selectedFund}
          onBack={() => {
            setSelectedFund(null);
            handleNavigate('financing');
          }}
        />
      );
    }
  
    // 根据当前页面渲染不同内容
    switch (currentPage) {
      case 'home':
          return <HomePage onNavigate={handleNavigate} user={user} />;
      
      case 'financing':
        // 理财页面显示基金标签
        return (
          <div className="financing-container">
            <div className="financing-tabs">
              <button 
                className={`financing-tab ${financingTab === 'funds' ? 'active' : ''}`}
                onClick={() => setFinancingTab('funds')}
              >
                基金
              </button>
            </div>
            <div className="financing-content">
              <FundList 
                onSelectFund={handleSelectFund}
                highlightedFundIds={highlightedFundIds}
              />
            </div>
          </div>
        );
      
      case 'account':
        return (
          <BillDetail 
            onNavigate={handleNavigate}
          />
        );
      
      case 'transfer':
        return (
          <TransferPage 
            onNavigate={handleNavigate}
          />
        );
      
      case 'assets':
        return (
          <AssetPage 
            onNavigate={handleNavigate}
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
      
      case 'news':
        return <NewsPage onNavigate={handleNavigate} />;
      
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
      'account': '交易记录',
      'transfer': '转账汇款',
      'assets': '我的资产',
      'financing': '投资理财',
      'deposit': '定期存款',
      'creditCard': '信用卡',
      'insurance': '保险服务',
      'loan': '贷款服务',
      'scan': '扫一扫',
      'withdraw': '取款',
      'more': '更多服务',
      'news': '金融资讯'
    };
    return titles[page] || '功能页面';
  };
  
  // 监听AI建议事件
  useEffect(() => {
    const handleAISuggestion = (event) => {
      const { suggestion, command, confidence, fund_id } = event.detail;
      console.log('[App] 收到AI建议:', suggestion, command, confidence);
      
      // 检查command字段，如果为null或undefined则不做任何反应
      if (command === null || command === undefined) {
        console.log('[App] command为null/undefined，不处理AI建议');
        return;
      }
      
      // 处理高亮基金逻辑（如果command为highlight且有fund_id）
      if (command === 'highlight' && fund_id) {
        // 设置高亮基金ID
        setHighlightedFundIds(Array.isArray(fund_id) ? fund_id : [fund_id]);
        
        // 如果是高亮命令，滚动到指定基金
        if (Array.isArray(fund_id) && fund_id.length > 0) {
          setTimeout(() => {
            const scrollEvent = new CustomEvent('scroll-to-fund', {
              detail: { fundId: fund_id[0] }
            });
            window.dispatchEvent(scrollEvent);
          }, 100);
        }
        
        // 15秒后清除高亮
        setTimeout(() => {
          setHighlightedFundIds([]);
        }, 15000);
        
        console.log('[App] 已设置基金高亮:', fund_id);
      }
      
      // 设置AI内容并显示弹窗
      ai.setAIContent({
        suggestion,
        command: command || 'bubble',
        confidence: confidence || 0
      }, {
        autoShow: true,
        autoHideDelay: command === 'highlight' ? 8000 : 5000,
        speakEnabled: false
      });
    };

    // 添加事件监听器
    window.addEventListener('ai-suggestion-received', handleAISuggestion);

    // 清理函数
    return () => {
      window.removeEventListener('ai-suggestion-received', handleAISuggestion);
    };
  }, [ai]);
  
  // 处理页面导航
  const handleNavigate = (page) => {
    // 清除详情页状态
    setSelectedFund(null);
    
    // 设置当前页面
    setCurrentPage(page);
    
    // 记录页面访问事件
    if (user && user.id) {
      BehaviorTracker.track('PAGE_VIEW', {
        page: page,
        page_url: window.location.pathname,
        timestamp: Date.now()
      }, { realtime: true });
    }
    
    // 清除建议气泡 - 使用统一的AI状态管理
    ai.hide();
  };
  
  // 如果用户未登录，显示登录页面
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }
  
  return (
    <div className="app" ref={appRef}>
      {/* 只有在非首页且非详情页时显示顶部导航栏 */}
      {(currentPage !== 'home' && !selectedFund) && (
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
      
      {/* 底部导航栏 */}
      {(currentPage === 'home' || currentPage === 'financing' || currentPage === 'news' || currentPage === 'assets') && !selectedFund && (
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
            <span className="nav-text">交易记录</span>
          </button>
          <button 
            className={`nav-item ${currentPage === 'financing' ? 'active' : ''}`}
            onClick={() => handleNavigate('financing')}
          >
            <span className="nav-icon">💰</span>
            <span className="nav-text">理财</span>
          </button>
          <button 
            className={`nav-item ${currentPage === 'assets' ? 'active' : ''}`}
            onClick={() => handleNavigate('assets')}
          >
            <span className="nav-icon">💼</span>
            <span className="nav-text">资产</span>
          </button>
          <button 
            className={`nav-item ${currentPage === 'news' ? 'active' : ''}`}
            onClick={() => handleNavigate('news')}
          >
            <span className="nav-icon">📰</span>
            <span className="nav-text">资讯</span>
          </button>
        </nav>
      )}
  
      {/* 悬浮AI助手按钮 */}
      <AIAssistant ai={ai} currentPage={currentPage} />

    </div>
  );
}

export default App;