// src/api/asset.js
import request from './request';

// 基础配置
const DEFAULT_USER_ID = 'UTSZ';

/**
 * 获取投资组合汇总信息
 * @param {number} userId 用户ID，默认为1
 * @returns {Promise} 投资组合汇总数据
 */
export const fetchPortfolioSummary = (userId = DEFAULT_USER_ID) => {
  return request(`/api/portfolio/summary?user_id=${userId}`);
};

/**
 * 获取基金持仓列表
 * @param {number} userId 用户ID，默认为1
 * @returns {Promise} 基金持仓列表
 */
export const fetchFundPositions = (userId = DEFAULT_USER_ID) => {
  return request(`/api/fund-positions?user_id=${userId}`);
};

/**
 * 获取存款和储蓄持仓列表
 * @param {number} userId 用户ID，默认为1
 * @returns {Promise} 存款/储蓄持仓列表
 */
export const fetchDepositPositions = (userId = DEFAULT_USER_ID) => {
  return request(`/api/deposit-positions?user_id=${userId}`);
};

/**
 * 获取所有持仓列表
 * @param {number} userId 用户ID，默认为1
 * @param {string} positionType 持仓类型（fund/deposit/savings），可选
 * @returns {Promise} 持仓列表
 */
export const fetchAllPositions = (userId = DEFAULT_USER_ID, positionType = null) => {
  const params = new URLSearchParams({ user_id: userId });
  if (positionType) {
    params.append('position_type', positionType);
  }
  return request(`/api/all-positions?${params.toString()}`);
};



/**
 * 更新持仓记录
 * @param {number} positionId 持仓记录ID
 * @param {object} data 更新数据 { shares, current_price }
 * @returns {Promise} 更新结果
 */
export const updatePosition = (positionId, data) => {
  return request(`/api/positions/${positionId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
};

/**
 * 创建新的持仓记录
 * @param {object} positionData 持仓数据
 * @returns {Promise} 创建结果
 */
export const createPosition = (positionData) => {
  const requiredFields = ['position_type', 'product_code', 'product_name', 'shares', 'purchase_price', 'purchase_date'];
  
  // 验证必要字段
  const missingFields = requiredFields.filter(field => !positionData[field]);
  if (missingFields.length > 0) {
    throw new Error(`缺少必要字段: ${missingFields.join(', ')}`);
  }
  
  // 设置默认用户ID
  const data = { user_id: DEFAULT_USER_ID, ...positionData };
  
  return request('/api/positions', {
    method: 'POST',
    body: JSON.stringify(data),
  });
};

/**
 * 删除持仓记录（软删除）
 * @param {number} positionId 持仓记录ID
 * @returns {Promise} 删除结果
 */
export const deletePosition = (positionId) => {
  return request(`/api/positions/${positionId}`, {
    method: 'DELETE',
  });
};

/**
 * 批量获取资产数据
 * @param {number} userId 用户ID
 * @returns {Promise} 包含所有资产相关数据的对象
 */
export const fetchAssetData = async (userId = DEFAULT_USER_ID) => {
  try {
    const [portfolioSummary, fundPositions, depositPositions] = await Promise.all([
      fetchPortfolioSummary(userId),
      fetchFundPositions(userId),
      fetchDepositPositions(userId),
    ]);

    return {
      success: true,
      portfolioSummary: portfolioSummary.data || {},
      fundPositions: fundPositions.data || [],
      depositPositions: depositPositions.data || [],
    };
  } catch (error) {
    console.error('获取资产数据失败:', error);
    return {
      success: false,
      error: error.message,
      portfolioSummary: {},
      fundPositions: [],
      depositPositions: [],
    };
  }
};

/**
 * 刷新持仓数据（用于手动刷新）
 * @param {number} userId 用户ID
 * @returns {Promise} 刷新后的资产数据
 */
export const refreshAssetData = async (userId = DEFAULT_USER_ID) => {
  try {
    const assetData = await fetchAssetData(userId);

    return {
      ...assetData,
      lastUpdated: new Date().toISOString(),
    };
  } catch (error) {
    console.error('刷新资产数据失败:', error);
    throw error;
  }
};

/**
 * 获取资产统计数据（用于仪表板等）
 * @param {number} userId 用户ID
 * @returns {Promise} 资产统计信息
 */
export const fetchAssetStatistics = (userId = DEFAULT_USER_ID) => {
  return fetchPortfolioSummary(userId).then(response => {
    const summary = response.data || {};
    const overall = summary.overall || {};
    
    return {
      success: true,
      data: {
        totalValue: overall.total_value || 0,
        totalInvestment: overall.total_investment || 0,
        totalProfitLoss: overall.total_profit_loss || 0,
        profitLossPercent: overall.total_profit_loss_percent || 0,
        positionCount: overall.position_count || 0,
        riskLevel: overall.risk_level || '低风险',
        allocationRatios: overall.allocation_ratios || { fund: 0, deposit: 0, savings: 0 },
      },
    };
  });
};

// 导出缓存相关配置
export const ASSET_CACHE_CONFIG = {
  // 缓存时间配置（毫秒）
  CACHE_DURATION: {
    PORTFOLIO_SUMMARY: 30 * 1000,      // 30秒
    FUND_POSITIONS: 60 * 1000,         // 1分钟
    DEPOSIT_POSITIONS: 60 * 1000,      // 1分钟
  },
  
  // 缓存键前缀
  CACHE_PREFIX: {
    PORTFOLIO_SUMMARY: 'asset_summary_',
    FUND_POSITIONS: 'asset_funds_',
    DEPOSIT_POSITIONS: 'asset_deposits_',
    AI_ANALYSIS: 'asset_ai_',
  },
};

// 资产数据类型验证工具
export const validateAssetData = (data, type) => {
  const validators = {
    fund_position: (item) => {
      const required = ['fund_code', 'fund_name', 'shares', 'current_value'];
      return required.every(field => item.hasOwnProperty(field));
    },
    deposit_position: (item) => {
      const required = ['product_code', 'product_name', 'amount', 'current_value'];
      return required.every(field => item.hasOwnProperty(field));
    },
    portfolio_summary: (summary) => {
      return summary.hasOwnProperty('overall') && summary.overall.hasOwnProperty('total_value');
    },
  };
  
  const validator = validators[type];
  if (!validator) return true;
  
  if (Array.isArray(data)) {
    return data.every(validator);
  } else {
    return validator(data);
  }
};