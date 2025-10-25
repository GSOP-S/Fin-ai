import React, { useState } from 'react';
import './TransferPage.css';

function TransferPage({ onNavigate }) {
  // 状态管理
  const [showAiAssistant, setShowAiAssistant] = useState(false);
  const [recipientAccount, setRecipientAccount] = useState('');
  const [transferAmount, setTransferAmount] = useState('');
  const [isFirstTimeAccount, setIsFirstTimeAccount] = useState(false);
  const [accountType, setAccountType] = useState('');

  // 模拟历史转账账户数据
  const recentAccounts = [
    {
      id: 1,
      name: '张三',
      accountNumber: '****1234',
      avatar: '张',
      lastTransfer: '2023-10-15'
    },
    {
      id: 2,
      name: '李四',
      accountNumber: '****5678',
      avatar: '李',
      lastTransfer: '2023-10-10'
    },
    {
      id: 3,
      name: '王五',
      accountNumber: '****9012',
      avatar: '王',
      lastTransfer: '2023-10-05'
    }
  ];

  // 处理收款账户输入变化
  const handleRecipientAccountChange = (e) => {
    const value = e.target.value;
    setRecipientAccount(value);
    // 模拟检测账户类型
    if (value.includes('6222')) {
      setAccountType('same_bank');
    } else if (value) {
      setAccountType('other_bank');
      setIsFirstTimeAccount(true); // 模拟首次添加账户
    } else {
      setAccountType('');
      setIsFirstTimeAccount(false);
    }
  };

  // 选择历史账户
  const selectAccount = (account) => {
    setRecipientAccount(account.accountNumber);
    setShowAiAssistant(false);
    // 简单判断是否为首次转账账户
    setIsFirstTimeAccount(Math.random() > 0.5);
    // 随机模拟账户类型（本行/跨行）
    setAccountType(Math.random() > 0.5 ? 'same_bank' : 'other_bank');
  };

  // 处理转账提交
  const handleTransferSubmit = (e) => {
    e.preventDefault();
    // 转账逻辑处理
    alert(`转账成功：${transferAmount}元 至 ${recipientAccount}`);
    onNavigate('home');
  };

  return (
    <div className="transfer-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => onNavigate('home')}>←</button>
        <h2>转账汇款</h2>
      </div>

      <div className="transfer-form">
        <div className="form-group">
          <label>收款账户</label>
          <div className="account-input-container">
            <input
              type="text"
              value={recipientAccount}
              onChange={handleRecipientAccountChange}
              placeholder="请输入收款账户"
              className="recipient-account-input"
            />
            <button
              className="ai-icon-btn"
              onClick={() => setShowAiAssistant(!showAiAssistant)}
              aria-label="AI助手"
            >
              <span className="ai-icon">AI</span>
            </button>
            {showAiAssistant && (
              <div className="ai-assistant-float">
                <div className="ai-float-header">
                  <h3>智能转账助手</h3>
                  <button onClick={() => setShowAiAssistant(false)}>×</button>
                </div>
                <div className="ai-section">
                  <h4>历史关联推荐</h4>
                  <div className="recent-accounts">
                    {recentAccounts.map(account => (
                      <div
                        key={account.id}
                        className="recent-account-item"
                        onClick={() => selectAccount(account)}
                      >
                        <div className="account-avatar">{account.avatar}</div>
                        <div className="account-info">
                          <div className="account-name">{account.name}</div>
                          <div className="account-number">{account.accountNumber}</div>
                          <div className="last-transfer">最近: {account.lastTransfer}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="ai-section">
                  <h4>到账时间预估</h4>
                  <div className="arrival-time-info">
                    {accountType === 'same_bank' ? (
                      <div className="same-bank-arrival">
                        <span className="time-label">本行账户 → 实时到账</span>
                      </div>
                    ) : (
                      <div className="other-bank-arrival">
                        <span className="time-label">跨行账户 → 预计1-2小时</span>
                        <div className="fee-suggestion">
                          <span className="peak-time-alert">当前时段转账高峰</span>
                          <span className="suggestion-text">建议优先选次日到账免手续费</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                {isFirstTimeAccount && (
                  <div className="ai-section risk-alert-section">
                    <h4>风险校验提醒</h4>
                    <div className="risk-alert">
                      <div className="risk-icon">⚠️</div>
                      <div className="risk-text">
                        该账户近3个月无交易记录，是否开启24小时到账保护？
                      </div>
                      <div className="risk-actions">
                        <button className="risk-btn confirm-btn">开启保护</button>
                        <button className="risk-btn cancel-btn">取消</button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* AI助手浮层 */}

        </div>

        <div className="form-group">
          <label>转账金额</label>
          <input
            type="number"
            value={transferAmount}
            onChange={(e) => setTransferAmount(e.target.value)}
            placeholder="请输入转账金额"
            className="transfer-amount-input"
          />
        </div>

        <button className="transfer-submit-btn">确认转账</button>
      </div>
    </div>
  );
}

export default TransferPage;