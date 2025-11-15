/**
 * 用户行为追踪配置
 * 定义事件类型、采集策略、敏感信息处理等
 */

// ===== 事件类型定义 =====
export const EventTypes = {
  // 页面级事件
  PAGE_VIEW: 'page_view',           // 页面访问
  PAGE_LEAVE: 'page_leave',         // 页面离开
  PAGE_FOCUS: 'page_focus',         // 页面获得焦点
  PAGE_BLUR: 'page_blur',           // 页面失去焦点
  HEARTBEAT: 'heartbeat',           // 心跳（10s无操作）
  
  // 通用交互事件
  CLICK: 'click',                   // 点击
  INPUT: 'input',                   // 输入
  SCROLL: 'scroll',                 // 滚动
  
  // 基金相关事件（重点追踪）
  FUND_SEARCH: 'fund_search',       // 搜索基金
  FUND_VIEW: 'fund_view',           // 查看基金详情
  FUND_FILTER: 'fund_filter',       // 筛选基金类型
  FUND_SORT: 'fund_sort',           // 基金排序
  
  // 资讯相关事件（重点追踪）
  NEWS_SEARCH: 'news_search',       // 搜索资讯
  NEWS_READ: 'news_read',           // 阅读资讯
  NEWS_CATEGORY: 'news_category',   // 切换分类
  
  // 转账相关事件
  TRANSFER_START: 'transfer_start',     // 开始转账
  TRANSFER_INPUT: 'transfer_input',     // 输入金额
  TRANSFER_SELECT: 'transfer_select',   // 选择收款人
  TRANSFER_SUBMIT: 'transfer_submit',   // 提交转账
  
  // 账单相关事件
  BILL_VIEW: 'bill_view',           // 查看账单
  BILL_FILTER: 'bill_filter',       // 筛选账单
  
  // AI交互事件
  AI_OPEN: 'ai_open',               // 打开AI助手
  AI_MESSAGE: 'ai_message',         // 发送AI消息
  AI_SUGGESTION: 'ai_suggestion',   // AI建议
  
  // 手动请求分析事件（触发后端智能分析）
  REQUEST_BILL_ANALYSIS: 'request_bill_analysis',       // 请求账单分析
  REQUEST_TRANSFER_ANALYSIS: 'request_transfer_analysis', // 请求转账分析
};

// ===== 实时上报事件（关键业务操作） =====
export const RealtimeEvents = [
  EventTypes.TRANSFER_SUBMIT,       // 转账提交
  EventTypes.FUND_VIEW,             // 查看基金详情
  EventTypes.NEWS_READ,             // 阅读资讯
  EventTypes.AI_MESSAGE,            // AI交互
  EventTypes.REQUEST_BILL_ANALYSIS,     // 请求账单分析（实时）
  EventTypes.REQUEST_TRANSFER_ANALYSIS, // 请求转账分析（实时）
];

// ===== 敏感字段配置 =====
export const SensitiveConfig = {
  // 完全不采集的字段
  blocked: ['password', 'pwd', 'cvv', 'pin'],
  
  // 需要脱敏的字段
  masked: ['cardNumber', 'card_number', 'bankCard', 'idCard'],
  
  // 脱敏规则：保留前4位和后4位
  maskRule: (value) => {
    if (!value || value.length < 8) return '****';
    const str = String(value);
    return str.slice(0, 4) + '****' + str.slice(-4);
  },
};

// ===== 追踪配置 =====
export const TrackingConfig = {
  // 是否启用追踪
  enabled: true,
  
  // 是否在开发环境输出调试信息
  debug: process.env.NODE_ENV === 'development',
  
  // 后端API地址
  apiEndpoint: '/api/behavior/track',
  
  // 批量上报配置
  batchUpload: {
    maxQueueSize: 50,          // 队列最大50条自动上报
    uploadInterval: 5000,      // 5秒批量上报一次
    retryTimes: 3,             // 失败重试3次
    retryDelay: 2000,          // 重试间隔2秒
  },
  
  // 心跳配置（10s无操作上报）
  heartbeat: {
    interval: 10000,           // 10秒心跳
    enabled: true,
  },
  
  // 会话配置
  session: {
    timeout: 30 * 60 * 1000,   // 30分钟无操作视为新会话
  },
  
  // 采样率（100%采集）
  samplingRate: 1.0,
  
  // 本地存储配置（失败重试用）
  localStorage: {
    key: 'fin_ai_tracking_queue',
    maxSize: 200,              // 最多缓存200条
  },
  
  // 需要追踪的页面
  trackedPages: ['home', 'account', 'transfer', 'financing', 'news'],
};

// ===== 业务上下文提取器（可选） =====
export const ContextExtractors = {
  // 基金页面上下文
  financing: () => ({
    current_tab: window.financingTab || 'funds',
  }),
  
  // 转账页面上下文
  transfer: () => ({
    // 从页面DOM提取上下文信息
  }),
};

export default TrackingConfig;

