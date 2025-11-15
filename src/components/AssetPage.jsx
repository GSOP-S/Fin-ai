import React, { useState, useEffect } from 'react';
import { fetchPortfolioSummary, fetchFundPositions, fetchDepositPositions } from '../api/asset';
import './AssetPage.css';

const AssetPage = ({ onNavigate }) => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [fundHoldings, setFundHoldings] = useState([]);
  const [depositHoldings, setDepositHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPortfolioData();
  }, []);

  const loadPortfolioData = async () => {
    try {
      setLoading(true);
      const [portfolioResponse, fundResponse, depositResponse] = await Promise.all([
        fetchPortfolioSummary(),
        fetchFundPositions(),
        fetchDepositPositions()
      ]);
      
      // 打印响应数据以便调试
      console.log('Portfolio response:', portfolioResponse);
      console.log('Fund response:', fundResponse);
      console.log('Deposit response:', depositResponse);
      
      setPortfolioData(portfolioResponse.data);
      setFundHoldings(fundResponse.data || []);
      setDepositHoldings(depositResponse.data || []);
      setError(null);
    } catch (err) {
      console.error('加载资产数据失败:', err);
      setError('加载资产数据失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  const formatYield = (yieldValue) => {
    if (!yieldValue) return '0.00%';
    return `${yieldValue.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="asset-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>正在加载资产数据...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="asset-page">
        <div className="error-container">
          <p>{error}</p>
          <button className="retry-button" onClick={loadPortfolioData}>重试</button>
        </div>
      </div>
    );
  }

  return (
    <div className="asset-page">
      <div className="asset-header">
        <h1>我的资产</h1>
        <button className="refresh-button" onClick={loadPortfolioData}>刷新</button>
      </div>

      {/* 总资产概览 */}
      <div className="asset-summary">
        <div className="summary-card total-assets">
          <h3>总资产</h3>
          <p className="amount">¥{portfolioData?.overall?.total_value?.toFixed(2) || '0.00'}</p>
          <p className="change">总收益: <span className={portfolioData?.overall?.total_profit_loss >= 0 ? 'positive' : 'negative'}>
            ¥{portfolioData?.overall?.total_profit_loss?.toFixed(2) || '0.00'} ({formatYield(portfolioData?.overall?.total_profit_loss_percent)})
          </span></p>
          <p className="risk-level">风险等级: {portfolioData?.overall?.risk_level || '低风险'}</p>
        </div>
        
        {/* 资产配置比例 */}
        <div className="summary-card allocation">
          <h3>资产配置</h3>
          <div className="allocation-item">
            <span>基金: {portfolioData?.overall?.allocation_ratios?.fund?.toFixed(2) || '0.00'}%</span>
          </div>
          <div className="allocation-item">
            <span>存款: {portfolioData?.overall?.allocation_ratios?.deposit?.toFixed(2) || '0.00'}%</span>
          </div>
          <div className="allocation-item">
            <span>储蓄: {portfolioData?.overall?.allocation_ratios?.savings?.toFixed(2) || '0.00'}%</span>
          </div>
        </div>
      </div>

      {/* 基金持仓列表 */}
      <div className="asset-section">
        <h2>基金持仓</h2>
        {fundHoldings.length > 0 ? (
          <div className="fund-list">
            {fundHoldings.map(fund => (
              <div key={fund.position_id} className="fund-item">
                <div className="fund-info">
                  <h3>{fund.fund_name}</h3>
                  <p>基金代码: {fund.fund_code}</p>
                </div>
                <div className="fund-value">
                  <p className="amount">¥{fund.current_value?.toFixed(2) || '0.00'}</p>
                  <p className={`change ${fund.profit_loss_percent >= 0 ? 'positive' : 'negative'}`}>
                    {formatYield(fund.profit_loss_percent)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>暂无基金持仓</p>
            <button onClick={() => onNavigate('financing')}>去理财</button>
          </div>
        )}
      </div>
      
      {/* 存款持仓列表 */}
      <div className="asset-section">
        <h2>存款持仓</h2>
        {depositHoldings.length > 0 ? (
          <div className="deposit-list">
            {depositHoldings.map(deposit => (
              <div key={deposit.position_id} className="deposit-item">
                <div className="deposit-info">
                  <h3>{deposit.product_name}</h3>
                  <p>产品代码: {deposit.product_code}</p>
                  <p>类型: {deposit.deposit_type}</p>
                </div>
                <div className="deposit-value">
                  <p className="amount">¥{deposit.current_value?.toFixed(2) || '0.00'}</p>
                  <p className="rate">年利率: {deposit.annual_rate}%</p>
                  {deposit.expected_interest && (
                    <p className="interest">预期收益: ¥{deposit.expected_interest?.toFixed(2) || '0.00'}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>暂无存款持仓</p>
            <button onClick={() => onNavigate('deposit')}>去存款</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetPage;