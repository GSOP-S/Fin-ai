/**
 * 点击追踪 Hook
 * 提供便捷的点击事件追踪方法
 */

import { useCallback } from 'react';
import { useBehaviorTracker } from './useBehaviorTracker';
import { EventTypes } from '../config/tracking.config';

export const useClickTracking = () => {
  const tracker = useBehaviorTracker();
  
  /**
   * 追踪点击事件
   * @param {string} elementId - 元素ID
   * @param {string} elementText - 元素文本
   * @param {object} businessContext - 业务上下文
   */
  const trackClick = useCallback((elementId, elementText, businessContext = {}) => {
    tracker.track(EventTypes.CLICK, {
      element_id: elementId,
      element_text: elementText,
      ...businessContext,
    });
  }, [tracker]);
  
  /**
   * 创建带追踪的点击处理器
   * @param {string} elementId - 元素ID
   * @param {Function} onClick - 原始点击处理器
   * @param {object} trackingData - 追踪数据
   */
  const withTracking = useCallback((elementId, onClick, trackingData = {}) => {
    return (e) => {
      // 先追踪
      tracker.track(EventTypes.CLICK, {
        element_id: elementId,
        element_type: e.target.tagName?.toLowerCase(),
        element_text: e.target.textContent?.trim().slice(0, 50),
        ...trackingData,
      });
      
      // 再执行原处理器
      if (onClick) {
        onClick(e);
      }
    };
  }, [tracker]);
  
  return {
    trackClick,
    withTracking,
    tracker,
  };
};

export default useClickTracking;

