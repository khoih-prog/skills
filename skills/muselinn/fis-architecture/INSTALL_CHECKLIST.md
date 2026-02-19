# Installation Checklist

## Pre-Installation Notice (应知必知义务)

**警告**: 安装此 Skill 将对您的系统产生以下文件夹改动：

### 1. 新增目录结构

```
~/.openclaw/
├── fis-hub/.fis3.1/        # ⭐ 共享基础设施 (自动创建)
│   ├── memories/                    # 共享记忆存储
│   │   ├── working/                 # 工作记忆 (TTL: 1h)
│   │   ├── short_term/              # 短期记忆 (TTL: 24h)
│   │   └── long_term/               # 长期记忆 (永久)
│   ├── skills/
│   │   ├── registry.json            # 技能注册表
│   │   └── manifests/               # Agent技能清单
│   ├── lib/                         # Python库
│   │   ├── memory_manager.py
│   │   ├── deadlock_detector.py
│   │   ├── skill_registry.py
│   │   ├── subagent_lifecycle.py    # ⭐ 新增自动清理功能
│   │   └── badge_image_pil.py
│   ├── heartbeat/                   # 心跳文件
│   └── subagent_registry.json       # 子代理注册表
│
└── workspace-subagent_{id}/         # ⭐ 动态创建 (子代理工作区)
    ├── AGENTS.md
    ├── TODO.md
    └── EMPLOYEE_CARD.json
```

### 2. 文件改动

| 位置 | 操作 | 说明 |
|------|------|------|
| `workspace/.fis3.1/` | 创建 | CyberMao 扩展目录 |
| `workspace-radar/.fis3.1/` | 创建 | Pulse 扩展目录 |
| `workspace-painter/.fis3.1/` | 创建 | Painter 扩展目录 |
| `AGENT_REGISTRY.md` | 更新 | 添加 FIS 环境配置 |
| `HEARTBEAT.md` | 更新 | 添加 FIS 维护检查 |
| `TOOLS.md` | 更新 | 添加 FIS 工具说明 |

### 3. 自动清理行为

**子代理终止时** (`subagent_lifecycle.terminate()`):
- ✅ 自动删除 `workspace-subagent_{id}/` 文件夹
- ✅ 保留 registry 记录用于审计
- ⚠️ 已删除的文件**不可恢复**

**批量清理命令**:
```bash
python3 ~/.openclaw/system/scripts/fis_subagent_cleanup.py
```

### 4. 数据安全

- **Core Files 保护**: 绝不修改 `MEMORY.md`, `HEARTBEAT.md` 等核心文件
- **Agent 隔离**: 各 Agent 工作区相互独立
- **权限控制**: SubAgent 只能访问授权资源
- **备份建议**: 重要数据请定期备份 `fis-hub/` 目录

### 5. 卸载说明

如需完全卸载本 Skill:

```bash
# 1. 停止所有 SubAgent
pkill -f subagent

# 2. 清理 SubAgent 工作区
rm -rf ~/.openclaw/workspace-subagent_*

# 3. 清理 FIS 3.1 目录 (可选)
rm -rf ~/.openclaw/fis-hub/.fis3.1/
rm -rf ~/.openclaw/workspace/.fis3.1/
rm -rf ~/.openclaw/workspace-*/.fis3.1/

# 4. 恢复备份的 Core Files (如有修改)
# (SKILL.md 不会修改 Core Files，此步可跳过)
```

## 安装确认

在安装前，请确认您已阅读并理解上述改动：

- [ ] 我了解将创建 `fis-hub/.fis3.1/` 目录结构
- [ ] 我了解各 Agent 将获得 `.fis3.1/` 扩展目录
- [ ] 我了解 SubAgent 终止时会自动删除工作区文件夹
- [ ] 我了解已删除的 SubAgent 文件夹不可恢复
- [ ] 我已备份重要数据（如需要）
- [ ] 我同意上述改动并继续安装

## 安装步骤

```bash
# 1. 验证安装环境
python3 -c "import sys; print(sys.version)"

# 2. 检查目录权限
ls -la ~/.openclaw/

# 3. 运行初始化
python3 examples/init_fis31.py

# 4. 验证安装
python3 -c "from lib.subagent_lifecycle import SubAgentLifecycleManager; print('✅ FIS 3.1 Lite installed')"
```

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| Permission denied | 检查 `~/.openclaw/` 目录权限 |
| Module not found | 确保从 skill 目录运行，或设置 PYTHONPATH |
| Import error | 检查 `lib/` 目录是否存在且包含 `.py` 文件 |
| SubAgent 未清理 | 运行 `fis_subagent_cleanup.py` 手动清理 |

---

**安装前请仔细阅读本清单，确保理解所有文件系统改动。**

*FIS 3.1 Lite - 透明、可控、可审计*
