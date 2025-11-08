import React, { useState } from 'react';
import './Register.css';

const Register = ({ onComplete, onBackToLogin }) => {
  const [currentStep, setCurrentStep] = useState(1); // 1-4步
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // 表单数据
  const [formData, setFormData] = useState({
    // 第1步：基本信息
    realName: '',
    idCard: '',
    phone: '',
    city: '',
    occupation: '',
    
    // 第2步：风险承受能力（5个问题的答案，存储分数）
    riskQ1: 0, // 风险偏好
    riskQ2: 0, // 投资经验
    riskQ3: 0, // 财务状况
    riskQ4: 0, // 投资期限
    riskQ5: 0, // 抗风险能力
    
    // 第3步：投资目的（多选）
    investmentPurposes: [],
    
    // 第4步：创建账号
    username: '',
    password: '',
    confirmPassword: '',
  });
  
  // 城市列表
  const cities = [
    '北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '重庆',
    '武汉', '西安', '天津', '苏州', '郑州', '长沙', '沈阳', '青岛',
    '宁波', '厦门', '济南', '哈尔滨'
  ];
  
  // 职业列表
  const occupations = [
    '学生', '企业职工', '个体工商户', '公务员', '退休人员', '自由职业者'
  ];
  
  // 风险问卷题目
  const riskQuestions = [
    {
      id: 'riskQ1',
      title: '1. 风险偏好（权重 30%）',
      question: '若投资 1 年亏损 10%，你的反应是？',
      options: [
        { text: '恐慌抛售', score: 1 },
        { text: '观望不动', score: 2 },
        { text: '适当补仓', score: 3 },
        { text: '大幅加仓', score: 4 },
        { text: '满仓买入', score: 5 },
      ],
      weight: 0.30
    },
    {
      id: 'riskQ2',
      title: '2. 投资经验（权重 25%）',
      question: '过往投资品类包含（可多选，按复杂度计分）？',
      options: [
        { text: '仅存款 / 国债', score: 1 },
        { text: '银行理财', score: 2 },
        { text: '基金 / 债券', score: 3 },
        { text: '股票 / 期货', score: 4 },
        { text: '衍生品 / 私募', score: 5 },
      ],
      weight: 0.25
    },
    {
      id: 'riskQ3',
      title: '3. 财务状况（权重 25%）',
      question: '可投资资产占家庭总资产的比例？',
      options: [
        { text: '< 10%', score: 1 },
        { text: '10%-30%', score: 2 },
        { text: '30%-50%', score: 3 },
        { text: '50%-70%', score: 4 },
        { text: '> 70%', score: 5 },
      ],
      weight: 0.25
    },
    {
      id: 'riskQ4',
      title: '4. 投资期限（权重 10%）',
      question: '计划持有投资资金的期限？',
      options: [
        { text: '< 6 个月', score: 1 },
        { text: '6 个月 - 1 年', score: 2 },
        { text: '1-3 年', score: 3 },
        { text: '3-5 年', score: 4 },
        { text: '> 5 年', score: 5 },
      ],
      weight: 0.10
    },
    {
      id: 'riskQ5',
      title: '5. 抗风险能力（权重 10%）',
      question: '若投资亏损 20%，是否影响家庭正常生活？',
      options: [
        { text: '严重影响', score: 1 },
        { text: '有一定影响', score: 2 },
        { text: '影响较小', score: 3 },
        { text: '基本无影响', score: 4 },
        { text: '完全无影响', score: 5 },
      ],
      weight: 0.10
    }
  ];
  
  // 投资目的选项（5类）
  const investmentPurposeOptions = [
    {
      id: 'purpose_1',
      title: '第 1 类：资本增值与长期财富积累',
      description: '追求资产的长远、显著增长，实现财富的倍增。通常投资周期较长（5年以上），愿意承受较高的短期波动以换取更高的潜在回报。',
      tags: '典型基金：股票型基金、偏股混合型基金、行业主题基金（如科技、消费、新能源等）',
      people: '人群画像：年轻投资者、收入稳定且风险承受能力较强的投资者，为养老、子女教育等长期目标做准备。'
    },
    {
      id: 'purpose_2',
      title: '第 2 类：稳健收益与资产保值',
      description: '在控制风险的前提下，获得超越银行存款的稳定收益，对抗通货膨胀，实现资产的稳健保值。',
      tags: '典型基金：债券型基金、偏债混合型基金、"固收+"策略基金。',
      people: '人群画像：风险偏好中性或保守的投资者，如中老年人、临近退休或需要定期现金流补充的投资者。'
    },
    {
      id: 'purpose_3',
      title: '第 3 类：现金管理与流动性管理',
      description: '将暂时闲置的资金进行管理，追求比活期存款更高的收益，同时保证资金的极高流动性和安全性，方便随时取用。',
      tags: '典型基金：货币市场基金。',
      people: '人群画像：所有投资者，尤其是将基金账户作为"资金中转站"或存放应急备用金的用户。'
    },
    {
      id: 'purpose_4',
      title: '第 4 类：分散风险与资产配置',
      description: '不把鸡蛋放在同一个篮子里。通过投资不同类型的基金（如跨市场、跨资产类别），降低整体投资组合的波动性。',
      tags: '典型基金：指数基金（尤其是宽基指数如沪深 300）、QDII 基金（投资海外市场）、商品基金（如黄金 ETF）、不同行业或风格的基金组合。',
      people: '人群画像：有一定投资经验、注重投资组合构建和风险管理的成熟投资者。'
    },
    {
      id: 'purpose_5',
      title: '第 5 类：教育学习与体验市场',
      description: '主要目的并非立即获得高额回报，而是通过小额投入来学习基金投资的知识、熟悉市场规则、体验投资过程，为未来的投资实践打下基础。',
      tags: '典型基金：各种类型的基金都可能涉及，但金额通常较小。',
      people: '人群画像：投资新手、在校学生、对金融市场充满好奇的学习者。'
    }
  ];
  
  // 字段更新
  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };
  
  // 投资目的切换
  const togglePurpose = (purposeId) => {
    setFormData(prev => {
      const purposes = prev.investmentPurposes.includes(purposeId)
        ? prev.investmentPurposes.filter(id => id !== purposeId)
        : [...prev.investmentPurposes, purposeId];
      return { ...prev, investmentPurposes: purposes };
    });
  };
  
  // 验证第1步
  const validateStep1 = () => {
    if (!formData.realName.trim()) {
      setError('请输入姓名');
      return false;
    }
    if (!formData.idCard.trim()) {
      setError('请输入身份证号');
      return false;
    }
    if (!/^\d{17}[\dXx]$/.test(formData.idCard)) {
      setError('身份证号格式不正确');
      return false;
    }
    if (!formData.phone.trim()) {
      setError('请输入手机号码');
      return false;
    }
    if (!/^1[3-9]\d{9}$/.test(formData.phone)) {
      setError('手机号码格式不正确');
      return false;
    }
    return true;
  };
  
  // 验证第2步
  const validateStep2 = () => {
    const answered = [
      formData.riskQ1, formData.riskQ2, formData.riskQ3,
      formData.riskQ4, formData.riskQ5
    ];
    if (answered.some(score => score === 0)) {
      setError('请完成所有风险评估问题');
      return false;
    }
    return true;
  };
  
  // 验证第3步
  const validateStep3 = () => {
    if (formData.investmentPurposes.length === 0) {
      setError('请至少选择一个投资目的');
      return false;
    }
    return true;
  };
  
  // 验证第4步
  const validateStep4 = () => {
    if (!formData.username.trim()) {
      setError('请输入用户名');
      return false;
    }
    if (formData.username.length < 3) {
      setError('用户名至少3个字符');
      return false;
    }
    if (!formData.password.trim()) {
      setError('请输入密码');
      return false;
    }
    if (formData.password.length < 6) {
      setError('密码至少6个字符');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('两次密码输入不一致');
      return false;
    }
    return true;
  };
  
  // 下一步
  const handleNext = () => {
    setError('');
    
    if (currentStep === 1 && !validateStep1()) return;
    if (currentStep === 2 && !validateStep2()) return;
    if (currentStep === 3 && !validateStep3()) return;
    
    setCurrentStep(currentStep + 1);
  };
  
  // 上一步
  const handlePrev = () => {
    setError('');
    setCurrentStep(currentStep - 1);
  };
  
  // 提交注册
  const handleSubmit = async () => {
    if (!validateStep4()) return;
    
    setLoading(true);
    setError('');
    
    try {
      // 计算风险评分
      const riskScore = 
        formData.riskQ1 * 0.30 +
        formData.riskQ2 * 0.25 +
        formData.riskQ3 * 0.25 +
        formData.riskQ4 * 0.10 +
        formData.riskQ5 * 0.10;
      
      // 确定风险等级
      let riskLevel;
      if (riskScore <= 1.5) riskLevel = '保守型';
      else if (riskScore <= 2.5) riskLevel = '稳健型';
      else if (riskScore <= 3.5) riskLevel = '平衡型';
      else if (riskScore <= 4.5) riskLevel = '积极型';
      else riskLevel = '激进型';
      
      const apiUrl = `${window.location.origin}/api/register`;
      console.log('[Register] 提交数据:', {
        username: formData.username,
        realName: formData.realName,
        riskScore: parseFloat(riskScore.toFixed(2)),
        riskLevel: riskLevel
      });
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          realName: formData.realName,
          idCard: formData.idCard,
          phone: formData.phone,
          city: formData.city,
          occupation: formData.occupation,
          riskScore: parseFloat(riskScore.toFixed(2)),
          riskLevel: riskLevel,
          investmentPurposes: formData.investmentPurposes.join(','),
        })
      });
      
      console.log('[Register] 响应状态:', response.status);
      const result = await response.json();
      console.log('[Register] 响应数据:', result);
      
      if (result.success) {
        alert('注册成功！请使用用户名和密码登录。');
        onComplete();
      } else {
        setError(result.message || '注册失败');
        console.error('[Register] 注册失败:', result);
      }
    } catch (err) {
      console.error('[Register] 注册异常:', err);
      setError(`注册失败: ${err.message || '请检查网络连接'}`);
    } finally {
      setLoading(false);
    }
  };
  
  // 渲染第1步：基本信息
  const renderStep1 = () => (
    <div className="step-content">
      <h3 className="step-title">基本信息</h3>
      
      <div className="form-group">
        <label htmlFor="realName">姓名 <span className="required">*</span></label>
        <input
          type="text"
          id="realName"
          value={formData.realName}
          onChange={(e) => updateField('realName', e.target.value)}
          placeholder="请输入真实姓名"
          autoFocus
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="idCard">身份证号 <span className="required">*</span></label>
        <input
          type="text"
          id="idCard"
          value={formData.idCard}
          onChange={(e) => updateField('idCard', e.target.value)}
          placeholder="请输入18位身份证号"
          maxLength={18}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="phone">手机号码 <span className="required">*</span></label>
        <input
          type="tel"
          id="phone"
          value={formData.phone}
          onChange={(e) => updateField('phone', e.target.value)}
          placeholder="请输入11位手机号"
          maxLength={11}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="city">城市</label>
        <select
          id="city"
          value={formData.city}
          onChange={(e) => updateField('city', e.target.value)}
        >
          <option value="">请选择城市</option>
          {cities.map(city => (
            <option key={city} value={city}>{city}</option>
          ))}
        </select>
      </div>
      
      <div className="form-group">
        <label htmlFor="occupation">职业</label>
        <select
          id="occupation"
          value={formData.occupation}
          onChange={(e) => updateField('occupation', e.target.value)}
        >
          <option value="">请选择职业</option>
          {occupations.map(occ => (
            <option key={occ} value={occ}>{occ}</option>
          ))}
        </select>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="button-group">
        <button type="button" onClick={onBackToLogin} className="btn-secondary">
          返回登录
        </button>
        <button type="button" onClick={handleNext} className="btn-primary">
          下一步
        </button>
      </div>
    </div>
  );
  
  // 渲染第2步：风险评估
  const renderStep2 = () => (
    <div className="step-content">
      <h3 className="step-title">风险承受能力评估</h3>
      <p className="step-desc">请根据您的实际情况如实填写，以便为您推荐合适的产品</p>
      
      {riskQuestions.map((q) => (
        <div key={q.id} className="question-block">
          <h4 className="question-title">{q.title}</h4>
          <p className="question-text">{q.question}</p>
          <div className="options-list">
            {q.options.map((opt, idx) => (
              <label key={idx} className="option-item">
                <input
                  type="radio"
                  name={q.id}
                  checked={formData[q.id] === opt.score}
                  onChange={() => updateField(q.id, opt.score)}
                />
                <span className="option-text">{opt.text}</span>
              </label>
            ))}
          </div>
        </div>
      ))}
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="button-group">
        <button type="button" onClick={handlePrev} className="btn-secondary">
          上一步
        </button>
        <button type="button" onClick={handleNext} className="btn-primary">
          下一步
        </button>
      </div>
    </div>
  );
  
  // 渲染第3步：投资目的
  const renderStep3 = () => (
    <div className="step-content">
      <h3 className="step-title">投资目的（可多选）</h3>
      
      <div className="purposes-list">
        {investmentPurposeOptions.map((purpose) => (
          <div 
            key={purpose.id} 
            className={`purpose-card ${formData.investmentPurposes.includes(purpose.id) ? 'selected' : ''}`}
            onClick={() => togglePurpose(purpose.id)}
          >
            <div className="purpose-header">
              <input
                type="checkbox"
                checked={formData.investmentPurposes.includes(purpose.id)}
                onChange={() => {}}
              />
              <h4 className="purpose-title">{purpose.title}</h4>
            </div>
            <p className="purpose-desc">{purpose.description}</p>
            <div className="purpose-tags">
              <span className="tag">📊 {purpose.tags}</span>
            </div>
            <div className="purpose-people">
              <span className="tag">👥 {purpose.people}</span>
            </div>
          </div>
        ))}
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="button-group">
        <button type="button" onClick={handlePrev} className="btn-secondary">
          上一步
        </button>
        <button type="button" onClick={handleNext} className="btn-primary">
          下一步
        </button>
      </div>
    </div>
  );
  
  // 渲染第4步：创建账号
  const renderStep4 = () => (
    <div className="step-content">
      <h3 className="step-title">创建账号</h3>
      
      <div className="form-group">
        <label htmlFor="username">用户名 <span className="required">*</span></label>
        <input
          type="text"
          id="username"
          value={formData.username}
          onChange={(e) => updateField('username', e.target.value)}
          placeholder="请输入用户名（至少3个字符）"
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="password">密码 <span className="required">*</span></label>
        <input
          type="password"
          id="password"
          value={formData.password}
          onChange={(e) => updateField('password', e.target.value)}
          placeholder="请输入密码（至少6个字符）"
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="confirmPassword">确认密码 <span className="required">*</span></label>
        <input
          type="password"
          id="confirmPassword"
          value={formData.confirmPassword}
          onChange={(e) => updateField('confirmPassword', e.target.value)}
          placeholder="请再次输入密码"
        />
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="button-group">
        <button type="button" onClick={handlePrev} className="btn-secondary">
          上一步
        </button>
        <button 
          type="button" 
          onClick={handleSubmit} 
          className="btn-primary"
          disabled={loading}
        >
          {loading ? '注册中...' : '完成注册'}
        </button>
      </div>
    </div>
  );
  
  return (
    <div className="register-container">
      <div className="register-card">
        <h2 className="register-header">用户注册</h2>
        
        {/* 步骤指示器 */}
        <div className="step-indicator">
          <div className={`step ${currentStep >= 1 ? 'active' : ''}`}>
            <span className="step-number">1</span>
            <span className="step-label">基本信息</span>
          </div>
          <div className="step-line"></div>
          <div className={`step ${currentStep >= 2 ? 'active' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-label">风险评估</span>
          </div>
          <div className="step-line"></div>
          <div className={`step ${currentStep >= 3 ? 'active' : ''}`}>
            <span className="step-number">3</span>
            <span className="step-label">投资目的</span>
          </div>
          <div className="step-line"></div>
          <div className={`step ${currentStep >= 4 ? 'active' : ''}`}>
            <span className="step-number">4</span>
            <span className="step-label">创建账号</span>
          </div>
        </div>
        
        {/* 表单内容 */}
        <div className="register-form">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
          {currentStep === 4 && renderStep4()}
        </div>
      </div>
    </div>
  );
};

export default Register;

