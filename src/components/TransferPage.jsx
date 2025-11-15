import React, { useState, useEffect } from 'react';
import './TransferPage.css';
import { usePageTracking } from '../hooks/usePageTracking';
import { useBehaviorTracker } from '../hooks/useBehaviorTracker';
import { EventTypes } from '../config/tracking.config';

function AssetsPage({ onNavigate }) {
  // ===== 行为追踪 =====
  const tracker = useBehaviorTracker();
  usePageTracking('assets');
  
  // 模拟用户资产数据
  const [assetsData, setAssetsData] = useState({
    totalAssets: 128563.45,
    funds: [
      { id: 1, name: '华夏成长混合', code: '000001', amount: 50000, yield: '+8.5%', nav: 1.256 },
      { id: 2, name: '易方达消费行业', code: '110022', amount: 30000, yield: '+12.3%', nav: 3.847 },
      { id: 3, name: '嘉实新兴产业', code: '000755', amount: 20000, yield: '-2.1%', nav: 2.134 },
      { id: 4, name: '南方中证500', code: '160119', amount: 15000, yield: '+5.7%', nav: 1.089 }
    ],
    deposits: [
      { id: 1, name: '定期存款(1年期)', amount: 10000, rate: '3.25%', maturity: '2024-12-31' },
      { id: 2, name: '大额存单(3年期)', amount: 50000, rate: '3.85%', maturity: '2027-03-15' }
    ]
  });

  // 处理基金点击，跳转到基金详情页
  const handleFundClick = (fund) => {
    // 追踪基金点击（实时上报）
    tracker.track(EventTypes.FUND_CLICK_ASSETS, {
      fund_code: fund.code,
      fund_name: fund.name,
      fund_amount: fund.amount,
      fund_yield: fund.yield,
    }, { realtime: true });
    
    // 跳转到基金详情页
    onNavigate('fund-detail', { fundCode: fund.code });
  };

  // 触发资产分析AI建议
  const triggerAssetAnalysis = () => {
    tracker.track('request_asset_analysis', {
      page: 'assets',
      total_assets: assetsData.totalAssets,
      fund_count: assetsData.funds.length,
      deposit_count: assetsData.deposits.length,
      fund_amounts: assetsData.funds.map(f => f.amount),
    }, { realtime: true });
    
    console.log('[AssetsPage] 已请求资产分析');
  };

  return (
    <div className="assets-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => onNavigate('home')}>←</button>
        <h2>我的资产</h2>
        <button className="ai-trigger-btn" onClick={triggerAssetAnalysis}>
          <span className="ai-icon">🤖</span>
        </button>
      </div>

      {/* 总资产概览 */}
      <div className="assets-overview">
        <div className="total-assets-card">
          <div className="assets-label">总资产</div>
          <div className="assets-amount">¥{assetsData.totalAssets.toLocaleString()}</div>
          <div className="assets-detail">
            <span>基金 {assetsData.funds.length}只</span>
            <span>存款 {assetsData.deposits.length}笔</span>
          </div>
        </div>
      </div>

      {/* 基金持仓 */}
      <div className="assets-section">
        <div className="section-header">
          <h3>基金持仓 ({assetsData.funds.length}只)</h3>
        </div>
        <div className="funds-list">
          {assetsData.funds.map((fund) => (
            <div 
              key={fund.id} 
              className="fund-asset-item"
              onClick={() => handleFundClick(fund)}
            >
              <div className="fund-info">
                <div className="fund-name">{fund.name}</div>
                <div className="fund-code">{fund.code}</div>
              </div>
              <div className="fund-amount">
                <div className="amount">¥{fund.amount.toLocaleString()}</div>
                <div className={`yield ${fund.yield.startsWith('+') ? 'positive' : 'negative'}`}>
                  {fund.yield}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 存款账户 */}
      <div className="assets-section">
        <div className="section-header">
          <h3>存款账户 ({assetsData.deposits.length}笔)</h3>
        </div>
        <div className="deposits-list">
          {assetsData.deposits.map((deposit) => (
            <div key={deposit.id} className="deposit-asset-item">
              <div className="deposit-info">
                <div className="deposit-name">{deposit.name}</div>
                <div className="deposit-maturity">到期日: {deposit.maturity}</div>
              </div>
              <div className="deposit-amount">
                <div className="amount">¥{deposit.amount.toLocaleString()}</div>
                <div className="rate">{deposit.rate}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AssetsPage;