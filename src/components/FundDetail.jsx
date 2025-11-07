import React, { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './FundDetail.css';
import { usePageTracking } from '../hooks/usePageTracking';
import { useBehaviorTracker } from '../hooks/useBehaviorTracker';
import { EventTypes } from '../config/tracking.config';

const FundDetail = ({ fund, onBack }) => {
  // ===== 行为追踪 =====
  const tracker = useBehaviorTracker();
  usePageTracking('fund_detail', { fund_code: fund.code });
  
  // ===== 状态管理 =====
  const [selectedPeriod, setSelectedPeriod] = useState('daily'); // daily, weekly, monthly, history
  
  // ===== Mock数据生成 =====
  
  // 生成历史净值数据（符合真实涨跌幅和成立以来收益）
  const generateNavHistory = () => {
    const data = [];
    
    // 当前基金数据
    const currentNav = parseFloat(fund.nav) || 2.8745;
    const dailyChangePercent = parseFloat(fund.changePercent?.replace('%', '').replace('+', '')) || 2.13;
    
    // 成立以来+300%，意味着初始净值 = currentNav / (1 + 3.00) ≈ 0.72
    const initialNav = currentNav / 4.0; // +300% = 4倍
    const totalDays = 1200; // 假设成立约3.3年
    
    // 计算平均每日增长率（复利）
    const avgDailyGrowth = Math.pow(currentNav / initialNav, 1 / totalDays) - 1;
    
    // 生成历史数据
    for (let i = totalDays; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      // 基础增长趋势
      const trendNav = initialNav * Math.pow(1 + avgDailyGrowth, totalDays - i);
      
      // 添加随机波动（±2%）
      const volatility = 0.02;
      const randomFactor = 1 + (Math.random() - 0.5) * volatility;
      
      // 最终净值
      let nav = trendNav * randomFactor;
      
      // 确保最后一天的净值等于当前净值
      if (i === 0) {
        nav = currentNav;
      }
      
      data.push({
        date: date.toISOString().slice(0, 10),
        nav: parseFloat(nav.toFixed(4)),
        displayDate: `${date.getMonth() + 1}/${date.getDate()}`
      });
    }
    
    return data;
  };
  
  const navHistory = useMemo(() => generateNavHistory(), [fund.code, fund.nav, fund.changePercent]);
  
  // 根据周期过滤数据
  const filteredData = useMemo(() => {
    switch(selectedPeriod) {
      case 'daily':
        return navHistory.slice(-30); // 近30天
      case 'weekly':
        return navHistory.filter((_, index) => index % 7 === 0).slice(-30); // 周K
      case 'monthly':
        return navHistory.filter((_, index) => index % 30 === 0).slice(-12); // 月K
      case 'history':
        return navHistory; // 全部历史
      default:
        return navHistory.slice(-30);
    }
  }, [navHistory, selectedPeriod]);
  
  // 计算昨日净值（确保数学关系正确）
  const calculateYesterdayNav = () => {
    const currentNav = parseFloat(fund.nav) || 2.8745;
    const dailyChange = parseFloat(fund.change?.replace('+', '')) || 0.0598;
    return (currentNav - dailyChange).toFixed(4);
  };
  
  const yesterdayNav = calculateYesterdayNav();
  
  // 自动计算历史业绩（基于生成的历史数据）
  const calculatePerformance = () => {
    if (navHistory.length < 30) {
      return {
        '近1月': fund.changePercent || '+3.21%',
        '近3月': '+8.45%',
        '近6月': '+15.32%',
        '成立来': '+300.00%'
      };
    }
    
    const currentNav = navHistory[navHistory.length - 1].nav;
    
    // 近1月（30天前）
    const nav1M = navHistory[navHistory.length - 30]?.nav || currentNav;
    const perf1M = ((currentNav - nav1M) / nav1M * 100).toFixed(2);
    
    // 近3月（90天前）
    const nav3M = navHistory[navHistory.length - 90]?.nav || currentNav;
    const perf3M = ((currentNav - nav3M) / nav3M * 100).toFixed(2);
    
    // 近6月（180天前）
    const nav6M = navHistory[navHistory.length - 180]?.nav || currentNav;
    const perf6M = ((currentNav - nav6M) / nav6M * 100).toFixed(2);
    
    // 成立以来
    const initialNav = navHistory[0]?.nav || currentNav;
    const perfTotal = ((currentNav - initialNav) / initialNav * 100).toFixed(2);
    
    return {
      '近1月': `${perf1M > 0 ? '+' : ''}${perf1M}%`,
      '近3月': `${perf3M > 0 ? '+' : ''}${perf3M}%`,
      '近6月': `${perf6M > 0 ? '+' : ''}${perf6M}%`,
      '成立来': `${perfTotal > 0 ? '+' : ''}${perfTotal}%`
    };
  };
  
  const performance = useMemo(() => calculatePerformance(), [navHistory]);
  
  // Mock资产占比数据
  const assetAllocation = {
    '股票': 92.91,
    '债券': 7.42,
    '其他': 5.28
  };
  
  // Mock重仓股票
  const topHoldings = [
    { name: '江波龙', change: '+2.47%', weight: '9.71%', positive: true },
    { name: '德邦科', change: '+6.08%', weight: '9.65%', positive: true },
    { name: '首钢股份', change: '-3.45%', weight: '9.31%', positive: false },
    { name: '春秋航空', change: '+5.54%', weight: '9.28%', positive: true },
    { name: '开云云', change: '-2.81%', weight: '9.15%', positive: false }
  ];
  
  // Mock基金经理信息
  const manager = {
    name: fund.manager || '张海瑞',
    experience: '从业16年',
    description: '深圳博时基投资管理有限公司,上海交易所,金融部监事。精于财富管理和资产配置,担任基金经理。'
  };
  
  // ===== 事件处理 =====
  
  const handlePeriodChange = (period) => {
    tracker.track(EventTypes.CLICK, {
      element_id: `period-${period}`,
      element_text: period,
      fund_code: fund.code,
      action_type: 'change_period'
    });
    setSelectedPeriod(period);
  };
  
  const handleBuyClick = () => {
    tracker.track(EventTypes.CLICK, {
      element_id: 'fund-buy-button',
      element_text: '买入',
      fund_code: fund.code,
      fund_name: fund.name,
      action_type: 'buy_fund_mock'
    });
    alert(`买入功能开发中\n基金：${fund.name}\n代码：${fund.code}`);
  };
  
  // 自定义Tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-date">{payload[0].payload.date}</p>
          <p className="tooltip-nav">净值: {payload[0].value}</p>
        </div>
      );
    }
    return null;
  };
  
  return (
    <div className="fund-detail-page">
      {/* 头部导航 */}
      <div className="fund-detail-header">
        <button className="back-button" onClick={onBack}>
          ← 返回
        </button>
        <div className="header-actions">
          <button className="icon-button">🔍</button>
          <button className="icon-button">📤</button>
        </div>
      </div>
      
      {/* 基金名称和代码 */}
      <div className="fund-title-section">
        <div className="fund-badges">
          <span className="badge">股票型</span>
          <span className="badge">已关注</span>
        </div>
        <h1 className="fund-name">{fund.name}</h1>
        <p className="fund-code">{fund.code} | 混合型 | 中高风险</p>
      </div>
      
      {/* 涨跌幅大字显示 */}
      <div className="fund-performance-big">
        <div className={`big-change ${fund.change?.startsWith('+') ? 'positive' : 'negative'}`}>
          {fund.changePercent || '+2.13%'}
        </div>
        <div className="performance-details">
          <div className="detail-item">
            <span className={`detail-value ${fund.change?.startsWith('+') ? 'positive' : 'negative'}`}>
              {fund.change || '+0.0598'}
            </span>
            <span className="detail-label">日涨跌额</span>
          </div>
          <div className="detail-item">
            <span className="detail-value">{fund.nav || '2.8745'}</span>
            <span className="detail-label">单位净值 (11-6)</span>
          </div>
          <div className="detail-item">
            <span className="detail-value secondary">{yesterdayNav}</span>
            <span className="detail-label">昨日净值</span>
          </div>
        </div>
      </div>
      
      {/* 业务主体标签 */}
      <div className="business-tabs">
        <button className="tab-item active">业务主体</button>
        <button className="tab-item">回撤管理</button>
      </div>
      
      {/* 净值走势图 */}
      <div className="chart-section">
        <div className="chart-header">
          <span className="chart-title">净值走势</span>
          <span className="chart-value">成立以来{performance['成立来']}</span>
        </div>
        
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={filteredData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="displayDate" 
              tick={{ fontSize: 12 }}
              stroke="#999"
            />
            <YAxis 
              domain={['auto', 'auto']}
              tick={{ fontSize: 12 }}
              stroke="#999"
              tickFormatter={(value) => {
                // 确保数值正确格式化为4位小数
                const num = Number(value);
                if (isNaN(num)) return '0.0000';
                return num.toFixed(4);
              }}
              allowDataOverflow={false}
              scale="linear"
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#666', strokeDasharray: '3 3' }} />
            <Line 
              type="monotone" 
              dataKey="nav" 
              stroke="#5B8FF9" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: '#5B8FF9' }}
            />
          </LineChart>
        </ResponsiveContainer>
        
        {/* 时间周期切换 */}
        <div className="period-selector">
          <button 
            className={`period-btn ${selectedPeriod === 'daily' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('daily')}
          >
            日K
          </button>
          <button 
            className={`period-btn ${selectedPeriod === 'weekly' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('weekly')}
          >
            周K
          </button>
          <button 
            className={`period-btn ${selectedPeriod === 'monthly' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('monthly')}
          >
            月K
          </button>
          <button 
            className={`period-btn ${selectedPeriod === 'history' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('history')}
          >
            历史业绩
          </button>
        </div>
      </div>
      
      {/* 历史业绩表格 */}
      <div className="performance-table-section">
        <h3 className="section-title">历史业绩</h3>
        <table className="performance-table">
          <thead>
            <tr>
              <th>时间周期</th>
              <th>收益率</th>
              <th>同类平均</th>
              <th>沪深300</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>近1月</td>
              <td className="positive">{performance['近1月']}</td>
              <td>--</td>
              <td>--</td>
            </tr>
            <tr>
              <td>近3月</td>
              <td className="positive">{performance['近3月']}</td>
              <td>-2.96%</td>
              <td>--</td>
            </tr>
            <tr>
              <td>近6月</td>
              <td className="positive">{performance['近6月']}</td>
              <td>--</td>
              <td>--</td>
            </tr>
            <tr>
              <td className="highlight">成立来</td>
              <td className="positive highlight">{performance['成立来']}</td>
              <td className="positive">+2.22%</td>
              <td>--</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      {/* 基金持仓 */}
      <div className="holdings-section">
        <h3 className="section-title">
          基金持仓 
          <span className="subtitle">截至2025年9月30日</span>
        </h3>
        
        {/* 资产类型占比 */}
        <div className="asset-allocation">
          <h4 className="subsection-title">资产类型</h4>
          <div className="allocation-bars">
            {Object.entries(assetAllocation).map(([type, percent]) => (
              <div key={type} className="allocation-item">
                <div className="allocation-header">
                  <span className="allocation-name">{type}</span>
                  <span className="allocation-percent">{percent}%</span>
                </div>
                <div className="allocation-bar">
                  <div 
                    className="allocation-fill" 
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* 重仓股票 */}
        <div className="top-holdings">
          <h4 className="subsection-title">
            重仓股票
            <span className="subtitle">前10大持仓占比72.36%，持股集中度</span>
          </h4>
          <div className="holdings-list">
            {topHoldings.map((stock, index) => (
              <div key={index} className="holding-item">
                <div className="holding-left">
                  <span className="holding-name">{stock.name}</span>
                  <span className="holding-tag">消费电子组装</span>
                </div>
                <div className="holding-right">
                  <span className={`holding-change ${stock.positive ? 'positive' : 'negative'}`}>
                    {stock.change}
                  </span>
                  <span className="holding-weight">{stock.weight}</span>
                  <span className="holding-arrow">→</span>
                </div>
              </div>
            ))}
          </div>
          <button className="view-more-btn">
            查看全部10只基金股票 →
          </button>
        </div>
      </div>
      
      {/* 基金档案 */}
      <div className="fund-archive-section">
        <h3 className="section-title">基金档案</h3>
        
        {/* 基金经理 */}
        <div className="manager-card">
          <div className="manager-header">
            <div className="manager-avatar">
              <span className="avatar-text">{manager.name[0]}</span>
            </div>
            <div className="manager-info">
              <h4 className="manager-name">{manager.name}</h4>
              <p className="manager-experience">{manager.experience}</p>
            </div>
          </div>
          <p className="manager-description">{manager.description}</p>
          <div className="manager-stats">
            <div className="stat-item">
              <span className="stat-label">从业16天</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">本基金任职-36.67%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">年均回报+13.53%</span>
            </div>
          </div>
        </div>
        
        {/* 基金规模 */}
        <div className="fund-info-grid">
          <div className="info-item">
            <span className="info-label">基金规模</span>
            <span className="info-value">12.53亿</span>
          </div>
          <div className="info-item">
            <span className="info-label">成立日期</span>
            <span className="info-value">2020-09-12</span>
          </div>
        </div>
      </div>
      
      {/* 交易规则 */}
      <div className="trading-rules-section">
        <h3 className="section-title">交易规则</h3>
        <div className="rules-grid">
          <div className="rule-item">
            <span className="rule-label">买入</span>
            <span className="rule-value">无限制</span>
          </div>
          <div className="rule-item">
            <span className="rule-label">申购回购</span>
            <span className="rule-value">0.00%</span>
          </div>
          <div className="rule-item">
            <span className="rule-label">赎回费率</span>
            <span className="rule-value">--</span>
          </div>
        </div>
      </div>
      
      {/* 持有人信息 */}
      <div className="holder-info-section">
        <h3 className="section-title">持有人信息</h3>
        <button className="link-button">
          查看本基金TOP100持有人信息 →
        </button>
      </div>
      
      {/* 底部买入按钮 */}
      <div className="bottom-actions">
        <button className="buy-button" onClick={handleBuyClick}>
          买入
        </button>
      </div>
    </div>
  );
};

export default FundDetail;

