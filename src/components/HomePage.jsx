import React from 'react';
import './HomePage.css';

function HomePage({ onNavigate }) {
  // 模拟用户账户信息
  const accountInfo = {
    balance: '128,563.45',
    accountNumber: '6222 **** **** 5678',
    userName: '张三',
    lastLogin: '2025-10-15 09:30:25'
  };

  // 快捷功能按钮配置
  const quickActions = [
    {
      id: 'account',
      title: '账户明细',
      icon: '📊',
      description: '查看近期交易记录',
      onClick: () => onNavigate('account')
    },
    {
      id: 'transfer',
      title: '转账汇款',
      icon: '💸',
      description: '快速转账到他人账户',
      onClick: () => onNavigate('transfer')
    },
    {
      id: 'financing',
      title: '投资理财',
      icon: '💰',
      description: '基金等金融产品',
      onClick: () => onNavigate('financing')
    },
    {
      id: 'deposit',
      title: '定期存款',
      icon: '🏦',
      description: '稳健理财新选择',
      onClick: () => onNavigate('deposit')
    },
    {
      id: 'creditCard',
      title: '信用卡',
      icon: '💳',
      description: '信用卡账单与还款',
      onClick: () => onNavigate('creditCard')
    },
    {
      id: 'insurance',
      title: '保险服务',
      icon: '🛡️',
      description: '人生保障全面覆盖',
      onClick: () => onNavigate('insurance')
    },
    {
      id: 'loan',
      title: '贷款服务',
      icon: '🏠',
      description: '房贷、车贷等贷款产品',
      onClick: () => onNavigate('loan')
    },
    {
      id: 'more',
      title: '更多服务',
      icon: '⋮⋮',
      description: '其他银行服务',
      onClick: () => onNavigate('more')
    }
  ];

  return (
    <div className="homepage">
      {/* 顶部账户信息卡片 */}
      <div className="account-card">
        <div className="account-header">
          <h2>我的账户</h2>
          <span className="account-number">{accountInfo.accountNumber}</span>
        </div>
        <div className="account-balance">
          ¥ {accountInfo.balance}
        </div>
        <div className="account-actions">
          <button className="action-btn" onClick={() => onNavigate('transfer')}>
            转账
          </button>
          <button className="action-btn" onClick={() => onNavigate('scan')}>
            扫码
          </button>
          <button className="action-btn" onClick={() => onNavigate('withdraw')}>
            取款
          </button>
          <button className="action-btn" onClick={() => onNavigate('deposit')}>
            存款
          </button>
        </div>
      </div>

      {/* 快捷功能区 */}
      <div className="quick-actions">
        <h3>快捷功能</h3>
        <div className="action-grid">
          {quickActions.map((action) => (
            <div 
              key={action.id} 
              className="action-item"
              onClick={action.onClick}
            >
              <div className="action-icon">{action.icon}</div>
              <div className="action-title">{action.title}</div>
              <div className="action-description">{action.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 金融资讯区 */}
      <div className="financial-news">
        <h3>金融资讯</h3>
        <div className="news-list">
          <div className="news-item">
            <span className="news-tag">财经要闻</span>
            <span className="news-title">央行降准0.5个百分点，释放长期资金约1万亿元</span>
          </div>
          <div className="news-item">
            <span className="news-tag">市场动态</span>
            <span className="news-title">A股三大指数集体收涨，科技股表现强势</span>
          </div>
          <div className="news-item">
            <span className="news-tag">银行公告</span>
            <span className="news-title">本行新版手机银行上线，优化用户体验</span>
          </div>
        </div>
      </div>

      {/* 推荐理财产品 */}
      <div className="recommended-products">
        <div className="section-header">
          <h3>推荐理财</h3>
          <button className="view-all-btn" onClick={() => onNavigate('financing')}>
            查看全部
          </button>
        </div>
        <div className="product-cards">
          <div 
            className="product-card" 
            onClick={() => {
              onNavigate('financing');
              // 延迟设置子标签，确保导航完成
              setTimeout(() => window.financingTab = 'funds', 100);
            }}
          >
            <div className="product-icon">📊</div>
            <div className="product-info">
              <h4>基金精选</h4>
            </div>
          </div>
          <div className="product-card" onClick={() => onNavigate('deposit')}>
            <div className="product-icon">🏦</div>
            <div className="product-info">
              <h4>定期存款</h4>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;