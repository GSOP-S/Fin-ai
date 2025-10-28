/**
 * AI功能配置文件
 * 定义不同页面的AI建议配置
 */

// 不同页面的AI配置
export const AI_PAGE_CONFIGS = {
  home: {
    autoShow: false,
    autoHideDelay: 20000,
    speakEnabled: false,
    bubbleTitle: '🏠 智能助手',
  },
  
  bill: {
    autoShow: true,
    autoHideDelay: 30000,  // 账单分析需要看久一点
    speakEnabled: true,
    bubbleTitle: '📊 账单分析',
  },
  
  transfer: {
    autoShow: true,
    autoHideDelay: 20000,
    speakEnabled: true,
    bubbleTitle: '💸 转账建议',
  },
  
  stock: {
    autoShow: false,  // 股票建议不自动弹出
    autoHideDelay: 15000,
    speakEnabled: false,
    bubbleTitle: '📈 投资建议',
  },
  
  fund: {
    autoShow: false,
    autoHideDelay: 15000,
    speakEnabled: false,
    bubbleTitle: '💰 基金建议',
  },
};

// 默认配置
export const DEFAULT_AI_CONFIG = {
  autoShow: true,
  autoHideDelay: 20000,
  speakEnabled: true,
  bubbleTitle: '💡 智能建议',
};

/**
 * 获取页面AI配置
 * @param {string} pageType - 页面类型
 * @param {object} overrides - 覆盖配置
 * @returns {object} 合并后的配置
 */
export function getAIConfig(pageType, overrides = {}) {
  const baseConfig = AI_PAGE_CONFIGS[pageType] || DEFAULT_AI_CONFIG;
  return { ...baseConfig, ...overrides };
}

// 缓存配置
export const AI_CACHE_CONFIG = {
  enabled: true,
  ttl: 5 * 60 * 1000,  // 5分钟
};

// 语音播报配置
export const AI_SPEECH_CONFIG = {
  rate: 1.0,      // 语速
  pitch: 1.0,     // 音调
  volume: 1.0,    // 音量
  lang: 'zh-CN',  // 语言
};

