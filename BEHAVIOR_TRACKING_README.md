# 用户行为追踪系统 - 使用指南

## 📊 系统概述

完整的用户行为日志采集系统，支持前端所有点击、页面访问等操作的追踪，为AI行为预测和用户行为分析提供数据基础。

### 核心特性

✅ **Hook封装** - 组件内灵活控制追踪内容  
✅ **混合上报** - 关键操作实时上报 + 普通操作批量上报 + 10秒心跳  
✅ **失败重试** - 本地缓存 + 自动重试  
✅ **零性能影响** - 异步处理，不阻塞用户操作  
✅ **敏感信息脱敏** - 密码不采集、银行卡号自动脱敏  
✅ **7天自动清理** - 数据库定时清理机制  

---

## 🚀 快速开始

### 1. 初始化数据库

```bash
python init_behavior_logs_table.py
```

**输出示例：**
```
✅ 用户行为日志表创建成功
✅ 启用MySQL事件调度器
✅ 自动清理事件创建成功（每天清理7天前的数据）
✅ 手动清理存储过程创建成功

🎉 数据库初始化完成！
```

### 2. 启动后端服务

```bash
python app.py
```

**新增API接口：**
- `POST /api/behavior/track` - 接收行为日志（前端自动调用）
- `POST /api/behavior/query` - 查询用户行为
- `POST /api/behavior/stats` - 获取行为统计
- `POST /api/behavior/path` - 获取用户访问路径

### 3. 启动前端

```bash
npm run dev
```

前端会自动开始采集用户行为！

---

## 📦 已集成的组件

### ✅ FundList（基金列表）- 优先级1
**追踪内容：**
- 页面访问（进入/离开基金页面）
- 基金筛选（类型、风险、排序）
- 基金详情查看（**实时上报**，含基金代码、名称、净值等）
- 分页操作

**示例日志：**
```json
{
  "event_type": "fund_view",
  "fund_code": "000001",
  "fund_name": "华夏成长",
  "fund_category": "混合型",
  "fund_nav": 1.2345
}
```

---

### ✅ HomePage（首页）- 优先级2
**追踪内容：**
- 页面访问
- 快捷操作点击（账户、转账、理财、更多）
- 推荐产品点击（基金精选、定期存款）
- 热门资讯点击

**示例日志：**
```json
{
  "event_type": "click",
  "element_id": "quick-action-transfer",
  "element_text": "转账",
  "action_type": "quick_action",
  "target_page": "transfer"
}
```

---

### ✅ NewsPage（资讯页）- 优先级3
**追踪内容：**
- 页面访问
- 资讯搜索（防抖500ms）
- 分类切换
- 资讯阅读（**实时上报**，含资讯ID、标题、分类、作者等）

**示例日志：**
```json
{
  "event_type": "news_read",
  "news_id": 123,
  "news_title": "央行降准释放资金",
  "news_category": "财经新闻",
  "current_search_query": "降准"
}
```

---

### ✅ TransferPage（转账页）
**追踪内容：**
- 页面访问
- 收款账户选择（**卡号自动脱敏**）
- 转账金额输入（**完全采集**）
- 转账提交（**实时上报**）

**示例日志：**
```json
{
  "event_type": "transfer_submit",
  "cardNumber": "6222****1234",  // 自动脱敏
  "transfer_amount": 500.00,     // 完全采集
  "amount_range": "100-1000",
  "account_type": "same_bank"
}
```

---

### ✅ BillDetail（账单明细）
**追踪内容：**
- 页面访问
- 月份筛选
- 账单条目查看

**示例日志：**
```json
{
  "event_type": "bill_view",
  "bill_merchant": "星巴克咖啡",
  "bill_category": "餐饮",
  "bill_amount": -45.00,
  "selected_month": "2023-10"
}
```

---

## 🔧 核心配置

### tracking.config.js

```javascript
export const TrackingConfig = {
  enabled: true,                    // 是否启用追踪
  debug: true,                      // 开发环境调试
  
  batchUpload: {
    maxQueueSize: 50,               // 50条自动上报
    uploadInterval: 5000,           // 5秒批量上报
    retryTimes: 3,                  // 失败重试3次
  },
  
  heartbeat: {
    interval: 10000,                // 10秒心跳（无操作时）
    enabled: true,
  },
  
  samplingRate: 1.0,                // 100%采集
};
```

### 敏感信息处理

```javascript
export const SensitiveConfig = {
  // 完全不采集
  blocked: ['password', 'pwd', 'cvv', 'pin'],
  
  // 自动脱敏（保留前4后4）
  masked: ['cardNumber', 'card_number', 'bankCard'],
};
```

---

## 💡 使用示例

### 在新组件中添加追踪

```javascript
import { usePageTracking } from '../hooks/usePageTracking';
import { useBehaviorTracker } from '../hooks/useBehaviorTracker';
import { EventTypes } from '../config/tracking.config';

function MyComponent() {
  // 1. 页面访问追踪
  usePageTracking('my_page');
  
  // 2. 获取tracker实例
  const tracker = useBehaviorTracker();
  
  // 3. 追踪点击事件
  const handleClick = () => {
    tracker.track(EventTypes.CLICK, {
      element_id: 'my-button',
      element_text: '点击我',
      custom_data: 'any value',
    });
  };
  
  // 4. 追踪业务事件（实时上报）
  const handleImportantAction = () => {
    tracker.track('important_action', {
      action_id: 123,
      result: 'success',
    }, { realtime: true }); // 实时上报
  };
  
  return <button onClick={handleClick}>点击我</button>;
}
```

---

## 📊 数据查询

### 查询用户行为日志

```bash
curl -X POST http://localhost:5000/api/behavior/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "12345",
    "event_type": "fund_view",
    "limit": 10
  }'
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "behaviors": [
      {
        "event_id": "uuid-123",
        "event_type": "fund_view",
        "user_id": "12345",
        "page": "financing",
        "business_data": {
          "fund_code": "000001",
          "fund_name": "华夏成长"
        },
        "timestamp": 1730899200000
      }
    ],
    "count": 1
  }
}
```

### 获取用户行为统计

```bash
curl -X POST http://localhost:5000/api/behavior/stats \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "12345",
    "days": 7
  }'
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "total_events": 1250,
    "event_type_stats": {
      "click": 450,
      "page_view": 320,
      "fund_view": 80
    },
    "page_stats": {
      "home": 320,
      "financing": 280,
      "news": 150
    }
  }
}
```

### 获取用户访问路径

```bash
curl -X POST http://localhost:5000/api/behavior/path \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "12345",
    "limit": 20
  }'
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "path": [
      {"page": "home", "timestamp": 1730899200000},
      {"page": "financing", "timestamp": 1730899210000},
      {"page": "news", "timestamp": 1730899220000}
    ]
  }
}
```

---

## 🗄️ 数据库结构

### user_behavior_logs 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 自增主键 |
| event_id | VARCHAR(64) | 事件唯一ID |
| event_type | VARCHAR(50) | 事件类型 |
| user_id | VARCHAR(50) | 用户ID |
| session_id | VARCHAR(100) | 会话ID |
| page | VARCHAR(50) | 当前页面 |
| page_url | VARCHAR(255) | 页面URL |
| element_id | VARCHAR(100) | 元素ID |
| element_text | VARCHAR(200) | 元素文本 |
| business_data | JSON | 业务数据 |
| context_data | JSON | 设备环境信息 |
| timestamp | BIGINT | 事件时间戳 |
| created_at | TIMESTAMP | 记录创建时间 |

**索引设计：**
- `idx_user_id` - 用户ID索引
- `idx_event_type` - 事件类型索引
- `idx_page` - 页面索引
- `idx_user_event` - 用户+事件复合索引
- `idx_created_at` - 创建时间索引（用于清理）

---

## 🔍 调试方法

### 开发环境日志

打开浏览器控制台，会看到：

```
[BehaviorTracker] 初始化完成 {sessionId: "sess_1730899200_abc123"}
[BehaviorTracker] 事件已追踪 {eventType: "page_view", isRealtime: false}
[BehaviorTracker] 批量上报成功 {count: 12}
🎯 点击追踪: {element_id: "quick-action-transfer", ...}
```

### 查看数据库

```sql
-- 查看最近100条日志
SELECT * FROM user_behavior_logs 
ORDER BY created_at DESC 
LIMIT 100;

-- 统计事件类型分布
SELECT event_type, COUNT(*) as count 
FROM user_behavior_logs 
GROUP BY event_type 
ORDER BY count DESC;

-- 查看用户访问路径
SELECT page, timestamp, event_type 
FROM user_behavior_logs 
WHERE user_id = '12345' 
  AND event_type IN ('page_view', 'page_leave')
ORDER BY timestamp DESC 
LIMIT 20;
```

---

## ⚙️ 维护与优化

### 手动清理旧数据

```sql
-- 清理7天前的数据
CALL sp_cleanup_behavior_logs(7);

-- 清理30天前的数据
CALL sp_cleanup_behavior_logs(30);
```

### 性能监控

```sql
-- 查看表大小
SELECT 
  table_name,
  ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES 
WHERE table_schema = 'Fin' 
  AND table_name = 'user_behavior_logs';

-- 查看索引使用情况
SHOW INDEX FROM user_behavior_logs;
```

---

## 🎯 下一步：接入AI预测

### 1. 数据已准备就绪

所有用户行为数据已自动采集并存入数据库，包括：
- 页面访问序列
- 点击行为
- 停留时长
- 业务操作（基金查看、转账、资讯阅读等）

### 2. 建议的AI预测场景

**场景1：页面跳转预测**
```python
# 分析用户历史路径
user_path = behavior_mapper.get_recent_user_path(user_id, 50)

# 构建AI提示词
prompt = f"""
用户最近访问路径：{user_path}
当前页面：financing
预测用户下一步最可能访问的页面是什么？
"""
```

**场景2：产品推荐**
```python
# 获取用户行为统计
stats = behavior_mapper.get_user_behavior_stats(user_id, 30)

# 分析：如果用户频繁查看基金，推荐相关产品
if stats['event_type_stats'].get('fund_view', 0) > 20:
    # 触发基金推荐
```

**场景3：风险预警**
```python
# 查询转账行为
transfer_logs = behavior_mapper.get_user_behaviors(
    user_id=user_id,
    event_type='transfer_submit',
    start_time=last_hour
)

# 如果短时间内多次转账，触发风险提示
if len(transfer_logs) > 5:
    # 触发AI风险提示
```

---

## 📝 总结

### 已完成功能

✅ 前端Hook封装（3个）  
✅ 所有组件集成（5个）  
✅ 后端API接口（4个）  
✅ 数据库表设计 + 自动清理  
✅ 批量上报 + 实时上报 + 心跳机制  
✅ 失败重试 + 本地缓存  
✅ 敏感信息脱敏  

### 系统特点

- **零侵入**：组件内3行代码完成集成
- **高性能**：批量上报 + 异步处理
- **高可靠**：失败重试 + 本地缓存
- **易扩展**：JSON字段灵活存储业务数据

### 数据价值

- **行为序列**：完整的用户操作路径
- **兴趣标签**：通过浏览行为推断兴趣
- **时间规律**：活跃时段、使用习惯
- **转化漏斗**：从浏览到转账的完整路径

---

## 🆘 常见问题

**Q: 数据上报失败怎么办？**  
A: 系统会自动重试3次，失败后会保存到LocalStorage，下次启动时自动恢复上报。

**Q: 如何临时关闭追踪？**  
A: 修改 `src/config/tracking.config.js` 中的 `enabled` 为 `false`。

**Q: 数据库表太大怎么办？**  
A: 自动清理机制每天清理7天前的数据。可手动调用 `CALL sp_cleanup_behavior_logs(3)` 清理3天前的数据。

**Q: 如何查看追踪是否正常？**  
A: 打开浏览器控制台，点击任意按钮，应该能看到 `🎯 点击追踪:` 日志输出。

---

## 📧 联系方式

如有问题，请查看：
- 配置文件：`src/config/tracking.config.js`
- 核心代码：`src/utils/BehaviorTracker.js`
- 后端API：`controllers/behavior_controller.py`
- 数据库表：`user_behavior_logs`

🎉 **用户行为追踪系统已就绪！开始采集数据，为AI预测做准备吧！**

