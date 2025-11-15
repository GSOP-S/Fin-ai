# AI弹窗控制逻辑完整指南

## 📊 系统架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                       触发源（3种）                          │
├─────────────────────────────────────────────────────────────┤
│  1. 页面自动触发 → App.jsx:triggerPageAISuggestion()       │
│  2. 用户操作触发 → 组件内调用 ai.show()                      │
│  3. 行为追踪触发 → BehaviorTracker → 后端分析 → 弹窗 ⭐新  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  控制中心：useAI Hook                        │
├─────────────────────────────────────────────────────────────┤
│  • ai.show(pageType, context, config)                       │
│  • ai.hide()                                                 │
│  • ai.analyzeAndShow(userId)  ← 新增（行为分析）            │
│  • 状态：isVisible, suggestionText                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              配置层：ai.config.js                            │
├─────────────────────────────────────────────────────────────┤
│  每个页面的配置：                                            │
│  • autoShow: 是否自动显示                                    │
│  • autoHideDelay: 延迟隐藏时间（ms）                         │
│  • speakEnabled: 是否语音播报                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           显示层：AISuggestionBubble组件                     │
├─────────────────────────────────────────────────────────────┤
│  • 根据 ai.isVisible 决定是否渲染                           │
│  • 显示 ai.suggestionText 内容                              │
│  • 提供关闭、语音、对话按钮                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 核心控制字段：`command`

### **command字段的作用**

`command` 是后端返回的**指令字段**，决定前端如何处理AI建议。

### **可选值及含义：**

| command值 | 含义 | 前端行为 | 使用场景 |
|-----------|------|---------|---------|
| `"yes"` | 显示弹窗 | 立即显示AI建议气泡 | 有价值的建议 |
| `"bubble"` | 显示弹窗 | 同"yes"，显示气泡 | 通用建议 |
| `"highlight"` | 高亮显示 | 高亮特定元素（如基金） | 推荐特定产品 |
| `"no"` | 不显示 | 不显示任何提示 | 无建议或建议价值低 |
| `"silent"` | 静默记录 | 记录但不打扰用户 | 低优先级信息 |

### **command设置位置：**

**A. 后端设置（推荐）**
```python
# services/mock.py 或 AI服务中
def analyze_user_logs(user_id):
    # 分析用户行为
    behavior_stats = get_user_behavior_stats(user_id)
    
    # 根据分析结果决定是否弹窗
    if behavior_stats['fund_view_count'] > 5:
        return {
            "command": "yes",  # 显示弹窗
            "suggestion": "您最近频繁查看基金，推荐以下产品...",
            "confidence": 0.85
        }
    else:
        return {
            "command": "no",  # 不显示
            "suggestion": "",
            "confidence": 0.0
        }
```

**B. 前端设置**
```javascript
// 手动调用时可以覆盖
ai.show('home', {}, { 
  autoShow: true,      // 强制显示
  autoHideDelay: 0     // 不自动隐藏
});
```

---

## 🎯 完整流程详解

### **流程1：页面自动触发弹窗**

```javascript
// ===== 步骤1：用户进入页面 =====
用户访问 → HomePage组件加载

// ===== 步骤2：App.jsx自动触发 =====
// App.jsx:52-56
const handleLogin = (userData) => {
  setUser(userData);
  setTimeout(() => {
    triggerPageAISuggestion('home');  // 登录后触发
  }, 1000);
};

// ===== 步骤3：调用AI =====
// App.jsx:219-244
const triggerPageAISuggestion = async (page) => {
  if (!user) return;
  
  switch(page) {
    case 'home':
      ai.show('home', { userId: user.id }, {
        autoShow: true,        // ← 配置1：自动显示
        autoHideDelay: 8000,   // ← 配置2：8秒后隐藏
        speakEnabled: false    // ← 配置3：不语音
      });
      break;
    // ...
  }
};

// ===== 步骤4：useAI.show()处理 =====
// src/hooks/useAI.js:62-251
const show = async (pageType, context, configOverrides) => {
  // 4.1 获取配置
  const config = getAIConfig(pageType, configOverrides);
  
  // 4.2 调用后端API
  const result = await generateAISuggestion(pageType, context);
  
  // 4.3 后端返回数据
  // {
  //   command: "yes",  ← 关键！决定是否显示
  //   suggestion: "欢迎回来！您今日收益+12.35元",
  //   confidence: 0.9
  // }
  
  // 4.4 检查command
  if (result.command === 'yes' || result.command === 'bubble') {
    // 更新状态
    setSuggestion(result);
    setSuggestionText(result.suggestion);
    
    // 4.5 根据配置决定是否自动显示
    if (config.autoShow) {
      setIsVisible(true);  // ← 关键！设置为true后弹窗显示
      
      // 4.6 设置自动隐藏定时器
      if (config.autoHideDelay > 0) {
        hideTimerRef.current = setTimeout(() => {
          setIsVisible(false);  // ← 自动隐藏
        }, config.autoHideDelay);
      }
    }
    
    // 4.7 语音播报（如果启用）
    if (config.speakEnabled) {
      speak(result.suggestion);
    }
  }
};

// ===== 步骤5：AISuggestionBubble渲染 =====
// src/components/ai/AISuggestionBubble.jsx:6-8
if (!ai || !ai.isVisible) {
  return null;  // ← isVisible=false时，组件不渲染
}

// isVisible=true时，渲染弹窗
return (
  <div className="ai-suggestion-bubble">
    {ai.suggestionText}  // ← 显示建议文本
  </div>
);
```

**总结：**
```
用户登录 
  → triggerPageAISuggestion('home')
    → ai.show('home', {...}, {autoShow:true})
      → 后端返回 {command: 'yes', suggestion: '...'}
        → setIsVisible(true)
          → AISuggestionBubble渲染
            → 8秒后自动隐藏
```

---

### **流程2：用户操作触发弹窗（点击基金）**

```javascript
// ===== 步骤1：用户点击基金 =====
<div onClick={() => handleFundClick(fund)}>基金卡片</div>

// ===== 步骤2：FundList.jsx处理 =====
const handleFundClick = (fund) => {
  // 2.1 行为追踪（实时上报）
  tracker.track(EventTypes.FUND_VIEW, {
    fund_code: fund.code,
    fund_name: fund.name,
    // ...
  }, { realtime: true });  // ← 立即上报
  
  // 2.2 调用父组件回调
  if (onSelectFund) {
    onSelectFund(fund);
  }
};

// ===== 步骤3：App.jsx处理 =====
// App.jsx:59-64
const handleSelectFund = async (fund) => {
  setSelectedFund(fund);
  
  // 调用基金建议显示函数
  showFundSuggestion(fund, ai);  // ← 这里触发弹窗
};

// ===== 步骤4：fund.js中的显示逻辑 =====
// src/api/fund.js
export const showFundSuggestion = (fund, ai) => {
  ai.show('fund', {
    fundData: {
      fundCode: fund.code,
      fundName: fund.name,
      // ...
    }
  }, {
    autoShow: false,  // ← 基金建议默认不自动显示！
    autoHideDelay: 15000,
    speakEnabled: false
  });
};

// ⚠️ 注意：基金页面 autoShow: false
// 所以即使后端返回 command: 'yes'，也不会自动弹窗
// 除非在配置中覆盖为 autoShow: true
```

**总结：**
```
点击基金
  → handleFundClick(fund)
    → onSelectFund(fund)
      → showFundSuggestion(fund, ai)
        → ai.show('fund', {...}, {autoShow: false})
          → 后端返回建议
            → ❌ 不显示（因为autoShow: false）
```

---

### **流程3：行为追踪智能弹窗** ⭐ 核心新功能

这是**最智能**的触发方式，基于用户行为自动判断！

```javascript
// ===== 完整流程图 =====

用户操作（点击、浏览、搜索等）
    │
    ▼
前端：BehaviorTracker.track()
    │ 收集行为数据
    ▼
批量上报/实时上报
    │ POST /api/behavior/track
    ▼
后端：behavior_controller.py
    │ 接收日志
    ▼
存入数据库：user_behavior_logs
    │
    ▼
后端：分析用户日志
    │ from services.mock import analyze_user_logs
    │ ai_suggestion = analyze_user_logs(user_id)
    ▼
后端分析逻辑（关键！）
    │
    ├─ 如果用户查看基金5次以上
    │    → command: "yes"
    │    → suggestion: "推荐购买XXX基金"
    │
    ├─ 如果用户停留时间>5分钟
    │    → command: "bubble"
    │    → suggestion: "需要帮助吗？"
    │
    ├─ 如果用户行为正常
    │    → command: "no"
    │    → 不弹窗
    │
    └─ 如果发现异常行为
         → command: "highlight"
         → 高亮显示风险提示
    ▼
返回响应（包含AI建议）
    │ {
    │   success: true,
    │   data: {
    │     inserted: 12,
    │     ai_suggestion: {
    │       command: "yes",  ← 关键字段！
    │       suggestion: "...",
    │       confidence: 0.85
    │     }
    │   }
    │ }
    ▼
前端：BehaviorTracker.sendToServer()
    │ 接收响应
    ▼
前端：handleAISuggestion()  ← 关键处理逻辑！
    │ if (command === 'bubble' || command === 'yes') {
    │   触发CustomEvent
    │ }
    ▼
触发自定义事件：ai-suggestion-received
    │ window.dispatchEvent(new CustomEvent(...))
    ▼
（需要在App.jsx中监听此事件）← 当前缺失！
    │ useEffect(() => {
    │   window.addEventListener('ai-suggestion-received', handler);
    │ }, []);
    ▼
调用：ai.show()显示弹窗
    │ ai.show({ content: suggestion, source: 'behavior' })
    ▼
设置 isVisible = true
    ▼
AISuggestionBubble组件渲染
    ▼
用户看到智能弹窗！
```

---

## 🔍 关键代码位置详解

### **1. command字段在哪里设置？**

#### **位置A：后端AI服务（推荐）**

```python
# services/mock.py 或真实AI服务
def analyze_user_logs(user_id: str) -> dict:
    """
    分析用户行为日志，决定是否弹窗
    
    Returns:
        {
            "command": "yes" | "no" | "bubble" | "highlight",
            "suggestion": "建议文本",
            "confidence": 0.0-1.0
        }
    """
    from mapper.behavior_mapper import behavior_mapper
    
    # 获取用户最近的行为统计
    stats = behavior_mapper.get_user_behavior_stats(user_id, days=7)
    
    # ===== 智能判断逻辑 =====
    
    # 规则1：频繁查看基金（5次以上）
    if stats['event_type_stats'].get('fund_view', 0) > 5:
        return {
            "command": "yes",  # ← 显示弹窗
            "suggestion": f"您最近查看了{stats['event_type_stats']['fund_view']}次基金，推荐热门基金产品...",
            "confidence": 0.85,
            "fund_id": "000001"  # 可选：推荐的基金ID
        }
    
    # 规则2：频繁搜索资讯（3次以上）
    if stats['event_type_stats'].get('news_search', 0) > 3:
        return {
            "command": "bubble",
            "suggestion": "根据您的搜索记录，为您推荐相关资讯...",
            "confidence": 0.75
        }
    
    # 规则3：转账金额异常（风险提示）
    recent_transfers = behavior_mapper.get_user_behaviors(
        user_id=user_id,
        event_type='transfer_submit',
        limit=10
    )
    
    if len(recent_transfers) > 5:  # 短时间内多次转账
        return {
            "command": "highlight",  # ← 高亮提示
            "suggestion": "检测到频繁转账，请注意资金安全",
            "confidence": 0.95,
            "alert_level": "warning"
        }
    
    # 规则4：无特殊行为
    return {
        "command": "no",  # ← 不显示
        "suggestion": "",
        "confidence": 0.0
    }
```

#### **位置B：前端配置覆盖**

```javascript
// 前端可以覆盖后端的command
ai.show('home', context, {
  autoShow: true  // 即使后端返回command:"no"，也强制显示
});
```

---

### **2. command如何传递到前端？**

#### **传递路径：**

```javascript
// ===== 路径1：用户操作上报 → 后端响应 =====

// 前端上报
BehaviorTracker.track('fund_view', {...}, {realtime: true})
    ↓
POST /api/behavior/track
    ↓
// 后端 behavior_controller.py:59-82
affected_rows = behavior_mapper.batch_insert_logs(valid_events)

# 分析用户日志
from services.mock import analyze_user_logs
ai_suggestion = analyze_user_logs(user_id)  # ← 生成command

# 返回响应
return success_response({
    'inserted': affected_rows,
    'ai_suggestion': ai_suggestion  # ← 包含command
})
    ↓
// 前端 BehaviorTracker.sendToServer():318-323
const result = await response.json();

if (result.success && result.data && result.data.ai_suggestion) {
  this.handleAISuggestion(result.data.ai_suggestion);  // ← 处理AI建议
}
    ↓
// BehaviorTracker.handleAISuggestion():335-350
handleAISuggestion(aiSuggestion) {
  const command = aiSuggestion.command || '';
  
  if (command === 'bubble' || command === 'yes') {  // ← 检查command
    // 触发自定义事件
    window.dispatchEvent(new CustomEvent('ai-suggestion-received', {
      detail: {
        suggestion: aiSuggestion.suggestion,
        command: command,
        confidence: aiSuggestion.confidence
      }
    }));
  }
}
```

---

### **3. 弹窗显示/隐藏的完整控制**

#### **显示条件（同时满足）：**

```javascript
// ===== 条件1：后端command允许 =====
command === 'yes' || command === 'bubble'

// ===== 条件2：前端配置允许 =====
config.autoShow === true

// ===== 条件3：状态更新 =====
setIsVisible(true)

// ===== 条件4：组件渲染检查 =====
// AISuggestionBubble.jsx:6
if (!ai || !ai.isVisible) {
  return null;  // 不显示
}
```

#### **隐藏触发方式：**

```javascript
// ===== 方式1：用户手动关闭 =====
<button onClick={onClose}>×</button>
    ↓
onClose() → ai.hide() → setIsVisible(false)

// ===== 方式2：自动延迟隐藏 =====
if (config.autoHideDelay > 0) {
  setTimeout(() => {
    setIsVisible(false);
  }, 8000);  // 8秒后自动隐藏
}

// ===== 方式3：切换页面时隐藏 =====
// App.jsx:210
const handleNavigate = (page) => {
  ai.hide();  // ← 切换页面时隐藏
  // ...
};

// ===== 方式4：新建议覆盖旧建议 =====
// useAI.js:66-68
const show = () => {
  if (hideTimerRef.current) {
    clearTimeout(hideTimerRef.current);  // 清除旧定时器
  }
  // 显示新建议
};
```

---

## 🎨 配置机制详解

### **配置文件：src/config/ai.config.js**

```javascript
export const AI_PAGE_CONFIGS = {
  home: {
    autoShow: true,         // ← 是否自动显示
    autoHideDelay: 20000,   // ← 延迟隐藏时间（0=不自动隐藏）
    speakEnabled: false,    // ← 是否语音播报
    bubbleTitle: '🏠 智能助手',
  },
  
  bill: {
    autoShow: true,
    autoHideDelay: 30000,   // 账单分析显示30秒
    speakEnabled: true,     // 启用语音
  },
  
  fund: {
    autoShow: false,        // ← 基金建议不自动显示
    autoHideDelay: 15000,
    speakEnabled: false,
  },
  
  behavior: {               // ← 行为追踪专用配置
    autoShow: true,
    autoHideDelay: 15000,
    speakEnabled: false,
  },
};
```

### **配置优先级：**

```
运行时覆盖 > 页面配置 > 默认配置

// 例子
ai.show('home', {}, {
  autoShow: false,      // ← 运行时覆盖（优先级最高）
  autoHideDelay: 5000
});

// 最终使用：
autoShow: false        // 使用运行时覆盖
autoHideDelay: 5000    // 使用运行时覆盖
speakEnabled: false    // 使用页面配置（未被覆盖）
```

---

## 🌟 **行为追踪智能弹窗实现方案** ⭐

### **当前实现状态：**

✅ **已完成：**
1. 前端上报行为日志 → 后端
2. 后端分析日志 → 返回AI建议（包含command）
3. 前端接收 → 触发CustomEvent

❌ **缺失：**
4. **App.jsx中未监听 `ai-suggestion-received` 事件**
5. 事件触发后无法调用 `ai.show()`

### **完整实现方案：**

#### **第1步：在App.jsx中添加事件监听**

```javascript
// src/App.jsx

function App() {
  const ai = useAI();
  
  // ===== 新增：监听行为追踪触发的AI建议 =====
  useEffect(() => {
    const handleBehaviorAISuggestion = (event) => {
      console.log('[App] 收到行为追踪AI建议:', event.detail);
      
      const { suggestion, command, confidence } = event.detail;
      
      // 调用ai.show()显示弹窗
      ai.show({
        content: suggestion,      // 直接传递建议内容
        source: 'behavior',       // 标记来源
        confidence: confidence
      }, {}, {
        autoShow: true,           // 行为追踪建议默认自动显示
        autoHideDelay: 15000,     // 15秒后隐藏
        speakEnabled: false
      });
    };
    
    // 添加监听器
    window.addEventListener('ai-suggestion-received', handleBehaviorAISuggestion);
    
    // 清理监听器
    return () => {
      window.removeEventListener('ai-suggestion-received', handleBehaviorAISuggestion);
    };
  }, [ai]);
  
  // ... 其他代码
}
```

#### **第2步：后端实现智能分析逻辑**

```python
# services/behavior_analysis_service.py（建议新建）

from mapper.behavior_mapper import behavior_mapper
from datetime import datetime, timedelta

class BehaviorAnalysisService:
    """用户行为分析服务，基于日志智能判断是否弹窗"""
    
    @staticmethod
    def analyze_and_suggest(user_id: str) -> dict:
        """
        分析用户行为，返回智能建议
        
        Returns:
            {
                "command": "yes" | "no" | "bubble" | "highlight",
                "suggestion": "建议文本",
                "confidence": 0.0-1.0,
                "trigger_reason": "触发原因"
            }
        """
        # 获取用户最近7天的行为
        stats = behavior_mapper.get_user_behavior_stats(user_id, 7)
        recent_path = behavior_mapper.get_recent_user_path(user_id, 20)
        
        # ===== 智能规则引擎 =====
        
        # 规则1：频繁查看基金但未购买（高价值建议）
        fund_view_count = stats['event_type_stats'].get('fund_view', 0)
        transfer_count = stats['event_type_stats'].get('transfer_submit', 0)
        
        if fund_view_count >= 5 and transfer_count == 0:
            return {
                "command": "yes",
                "suggestion": f"您最近查看了{fund_view_count}次基金，是否需要购买建议？推荐：华夏成长混合型基金，近3月收益+8.45%",
                "confidence": 0.9,
                "trigger_reason": "frequent_fund_view_no_purchase"
            }
        
        # 规则2：查看资讯后长时间停留（中等价值）
        news_read_count = stats['event_type_stats'].get('news_read', 0)
        if news_read_count >= 3:
            return {
                "command": "bubble",
                "suggestion": "根据您的阅读记录，为您推荐相关金融产品和资讯",
                "confidence": 0.7,
                "trigger_reason": "news_engagement"
            }
        
        # 规则3：连续心跳（用户迷茫/停滞）
        heartbeat_count = stats['event_type_stats'].get('heartbeat', 0)
        if heartbeat_count > 10:
            return {
                "command": "bubble",
                "suggestion": "您似乎在犹豫？我可以为您提供一些建议",
                "confidence": 0.6,
                "trigger_reason": "user_hesitation"
            }
        
        # 规则4：异常转账行为（风险提示）
        if transfer_count > 5:
            return {
                "command": "highlight",
                "suggestion": "⚠️ 检测到频繁转账操作，请确认收款人信息，注意资金安全",
                "confidence": 0.95,
                "trigger_reason": "abnormal_transfer",
                "alert_level": "warning"
            }
        
        # 规则5：访问路径异常（回退行为）
        back_count = sum(1 for p in recent_path if p['event_type'] == 'page_leave')
        if back_count > 10:
            return {
                "command": "bubble",
                "suggestion": "您似乎在寻找什么功能？可以告诉我，我来帮您",
                "confidence": 0.65,
                "trigger_reason": "navigation_confusion"
            }
        
        # 默认：无建议
        return {
            "command": "no",
            "suggestion": "",
            "confidence": 0.0,
            "trigger_reason": "normal_behavior"
        }
```

#### **位置B：集成到现有controller**

```python
# controllers/behavior_controller.py:61-82（当前已有）

# 如果有用户ID，调用分析服务
ai_suggestion = None
if user_id:
    try:
        from services.mock import analyze_user_logs  # ← 调用分析
        ai_suggestion = analyze_user_logs(user_id)
        print(f"[behavior_controller] AI建议: {ai_suggestion}")
    except Exception as e:
        print(f"[behavior_controller] 生成AI建议失败: {str(e)}")

# 添加到响应中
if ai_suggestion:
    response_data['ai_suggestion'] = ai_suggestion  # ← 返回给前端
```

---

### **3. 前端如何接收并处理command？**

#### **当前代码：BehaviorTracker.js**

```javascript
// src/utils/BehaviorTracker.js:334-350

handleAISuggestion(aiSuggestion) {
  const command = aiSuggestion.command || '';
  
  // ===== 核心判断逻辑 =====
  if (command === 'bubble' || command === 'yes') {
    // 触发自定义事件（但当前App.jsx未监听！）
    window.dispatchEvent(new CustomEvent('ai-suggestion-received', {
      detail: {
        suggestion: aiSuggestion.suggestion,
        command: command,
        confidence: aiSuggestion.confidence || 0
      }
    }));
    
    console.log('[BehaviorTracker] 已触发AI建议弹窗事件');
  } else if (command === 'highlight') {
    // TODO: 实现高亮逻辑
    console.log('[BehaviorTracker] 高亮模式:', aiSuggestion);
  } else {
    // command === 'no' 或其他，不做任何处理
    console.log('[BehaviorTracker] 不显示建议，command:', command);
  }
}
```

#### **缺失的监听逻辑（需要添加）：**

```javascript
// src/App.jsx（需要新增）

useEffect(() => {
  // 监听行为追踪触发的AI建议
  const handleBehaviorSuggestion = (event) => {
    const { suggestion, command, confidence } = event.detail;
    
    console.log('[App] 行为追踪触发AI建议:', {
      suggestion,
      command,
      confidence
    });
    
    // 显示弹窗
    ai.show({
      content: suggestion,
      source: 'behavior',
      confidence: confidence
    });
  };
  
  window.addEventListener('ai-suggestion-received', handleBehaviorSuggestion);
  
  return () => {
    window.removeEventListener('ai-suggestion-received', handleBehaviorSuggestion);
  };
}, [ai]);
```

---

## 🎯 实际触发场景示例

### **场景1：用户频繁查看基金**

```
时间线：
10:00 - 用户查看"华夏成长"基金
10:05 - 用户查看"易方达蓝筹"基金
10:10 - 用户查看"嘉实增长"基金
10:15 - 用户查看"南方积配"基金
10:20 - 用户查看"博时主题"基金
10:25 - 用户查看"广发稳健"基金 ← 第6次查看

触发流程：
1. 第6次fund_view上报到后端（实时上报）
2. 后端分析：发现6次基金查看
3. 后端返回：
   {
     "command": "yes",
     "suggestion": "您已查看6次基金，推荐热门产品..."
   }
4. 前端收到响应 → handleAISuggestion()
5. 触发CustomEvent
6. App.jsx监听到事件 → ai.show()
7. 弹窗显示："您已查看6次基金..."
```

---

### **场景2：用户长时间无操作**

```
时间线：
14:00 - 用户进入首页
14:00-14:10 - 无任何操作（10次心跳）

触发流程：
1. 每10秒发送一次heartbeat事件
2. 第10次心跳上报时，后端分析
3. 后端检测：10次心跳，用户可能需要帮助
4. 返回：
   {
     "command": "bubble",
     "suggestion": "需要帮助吗？可以问我任何金融问题"
   }
5. 前端显示弹窗
```

---

### **场景3：异常转账行为**

```
时间线：
15:00 - 用户转账500元
15:05 - 用户转账1000元
15:10 - 用户转账2000元
15:15 - 用户转账5000元
15:20 - 用户转账3000元
15:25 - 用户转账1500元 ← 第6次转账

触发流程：
1. 第6次transfer_submit上报（实时上报）
2. 后端分析：短时间内6次转账（异常）
3. 返回：
   {
     "command": "highlight",
     "suggestion": "⚠️ 检测到频繁转账，请注意资金安全",
     "alert_level": "warning"
   }
4. 前端显示高亮提示（红色警告弹窗）
```

---

## 🔧 控制弹窗的4个维度

### **维度1：后端决策（command字段）**
```python
# 后端完全控制
if 条件满足:
    return {"command": "yes"}   # 显示
else:
    return {"command": "no"}    # 不显示
```

### **维度2：前端配置（autoShow）**
```javascript
// 前端配置文件
home: {
  autoShow: true   // 自动显示
}

fund: {
  autoShow: false  // 不自动显示（需要手动调用）
}
```

### **维度3：运行时覆盖**
```javascript
// 调用时强制覆盖
ai.show('home', {}, {
  autoShow: true,  // 强制显示
  autoHideDelay: 0 // 不自动隐藏
});
```

### **维度4：状态管理（isVisible）**
```javascript
// useAI Hook中
const [isVisible, setIsVisible] = useState(false);

// 显示
setIsVisible(true);

// 隐藏
setIsVisible(false);
```

---

## 📈 决策树

```
收到AI建议
    │
    ▼
检查 command 字段
    │
    ├─ command === "yes" || "bubble"
    │    │
    │    ▼
    │  检查 config.autoShow
    │    │
    │    ├─ autoShow === true
    │    │    │
    │    │    ▼
    │    │  setIsVisible(true)
    │    │    │
    │    │    ▼
    │    │  ✅ 弹窗显示
    │    │    │
    │    │    ▼
    │    │  检查 autoHideDelay
    │    │    │
    │    │    ├─ autoHideDelay > 0
    │    │    │    │
    │    │    │    ▼
    │    │    │  setTimeout → setIsVisible(false)
    │    │    │    │
    │    │    │    ▼
    │    │    │  ✅ 自动隐藏
    │    │    │
    │    │    └─ autoHideDelay === 0
    │    │         │
    │    │         ▼
    │    │       ✅ 不自动隐藏（手动关闭）
    │    │
    │    └─ autoShow === false
    │         │
    │         ▼
    │       ❌ 不显示
    │
    ├─ command === "highlight"
    │    │
    │    ▼
    │  高亮显示（特殊样式）
    │
    └─ command === "no"
         │
         ▼
       ❌ 不显示
```

---

## 🎨 实际代码示例

### **完整示例：用户频繁查看基金后智能推荐**

#### **1. 用户操作**
```javascript
// 用户点击第6个基金
<div onClick={() => handleFundClick(fund)}>
  华夏成长
</div>
```

#### **2. 前端追踪**
```javascript
// FundList.jsx:130-140
tracker.track(EventTypes.FUND_VIEW, {
  fund_code: '000001',
  fund_name: '华夏成长',
  // ...
}, { realtime: true });  // ← 实时上报
```

#### **3. 后端接收并分析**
```python
# behavior_controller.py:15-82
@behavior_bp.route('/track', methods=['POST'])
def track_behaviors():
    # 存储日志
    affected_rows = behavior_mapper.batch_insert_logs(valid_events)
    
    # 分析用户行为
    ai_suggestion = analyze_user_logs(user_id)
    # 返回：
    # {
    #   "command": "yes",
    #   "suggestion": "您已查看6次基金，推荐购买...",
    #   "confidence": 0.9
    # }
    
    return success_response({
        'inserted': affected_rows,
        'ai_suggestion': ai_suggestion  # ← 返回AI建议
    })
```

#### **4. 前端接收响应**
```javascript
// BehaviorTracker.js:318-326
const result = await response.json();

if (result.success && result.data && result.data.ai_suggestion) {
  this.handleAISuggestion(result.data.ai_suggestion);
}
```

#### **5. 触发弹窗事件**
```javascript
// BehaviorTracker.js:335-350
handleAISuggestion(aiSuggestion) {
  if (aiSuggestion.command === 'yes') {
    window.dispatchEvent(new CustomEvent('ai-suggestion-received', {
      detail: {
        suggestion: "您已查看6次基金，推荐购买...",
        command: 'yes',
        confidence: 0.9
      }
    }));
  }
}
```

#### **6. App.jsx监听并显示**
```javascript
// App.jsx（需要添加的代码）
useEffect(() => {
  window.addEventListener('ai-suggestion-received', (event) => {
    ai.show({
      content: event.detail.suggestion,
      source: 'behavior',
      confidence: event.detail.confidence
    });
  });
}, [ai]);
```

#### **7. 用户看到弹窗**
```
┌──────────────────────────────────┐
│ 💡 智能建议                   × │
├──────────────────────────────────┤
│ 您已查看6次基金，推荐购买...    │
│                                  │
│ 华夏成长混合型基金               │
│ 近3月收益: +8.45%                │
│                                  │
│  🔊   详细对话                   │
└──────────────────────────────────┘
```

---

## 🚨 **当前系统缺失的关键环节**

### **❌ 缺失1：App.jsx未监听 ai-suggestion-received 事件**

**现状：**
- BehaviorTracker触发了事件
- 但App.jsx没有监听
- 导致行为追踪弹窗**无法显示**

**需要添加的代码位置：**
`src/App.jsx` 第18行后（useAI声明之后）

---

### **❌ 缺失2：后端分析逻辑未完善**

**现状：**
- `services/mock.py` 中的 `analyze_user_logs` 存在
- 但逻辑可能过于简单
- 需要增强智能判断规则

---

## 📋 总结：弹窗显示的完整条件

### **必须同时满足：**

```
[后端条件]
  后端分析用户行为
    ↓
  返回 command = "yes" 或 "bubble"
    ↓
[事件触发]
  BehaviorTracker.handleAISuggestion()
    ↓
  window.dispatchEvent('ai-suggestion-received')
    ↓
[事件监听] ← 当前缺失！
  App.jsx监听到事件
    ↓
  调用 ai.show()
    ↓
[前端配置]
  config.autoShow = true
    ↓
[状态更新]
  setIsVisible(true)
    ↓
[组件渲染]
  AISuggestionBubble检查 ai.isVisible = true
    ↓
✅ 弹窗显示成功！
```

---

## 🎯 下一步建议

### **为了完整实现行为追踪智能弹窗，需要：**

1. ✅ **在App.jsx添加事件监听**（补全缺失环节）
2. ✅ **完善后端分析逻辑**（增强智能判断规则）
3. ✅ **测试完整流程**（验证弹窗能否正常显示）

---

## ❓ 请您确认

**您现在希望我：**

- [ ] A. **立即补全缺失代码**（添加事件监听 + 完善后端逻辑）
- [ ] B. **仅提供代码示例**（您自己集成）
- [ ] C. **先测试当前逻辑**（看看是否真的不显示）
- [ ] D. **详细讲解某个具体环节**（请指定：___）

**或直接告诉我：**
- "补全所有缺失代码，让行为追踪弹窗能工作"
- "先测试一下当前系统"
- "我有其他问题：___"

我已准备好完整的修复方案，等待您的指示！🚀

