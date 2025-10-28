/**
 * AI响应格式化工具
 * 统一处理不同类型的AI响应数据
 */

/**
 * 格式化AI建议文本
 * @param {object|string} result - AI响应结果
 * @param {string} pageType - 页面类型
 * @returns {string} 格式化后的文本
 */
export function formatAISuggestion(result, pageType = 'default') {
  // 如果是字符串，直接返回
  if (typeof result === 'string') {
    return result;
  }
  
  // 如果有suggestion字段，优先使用
  if (result.suggestion) {
    return result.suggestion;
  }
  
  // 如果有analysis字段
  if (result.analysis) {
    return typeof result.analysis === 'string' 
      ? result.analysis 
      : formatAnalysis(result.analysis);
  }
  
  // 根据页面类型格式化
  const formatters = {
    bill: formatBillSuggestion,
    transfer: formatTransferSuggestion,
    stock: formatStockSuggestion,
    fund: formatFundSuggestion,
    default: formatDefaultSuggestion,
  };
  
  const formatter = formatters[pageType] || formatters.default;
  return formatter(result);
}

/**
 * 格式化账单建议
 */
function formatBillSuggestion(result) {
  let text = '';
  
  // 财务概览
  if (result.summary) {
    text += '📊 财务概览\n';
    if (result.summary.totalIncome) {
      text += `总收入：¥${result.summary.totalIncome.toFixed(2)}\n`;
    }
    if (result.summary.totalExpense) {
      text += `总支出：¥${result.summary.totalExpense.toFixed(2)}\n`;
    }
    if (result.summary.savingRate) {
      text += `储蓄率：${result.summary.savingRate}%\n`;
    }
    text += '\n';
  }
  
  // 优化建议
  if (result.suggestions && result.suggestions.length > 0) {
    text += '💡 优化建议\n';
    result.suggestions.slice(0, 5).forEach((suggestion, index) => {
      text += `${index + 1}. ${suggestion}\n`;
    });
  }
  
  return text || '暂无账单分析';
}

/**
 * 格式化转账建议
 */
function formatTransferSuggestion(result) {
  let text = result.suggestion || '';
  
  if (result.arrivalTime) {
    text += `\n\n⏰ 到账时间：${result.arrivalTime}`;
  }
  
  if (result.feeSuggestion) {
    text += `\n💰 手续费：${result.feeSuggestion}`;
  }
  
  if (result.riskLevel === 'high') {
    text += '\n\n⚠️ 风险提示：首次转账或大额转账，请仔细核对信息';
  }
  
  return text || '暂无转账建议';
}

/**
 * 格式化股票建议
 */
function formatStockSuggestion(result) {
  if (result.stock) {
    const { name, code, changePercent } = result.stock;
    return result.suggestion || `${name}(${code}) 当前涨跌：${changePercent}`;
  }
  return result.suggestion || '暂无股票建议';
}

/**
 * 格式化基金建议
 */
function formatFundSuggestion(result) {
  if (result.fund) {
    const { name, code, changePercent } = result.fund;
    return result.suggestion || `${name}(${code}) 当前涨跌：${changePercent}`;
  }
  return result.suggestion || '暂无基金建议';
}

/**
 * 格式化默认建议
 */
function formatDefaultSuggestion(result) {
  // 尝试从各种可能的字段提取文本
  return result.suggestion 
    || result.message 
    || result.text 
    || result.content 
    || '暂无相关建议';
}

/**
 * 格式化分析数据
 */
function formatAnalysis(analysis) {
  if (typeof analysis === 'string') {
    return analysis;
  }
  
  // 如果是对象，尝试提取有用信息
  const parts = [];
  
  if (analysis.summary) {
    parts.push(analysis.summary);
  }
  
  if (analysis.recommendations && Array.isArray(analysis.recommendations)) {
    parts.push('\n建议：\n' + analysis.recommendations.join('\n'));
  }
  
  return parts.join('\n\n') || '分析结果';
}

/**
 * 提取建议的关键信息（用于简短展示）
 * @param {string} suggestionText - 完整建议文本
 * @param {number} maxLength - 最大长度
 * @returns {string} 摘要文本
 */
export function getSuggestionSummary(suggestionText, maxLength = 100) {
  if (!suggestionText) return '';
  
  // 取第一行或前maxLength个字符
  const firstLine = suggestionText.split('\n')[0];
  if (firstLine.length <= maxLength) {
    return firstLine;
  }
  
  return firstLine.substring(0, maxLength) + '...';
}

