# Configuration Guide - FIS 3.1 Lite

> **自定义 Shared Hub 名称**  
> FIS 架构是通用的，不绑定任何特定领域

---

## 默认配置

安装后默认使用：
```
~/.openclaw/
├── fis-hub/                      # ⭐ 默认 Shared Hub
│   └── .fis3.1/                  # FIS 3.1 基础设施
├── workspace/                    # CyberMao 工作区
└── workspace-subagent_*/         # SubAgent 工作区
```

## 自定义 Shared Hub 名称

### 方法 1: 初始化时指定（推荐）

```bash
cd ~/.openclaw/workspace/skills/fis-architecture
python3 examples/init_fis31.py

# 提示时输入自定义名称：
# Enter shared hub name: my-research-project
```

这将创建：
```
~/.openclaw/
├── my-research-project/          # 你的自定义 Shared Hub
│   └── .fis3.1/
```

### 方法 2: 修改配置文件

编辑 `lib/fis_config.py`：

```python
# 修改默认名称
DEFAULT_SHARED_HUB_NAME = "my-research-project"
```

### 方法 3: 代码中动态设置

```python
from fis_config import set_shared_hub_name, get_shared_hub_path

# 设置自定义名称
set_shared_hub_name("my-research-project")

# 后续所有操作使用这个新路径
from subagent_lifecycle import SubAgentLifecycleManager
manager = SubAgentLifecycleManager("cybermao")  # 自动使用新路径
```

---

## 多项目支持

你可以为不同项目创建不同的 Shared Hub：

```bash
# 项目 1: 科研工作
python3 examples/init_fis31.py
# Enter shared hub name: research-lab

# 项目 2: 产品开发  
python3 examples/init_fis31.py
# Enter shared hub name: product-dev

# 项目 3: 团队协作
python3 examples/init_fis31.py
# Enter shared hub name: team-collaboration
```

每个 Shared Hub 完全独立：
```
~/.openclaw/
├── research-lab/
│   └── .fis3.1/
├── product-dev/
│   └── .fis3.1/
└── team-collaboration/
    └── .fis3.1/
```

---

## 命名建议

| 场景 | 推荐名称 |
|------|---------|
| 个人通用 | `fis-hub` (默认) |
| 科研项目 | `research-lab`, `lab-name` |
| 产品开发 | `product-dev`, `project-name` |
| 团队协作 | `team-hub`, `org-name` |
| 临时实验 | `experiment-2026`, `test-bed` |

---

## 迁移现有数据

如果你之前使用 `research-uav-gpr`，想迁移到新名称：

```bash
# 1. 复制数据
cp -r ~/.openclaw/research-uav-gpr ~/.openclaw/my-new-hub

# 2. 更新配置文件中的默认名称
# 编辑 lib/fis_config.py

# 3. 验证
python3 -c "
from fis_config import get_shared_hub_path
print(get_shared_hub_path())
"
```

---

## 检查当前配置

```python
from fis_config import get_shared_hub_path, DEFAULT_SHARED_HUB_NAME

print(f"Current hub name: {DEFAULT_SHARED_HUB_NAME}")
print(f"Current hub path: {get_shared_hub_path()}")
```

---

## 向后兼容

如果你已有 `research-uav-gpr` 数据，可以：

1. **继续使用**: 在初始化时输入 `research-uav-gpr`
2. **迁移数据**: 复制到新名称
3. **创建符号链接**: `ln -s research-uav-gpr fis-hub`

---

*FIS 3.1 Lite - 通用、灵活、可配置 🐱⚡*
