import React, { useState, useEffect } from 'react';
import { fetchUserBills, fetchBillAnalysis } from '../api/bill';
import './BillDetail.css';
import { usePageTracking } from '../hooks/usePageTracking';
import { useBehaviorTracker } from '../hooks/useBehaviorTracker';
import { EventTypes } from '../config/tracking.config';

const BillDetail = ({ onNavigate, onShowAI }) => {
  // ===== 行为追踪 =====
  const tracker = useBehaviorTracker();
  usePageTracking('account', { section: 'bill_detail' });
  
  // 状态管理
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7));
  const [aiSuggestionTriggered, setAiSuggestionTriggered] = useState(false);
  const [billAnalysis, setBillAnalysis] = useState(null);

  // 模拟账单数据
  useEffect(() => {
    // 模拟API请求延迟
    setTimeout(() => {
      const mockBills = [
        {
          id: 1,
          merchant: '星巴克咖啡',
          category: '餐饮',
          amount: -45.00,
          date: '2023-10-28',
          time: '09:25',
          status: 'completed'
        },
        {
          id: 2,
          merchant: '沃尔玛超市',
          category: '购物',
          amount: -189.50,
          date: '2023-10-27',
          time: '18:42',
          status: 'completed'
        },
        {
          id: 3,
          merchant: '滴滴出行',
          category: '交通',
          amount: -28.60,
          date: '2023-10-27',
          time: '08:15',
          status: 'completed'
        },
        {
          id: 4,
          merchant: '工资入账',
          category: '收入',
          amount: 12500.00,
          date: '2023-10-25',
          time: '10:30',
          status: 'completed'
        },
        {
          id: 5,
          merchant: '电影票',
          category: '娱乐',
          amount: -98.00,
          date: '2023-10-24',
          time: '19:00',
          status: 'completed'
        },
        {
          id: 6,
          merchant: '房租支出',
          category: '住房',
          amount: -3500.00,
          date: '2023-10-01',
          time: '00:00',
          status: 'completed'
        }
      ];
      setBills(mockBills);
      setLoading(false);
      setAiSuggestionTriggered(false); // 重置触发状态
      setBillAnalysis(null); // 重置账单分析
    }, 800);
  }, [selectedMonth]);
  
  // 数据加载完成后，自动触发AI建议
  useEffect(() => {
    if (!loading && bills.length > 0 && !aiSuggestionTriggered && onShowAI) {
      // 延迟触发，让用户先看到账单列表
      setTimeout(() => {
        // 调用后端API获取账单分析
        fetchBillAnalysis('user123', bills, selectedMonth)
          .then(analysis => {
            if (analysis && analysis.success) {
              setBillAnalysis(analysis.data);
              // 触发AI建议显示
              onShowAI('bill', { 
                bills,
                billData: analysis.data  // 使用后端返回的分析数据
              }, {
                autoShow: true,
                autoHideDelay: 30000, // 账单分析显示30秒
                speakEnabled: true
              });
              setAiSuggestionTriggered(true);
            }
          })
          .catch(error => {
            console.error('获取账单分析失败:', error);
          });
      }, 1500);
    }
  }, [loading, bills, aiSuggestionTriggered, onShowAI, selectedMonth]);

  // 格式化金额显示
  const formatAmount = (amount) => {
    const sign = amount > 0 ? '+' : '';
    return `${sign}${amount.toFixed(2)}`;
  };

  // 生成金额颜色样式
  const getAmountColor = (amount) => {
    if (amount > 0) return 'positive';
    if (amount < 0) return 'negative';
    return '';
  };

  return (
    <div className="bill-detail-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => onNavigate('home')}>返回</button>
        <h2>账单明细</h2>
        <div className="month-selector">
          <button onClick={() => {
            const date = new Date(selectedMonth);
            date.setMonth(date.getMonth() - 1);
            const newMonth = date.toISOString().slice(0, 7);
            
            // 追踪月份筛选
            tracker.track(EventTypes.BILL_FILTER, {
              filter_type: 'month',
              from_month: selectedMonth,
              to_month: newMonth,
            });
            
            setSelectedMonth(newMonth);
          }}>&lt;</button>
          <span>{selectedMonth}</span>
          <button onClick={() => {
            const date = new Date(selectedMonth);
            const currentMonth = new Date().toISOString().slice(0, 7);
            if (selectedMonth < currentMonth) {
              date.setMonth(date.getMonth() + 1);
              const newMonth = date.toISOString().slice(0, 7);
              
              // 追踪月份筛选
              tracker.track(EventTypes.BILL_FILTER, {
                filter_type: 'month',
                from_month: selectedMonth,
                to_month: newMonth,
              });
              
              setSelectedMonth(newMonth);
            }
          }}>&gt;</button>
        </div>
      </div>

      {/* 添加手动触发AI分析按钮 */}
      {!loading && bills.length > 0 && (
        <div className="ai-trigger-bar">
          <button 
            className="ai-analysis-btn"
            onClick={() => {
              if (onShowAI) {
                // 如果已有分析数据，直接显示；否则重新获取
                if (billAnalysis) {
                  onShowAI('bill', { 
                    bills,
                    billData: billAnalysis  // 使用已有的分析数据
                  }, {
                    autoShow: true,
                    autoHideDelay: 0, // 手动触发时不自动隐藏
                    speakEnabled: false
                  });
                } else {
                  // 重新获取分析数据
                  fetchBillAnalysis('user123', bills, selectedMonth)
                    .then(analysis => {
                      if (analysis && analysis.success) {
                        setBillAnalysis(analysis.data);
                        onShowAI('bill', { 
                          bills,
                          billData: analysis.data  // 使用后端返回的分析数据
                        }, {
                          autoShow: true,
                          autoHideDelay: 0, // 手动触发时不自动隐藏
                          speakEnabled: false
                        });
                      }
                    })
                    .catch(error => {
                      console.error('获取账单分析失败:', error);
                    });
                }
              }
            }}
          >
            <span className="ai-icon">🤖</span>
            <span className="ai-text">查看AI消费分析</span>
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>加载账单数据中...</p>
        </div>
      ) : (
        <div className="bills-list">
          {bills.length === 0 ? (
            <div className="empty-state">
              <p>本月暂无账单记录</p>
            </div>
          ) : (
            bills.map(bill => (
              <div 
                key={bill.id} 
                className="bill-item"
                onClick={() => {
                  // 追踪查看账单详情
                  tracker.track(EventTypes.BILL_VIEW, {
                    bill_id: bill.id,
                    bill_merchant: bill.merchant,
                    bill_category: bill.category,
                    bill_amount: bill.amount,
                    bill_date: bill.date,
                    selected_month: selectedMonth,
                  });
                }}
              >
                <div className="bill-icon">
                  {bill.category === '餐饮' && '🍽️'}
                  {bill.category === '购物' && '🛒'}
                  {bill.category === '交通' && '🚗'}
                  {bill.category === '住房' && '🏠'}
                  {bill.category === '娱乐' && '🎬'}
                  {bill.category === '收入' && '💰'}
                  {!['餐饮','购物','交通','住房','娱乐','收入'].includes(bill.category) && '📋'}
                </div>
                <div className="bill-details">
                  <div className="merchant-info">
                    <h4 className="merchant-name">{bill.merchant}</h4>
                    <div className="bill-meta">
                      <span className="category-tag">{bill.category}</span>
                      <span className="bill-time">{bill.time}</span>
                    </div>
                  </div>
                  <div className={`bill-amount ${getAmountColor(bill.amount)}`}>
                    {formatAmount(bill.amount)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default BillDetail;