import React, { useState, useEffect } from 'react';
import './NewsPage.css';
import { getNewsList } from '../api/news';

function NewsPage({ onNavigate }) {
  const [newsList, setNewsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentCategory, setCurrentCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredNews, setFilteredNews] = useState([]);

  // 分类配置
  const categories = [
    { id: 'all', name: '全部' },
    { id: '财经新闻', name: '财经新闻' },
    { id: '市场行情', name: '市场行情' },
    { id: '政策解读', name: '政策解读' },
    { id: '理财知识', name: '理财知识' }
  ];

  // 获取资讯列表
  useEffect(() => {
    fetchNews();
  }, []);

  // 筛选资讯
  useEffect(() => {
    filterNews();
  }, [currentCategory, searchQuery, newsList]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const data = await getNewsList();
      setNewsList(data);
    } catch (error) {
      console.error('获取资讯失败:', error);
      setNewsList([]);
    } finally {
      setLoading(false);
    }
  };

  const filterNews = () => {
    let filtered = newsList;

    // 按分类筛选
    if (currentCategory !== 'all') {
      filtered = filtered.filter(news => news.category === currentCategory);
    }

    // 按搜索关键词筛选
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(news => 
        news.title.toLowerCase().includes(query) ||
        news.summary.toLowerCase().includes(query)
      );
    }

    setFilteredNews(filtered);
  };

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
  };

  const formatTime = (timeStr) => {
    const time = new Date(timeStr);
    const now = new Date();
    const diff = Math.floor((now - time) / 1000); // 秒

    if (diff < 60) return '刚刚';
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
    if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`;
    
    return time.toLocaleDateString('zh-CN');
  };

  const getCategoryColor = (category) => {
    const colors = {
      '财经新闻': '#5B8FF9',
      '市场行情': '#5AD8A6',
      '政策解读': '#F6BD16',
      '理财知识': '#E8684A'
    };
    return colors[category] || '#5B8FF9';
  };

  return (
    <div className="news-page">
      {/* 搜索栏 */}
      <div className="news-search-bar">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            className="search-input" 
            placeholder="搜索资讯标题或内容..."
            value={searchQuery}
            onChange={handleSearch}
          />
          {searchQuery && (
            <span 
              className="clear-icon" 
              onClick={() => setSearchQuery('')}
            >
              ×
            </span>
          )}
        </div>
      </div>

      {/* 分类标签 */}
      <div className="news-categories">
        {categories.map(cat => (
          <button
            key={cat.id}
            className={`category-btn ${currentCategory === cat.id ? 'active' : ''}`}
            onClick={() => setCurrentCategory(cat.id)}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* 资讯列表 */}
      <div className="news-list-container">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>加载中...</p>
          </div>
        ) : filteredNews.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📰</span>
            <p>暂无相关资讯</p>
          </div>
        ) : (
          <div className="news-cards">
            {filteredNews.map((news) => (
              <div 
                key={news.id} 
                className="news-card"
              >
                {news.image_url && (
                  <div className="news-image">
                    <img src={news.image_url} alt={news.title} />
                  </div>
                )}
                <div className="news-card-content">
                  <div className="news-card-header">
                    <span 
                      className="news-category-tag"
                      style={{ backgroundColor: getCategoryColor(news.category) }}
                    >
                      {news.category}
                    </span>
                    <span className="news-source">{news.source}</span>
                  </div>
                  <h3 className="news-card-title">{news.title}</h3>
                  <p className="news-card-summary">{news.summary}</p>
                  <div className="news-card-footer">
                    <div className="news-meta">
                      <span className="news-author">👤 {news.author}</span>
                      <span className="news-time">🕐 {formatTime(news.publish_time)}</span>
                    </div>
                    <div className="news-stats">
                      <span className="read-count">👁 {news.read_count || 0}</span>
                    </div>
                  </div>
                  {news.tags && news.tags.length > 0 && (
                    <div className="news-tags">
                      {news.tags.split(',').slice(0, 3).map((tag, index) => (
                        <span key={index} className="news-tag">#{tag.trim()}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default NewsPage;

