import React, { useState, useEffect } from 'react';
import './FundList.css';

const FundList = ({ onSelectFund }) => {
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

  // 模拟基金数据
  const mockFunds = [
    {
      id: '000001',
      name: '易方达蓝筹精选混合',
      code: '005827',
      nav: 2.8745,
      changePercent: '2.13%',
      change: '+0.0598',
      category: '混合型',
      risk: '中高风险',
      manager: '张坤'
    },
    {
      id: '000002',
      name: '诺安成长混合',
      code: '320007',
      nav: 1.7654,
      changePercent: '-1.24%',
      change: '-0.0222',
      category: '混合型',
      risk: '高风险',
      manager: '蔡嵩松'
    },
    {
      id: '000003',
      name: '华夏回报混合A',
      code: '002001',
      nav: 3.2456,
      changePercent: '0.89%',
      change: '+0.0288',
      category: '混合型',
      risk: '中风险',
      manager: '王宗合'
    },
    {
      id: '000004',
      name: '富国天惠成长混合A',
      code: '161005',
      nav: 4.5678,
      changePercent: '1.56%',
      change: '+0.0695',
      category: '混合型',
      risk: '中高风险',
      manager: '朱少醒'
    },
    {
      id: '000005',
      name: '兴全合润混合',
      code: '163406',
      nav: 3.8923,
      changePercent: '1.23%',
      change: '+0.0473',
      category: '混合型',
      risk: '中高风险',
      manager: '谢治宇'
    }
  ];

  // 从后端获取基金数据 - 支持分页、筛选和排序
  const fetchFunds = async (page = 1, filterOptions = filters) => {
    setLoading(true);
    try {
      // 构建查询参数
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pagination.pageSize.toString(),
        orderBy: filterOptions.orderBy,
        orderDir: filterOptions.orderDir
      });
      
      // 添加类别和风险等级筛选
      if (filterOptions.category) {
        params.append('category', filterOptions.category);
      }
      if (filterOptions.riskLevel) {
        params.append('riskLevel', filterOptions.riskLevel);
      }
      
      // 调用后端API获取基金列表
      const response = await fetch(`http://localhost:5000/api/funds?${params.toString()}`);
      const data = await response.json();
      
      // 检查数据是否存在
      if (data && data.data) {
        // 更新分页信息
        if (data.pagination) {
          setPagination(data.pagination);
        }
        
        // 如果后端数据为空但有模拟数据，使用模拟数据
        if (data.data.length === 0 && mockFunds.length > 0) {
          setFunds(mockFunds);
        } else {
          setFunds(data.data);
        }
      } else {
        setError('获取基金列表失败: 无效的响应格式');
      }
    } catch (err) {
      setError('获取基金数据失败，请稍后重试');
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

    return (
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
              className="fund-item"
              onClick={() => handleFundClick(fund)}
            >
              <div className="fund-info">
                <div className="fund-name">{fund.name}</div>
                <div className="fund-code">{fund.code}</div>
              </div>
              <div className="fund-details">
                <div className="fund-nav">{Number(fund.nav)?.toFixed(4) || '0.0000'}</div>
                <div className={`fund-change ${fund.change.startsWith('+') ? 'positive' : 'negative'}`}>
                  {fund.changePercent}
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
    );
  };
  
  return renderContent();
};

export default FundList;