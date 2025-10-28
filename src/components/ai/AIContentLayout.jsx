/**
 * AI内容布局组件
 * 统一的AI内容展示布局
 */

import React from 'react';
import './AIContentLayout.css';

export const AIContentLayout = ({ page, title, children }) => {
  return (
    <div className={`ai-content ${page}-ai`}>
      <h3 className="ai-content-title">{title}</h3>
      <div className="ai-content-body">
        {children}
      </div>
    </div>
  );
};

export const AISection = ({ title, children, highlight = false }) => {
  return (
    <div className={`ai-section ${highlight ? 'ai-section-highlight' : ''}`}>
      {title && <h4 className="ai-section-title">{title}</h4>}
      <div className="ai-section-content">
        {children}
      </div>
    </div>
  );
};

export default AIContentLayout;

