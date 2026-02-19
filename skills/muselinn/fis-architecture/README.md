# FIS Architecture 3.1 Lite

[![Version](https://img.shields.io/badge/version-3.1.1-blue.svg)](./skill.json)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

> **Federal Intelligence System (FIS) 3.1 Lite**
> 
> OpenClaw 多 Agent 协作架构 - 分形文件系统 + 零污染 Core Files + 纯文件机制

## 🌟 核心特性

- **分形架构** - 每个 Agent 工作区是完整缩放的系统副本
- **零污染** - 绝不修改其他 Agent 的 `MEMORY.md` / `HEARTBEAT.md`
- **纯文件机制** - 无服务/无数据库，JSON + Python
- **SubAgent 生命周期** - 工卡系统 + 自动清理
- **工卡图片生成** - 机票风格，支持批量生成
- **任务票据管理** - 创建/更新/完成 + 统计
- **死锁检测** - 自动检测任务依赖循环

## 📦 安装与配置

### ⚠️ 重要：两步流程

**Step 1: 安装 Skill**
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/cybermao/fis-architecture.git
```

**Step 2: 配置 FIS 架构 (必须!)**
```bash
cd fis-architecture
python3 examples/init_fis31.py
```

**安装 ≠ 配置完成！** 必须运行初始化脚本创建目录结构。

### 安装前检查

**[INSTALL_CHECKLIST.md](./INSTALL_CHECKLIST.md)** - 文件夹改动告知义务  
**[POST_INSTALL.md](./POST_INSTALL.md)** - 详细配置指南

安装本 Skill 将创建以下目录：
```
~/.openclaw/
├── fis-hub/.fis3.1/     # 共享基础设施 (手动创建)
├── workspace/.fis3.1/             # CyberMao 扩展 (手动创建)
├── workspace-radar/.fis3.1/       # Pulse 扩展 (可选)
└── workspace-subagent_{id}/       # 动态创建 (自动清理)
```

## 🚀 快速开始

### 1. 创建 SubAgent

```python
from lib.subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

manager = SubAgentLifecycleManager("cybermao")

# 发放工卡
card = manager.spawn(
    name="Worker-001",
    role=SubAgentRole.WORKER,
    task_description="实现 PTVF 滤波算法",
    timeout_minutes=120
)

print(f"工号: {card['employee_id']}")
# 输出: CYBERMAO-SA-2026-0001
```

### 2. 生成工卡图片

```python
# 单张工卡
image_path = manager.generate_badge_image(card['employee_id'])

# 批量工卡 (2x2 网格)
multi_image = manager.generate_multi_badge_image([id1, id2, id3, id4])
```

### 3. 终止并自动清理

```python
# 终止 SubAgent (自动删除 workspace-subagent_{id}/)
manager.terminate(card['employee_id'], "completed")
# ✅ 工作区文件夹已自动清理
```

## 📚 文档

- **[SKILL.md](./SKILL.md)** - 完整架构文档
- **[AGENT_GUIDE.md](./AGENT_GUIDE.md)** - ⭐ Agent 使用指南 (什么时候用 SubAgent)
- **[POST_INSTALL.md](./POST_INSTALL.md)** - ⭐ 安装后配置指南 (必须阅读!)
- **[CONFIGURATION.md](./CONFIGURATION.md)** - ⭐ 自定义 Shared Hub 名称
- **[OPENCLAW_COMPATIBILITY.md](./OPENCLAW_COMPATIBILITY.md)** - ⭐ OpenClaw 版本兼容性
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - 快速参考手册
- **[INSTALL_CHECKLIST.md](./INSTALL_CHECKLIST.md)** - 安装前检查清单

## 🏗️ 架构

```
~/.openclaw/
├── workspace/                    # CyberMao (主控)
│   ├── [9 Core Files]
│   └── .fis3.1/                 # FIS 3.1 扩展
│
├── workspace-radar/              # Pulse (雷达专家)
│   └── .fis3.1/
│       └── skill_manifest.json  # 技能清单
│
├── workspace-painter/            # Painter (视觉专家)
│   └── .fis3.1/
│
└── fis-hub/.fis3.1/    # 共享中心
    ├── memories/                 # 分层共享记忆
    ├── skills/                   # 技能注册表
    ├── lib/                      # Python 库
    └── subagent_registry.json    # 子代理注册表
```

## 🔄 更新日志

### 3.1.1 (2026-02-18)
- ✅ 添加 SubAgent 自动清理 (`terminate()` 自动删文件夹)
- ✅ 添加安装检查清单 (应知必知义务)
- ✅ 添加 `skill.json` 元数据
- ✅ 创建 Git repo 准备发布

### 3.1.0 (2026-02-17)
- 🎉 FIS 3.1 Lite 初始发布
- 分形文件架构
- SubAgent 工卡系统
- 工卡图片生成

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

[MIT](./LICENSE)

---

*FIS 3.1 Lite - 质胜于量 🐱⚡*
