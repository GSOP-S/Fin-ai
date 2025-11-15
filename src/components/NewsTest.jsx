import React, { useState, useEffect } from 'react';
import { getNewsList } from '../api/news';

const NewsTest = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const data = await getNewsList();
        console.log('获取到的新闻数据:', data);
        setNews(data);
        setError(null);
      } catch (err) {
        console.error('获取新闻失败:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>新闻API测试</h1>
      
      {loading && <p>加载中...</p>}
      
      {error && (
        <div style={{ color: 'red', padding: '10px', backgroundColor: '#ffeeee', borderRadius: '5px' }}>
          <strong>错误:</strong> {error}
        </div>
      )}
      
      {!loading && !error && (
        <div>
          <p>获取到 {news.length} 条新闻</p>
          
          {news.length === 0 ? (
            <p>暂无新闻数据</p>
          ) : (
            <div>
              {news.slice(0, 3).map((item) => (
                <div key={item.id} style={{ 
                  border: '1px solid #ddd', 
                  padding: '15px', 
                  marginBottom: '15px', 
                  borderRadius: '5px' 
                }}>
                  <h3>{item.title}</h3>
                  <p>{item.summary}</p>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    <span>来源: {item.source}</span> | 
                    <span>作者: {item.author}</span> | 
                    <span>分类: {item.category}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NewsTest;