// 测试新闻API
async function testNewsAPI() {
  try {
    console.log('开始测试新闻API...');
    
    // 直接测试后端API
    const backendResponse = await fetch('http://localhost:5000/api/news');
    const backendData = await backendResponse.json();
    console.log('后端API调用成功，返回数据:', backendData);
    console.log('后端新闻数量:', backendData.data?.list?.length || 0);
    
    // 测试前端代理API
    const frontendResponse = await fetch('http://localhost:3000/api/news');
    const frontendData = await frontendResponse.json();
    console.log('前端代理API调用成功，返回数据:', frontendData);
    console.log('前端新闻数量:', frontendData.data?.list?.length || 0);
    
  } catch (error) {
    console.error('API调用失败:', error);
  }
}

testNewsAPI();