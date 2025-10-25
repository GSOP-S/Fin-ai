import React, { useState } from 'react';
import './TransferPage.css';

function TransferPage({ onNavigate, onShowAISuggestion }) {
  // 状态管理
  const [recipientAccount, setRecipientAccount] = useState('');
  const [transferAmount, setTransferAmount] = useState('');
  const [isFirstTimeAccount, setIsFirstTimeAccount] = useState(false);
  const [accountType, setAccountType] = useState('');
  const [aiSuggestionData, setAiSuggestionData] = useState(null);

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
    let detectedAccountType = '';
    let isFirstTime = false;
    
    if (value.includes('6222')) {
      detectedAccountType = 'same_bank';
    } else if (value.length >= 10) {
      detectedAccountType = 'other_bank';
      isFirstTime = Math.random() > 0.5; // 模拟首次添加账户
    }
    
    setAccountType(detectedAccountType);
    setIsFirstTimeAccount(isFirstTime);
    
    // 当输入完整账号后，触发AI建议
    if (value.length >= 10 && onShowAISuggestion) {
      const suggestionData = {
        recipientAccount: value,
        accountType: detectedAccountType,
        isFirstTimeAccount: isFirstTime,
        recentAccounts,
        arrivalTime: detectedAccountType === 'same_bank' ? '实时到账' : '预计1-2小时',
        suggestion: isFirstTime ? '该账户近期无交易记录，建议核实收款人信息' : '常用账户，可放心转账'
      };
      
      setAiSuggestionData(suggestionData);
      
      // 自动触发AI建议气泡（延迟500ms，让用户看到账户类型变化）
      setTimeout(() => {
        onShowAISuggestion('transfer', suggestionData, {
          autoShow: true,
          autoHideDelay: 25000,
          speakEnabled: false
        });
      }, 500);
    }
  };

  // 手动触发AI转账建议
  const triggerAISuggestion = () => {
    if (onShowAISuggestion) {
      const suggestionData = aiSuggestionData || {
        recentAccounts,
        suggestion: '选择常用账户可以更快完成转账'
      };
      
      onShowAISuggestion('transfer', suggestionData, {
        autoShow: true,
        autoHideDelay: 0, // 手动触发不自动隐藏
        speakEnabled: false
      });
    }
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
              placeholder="请输入收款账户或选择历史账户"
              className="recipient-account-input"
            />
            <button
              className="ai-trigger-btn"
              onClick={triggerAISuggestion}
              aria-label="AI转账助手"
              title="获取智能转账建议"
            >
              <span className="ai-icon">🤖</span>
            </button>
          </div>
          {accountType && (
            <div className="account-type-indicator">
              {accountType === 'same_bank' ? (
                <span className="same-bank">✓ 本行账户 · 实时到账</span>
              ) : (
                <span className="other-bank">⚠️ 跨行账户 · 预计1-2小时</span>
              )}
            </div>
          )}
          {isFirstTimeAccount && (
            <div className="risk-indicator">
              ⚠️ 新账户，建议核实收款人信息
            </div>
          )}
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