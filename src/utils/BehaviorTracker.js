/**
 * 用户行为追踪核心类
 * 负责：事件采集、队列管理、批量上报、失败重试、心跳机制
 */

import TrackingConfig, { EventTypes, RealtimeEvents, SensitiveConfig } from '../config/tracking.config';

class BehaviorTracker {
  constructor() {
    // 内存队列
    this.queue = [];
    
    // 会话管理
    this.sessionId = this.initSession();
    this.userId = null;
    this.lastActivityTime = Date.now();
    
    // 定时器
    this.uploadTimer = null;
    this.heartbeatTimer = null;
    
    // 重试队列
    this.retryQueue = [];
    
    // 初始化
    this.init();
  }
  
  // 单例模式
  static instance = null;
  
  /**
   * 获取单例实例
   */
  static getInstance() {
    if (!BehaviorTracker.instance) {
      BehaviorTracker.instance = new BehaviorTracker();
    }
    return BehaviorTracker.instance;
  }
  
  /**
   * 初始化追踪器
   */
  static init(userId) {
    const tracker = BehaviorTracker.getInstance();
    if (userId) {
      tracker.setUserId(userId);
    }
    return tracker;
  }
  
  /**
   * 初始化追踪器
   */
  init() {
    if (!TrackingConfig.enabled) {
      console.warn('[BehaviorTracker] 追踪已禁用');
      return;
    }
    
    // 启动批量上报定时器
    this.startUploadTimer();
    
    // 启动心跳定时器
    this.startHeartbeat();
    
    // 从本地存储恢复失败的日志
    this.recoverFromLocalStorage();
    
    // 监听页面卸载，上报剩余日志
    window.addEventListener('beforeunload', () => {
      this.flush();
    });
    
    // 监听页面可见性变化
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.track(EventTypes.PAGE_BLUR, {});
      } else {
        this.track(EventTypes.PAGE_FOCUS, {});
      }
    });
    
    this.log('初始化完成', { sessionId: this.sessionId });
  }
  
  /**
   * 初始化或恢复会话
   */
  initSession() {
    const sessionKey = 'fin_ai_session_id';
    const lastActivityKey = 'fin_ai_last_activity';
    
    const lastActivity = localStorage.getItem(lastActivityKey);
    const now = Date.now();
    
    // 检查会话是否过期
    if (lastActivity && (now - parseInt(lastActivity)) < TrackingConfig.session.timeout) {
      // 恢复旧会话
      const sessionId = localStorage.getItem(sessionKey);
      if (sessionId) {
        return sessionId;
      }
    }
    
    // 创建新会话
    const newSessionId = this.generateSessionId();
    localStorage.setItem(sessionKey, newSessionId);
    return newSessionId;
  }
  
  /**
   * 设置用户ID
   */
  setUserId(userId) {
    this.userId = userId;
    this.log('设置用户ID', { userId });
  }
  
  /**
   * 核心方法：记录事件
   * @param {string} eventType - 事件类型
   * @param {object} eventData - 事件数据
   * @param {object} options - 可选配置（如强制实时上报）
   */
  track(eventType, eventData = {}, options = {}) {
    if (!TrackingConfig.enabled) return;
    
    // 采样检查
    if (Math.random() > TrackingConfig.samplingRate) {
      return;
    }
    
    // 更新最后活动时间
    this.updateActivity();
    
    // 规范化事件
    const event = this.normalizeEvent(eventType, eventData);
    
    // 敏感信息处理
    const sanitizedEvent = this.sanitizeEvent(event);
    
    // 判断是否需要实时上报
    const isRealtime = options.realtime || RealtimeEvents.includes(eventType);
    
    if (isRealtime) {
      // 实时上报
      this.uploadImmediate([sanitizedEvent]);
    } else {
      // 加入批量队列
      this.addToQueue(sanitizedEvent);
    }
    
    this.log('事件已追踪', { eventType, isRealtime });
  }
  
  /**
   * 事件规范化
   */
  normalizeEvent(type, data) {
    return {
      // 核心字段
      event_id: this.generateUUID(),
      event_type: type,
      timestamp: Date.now(),
      
      // 用户信息
      user_id: this.userId,
      session_id: this.sessionId,
      
      // 页面信息
      page: this.getCurrentPage(),
      page_url: window.location.pathname,
      referrer: document.referrer || null,
      
      // 事件数据
      ...data,
      
      // 上下文信息
      context: this.getContext(),
    };
  }
  
  /**
   * 敏感信息处理
   */
  sanitizeEvent(event) {
    const sanitized = { ...event };
    
    // 检查所有字段
    Object.keys(sanitized).forEach(key => {
      // 完全不采集的字段
      if (SensitiveConfig.blocked.includes(key)) {
        delete sanitized[key];
        return;
      }
      
      // 需要脱敏的字段
      if (SensitiveConfig.masked.includes(key)) {
        sanitized[key] = SensitiveConfig.maskRule(sanitized[key]);
      }
    });
    
    return sanitized;
  }
  
  /**
   * 添加到队列
   */
  addToQueue(event) {
    this.queue.push(event);
    
    // 队列满了立即上报
    if (this.queue.length >= TrackingConfig.batchUpload.maxQueueSize) {
      this.flush();
    }
  }
  
  /**
   * 启动批量上报定时器
   */
  startUploadTimer() {
    if (this.uploadTimer) {
      clearInterval(this.uploadTimer);
    }
    
    this.uploadTimer = setInterval(() => {
      this.flush();
    }, TrackingConfig.batchUpload.uploadInterval);
  }
  
  /**
   * 启动心跳定时器
   */
  startHeartbeat() {
    if (!TrackingConfig.heartbeat.enabled) return;
    
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }
    
    this.heartbeatTimer = setInterval(() => {
      // 检查是否有活动
      const now = Date.now();
      const idleTime = now - this.lastActivityTime;
      
      // 如果10秒内无操作，发送心跳
      if (idleTime >= TrackingConfig.heartbeat.interval - 100) {
        this.track(EventTypes.HEARTBEAT, {
          idle_time: idleTime,
        });
      }
    }, TrackingConfig.heartbeat.interval);
  }
  
  /**
   * 更新最后活动时间
   */
  updateActivity() {
    this.lastActivityTime = Date.now();
    localStorage.setItem('fin_ai_last_activity', String(this.lastActivityTime));
  }
  
  /**
   * 立即上报（实时事件）
   */
  async uploadImmediate(events) {
    try {
      await this.sendToServer(events);
    } catch (error) {
      console.error('[BehaviorTracker] 实时上报失败', error);
      // 失败后加入批量队列
      this.queue.push(...events);
    }
  }
  
  /**
   * 批量上报（flush）
   */
  async flush() {
    if (this.queue.length === 0) return;
    
    const events = this.queue.splice(0, TrackingConfig.batchUpload.maxQueueSize);
    
    try {
      await this.sendToServer(events);
      this.log('批量上报成功', { count: events.length });
    } catch (error) {
      console.error('[BehaviorTracker] 批量上报失败', error);
      // 失败重新入队
      this.handleUploadFailure(events);
    }
  }
  
  /**
   * 发送到服务器
   */
  async sendToServer(events, retryCount = 0) {
    const response = await fetch(`${window.location.origin}/api/behavior/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        events,
        meta: {
          client_time: Date.now(),
          version: '1.0.0',
        }
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const result = await response.json();
    
    // 如果服务器返回了AI建议，触发弹窗显示
    if (result.success && result.data && result.data.ai_suggestion) {
      this.handleAISuggestion(result.data.ai_suggestion);
    }
    
    return result;
  }

  // 处理AI建议
  handleAISuggestion(aiSuggestion) {
    // 检查是否需要显示弹窗
    const command = aiSuggestion.command || '';
    if (command === 'bubble' || command === 'yes') {
      // 触发自定义事件，通知应用显示AI建议弹窗
      const event = new CustomEvent('ai-suggestion-received', {
        detail: {
          suggestion: aiSuggestion.suggestion || '',
          command: command,
          confidence: aiSuggestion.confidence || 0,
        }
      });
      window.dispatchEvent(event);
      console.log('[BehaviorTracker] 已触发AI建议弹窗事件');
    }
  }
  
  /**
   * 处理上报失败
   */
  handleUploadFailure(events) {
    // 保存到本地存储
    this.saveToLocalStorage(events);
    
    // 加入重试队列
    this.retryQueue.push({
      events,
      retryCount: 0,
      nextRetry: Date.now() + TrackingConfig.batchUpload.retryDelay,
    });
    
    // 启动重试
    this.scheduleRetry();
  }
  
  /**
   * 调度重试
   */
  scheduleRetry() {
    setTimeout(() => {
      this.processRetryQueue();
    }, TrackingConfig.batchUpload.retryDelay);
  }
  
  /**
   * 处理重试队列
   */
  async processRetryQueue() {
    const now = Date.now();
    const pending = [];
    
    for (const item of this.retryQueue) {
      if (now >= item.nextRetry && item.retryCount < TrackingConfig.batchUpload.retryTimes) {
        try {
          await this.sendToServer(item.events);
          this.log('重试上报成功', { retryCount: item.retryCount });
        } catch (error) {
          // 重试失败，增加计数
          item.retryCount++;
          item.nextRetry = now + TrackingConfig.batchUpload.retryDelay * (item.retryCount + 1);
          pending.push(item);
        }
      } else if (item.retryCount < TrackingConfig.batchUpload.retryTimes) {
        pending.push(item);
      }
    }
    
    this.retryQueue = pending;
    
    // 如果还有待重试的，继续调度
    if (this.retryQueue.length > 0) {
      this.scheduleRetry();
    }
  }
  
  /**
   * 保存到本地存储
   */
  saveToLocalStorage(events) {
    try {
      const stored = JSON.parse(localStorage.getItem(TrackingConfig.localStorage.key) || '[]');
      const merged = [...stored, ...events].slice(-TrackingConfig.localStorage.maxSize);
      localStorage.setItem(TrackingConfig.localStorage.key, JSON.stringify(merged));
    } catch (error) {
      console.error('[BehaviorTracker] 保存到本地存储失败', error);
    }
  }
  
  /**
   * 从本地存储恢复
   */
  recoverFromLocalStorage() {
    try {
      const stored = localStorage.getItem(TrackingConfig.localStorage.key);
      if (stored) {
        const events = JSON.parse(stored);
        if (events.length > 0) {
          this.log('从本地存储恢复日志', { count: events.length });
          this.queue.push(...events);
          localStorage.removeItem(TrackingConfig.localStorage.key);
        }
      }
    } catch (error) {
      console.error('[BehaviorTracker] 从本地存储恢复失败', error);
    }
  }
  
  /**
   * 获取当前页面
   */
  getCurrentPage() {
    const path = window.location.pathname;
    if (path === '/' || path === '/index.html') return 'home';
    return path.replace(/^\//, '').replace(/\/$/, '') || 'home';
  }
  
  /**
   * 获取上下文信息
   */
  getContext() {
    return {
      screen_width: window.screen.width,
      screen_height: window.screen.height,
      viewport_width: window.innerWidth,
      viewport_height: window.innerHeight,
      user_agent: navigator.userAgent,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      platform: navigator.platform,
    };
  }
  
  /**
   * 生成UUID
   */
  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  /**
   * 生成会话ID
   */
  generateSessionId() {
    return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * 调试日志
   */
  log(message, data = {}) {
    if (TrackingConfig.debug) {
      console.log(`[BehaviorTracker] ${message}`, data);
    }
  }
  
  /**
   * 销毁追踪器
   */
  destroy() {
    if (this.uploadTimer) {
      clearInterval(this.uploadTimer);
    }
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }
    this.flush();
  }
  
  /**
   * 静态方法：记录事件
   */
  static track(eventType, eventData = {}, options = {}) {
    const tracker = BehaviorTracker.getInstance();
    return tracker.track(eventType, eventData, options);
  }
  
  /**
   * 静态方法：立即上报所有事件
   */
  static flush() {
    const tracker = BehaviorTracker.getInstance();
    return tracker.flush();
  }
  
  /**
   * 静态方法：设置用户ID
   */
  static setUserId(userId) {
    const tracker = BehaviorTracker.getInstance();
    return tracker.setUserId(userId);
  }
}

// 导出单例实例
export const behaviorTracker = BehaviorTracker.getInstance();

// 导出类
export { BehaviorTracker };

export default BehaviorTracker;

