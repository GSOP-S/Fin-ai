/**
 * 页面访问追踪 Hook
 * 自动追踪页面访问、停留时长、焦点变化
 */

import { useEffect, useRef } from 'react';
import { useBehaviorTracker } from './useBehaviorTracker';
import { EventTypes } from '../config/tracking.config';

export const usePageTracking = (pageName, additionalData = {}) => {
  const tracker = useBehaviorTracker();
  const startTimeRef = useRef(Date.now());
  const pageNameRef = useRef(pageName);
  
  useEffect(() => {
    pageNameRef.current = pageName;
    startTimeRef.current = Date.now();
    
    // 页面进入
    tracker.track(EventTypes.PAGE_VIEW, {
      page: pageName,
      referrer: document.referrer || null,
      entry_time: startTimeRef.current,
      ...additionalData,
    });
    
    // 页面离开
    return () => {
      const duration = Date.now() - startTimeRef.current;
      tracker.track(EventTypes.PAGE_LEAVE, {
        page: pageNameRef.current,
        duration: duration,
        leave_time: Date.now(),
      });
    };
  }, [pageName]);
  
  return tracker;
};

export default usePageTracking;

