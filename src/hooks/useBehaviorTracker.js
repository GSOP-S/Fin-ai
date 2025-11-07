/**
 * 行为追踪 Hook
 * 提供track方法供组件使用
 */

import { useEffect, useRef } from 'react';
import { getTracker } from '../utils/BehaviorTracker';

export const useBehaviorTracker = () => {
  const trackerRef = useRef(null);
  
  useEffect(() => {
    // 获取tracker单例
    trackerRef.current = getTracker();
  }, []);
  
  // 返回track方法
  return {
    track: (eventType, eventData, options) => {
      if (trackerRef.current) {
        trackerRef.current.track(eventType, eventData, options);
      }
    },
    setUserId: (userId) => {
      if (trackerRef.current) {
        trackerRef.current.setUserId(userId);
      }
    },
  };
};

export default useBehaviorTracker;

