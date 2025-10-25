import React, { useState, useEffect } from 'react';
import './AIAssistant.css';
import { useLocation } from 'react-router-dom';

// AI建议内容组件 - 根据页面动态显示不同内容
const AIContent = ({ page, data, onClose }) => {
  switch(page) {
    case 'transfer':
      return (
        <div className="ai-content transfer-ai">
          <h3>转账智能建议</h3>
          <div className="ai-section">
            <h4>历史关联推荐</h4>
            <div className="recent-accounts">
              {data.recentAccounts?.map(account => (
                <div key={account.id} className="recent-account-item">
                  <div className="account-avatar">{account.avatar}</div>
                  <div className="account-info">
                    <div className="account-name">{account.name}</div>
                    <div className="account-number">{account.accountNumber}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          {data.accountType && (
            <div className="ai-section">
              <h4>到账时间预估</h4>
              <div className="arrival-time-info">
                {data.accountType === 'same_bank' ? (
                  <div className="same-bank-arrival">本行账户 → 实时到账</div>
                ) : (
                  <div className="other-bank-arrival">
                    跨行账户 → 预计1-2小时
                    <div className="fee-suggestion">当前高峰，建议次日到账免手续费</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      );
    case 'financing':
      return (
        <div className="ai-content financing-ai">
          <h3>理财智能分析</h3>
          <div className="ai-section">
            <h4>产品适配度</h4>
            <div className="match-index">
              <div className="progress-label">匹配指数: {data.matchIndex || '--'}</div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${data.matchIndex || 0}%` }}></div>
              </div>
            </div>
            <div className="risk-assessment">风险评估: {data.riskLevel || '中等'}</div>
          </div>
          <div className="ai-section">
            <h4>参数解读</h4>
            <ul className="param-explanations">
              {data.paramExplanations?.map((param, index) => (
                <li key={index}>{param.name}: {param.explanation}</li>
              ))}
            </ul>
          </div>
        </div>
      );
    case 'bill':
      return (
        <div className="ai-content bill-ai">
          <h3>账单智能解读</h3>
          <div className="ai-section">
            <h4>消费结构分析</h4>
            <div className="category-analysis">
              {data.categoryAnalysis?.map((category, index) => (
                <div key={index} className="category-item">
                  <div className="category-name">{category.name}</div>
                  <div className="category-bar-container">
                    <div className="category-bar">
                      <div className="category-fill" style={{ width: `${category.percentage}%` }}></div>
                    </div>
                    <div className="category-percentage">{category.percentage}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          {data.abnormalItems?.length > 0 && (
            <div className="ai-section abnormal-alert">
              <h4>异常消费提醒</h4>
              <div className="abnormal-list">
                {data.abnormalItems.slice(0, 2).map((item, index) => (
                  <div key={index} className="abnormal-item">{item.merchant}: {item.amount}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    default:
      return (
        <div className="ai-content default-ai">
          <h3>智能助手</h3>
          <p>欢迎使用AI助手，我可以为您提供个性化的金融服务建议。</p>
          <div className="ai-features">
            <div className="feature-item">转账汇款智能推荐</div>
            <div className="feature-item">理财产品适配分析</div>
            <div className="feature-item">账单消费结构解读</div>
          </div>
        </div>
      );
  }
};

const AIAssistant = ({ onAction }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ bottom: '80px', right: '20px' });
  const [suggestions, setSuggestions] = useState({});
  const [loading, setLoading] = useState(false);
  const location = useLocation();
  const currentPage = location.pathname.split('/')[1] || 'home';

  // 根据当前页面获取AI建议
  useEffect(() => {
    const fetchAISuggestions = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5000/api/ai-suggestions/${getCurrentPage()}`);
        const data = await response.json();
        if (data.success) {
          setSuggestions(data.data);
        } else {
          console.error('获取AI建议失败:', data.error);
        }
      } catch (error) {
        console.error('AI建议网络请求失败:', error);
      } finally {
        setLoading(false);
      }
    };

    if (isOpen || ['transfer', 'financing', 'account'].includes(getCurrentPage())) {
      fetchAISuggestions();
    }
  }, [currentPage, isOpen]);

  // 根据当前页面确定AI内容类型
  useEffect(() => {
    // 关闭弹窗时重置位置
    if (!isOpen) {
      setPosition({ bottom: '80px', right: '20px' });
    }
  }, [isOpen]);

  // 处理点击外部关闭弹窗
  useEffect(() => {
    const handleClickOutside = (event) => {
      const aiContainer = document.querySelector('.ai-assistant-container');
      const aiDialog = document.querySelector('.ai-dialog');
      if (aiContainer && !aiContainer.contains(event.target) && aiDialog && !aiDialog.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 确定当前页面
  const getCurrentPage = () => {
    switch(currentPage) {
      case 'transfer': return 'transfer';
      case 'financing': return 'financing';
      case 'account': return 'bill';
      default: return 'default';
    }
  };

  return (
    <div className="ai-assistant-root">
      {/* AI助手图标 */}
      <div 
        className={`ai-assistant-container ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="ai-assistant-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
            <rect x="2" y="2" width="20" height="20" rx="10" fill="#28a745"/>
            <circle cx="8" cy="12" r="2" fill="white"/>
            <circle cx="16" cy="12" r="2" fill="white"/>
          </svg>
        </div>
        <span className="ai-assistant-label">AI助手</span>
        
      </div>

      {/* AI气泡弹窗 */}
      {isOpen && (
        <div 
          className="ai-dialog" 
          style={position}
          onMouseDown={(e) => e.stopPropagation()}
        >
          <div className="ai-dialog-header">
            <h2>智能金融助手</h2>
            <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
            <div className="dialog-drag-handle"></div>
          </div>
          <div className="ai-dialog-content">
            <AIContent 
              page={getCurrentPage()}
              data={suggestions}
              onClose={() => setIsOpen(false)}
            />
          </div>
          <div className="ai-dialog-footer">
            <button className="action-btn primary-btn" onClick={() => {
              onAction?.('primary', getCurrentPage());
              setIsOpen(false);
            }}>
              {getCurrentPage() === 'transfer' ? '应用推荐' : 
               getCurrentPage() === 'financing' ? '查看详情' : '查看完整报告'}
            </button>
            <button className="action-btn secondary-btn" onClick={() => setIsOpen(false)}>
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;