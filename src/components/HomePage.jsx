import React from 'react';
import './HomePage.css';

function HomePage({ onNavigate, user }) {
  // 模拟用户账户信息
  const accountInfo = {
    balance: '128,563.45',
    accountNumber: '6222 **** **** 5678',
    userName: user?.displayName || '张三',
    todayIncome: '12.35'
  };

  // 顶部快捷操作（4个）
  const quickActions = [
    {
      id: 'account',
      title: '账户',
      icon: '📊',
      onClick: () => onNavigate('account')
    },
    {
      id: 'transfer',
      title: '转账',
      icon: '💸',
      onClick: () => onNavigate('transfer')
    },
    {
      id: 'financing',
      title: '理财',
      icon: '💰',
      onClick: () => onNavigate('financing')
    },
    {
      id: 'more',
      title: '更多服务',
      icon: '⋮⋮',
      onClick: () => onNavigate('more')
    }
  ];

  // 热门资讯预览（3条）
  const hotNews = [
    {
      id: 1,
      category: '财经要闻',
      title: '央行降准0.5个百分点，释放长期资金约1万亿元',
      time: '2小时前'
    },
    {
      id: 2,
      category: '市场动态',
      title: 'A股三大指数集体收涨，科技股表现强势',
      time: '4小时前'
    },
    {
      id: 3,
      category: '政策解读',
      title: '新版金融监管政策出台，助力实体经济发展',
      time: '6小时前'
    }
  ];

  return (
    <div className="homepage">
      {/* 顶部蓝色渐变区域 */}
      <div className="homepage-header">
        <div className="user-greeting">
          <div className="greeting-text">
            <span className="greeting-time">下午好</span>
            <span className="user-name">{accountInfo.userName}</span>
          </div>
          <div className="header-icons">
            <span className="icon-btn">🔍</span>
            <span className="icon-btn">🔔</span>
          </div>
        </div>

        {/* 快捷操作图标区 */}
        <div className="quick-icons">
          {quickActions.map((action) => (
            <div 
              key={action.id} 
              className="quick-icon-item"
              onClick={action.onClick}
            >
              <div className="quick-icon">{action.icon}</div>
              <div className="quick-title">{action.title}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 账户余额卡片 */}
      <div className="balance-card">
        <div className="balance-header">
          <span className="balance-label">总资产</span>
          <span className="balance-eye">👁</span>
        </div>
        <div className="balance-amount">¥{accountInfo.balance}</div>
        <div className="balance-detail">
          <span className="detail-item">累计收益 0.00</span>
          <span className="detail-item">昨日收益 {accountInfo.todayIncome}</span>
        </div>
      </div>

      {/* 推荐理财产品 */}
      <div className="recommended-products">
        <div className="section-header">
          <h3>推荐理财</h3>
          <button className="view-all-btn" onClick={() => onNavigate('financing')}>
            查看全部 →
          </button>
        </div>
        <div className="product-list">
          <div 
            className="product-card" 
            onClick={() => {
              onNavigate('financing');
              setTimeout(() => window.financingTab = 'funds', 100);
            }}
          >
            <div className="product-header">
              <span className="product-icon">📊</span>
              <span className="product-name">基金精选</span>
            </div>
            <div className="product-rate">4.85%</div>
            <div className="product-desc">近七日年化</div>
          </div>
          <div className="product-card" onClick={() => onNavigate('deposit')}>
            <div className="product-header">
              <span className="product-icon">🏦</span>
              <span className="product-name">定期存款</span>
            </div>
            <div className="product-rate">3.25%</div>
            <div className="product-desc">年化收益</div>
          </div>
        </div>
      </div>

      {/* 热门资讯预览 */}
      <div className="news-preview">
        <div className="section-header">
          <h3>热门资讯</h3>
          <button className="view-all-btn" onClick={() => onNavigate('news')}>
            更多 →
          </button>
        </div>
        <div className="news-list">
          {hotNews.map((news) => (
            <div 
              key={news.id} 
              className="news-item"
              onClick={() => onNavigate('news')}
            >
              <div className="news-content">
                <span className="news-tag">{news.category}</span>
                <span className="news-title">{news.title}</span>
              </div>
              <span className="news-time">{news.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default HomePage;