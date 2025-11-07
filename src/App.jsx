import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import AIAssistant from './components/AIAssistant';
import AISuggestionBubble from './components/ai/AISuggestionBubble';
import Login from './components/Login';
import FundList from './components/FundList';
import FundDetail from './components/FundDetail';
import HomePage from './components/HomePage';
import TransferPage from './components/TransferPage';
import BillDetail from './components/BillDetail';
import NewsPage from './components/NewsPage';
import { generateAIResponse, generateAISuggestion } from './api/ai';
import { submitFeedback } from './api/feedback';
import { showFundSuggestion } from './api/fund';
import request from './api/request';
import { useAI} from './hooks/useAI';


function App() {
  // 统一的AI气泡管理 - 所有页面共用
  const ai = useAI();
    

  const [selectedFund, setSelectedFund] = useState(null);
  const [userActions, setUserActions] = useState([]);
  const [hasNewSuggestion, setHasNewSuggestion] = useState(false);
  const [showSuggestionBubble, setShowSuggestionBubble] = useState(false);
  const [currentSuggestion, setCurrentSuggestion] = useState('');

  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home'); // 'home', 'account', 'transfer', 'financing', 'deposit', etc.
  const [financingTab, setFinancingTab] = useState('funds'); // 仅保留基金页

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
    
    // 确保用户登录后立即触发首页AI建议
    setTimeout(() => {
      console.log('[App] 登录后触发AI建议');
      triggerPageAISuggestion('home');
    }, 1000);
  };

  // 处理选择基金
  const handleSelectFund = async (fund) => {
    setSelectedFund(fund);
    
    // 使用fund.js中的showFundSuggestion函数处理基金建议的显示
    showFundSuggestion(fund, ai);
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
          />
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
      'account': '账户明细',
      'transfer': '转账汇款',
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
  
  // 处理页面导航
  const handleNavigate = (page) => {
    // 清除详情页状态
    setSelectedFund(null);
    
    // 设置当前页面
    setCurrentPage(page);
    
    // 清除建议气泡 - 使用统一的AI状态管理
    ai.hide();
    
    // 延迟触发新页面的AI建议
    setTimeout(() => {
      triggerPageAISuggestion(page);
    }, 1000);
  };
  
  // 根据页面类型自动触发AI建议
  const triggerPageAISuggestion = async (page) => {
    console.log(`[App] 触发AI建议: page=${page}, user=`, user);
    
    if (!user) {
      console.log('[App] 用户未登录，不触发AI建议');
      return; // 未登录不触发
    }
    
    // 确保AI状态已初始化
    if (!ai || !ai.show) {
      console.log('[App] AI状态未初始化，延迟重试');
      setTimeout(() => {
        triggerPageAISuggestion(page);
      }, 100);
      return;
    }
    
    switch(page) {
      case 'home':
        // 首页显示欢迎和快捷操作建议
        console.log('[App] 触发首页AI建议');
        ai.show('home', { userId: user.id }, {
          autoShow: true,
          autoHideDelay: 8000,
          speakEnabled: false
        });
        break;
        
      case 'financing':
        // 理财页面显示市场分析
        console.log('[App] 触发理财页面AI建议');
        ai.show('market', {}, {
          autoShow: true,
          autoHideDelay: 10000,
          speakEnabled: false
        });
        break;
        
      case 'account':
        // 账单页面由BillDetail组件内部处理
        console.log('[App] 账单页面AI建议由BillDetail组件处理');
        break;
        
      case 'transfer':
        // 转账页面显示常用账户推荐
        console.log('[App] 触发转账页面AI建议');
        ai.show('transfer', { userId: user.id }, {
          autoShow: true,
          autoHideDelay: 8000,
          speakEnabled: false
        });
        break;
        
      default:
        // 其他页面不自动触发
        console.log(`[App] ${page}页面不自动触发AI建议`);
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
      {(currentPage === 'home' || currentPage === 'financing' || currentPage === 'news') && !selectedFund && (
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