import React, { useState, useEffect, useMemo } from 'react';
import { getNewsDetail } from '../api/news';
import './NewsDetail.css';

const NewsDetail = ({ newsId, onBack }) => {
  const [news, setNews] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const assetBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const fetchNewsDetail = async () => {
      try {
        setLoading(true);
        const response = await getNewsDetail(newsId);
        if (response && response.success) {
          setNews(response.data);
        } else {
          setError('获取资讯详情失败');
        }
      } catch (err) {
        setError('网络错误，请稍后重试');
        console.error('获取资讯详情错误:', err);
      } finally {
        setLoading(false);
      }
    };

    if (newsId) {
      fetchNewsDetail();
    }
  }, [newsId]);

  const images = useMemo(() => {
    if (!news) return [];
    if (news.images && news.images.length > 0) return news.images;
    return news.image_url ? [news.image_url] : [];
  }, [news]);

  const handlePrev = () => {
    setCurrentIndex((idx) => (idx - 1 + images.length) % images.length);
  };
  const handleNext = () => {
    setCurrentIndex((idx) => (idx + 1) % images.length);
  };

  const formatDate = (dateString) => {
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    };
    return new Date(dateString).toLocaleDateString('zh-CN', options);
  };

  if (loading) {
    return (
      <div className="news-detail-container">
        <div className="loading">加载中...</div>
      </div>
    );
  }

  if (error || !news) {
    return (
      <div className="news-detail-container">
        <button className="back-btn" onClick={onBack}>返回</button>
        <div className="error-message">{error || '资讯不存在'}</div>
      </div>
    );
  }

  return (
    <div className="news-detail-container">
      <div className="news-detail-header">
        <button className="back-btn" onClick={onBack}>返回</button>
      </div>
      
      <div className="news-detail-content">
        <h1 className="news-title">{news.title}</h1>
        
        <div className="news-meta">
          <span className="news-category">{news.category}</span>
          <span className="news-source">来源：{news.source}</span>
          <span className="news-author">作者：{news.author}</span>
          <span className="news-time">{formatDate(news.publish_time)}</span>
        </div>
        
        {images.length > 0 && (
          <div className="news-carousel">
            <div
              className="news-carousel-track"
              style={{ transform: `translateX(-${currentIndex * 100}%)` }}
            >
              {images.map((img, idx) => (
                <div key={idx} className="news-carousel-item">
                  <img src={`${assetBase}${img}`} alt={news.title} />
                </div>
              ))}
            </div>
            {images.length > 1 && (
              <div className="news-carousel-nav">
                <button className="news-carousel-btn" onClick={handlePrev}>‹</button>
                <button className="news-carousel-btn" onClick={handleNext}>›</button>
              </div>
            )}
            {images.length > 1 && (
              <div className="news-carousel-dots">
                {images.map((_, i) => (
                  <span key={i} className={`news-carousel-dot ${i === currentIndex ? 'active' : ''}`}></span>
                ))}
              </div>
            )}
          </div>
        )}
        
        <div className="news-summary">
          <h3>内容摘要</h3>
          <p>{news.summary}</p>
        </div>
        
        <div className="news-body">
          <div dangerouslySetInnerHTML={{ __html: news.content.replace(/\n/g, '<br>') }} />
        </div>
        
        {news.tags && (
          <div className="news-tags">
            <h3>相关标签</h3>
            <div className="tags-container">
              {news.tags.split(',').map((tag, index) => (
                <span key={index} className="tag">{tag}</span>
              ))}
            </div>
          </div>
        )}
        
        <div className="news-stats">
          <span className="read-count">阅读量：{news.read_count}</span>
        </div>
      </div>
    </div>
  );
};

export default NewsDetail;