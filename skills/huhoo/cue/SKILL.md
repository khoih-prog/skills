---
name: cue
description: AI-powered financial research assistant with "White-Box" evidence engineering. Multi-Agent architecture for automated information collection, verification, and analysis. From "AI chat" to "Skill Partner" - building trust foundations for financial digital decisions.
description-zh: 「白盒」深度调研助理，采用 Multi-Agent 架构实现信息搜集、处理与验证分析的自动化。不只提供答案，更提供支撑答案的完整证据链。从「AI对话」进化为「技能伙伴」，构建金融数字化决策的信任基石。
metadata:
  {
    "openclaw":
      {
        "requires": { 
          "bins": ["cuecue-research", "python3", "jq"],
          "env": ["CUECUE_API_KEY", "CUECUE_BASE_URL"]
        }
      }
  }
---

# Cue - 智能投研助手 | AI-Powered Financial Research Assistant

> **English**: Your "White-Box" deep research assistant. From "AI Chat" to "Skill Partner" - building trust foundations for financial digital decisions.
>
> **中文**: 你的「白盒」深度调研助理。从「AI对话」进化为「技能伙伴」，构建金融数字化决策的信任基石。

---

## 💡 为什么选择 Cue | Why Cue

### 🎯 终结三大痛点 | Solve 3 Key Pain Points

| 传统方式 Traditional | Cue 方案 Cue Solution |
|---------------------|----------------------|
| 跨站搜索、机械下载、低效比对<br>Endless searching, manual downloads | 自动化信息搜集与验证<br>Automated info collection & verification |
| LLM 幻觉、无法溯源的黑盒输出<br>LLM hallucinations, black-box outputs | 「白盒」证据工程，每结论都有据可查<br>White-box evidence engineering, every conclusion traceable |
| 调研经验难以复用<br>Hard to reuse research experience | 沉淀为可复用的技能搭子<br>Reusable skill partners (SOPs) |

### 🔍 核心差异 | Core Differentiation

**不只是工具，更是伙伴 | Not Just a Tool, But a Partner**

- **低幻觉 Low Hallucination**: 全局事实校验体系，长程多步任务误差率极低
- **可溯源 Traceable**: 每个结论都附带完整证据链与原始来源
- **可复用 Reusable**: 优秀调研路径自动沉淀为技能搭子 (SOP)
- **个性化 Personalized**: 从任务规划到结果呈现，成为你的专属数字分身

---

## 🚀 快速开始 | Quick Start

```bash
# 深度研究 | Deep Research
/cue Tesla 2024 Financial Analysis

# 指定研究模式 | Specify Research Mode
/cue --mode fund-manager CATL Investment Analysis

# 自然语言输入 | Natural Language
分析一下新能源汽车行业竞争格局
Analyze the competitive landscape of the EV industry
```

---

## 📚 命令列表 | Command Reference

| 命令 Command | 功能 Function | 配额 Quota |
|--------------|---------------|------------|
| `/cue <topic>` | 深度研究 Deep Research | 3/day guest, unlimited registered |
| `/cue --mode <role> <topic>` | 指定模式研究 Mode-specific Research | Same as above |
| `/monitor generate` | 从报告生成监控 Generate monitors from report | Unlimited |
| `/register <api_key>` | 绑定 API Key Bind API Key | Unlimited |
| `/usage` | 查看配额 Check quota | Unlimited |
| `/help` | 显示帮助 Show help | Unlimited |

---

## 🎭 研究模式 | Research Modes

| 模式 Mode | 说明 Description | 适用场景 Use Case |
|-----------|------------------|-------------------|
| `理财顾问` / `advisor` | 投资建议、配置方案 Investment advice & portfolio | 个人投资决策 Personal investment |
| `研究员` / `researcher` | 产业链分析、竞争格局 Industry analysis & competition | 行业研究 Industry research |
| `基金经理` / `fund-manager` | 估值模型、投资策略 Valuation & investment strategy | 专业投资分析 Professional analysis |

---

## 📊 监控功能 | Monitoring Features

### 从研究报告生成监控 | Generate Monitors from Research

```bash
# 完成研究后，生成监控项
# After completing research, generate monitors
/monitor generate
```

**工作流程 Workflow:**
1. 完成深度研究 Complete deep research
2. 输入 `/monitor generate`
3. 系统自动提取关键信号 System extracts key signals
4. 监控项激活并定期执行 Monitors activate and run periodically

---

## 👤 用户类型 | User Types

### 体验用户 Guest User
- 使用默认 API Key Uses default API Key
- 每日 3 次深度研究配额 3 research sessions/day
- 独立工作空间 Independent workspace

### 注册用户 Registered User
- 绑定自己的 Cue API Key Bind personal API Key
- 无本地配额限制 No local quota limits
- 独立工作空间 Independent workspace

**注册流程 Registration:**
1. 访问 Visit https://cuecue.cn → 注册账号 Register
2. 获取 API Key Get API Key (Settings → API Keys)
3. 输入 Enter `/register sk-your-key`

---

## ⚙️ 环境变量 | Environment Variables

```bash
export CUECUE_API_KEY="sk-xxx"          # Cue API 密钥
export CUECUE_BASE_URL="https://cuecue.cn"  # Cue 服务地址
```

---

## 📖 使用示例 | Usage Examples

### 自然语言（推荐）| Natural Language (Recommended)
```
分析宁德时代竞争优势
Analyze CATL's competitive advantages

新能源汽车行业投资前景如何？
What's the investment outlook for the EV industry?

基金经理视角分析茅台投资价值
Analyze Moutai's investment value from fund manager perspective
```

### 显式命令 | Explicit Commands
```
/cue 特斯拉 2024 财务分析
/cue Tesla 2024 Financial Analysis

/cue --mode 研究员 锂电池产业链
/cue --mode researcher Lithium battery industry chain

/cue --mode 基金经理 特斯拉2024投资分析
/cue --mode fund-manager Tesla 2024 Investment Analysis
```

---

## 🔄 工作流程 | Workflows

### 深度研究工作流 | Research Workflow
```
User Input
    ↓
[Cue Router]
    ↓
├─ Explicit command? → Execute directly
└─ Natural language? → Intent recognition
    ↓
Deep Research → CueCue API
    ↓
Async execution + Auto-push results
```

### 监控生成工作流 | Monitor Generation Workflow
```
Research Report Complete
    ↓
/monitor generate
    ↓
Parse report → Extract key signals
    ↓
Generate monitor configuration
    ↓
Activate monitor tasks
    ↓
Periodic execution + Trigger notifications
```

---

## 🏢 典型应用场景 | Use Cases

### 场景一：消失的重复劳动 | Eliminate Repetitive Work
- **财富管理** | Wealth Management: 一键对比全市场竞品，生成深度解读报告
- **信贷审查** | Credit Review: 自动交叉验证企业信披、工商司法、行业政策
- **营销情报** | Marketing Intelligence: 定时收集行业异动，精准提取相关条款

### 场景二：捕捉水面下的商机 | Capture Hidden Opportunities
- **股权激励监控** | Equity Incentive Monitoring: 锁定激励计划到期公司，定位高净值客户需求
- **投行/固收前瞻** | Investment Banking/Fixed Income: 监测发债意向、并购传闻，抢先建立连接
- **动态风险穿透** | Dynamic Risk Analysis: 关联路径分析，提前发现传导风险

### 场景三：高质内容的策展工厂 | Content Curation Factory
- **AEO 深度适配** | AEO Optimized: 输出自带结构化数据与引用，天然适配 AI 搜索
- **多维模块化输出** | Multi-dimensional Output: 自动生成竞品矩阵、事件时序等多维度分析

---

## ✨ 核心特性 | Core Features

### 🔬 白盒证据工程 | White-Box Evidence Engineering
- ✅ **低幻觉 Low Hallucination**: 全局事实校验，误差率极低
- 🔗 **完整证据链 Full Evidence Chain**: 每个结论都有据可查、可溯源
- 📋 **原始来源引用** | Original Source Citations: 过滤网络噪声，只给真实干货

### 🤖 Multi-Agent 自动化 | Multi-Agent Automation
- 🔄 **大规模信息搜集** | Large-scale Info Collection: 自动化搜索、下载、比对
- ✔️ **验证分析** | Verification & Analysis: 多 Agent 并行验证，确保准确性
- ⏱️ **5-10 分钟完成** | 5-10 Min Completion: 将调研从「手工时代」推向「自动化时代」

### 👤 个性化与复用 | Personalization & Reusability
- 🎭 **专属数字分身** | Digital Twin: 从任务规划到结果呈现，完全个性化
- 💾 **技能搭子沉淀** | Skill Partner (SOP): 优秀调研路径自动沉淀为可复用模板
- 📈 **持续进化** | Continuous Improvement: 越用越懂你，决策分析更有针对性

### 🔧 技能功能 | Skill Capabilities
- 📝 **深度研究** | Deep Research: `/cue <topic>` 一键生成专业报告
- 🎭 **多模式支持** | Multi-mode: 理财顾问/研究员/基金经理三种视角
- 📊 **智能监控** | Intelligent Monitoring: `/monitor generate` 从报告自动提取监控信号
- 👥 **多用户管理** | Multi-user: 体验用户 3次/天，注册用户无限制
- 🔔 **自动推送** | Auto-push: 研究完成自动通知结果

---

## 🔗 相关链接 | Links

- **CueCue Platform**: https://cuecue.cn
- **OpenClaw Docs**: https://docs.openclaw.ai
- **ClawHub Skills**: https://clawhub.com/skills

---

## 📌 关于 Cue | About Cue

**Cue** 采用 Multi-Agent 架构，实现大规模信息搜集处理与验证分析的自动化，构建起行业首个「白盒」证据工程。

> 不只提供答案，更提供支撑答案的完整证据链。
> Not just answers, but the complete evidence chain supporting those answers.

---

*Powered by [CueCue](https://cuecue.cn) | [OpenClaw](https://openclaw.ai) Skill v1.0*
