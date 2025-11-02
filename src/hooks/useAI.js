/**
 * AI功能自定义Hook
 * 封装所有AI相关逻辑，替代App.jsx中的复杂函数
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { generateAISuggestion } from '../api/ai';
import { formatAISuggestion } from '../utils/aiFormatter';
import { getAIConfig, AI_SPEECH_CONFIG } from '../config/ai.config';

/**
 * AI功能Hook
 * @param {object} options - 配置选项
 * @returns {object} AI功能接口
 */
export function useAI(options = {}) {
  // 状态管理
  const [suggestion, setSuggestion] = useState(null);
  const [suggestionText, setSuggestionText] = useState('');
  const [isVisible, setIsVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 定时器引用
  const hideTimerRef = useRef(null);
  const speechRef = useRef(null);
  
  /**
   * 显示AI建议
   * @param {string} pageType - 页面类型 (bill/transfer/fund...)
   * @param {object} context - 上下文数据
   * @param {object} configOverrides - 配置覆盖
   */
  const show = useCallback(async (pageType, context = {}, configOverrides = {}) => {
    console.log(`[AI] 显示建议: pageType=${pageType}, context=`, context);
    
    // 清除之前的定时器
    if (hideTimerRef.current) {
      clearTimeout(hideTimerRef.current);
    }
    
    // 停止之前的语音
    if (speechRef.current) {
      window.speechSynthesis.cancel();
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // 获取配置
      // 获取配置并处理可能的配置错误
      let config;
      try {
        config = getAIConfig(pageType, { ...options, ...configOverrides });
        console.log(`[AI] 配置:`, config);
      } catch (configError) {
        console.error('AI配置获取失败:', configError);
        // 使用默认配置继续
        config = { autoShow: true, autoHideDelay: 5000, speakEnabled: false };
      }
      
      // 调用API
      console.log(`[AI] 调用API: pageType=${pageType}`);
      // 确保用户信息被正确传递
      const apiContext = {
        ...context,
        userId: options.userId || context.userId || null
      };
      const result = await generateAISuggestion(pageType, apiContext);
      console.log(`[AI] API返回结果:`, result);
      
      // 即使AI调用失败，generateAISuggestion已返回备用建议
      
      // 格式化建议文本
      // 为格式化步骤添加错误处理，确保备用建议能正常显示
      let text;
      try {
        text = formatAISuggestion(result, pageType);
        console.log(`[AI] 格式化后的文本:`, text);
      } catch (formatError) {
        console.error('AI建议格式化失败:', formatError);
        // 直接使用备用建议中的文本内容
        text = result.suggestion || result.analysis || '暂无建议';
      }
      
      // 更新状态
      setSuggestion(result);
      setSuggestionText(text);
      
      // 自动显示
      if (config.autoShow) {
        console.log(`[AI] 自动显示建议: ${text}`);
        setIsVisible(true);
        
        // 自动隐藏
        if (config.autoHideDelay > 0) {
          hideTimerRef.current = setTimeout(() => {
            setIsVisible(false);
          }, config.autoHideDelay);
        }
      }
      
      // 语音播报
      // 语音播报添加错误处理
      if (config.speakEnabled && text) {
        try {
          speak(text);
        } catch (speechError) {
          console.error('语音播报调用失败:', speechError);
        }
      }
      
      return result.data;
    } catch (err) {
      console.error('AI建议获取失败:', err);
      setError(err.message);
      
      // 显示错误提示，使用备用建议
      const fallbackSuggestions = {
        home: '欢迎使用智能银行系统！建议您定期查看账户明细，合理规划理财投资。',
        fund: '基金投资有风险，建议根据自身风险承受能力选择合适的基金产品。',
        bill: '建议您定期查看账单明细，合理控制支出，提高储蓄率。',
        transfer: '转账时请仔细核对收款人信息，大额转账建议分批进行。',
        market: '市场有风险，投资需谨慎。建议分散投资，降低风险。',
      };
      
      // 使用页面类型对应的备用建议，如果没有则使用通用建议
      const pageType = err.pageType || 'default';
      const fallbackText = fallbackSuggestions[pageType] || '暂无相关建议，请稍后再试。';
      
      setSuggestionText(fallbackText);
      setIsVisible(true);
      
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [options]);
  
  /**
   * 隐藏建议
   */
  const hide = useCallback(() => {
    setIsVisible(false);
    if (hideTimerRef.current) {
      clearTimeout(hideTimerRef.current);
    }
    if (speechRef.current) {
      window.speechSynthesis.cancel();
    }
  }, []);
  
  /**
   * 语音播报
   * @param {string} text - 要播报的文本
   */
  const speak = useCallback((text) => {
    if (!window.speechSynthesis) {
      console.warn('浏览器不支持语音播报');
      return;
    }
    
    try {
      // 取消之前的播报
      window.speechSynthesis.cancel();
      
      // 创建语音对象
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = AI_SPEECH_CONFIG.rate;
      utterance.pitch = AI_SPEECH_CONFIG.pitch;
      utterance.volume = AI_SPEECH_CONFIG.volume;
      utterance.lang = AI_SPEECH_CONFIG.lang;
      
      speechRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error('语音播报失败:', err);
    }
  }, []);
  
  /**
   * 切换语音播报状态 - 从App.jsx迁移而来
   * @param {string} text - 要播报的文本（可选）
   */
  const toggleSpeech = useCallback((text) => {
    if (!window.speechSynthesis) {
      console.warn('浏览器不支持语音播报');
      return;
    }
    
    // 如果有正在播放的语音，先停止
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      return; // 点击按钮时停止播放，不再继续
    }
    
    // 如果提供了文本，则开始播报
    if (text) {
      try {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.9;
        speechRef.current = utterance;
        window.speechSynthesis.speak(utterance);
      } catch (err) {
        console.error('语音播报失败:', err);
      }
    }
  }, []);
  
  /**
   * 停止语音播报
   */
  const stopSpeaking = useCallback(() => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  }, []);
  
  /**
   * 清理资源
   */
  useEffect(() => {
    return () => {
      if (hideTimerRef.current) {
        clearTimeout(hideTimerRef.current);
      }
      if (speechRef.current) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);
  
  return {
    // 状态
    suggestion,        // 原始建议数据
    suggestionText,    // 格式化后的文本
    isVisible,         // 是否显示
    isLoading,         // 是否加载中
    error,            // 错误信息
    
    // 操作方法
    show,             // 显示建议
    hide,             // 隐藏建议
    speak,            // 语音播报
    toggleSpeech,     // 切换语音播报状态（从App.jsx迁移而来）
    stopSpeaking,     // 停止播报
  };
}

/**
 * AI聊天Hook（用于对话功能）
 */
export function useAIChat() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  
  const sendMessage = useCallback(async (message, context = {}) => {
    // 添加用户消息
    const userMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    
    try {
      const { generateAIResponse } = await import('../api/ai');
      const result = await generateAIResponse(message, context);
      
      // 添加AI回复
      const aiMessage = {
        id: `ai-${Date.now()}`,
        type: 'ai',
        content: result.data || result,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, aiMessage]);
      return aiMessage;
    } catch (error) {
      console.error('AI回复失败:', error);
      const errorMessage = {
        id: `error-${Date.now()}`,
        type: 'ai',
        content: '抱歉，我遇到了一些问题，请稍后再试。',
        timestamp: new Date().toISOString(),
        error: true,
      };
      setMessages(prev => [...prev, errorMessage]);
      return errorMessage;
    } finally {
      setIsTyping(false);
    }
  }, []);
  
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);
  
  return {
    messages,
    isTyping,
    sendMessage,
    clearMessages,
  };
}

