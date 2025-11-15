// 高亮功能测试脚本
// 在浏览器控制台中执行这些命令来测试基金高亮效果

console.log('=== 基金高亮功能测试命令 ===\n');

// 测试1: 高亮单个基金
function testHighlightSingleFund() {
  console.log('🎯 测试1: 高亮单个基金');
  console.log('命令: testHighlightSingleFund()');
  console.log('效果: 高亮基金ID为"fund_001"的基金，显示AI建议弹窗\n');
  
  // 模拟AI建议事件
  const event = new CustomEvent('ai-suggestion-received', {
    detail: {
      suggestion: '根据您的投资偏好，建议关注这只稳健型基金',
      command: 'highlight',
      confidence: 0.85,
      fund_id: 'fund_001',
      source: 'ai_analysis'
    }
  });
  
  window.dispatchEvent(event);
}

// 测试2: 高亮多个基金
function testHighlightMultipleFunds() {
  console.log('🎯 测试2: 高亮多个基金');
  console.log('命令: testHighlightMultipleFunds()');
  console.log('效果: 高亮基金ID为["fund_001", "fund_003", "fund_005"]的基金，显示AI建议弹窗\n');
  
  const event = new CustomEvent('ai-suggestion-received', {
    detail: {
      suggestion: '根据市场分析，这3只基金表现优异，建议重点关注',
      command: 'highlight',
      confidence: 0.92,
      fund_id: ['fund_001', 'fund_003', 'fund_005'],
      source: 'market_analysis'
    }
  });
  
  window.dispatchEvent(event);
}

// 测试3: 仅显示弹窗（bubble模式）
function testBubbleOnly() {
  console.log('🎯 测试3: 仅显示弹窗');
  console.log('命令: testBubbleOnly()');
  console.log('效果: 只显示AI建议弹窗，不高亮任何基金\n');
  
  const event = new CustomEvent('ai-suggestion-received', {
    detail: {
      suggestion: '市场波动较大，建议保持谨慎投资策略',
      command: 'bubble',
      confidence: 0.78,
      fund_id: null,
      source: 'market_warning'
    }
  });
  
  window.dispatchEvent(event);
}

// 测试4: 不做任何反应（null命令）
function testNoAction() {
  console.log('🎯 测试4: 不做任何反应');
  console.log('命令: testNoAction()');
  console.log('效果: 不会显示弹窗，也不会高亮基金\n');
  
  const event = new CustomEvent('ai-suggestion-received', {
    detail: {
      suggestion: '这条建议不触发任何UI反应',
      command: null,
      confidence: 0.65,
      fund_id: null,
      source: 'background_analysis'
    }
  });
  
  window.dispatchEvent(event);
}

// 测试5: 清除当前高亮
function clearHighlight() {
  console.log('🧹 清除高亮: clearHighlight()');
  console.log('效果: 立即清除所有基金高亮状态\n');
  
  // 触发清除高亮事件
  const clearEvent = new CustomEvent('clear-fund-highlight');
  window.dispatchEvent(clearEvent);
}

// 测试6: 检查当前状态
function checkCurrentState() {
  console.log('📊 当前状态检查: checkCurrentState()');
  console.log('请在控制台中查看返回的状态信息\n');
  
  // 检查高亮基金ID状态
  if (window.React && window.React.useState) {
    console.log('💡 提示: 高亮状态由React状态管理，无法直接在控制台查看');
  }
  
  // 检查是否有事件监听器
  const aiListenerExists = window.addEventListener.toString().includes('ai-suggestion-received');
  console.log('✅ AI建议事件监听器:', aiListenerExists ? '已注册' : '未找到');
}

// 显示所有测试命令
console.log('📋 可用的测试命令:');
console.log('1. testHighlightSingleFund()  - 高亮单个基金');
console.log('2. testHighlightMultipleFunds() - 高亮多个基金');
console.log('3. testBubbleOnly() - 仅显示弹窗');
console.log('4. testNoAction() - 不做任何反应');
console.log('5. clearHighlight() - 清除高亮');
console.log('6. checkCurrentState() - 检查当前状态\n');

console.log('🚀 快速测试序列:');
console.log('依次执行以下命令来测试完整流程:');
console.log('testHighlightSingleFund() → clearHighlight() → testBubbleOnly() → testNoAction()\n');

// 自动执行快速测试序列（可选，取消注释以启用）
// console.log('🔄 开始自动测试序列...');
// setTimeout(() => testHighlightSingleFund(), 1000);
// setTimeout(() => clearHighlight(), 3000);
// setTimeout(() => testBubbleOnly(), 5000);
// setTimeout(() => testNoAction(), 7000);