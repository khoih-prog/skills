# Post-Installation Setup

> **⚠️ 重要：安装 Skill 后必须手动完成配置！**

## 安装 ≠ 配置完成

安装本 Skill 只是将代码放到你的 `workspace/skills/` 目录。

**必须手动运行初始化脚本** 来创建 FIS 3.1 架构所需的目录结构。

---

## 配置步骤

### Step 1: 阅读安装检查清单

```bash
cat ~/.openclaw/workspace/skills/fis-architecture/INSTALL_CHECKLIST.md
```

确认你理解：
- ✅ 将创建哪些文件夹
- ✅ 自动清理行为
- ✅ 数据安全措施

### Step 2: 运行初始化脚本

```bash
cd ~/.openclaw/workspace/skills/fis-architecture
python3 examples/init_fis31.py
```

这个脚本会：
1. **创建共享中心** `fis-hub/.fis3.1/`
   - memories/ (分层共享记忆)
   - skills/ (技能注册表)
   - lib/ (Python 库)
   - heartbeat/
   - subagent_registry.json

2. **创建 Agent 分形扩展** `workspace/.fis3.1/`
   - local_cache/
   - skill_manifest.json

### Step 3: 验证配置

```bash
# 检查共享中心
ls ~/.openclaw/fis-hub/.fis3.1/

# 检查 Agent 扩展
ls ~/.openclaw/workspace/.fis3.1/

# 测试导入
python3 -c "
import sys
sys.path.insert(0, '/home/muselinn/.openclaw/fis-hub/.fis3.1/lib')
from subagent_lifecycle import SubAgentLifecycleManager
print('✅ FIS 3.1 configured successfully')
"
```

---

## 如果没有配置会怎样？

**错误示例**:
```python
from lib.subagent_lifecycle import SubAgentLifecycleManager
# ❌ ModuleNotFoundError: No module named 'lib'

# 或者
manager = SubAgentLifecycleManager("cybermao")
# ❌ FileNotFoundError: subagent_registry.json not found
```

**解决**: 运行 `python3 examples/init_fis31.py`

---

## 为多个 Agent 配置

如果你有多个 Agent (如 pulse, painter):

```bash
# 为每个 Agent 创建扩展
python3 examples/setup_agent_extension.py cybermao
python3 examples/setup_agent_extension.py pulse
python3 examples/setup_agent_extension.py painter
```

---

## 配置后检查清单

- [ ] 共享中心已创建: `fis-hub/.fis3.1/`
- [ ] Agent 扩展已创建: `workspace/.fis3.1/`
- [ ] 可以导入 `subagent_lifecycle`
- [ ] 可以创建 SubAgent
- [ ] 已阅读 AGENT_GUIDE.md

---

## 故障排除

### 问题: "No module named 'lib'"
**原因**: Python 找不到 FIS 库路径
**解决**:
```python
import sys
sys.path.insert(0, '/home/muselinn/.openclaw/fis-hub/.fis3.1/lib')
```

### 问题: "subagent_registry.json not found"
**原因**: 未运行初始化脚本
**解决**: `python3 examples/init_fis31.py`

### 问题: "Permission denied"
**原因**: 目录权限问题
**解决**: `chmod -R u+rw ~/.openclaw/`

---

*配置完成后，别忘了阅读 [AGENT_GUIDE.md](./AGENT_GUIDE.md) 学习如何正确使用 SubAgent！*
