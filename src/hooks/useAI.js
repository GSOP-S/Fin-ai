/**
 * AI功能自定义Hook
 * 封装所有AI相关逻辑，替代App.jsx中的复杂函数
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { getPageSuggestion } from '../api/ai';
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
   * @param {string} pageType - 页面类型 (bill/transfer/stock...)
   * @param {object} context - 上下文数据
   * @param {object} configOverrides - 配置覆盖
   */
  const show = useCallback(async (pageType, context = {}, configOverrides = {}) => {
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
      const config = getAIConfig(pageType, { ...options, ...configOverrides });
      
      // 调用API
      const result = await getPageSuggestion(pageType, context);
      
      if (!result || !result.success) {
        throw new Error(result?.error || 'AI建议获取失败');
      }
      
      // 格式化建议文本
      const text = formatAISuggestion(result.data, pageType);
      
      // 更新状态
      setSuggestion(result.data);
      setSuggestionText(text);
      
      // 自动显示
      if (config.autoShow) {
        setIsVisible(true);
        
        // 自动隐藏
        if (config.autoHideDelay > 0) {
          hideTimerRef.current = setTimeout(() => {
            setIsVisible(false);
          }, config.autoHideDelay);
        }
      }
      
      // 语音播报
      if (config.speakEnabled && text) {
        speak(text);
      }
      
      return result.data;
    } catch (err) {
      console.error('AI建议获取失败:', err);
      setError(err.message);
      
      // 显示错误提示
      setSuggestionText('抱歉，AI助手暂时不可用，请稍后再试。');
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

