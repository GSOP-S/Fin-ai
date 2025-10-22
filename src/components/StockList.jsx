import React, { useState, useEffect } from 'react';
import './StockList.css';

// 模拟股票数据（作为备用）
const mockStocks = [
  {
    id: 1,
    code: '600519',
    name: '贵州茅台',
    price: 1820.00,
    change: +25.60,
    changePercent: '+1.43%'
  },
  {
    id: 2,
    code: '000858',
    name: '五粮液',
    price: 162.50,
    change: -3.20,
    changePercent: '-1.93%'
  },
  {
    id: 3,
    code: '000002',
    name: '万科A',
    price: 12.50,
    change: +0.25,
    changePercent: '+2.05%'
  },
  {
    id: 4,
    code: '000001',
    name: '平安银行',
    price: 10.80,
    change: -0.12,
    changePercent: '-1.10%'
  },
  {
    id: 5,
    code: '601318',
    name: '中国平安',
    price: 45.60,
    change: +0.80,
    changePercent: '+1.79%'
  },
  {
    id: 6,
    code: '002594',
    name: '比亚迪',
    price: 288.50,
    change: -5.60,
    changePercent: '-1.90%'
  },
  {
    id: 7,
    code: '000333',
    name: '美的集团',
    price: 58.20,
    change: +1.20,
    changePercent: '+2.10%'
  },
  {
    id: 8,
    code: '000651',
    name: '格力电器',
    price: 36.50,
    change: -0.45,
    changePercent: '-1.22%'
  }
];

const StockList = ({ onSelectStock, onStockHover, onStockLeave }) => {
  const [stocks, setStocks] = useState(mockStocks);
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
      // 构建查询参数
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pagination.pageSize.toString(),
        orderBy: filterOptions.orderBy,
        orderDir: filterOptions.orderDir
      });
      
      // 添加行业筛选
      if (filterOptions.industry) {
        params.append('industry', filterOptions.industry);
      }
      
      const response = await fetch(`http://localhost:5000/api/stocks?${params.toString()}`);
      if (!response.ok) {
        throw new Error('获取股票数据失败');
      }
      
      const data = await response.json();
      if (data.success && data.data && data.data.length > 0) {
        // 更新分页信息
        if (data.pagination) {
          setPagination(data.pagination);
        }
        
        // 将后端数据与本地价格数据合并
        const enhancedStocks = data.data.map((stock, index) => {
          const mockData = mockStocks.find(m => m.code === stock.code) || mockStocks[index % mockStocks.length];
          return {
            ...stock,
            id: stock.id || index + 1,
            price: mockData.price,
            change: mockData.change,
            changePercent: mockData.changePercent
          };
        });
        setStocks(enhancedStocks);
      }
    } catch (err) {
      console.error('Error fetching stocks:', err);
      setError(err.message);
      // 出错时使用模拟数据
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
              <div className="stock-price">{stock.price.toFixed(2)}</div>
              <div 
                className={`stock-change ${stock.change >= 0 ? 'positive' : 'negative'}`}
              >
                {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                <span className="change-percent">{stock.changePercent}</span>
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