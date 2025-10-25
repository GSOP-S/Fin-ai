import React, { useState, useEffect } from 'react';
import './AIAnalysisPanel.css';

const AIAnalysisPanel = ({ selectedProduct, productType }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [matchScore, setMatchScore] = useState(0);
  const [riskAssessment, setRiskAssessment] = useState('');
  const [performanceData, setPerformanceData] = useState(null);

  // 模拟用户风险偏好数据
  const userRiskProfile = {
    riskTolerance: 'moderate', // conservative, moderate, aggressive
    investmentHorizon: 'medium', // short, medium, long
    experienceLevel: 'intermediate', // beginner, intermediate, advanced
    liquidityNeeds: 'low'
  };

  // 组件挂载时计算匹配度
  useEffect(() => {
    if (selectedProduct) {
      calculateMatchScore();
      analyzeProductPerformance();
    }
  }, [selectedProduct]);

  // 计算产品匹配度
  const calculateMatchScore = () => {
    // 简单模拟匹配度计算逻辑
    let score = 70;

    // 根据产品风险等级和用户风险承受能力调整分数
    if (selectedProduct.risk === '高风险') {
      score += userRiskProfile.riskTolerance === 'aggressive' ? 20 : -10;
    } else if (selectedProduct.risk === '中高风险') {
      score += userRiskProfile.riskTolerance === 'aggressive' ? 10 : 
               userRiskProfile.riskTolerance === 'moderate' ? 15 : -15;
    } else if (selectedProduct.risk === '中风险') {
      score += userRiskProfile.riskTolerance === 'moderate' ? 20 : 
               userRiskProfile.riskTolerance === 'conservative' ? 10 : -5;
    } else {
      score += userRiskProfile.riskTolerance === 'conservative' ? 20 : -10;
    }

    // 根据投资期限调整分数
    if (productType === 'fund' && selectedProduct.category.includes('长期')) {
      score += userRiskProfile.investmentHorizon === 'long' ? 15 : 
               userRiskProfile.investmentHorizon === 'medium' ? 5 : -10;
    }

    setMatchScore(Math.min(100, Math.max(30, score)));
    setRiskAssessment(generateRiskAssessment(score));
  };

  // 生成风险评估文本
  const generateRiskAssessment = (score) => {
    if (score >= 85) return '非常匹配您的风险偏好和投资目标';
    if (score >= 70) return '较匹配您的风险偏好和投资目标';
    if (score >= 55) return '基本匹配您的投资需求';
    return '与您的风险偏好存在一定差异，请谨慎考虑';
  };

  // 分析产品表现
  const analyzeProductPerformance = () => {
    // 模拟产品表现数据
    setPerformanceData({
      benchmarkComparison: productType === 'stock' ? 
        `优于大盘${(Math.random() * 15).toFixed(1)}%` : 
        `优于同类平均${(Math.random() * 10).toFixed(1)}%`,
      volatility: productType === 'stock' ? 
        `${(Math.random() * 15 + 5).toFixed(2)}%` : 
        `${(Math.random() * 8 + 2).toFixed(2)}%`,
      returnRate: productType === 'stock' ? 
        `${(Math.random() * 30 - 5).toFixed(2)}%` : 
        `${(Math.random() * 15 + 3).toFixed(2)}%`,
      sharpeRatio: (Math.random() * 1.5 + 0.5).toFixed(2)
    });
  };

  // 简化专业术语解释
  const simplifyTerminology = (term) => {
    const translations = {
      '业绩比较基准': '衡量基金业绩的参考标准',
      '夏普比率': '单位风险所获得的超额收益',
      '波动率': '衡量价格变动的不确定性',
      '最大回撤': '投资期间最大亏损幅度',
      '阿尔法系数': '超额收益能力指标',
      '贝塔系数': '市场风险敏感度指标',
      'R平方': '基金收益与基准相关性'
    };
    return translations[term] || term;
  };

  // 切换面板展开/收起状态
  const togglePanel = () => {
    setIsExpanded(!isExpanded);
  };

  // 对比同类产品
  const compareWithSimilar = () => {
    alert('正在加载同类产品对比数据...\n此功能将展示与该产品风险收益特征相似的3-5款产品对比');
  };

  // 测算收益
  const calculateReturns = () => {
    if (!selectedProduct) return;
    const amount = prompt('请输入投资金额(元):', '10000');
    if (amount && !isNaN(amount)) {
      const yearlyReturn = (parseFloat(amount) * parseFloat(performanceData.returnRate) / 100).toFixed(2);
      alert(`基于历史数据测算:\n投资 ${amount} 元，预计年收益约 ${yearlyReturn} 元\n(历史收益不代表未来表现)`);
    }
  };

  return (
    <div className={`ai-analysis-panel ${isExpanded ? 'expanded' : ''}`} onMouseEnter={togglePanel} onMouseLeave={!isExpanded ? null : togglePanel}>
      {/* 收起状态 - 仅显示橙色竖条 */}
      {!isExpanded && (
        <div className="panel-collapse-indicator">
          <div className="color-bar"></div>
        </div>
      )}

      {/* 展开状态 - 显示完整面板内容 */}
      {isExpanded && (
        <div className="panel-content">
          <div className="panel-header">
            <h3>AI投资分析</h3>
            <button className="close-btn" onClick={togglePanel}>&times;</button>
          </div>

          {!selectedProduct ? (
            <div className="empty-state">
              <p>选择产品查看详细分析</p>
              <div className="tip">提示: 点击任意产品卡片开始分析</div>
            </div>
          ) : (
            <div className="analysis-sections">
              {/* 用户适配度分析 */}
              <div className="analysis-section">
                <h4>用户适配度</h4>
                <div className="match-score-container">
                  <div className="score-label">匹配指数</div>
                  <div className="score-value">{matchScore}%</div>
                  <div className="score-bar">
                    <div className="score-progress" style={{ width: `${matchScore}%` }}></div>
                  </div>
                </div>
                <div className="risk-assessment">{riskAssessment}</div>
                <div className="risk-details">
                  <span>风险等级: {selectedProduct.risk}</span>
                  <span>投资期限: {userRiskProfile.investmentHorizon === 'short' ? '短期(1年内)' : 
                                  userRiskProfile.investmentHorizon === 'medium' ? '中期(1-3年)' : '长期(3年以上)'}</span>
                </div>
              </div>

              {/* 关键参数解读 */}
              <div className="analysis-section">
                <h4>参数解读</h4>
                <div className="parameter-list">
                  {productType === 'fund' && (
                    <>{
                      selectedProduct.nav && (
                        <div className="parameter-item">
                          <span className="param-name">单位净值</span>
                          <span className="param-value">{Number(selectedProduct.nav).toFixed(4)}元</span>
                        </div>
                      )}
                      <div className="parameter-item">
                        <span className="param-name">业绩比较基准</span>
                        <span className="param-value">{simplifyTerminology('业绩比较基准')}</span>
                      </div>
                      <div className="parameter-item">
                        <span className="param-name">夏普比率</span>
                        <span className="param-value">{performanceData?.sharpeRatio} ({simplifyTerminology('夏普比率')})</span>
                      </div>
                    </>
                  )}
                  {productType === 'stock' && (
                    <>{
                      selectedProduct.industry && (
                        <div className="parameter-item">
                          <span className="param-name">所属行业</span>
                          <span className="param-value">{selectedProduct.industry}</span>
                        </div>
                      )}
                      <div className="parameter-item">
                        <span className="param-name">波动率</span>
                        <span className="param-value">{performanceData?.volatility} ({simplifyTerminology('波动率')})</span>
                      </div>
                      <div className="parameter-item">
                        <span className="param-name">近一年收益</span>
                        <span className="param-value">{performanceData?.returnRate}%</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* 操作决策辅助 */}
              <div className="analysis-section action-section">
                <h4>决策辅助</h4>
                <div className="action-buttons">
                  <button className="compare-btn" onClick={compareWithSimilar}>对比同类</button>
                  <button className="calculate-btn" onClick={calculateReturns}>测算收益</button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIAnalysisPanel;