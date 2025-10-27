import React, { useState, useEffect } from 'react';
import './StockList.css';
import { fetchStockList } from '../api/stock';

// 已移除模拟股票数据

const StockList = ({ onSelectStock, onStockHover, onStockLeave }) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 分页和筛选状态
  const [pagination, setPagination] = useState({
    currentPage: 1,
    pageSize: 20,
    totalItems: 0,
    totalPages: 1
  });
  
  // 筛选条件
  const [filters, setFilters] = useState({
    industry: '',
    orderBy: 'code',
    orderDir: 'asc'
  });
  
  // 从后端获取股票数据 - 支持分页、筛选和排序
  const fetchStocks = async (page = 1, filterOptions = filters) => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        page,
        pageSize: pagination.pageSize,
        orderBy: filterOptions.orderBy,
        orderDir: filterOptions.orderDir,
      };
      if (filterOptions.industry) {
        params.industry = filterOptions.industry;
      }

      const result = await fetchStockList(params);

      // 解析后端统一响应结构 { success, data, message }
      const payload = result?.data || {};

      if (payload.pagination) {
        setPagination(payload.pagination);
      }
      setStocks(payload.data || payload.stocks || []);
    } catch (err) {
      console.error('Error fetching stocks:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  // 初始化时获取数据
  useEffect(() => {
    fetchStocks();
  }, []);
  
  // 处理筛选和排序变化
  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    fetchStocks(1, newFilters);
  };
  
  // 处理页码变化
  const handlePageChange = (page) => {
    fetchStocks(page);
  };

  return (
    <div className="stock-list">
      <div className="stock-list-header">
        <h2>股票列表</h2>
        {loading && <span className="loading-indicator">加载中...</span>}
        {error && <span className="error-indicator">{error}</span>}
      </div>

      {/* 无数据提示 */}
      {!loading && stocks.length === 0 && !error && (
        <p style={{ textAlign: 'center', padding: '20px 0' }}>暂无数据</p>
      )}
      
      {/* 筛选和排序控件 - 为未来扩展预留 */}
      <div className="stock-filter-controls">
        {/* 这些控件可以在未来连接真实金融数据库时实现具体功能 */}
        <select 
          value={filters.industry} 
          onChange={(e) => handleFilterChange({...filters, industry: e.target.value})}
          disabled={loading}
        >
          <option value="">全部行业</option>
          <option value="白酒">白酒</option>
          <option value="金融">金融</option>
          <option value="房地产">房地产</option>
          <option value="新能源">新能源</option>
          <option value="家电">家电</option>
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
      
      <div className="stock-items">
        {stocks.map((stock) => (
          <div 
            key={stock.id} 
            className="stock-item" 
            onClick={() => onSelectStock(stock)}
            onMouseEnter={() => onStockHover && onStockHover(stock)}
            onMouseLeave={() => onStockLeave && onStockLeave()}
          >
            <div className="stock-info">
              <div className="stock-name">{stock.name}</div>
              <div className="stock-code">{stock.code}</div>
              {stock.industry && <div className="stock-industry">{stock.industry}</div>}
            </div>
            <div className="stock-price-info">
              <div className="stock-price">{Number(stock.price ?? 0).toFixed(2)}</div>
              <div 
                className={`stock-change ${(stock.change ?? 0) >= 0 ? 'positive' : 'negative'}`}
              >
                {(stock.change ?? 0) >= 0 ? '+' : ''}{Number(stock.change ?? 0).toFixed(2)}
                <span className="change-percent">{stock.changePercent ?? ''}</span>
              </div>
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
  );
};

export default StockList;