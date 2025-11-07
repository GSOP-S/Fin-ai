import React, { useState } from 'react';
import './TransferPage.css';
import { usePageTracking } from '../hooks/usePageTracking';
import { useBehaviorTracker } from '../hooks/useBehaviorTracker';
import { EventTypes } from '../config/tracking.config';

function TransferPage({ onNavigate, onShowAI }) {
  // ===== 行为追踪 =====
  const tracker = useBehaviorTracker();
  usePageTracking('transfer');
  
  // 状态管理
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
    
    // 追踪收款账户选择（卡号会自动脱敏）
    if (value.length >= 10) {
      tracker.track(EventTypes.TRANSFER_SELECT, {
        cardNumber: value, // 会被自动脱敏（保留前4后4）
        account_type: detectedAccountType,
        is_first_time: isFirstTime,
      });
    }
    
    // 当输入完整账号后，触发AI建议
    if (value.length >= 10 && onShowAI) {
      // 准备传递给后端AI服务的数据
      const transferData = {
        recipientAccount: value,
        accountType: detectedAccountType,
        isFirstTimeAccount: isFirstTime,
        recentAccounts,
        amount: transferAmount
      };
      
      // 自动触发AI建议气泡（延迟500ms，让用户看到账户类型变化）
      setTimeout(() => {
        onShowAI('transfer', {
          transferData
        }, {
          autoShow: true,
          autoHideDelay: 25000,
          speakEnabled: false
        });
      }, 500);
    }
  };

  // 手动触发AI转账建议
  const triggerAISuggestion = () => {
    if (!onShowAI) return;
    
    // 准备传递给后端AI服务的数据
    const transferData = {
      recipientAccount,
      accountType,
      isFirstTimeAccount,
      recentAccounts,
      amount: transferAmount
    };
    
    onShowAI('transfer', {
      transferData
    }, {
      autoShow: true,
      autoHideDelay: 0, // 手动触发不自动隐藏
      speakEnabled: false
    });
  };

  // 处理金额输入
  const handleAmountChange = (e) => {
    const amount = e.target.value;
    setTransferAmount(amount);
    
    // 追踪金额输入（完全采集）
    if (amount) {
      tracker.track(EventTypes.TRANSFER_INPUT, {
        transfer_amount: parseFloat(amount) || 0, // 完全采集金额
        amount_range: getAmountRange(amount),
        has_recipient: !!recipientAccount,
      });
    }
  };
  
  // 金额范围分类（用于分析）
  const getAmountRange = (amount) => {
    const num = parseFloat(amount) || 0;
    if (num < 100) return '0-100';
    if (num < 1000) return '100-1000';
    if (num < 10000) return '1000-10000';
    if (num < 100000) return '10000-100000';
    return '100000+';
  };
  
  // 处理转账提交
  const handleTransferSubmit = (e) => {
    e.preventDefault();
    
    // 追踪转账提交（实时上报）
    tracker.track(EventTypes.TRANSFER_SUBMIT, {
      cardNumber: recipientAccount, // 会被自动脱敏
      transfer_amount: parseFloat(transferAmount) || 0, // 完全采集
      amount_range: getAmountRange(transferAmount),
      account_type: accountType,
      is_first_time: isFirstTimeAccount,
    }, { realtime: true }); // 实时上报
    
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
            onChange={handleAmountChange}
            placeholder="请输入转账金额"
            className="transfer-amount-input"
          />
        </div>

        <button 
          className="transfer-submit-btn"
          onClick={handleTransferSubmit}
        >
          确认转账
        </button>
      </div>
    </div>
  );
}

export default TransferPage;