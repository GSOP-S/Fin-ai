import React, { useState, useEffect } from 'react';
import './BillDetail.css';
import { useAI } from '../hooks/useAI';

const BillDetail = ({ onNavigate }) => {
  // AI功能Hook
  const ai = useAI();
  // 状态管理
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiAnalysisData, setAiAnalysisData] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7));
  const [aiSuggestionTriggered, setAiSuggestionTriggered] = useState(false);

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
      // 生成AI分析数据（但不直接显示）
      const analysisData = generateAiAnalysis(mockBills);
      setAiAnalysisData(analysisData);
      setAiSuggestionTriggered(false); // 重置触发状态
    }, 800);
  }, [selectedMonth]);
  
  // 数据加载完成后，自动触发AI建议
  useEffect(() => {
    if (!loading && aiAnalysisData && !aiSuggestionTriggered) {
      // 延迟触发，让用户先看到账单列表
      setTimeout(() => {
        ai.show('bill', { 
          bills,
          analysis: aiAnalysisData,
          billData: aiAnalysisData  // 后端需要的格式
        }, {
          autoShow: true,
          autoHideDelay: 30000, // 账单分析显示30秒
          speakEnabled: true
        });
        setAiSuggestionTriggered(true);
      }, 1500);
    }
  }, [loading, aiAnalysisData, aiSuggestionTriggered, bills, ai]);

  // 生成AI消费分析
  const generateAiAnalysis = (transactions) => {
    // 计算总支出和收入
    const totalIncome = transactions
      .filter(t => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);

    const totalExpense = transactions
      .filter(t => t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);

    // 按类别统计支出
    const categoryExpenses = {};
    transactions
      .filter(t => t.amount < 0 && t.category !== '收入')
      .forEach(t => {
        const absAmount = Math.abs(t.amount);
        categoryExpenses[t.category] = (categoryExpenses[t.category] || 0) + absAmount;
      });

    // 找出主要支出类别
    const mainCategories = Object.entries(categoryExpenses)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);

    // 检测异常消费
    const abnormalTransactions = transactions
      .filter(t => t.amount < 0)
      .filter(t => Math.abs(t.amount) > totalExpense * 0.3 || // 超过总支出30%
                  (t.category === '餐饮' && t.amount < -200) || // 单次餐饮超过200
                  (t.category === '购物' && t.amount < -1000)); // 单次购物超过1000

    // 生成优化建议
    const suggestions = [];
    if (categoryExpenses['餐饮'] > totalExpense * 0.3) {
      suggestions.push('您的餐饮支出占比过高（超过30%），建议适当减少外出就餐频率。');
    }
    if (abnormalTransactions.length > 0) {
      suggestions.push('本月检测到异常大额消费，请注意核实是否为本人操作。');
    }
    if (totalExpense > totalIncome * 0.8) {
      suggestions.push('支出已超过收入的80%，建议控制非必要开支，适当增加储蓄比例。');
    }

    // 返回AI分析结果（而不是设置状态）
    return {
      summary: {
        totalIncome,
        totalExpense,
        savingRate: totalIncome > 0 ? ((totalIncome - totalExpense) / totalIncome * 100).toFixed(1) : 0
      },
      categoryDistribution: mainCategories.map(([category, amount]) => ({
        category,
        amount,
        percentage: (amount / totalExpense * 100).toFixed(1)
      })),
      abnormalTransactions: abnormalTransactions.map(t => ({
        id: t.id,
        merchant: t.merchant,
        amount: t.amount,
        date: t.date,
        reason: Math.abs(t.amount) > totalExpense * 0.3 ? '超过月总支出30%' : 
               t.category === '餐饮' ? '单次餐饮消费过高' : '单次购物消费过高'
      })),
      suggestions
    };
  };

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
            setSelectedMonth(date.toISOString().slice(0, 7));
          }}>&lt;</button>
          <span>{selectedMonth}</span>
          <button onClick={() => {
            const date = new Date(selectedMonth);
            const currentMonth = new Date().toISOString().slice(0, 7);
            if (selectedMonth < currentMonth) {
              date.setMonth(date.getMonth() + 1);
              setSelectedMonth(date.toISOString().slice(0, 7));
            }
          }}>&gt;</button>
        </div>
      </div>

      {/* 添加手动触发AI分析按钮 */}
      {!loading && aiAnalysisData && (
        <div className="ai-trigger-bar">
          <button 
            className="ai-analysis-btn"
            onClick={() => {
              ai.show('bill', { 
                bills,
                analysis: aiAnalysisData,
                billData: aiAnalysisData
              }, {
                autoShow: true,
                autoHideDelay: 0, // 手动触发时不自动隐藏
                speakEnabled: false
              });
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
              <div key={bill.id} className="bill-item">
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