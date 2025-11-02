import React, { useState, useEffect } from 'react';
import './FundList.css';
import { fetchFundList } from '../api/fund';

const FundList = ({ onSelectFund }) => {
  const [selectedFund, setSelectedFund] = useState(null);
  const [funds, setFunds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // 分页和筛选状态
  const [pagination, setPagination] = useState({
    currentPage: 1,
    pageSize: 20,
    totalItems: 0,
    totalPages: 1
  });
  
  // 筛选条件
  const [filters, setFilters] = useState({
    category: '',
    riskLevel: '',
    orderBy: 'code',
    orderDir: 'asc'
  });


  // 从后端获取基金数据 - 支持分页、筛选和排序
  const fetchFunds = async (page = 1, filterOptions = filters) => {
    setLoading(true);
    setError('');
    try {
      const params = {
        page,
        pageSize: pagination.pageSize,
        orderBy: filterOptions.orderBy,
        orderDir: filterOptions.orderDir,
      };
      if (filterOptions.category) params.category = filterOptions.category;
      if (filterOptions.riskLevel) params.riskLevel = filterOptions.riskLevel;

      const result = await fetchFundList(params);
      
      // 处理统一后端响应结构 { success, data, message }
      if (result.success && result.data) {
        // 从 data 中提取分页信息和基金数据
        if (result.data.pagination) setPagination(result.data.pagination);
        // 确保 funds 是数组 - 后端返回的是 data.data
        setFunds(Array.isArray(result.data.data) ? result.data.data : []);
        console.log("获取到基金数据:", result.data);
      } else {
        setFunds([]);
        throw new Error(result.message || '获取基金数据失败');
      }
    } catch (err) {
      setError(err.message || '获取基金数据失败，请稍后重试');
      console.error('获取基金数据失败:', err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchFunds();
  }, []);
  
  // 处理筛选和排序变化
  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    fetchFunds(1, newFilters);
  };
  
  // 处理页码变化
  const handlePageChange = (page) => {
    fetchFunds(page);
  };

  const handleFundClick = (fund) => {
    setSelectedFund(fund);
    // 如果传入了onSelectFund回调，则调用它
    if (onSelectFund) {
      onSelectFund(fund);
    }
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="fund-list-container">
          <div className="fund-list-header">
            <h2>基金列表</h2>
          </div>
          <div className="loading-indicator">
            <div className="loading-spinner"></div>
            <p>加载中...</p>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="fund-list-container">
          <div className="fund-list-header">
            <h2>基金列表</h2>
          </div>
          <div className="error-indicator">
            <p>{error}</p>
            <button onClick={() => fetchFunds()} className="retry-btn">重试</button>
          </div>
        </div>
      );
    }

   // 无数据提示
    if (!loading && funds.length === 0) {
      return (
        <div className="fund-list-container">
          <div className="fund-list-header">
            <h2>基金列表</h2>
          </div>
          <p style={{ textAlign: 'center', padding: '20px 0' }}>暂无数据</p>
        </div>
      );
    }

    return (
    <>
      <div className="fund-list-container">
        <div className="fund-list-header">
          <h2>基金列表</h2>
        </div>
        
        {/* 筛选和排序控件 - 为未来连接金融数据库预留 */}
        <div className="fund-filter-controls">
          {/* 这些控件可以在未来连接真实金融数据库时实现具体功能 */}
          <select 
            value={filters.category} 
            onChange={(e) => handleFilterChange({...filters, category: e.target.value})}
            disabled={loading}
          >
            <option value="">全部类型</option>
            <option value="混合型">混合型</option>
            <option value="股票型">股票型</option>
            <option value="债券型">债券型</option>
            <option value="指数型">指数型</option>
          </select>
          
          <select 
            value={filters.riskLevel} 
            onChange={(e) => handleFilterChange({...filters, riskLevel: e.target.value})}
            disabled={loading}
          >
            <option value="">全部风险</option>
            <option value="低风险">低风险</option>
            <option value="中风险">中风险</option>
            <option value="中高风险">中高风险</option>
            <option value="高风险">高风险</option>
          </select>
          
          <select 
            value={filters.orderBy} 
            onChange={(e) => handleFilterChange({...filters, orderBy: e.target.value})}
            disabled={loading}
          >
            <option value="code">按代码</option>
            <option value="name">按名称</option>
          </select>
          
          <button 
            className="sort-btn"
            onClick={() => handleFilterChange({...filters, orderDir: filters.orderDir === 'asc' ? 'desc' : 'asc'})}
            disabled={loading}
          >
            {filters.orderDir === 'asc' ? '↑' : '↓'}
          </button>
        </div>
        
        <div className="fund-list">
          {funds.map((fund) => (
            <div 
            key={fund.id || fund.code} 
            className={`fund-item ${selectedFund?.id === fund.id ? 'selected' : ''}`}
            onClick={() => handleFundClick(fund)}
          >
              <div className="fund-info">
                <div className="fund-name">{fund.name}</div>
                <div className="fund-code">{fund.code}</div>
              </div>
              <div className="fund-details">
                <div className="fund-nav">{Number(fund.nav ?? 0).toFixed(4)}</div>
                <div className={`fund-change ${(fund.change ?? '').startsWith('+') ? 'positive' : 'negative'}`}>
                  {fund.changePercent ?? '0.00%'}
                </div>
                <div className="fund-category">{fund.category}</div>
              </div>
            </div>
          ))}
        </div>
        
        {/* 分页控件 - 为未来连接金融数据库预留 */}
        <div className="pagination-controls">
          <button 
            onClick={() => handlePageChange(pagination.currentPage - 1)} 
            disabled={loading || pagination.currentPage === 1}
          >
            上一页
          </button>
          <span className="page-info">
            第 {pagination.currentPage} 页，共 {pagination.totalPages} 页
          </span>
          <button 
            onClick={() => handlePageChange(pagination.currentPage + 1)} 
            disabled={loading || pagination.currentPage === pagination.totalPages}
          >
            下一页
          </button>
        </div>
      </div>
      {/* <AIAnalysisPanel selectedProduct={selectedFund} productType="fund" /> */}
    </>
    )
  };
  
  return renderContent();
};

export default FundList;