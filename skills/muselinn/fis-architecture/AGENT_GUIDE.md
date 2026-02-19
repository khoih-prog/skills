# Agent Guide - FIS 3.1 Lite

> **给 Agent 的使用指南**  
> 当你被安装了 FIS Architecture skill，这份文档告诉你什么时候该用、怎么用。

---

## ⚠️ 安装后必须先配置！

**Skill 安装 ≠ 立即可用**

安装完成后，必须运行初始化脚本：

```bash
cd ~/.openclaw/workspace/skills/fis-architecture
python3 examples/init_fis31.py
```

这会创建：
- 共享中心 `fis-hub/.fis3.1/`
- 你的 Agent 扩展 `workspace/.fis3.1/`

详见 [POST_INSTALL.md](./POST_INSTALL.md)

---

## 你获得了什么能力？

安装此 skill 后，你可以：

```python
from lib.subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

manager = SubAgentLifecycleManager("你的Agent名")

# 1. 创建子代理
card = manager.spawn(name="Worker-001", role=SubAgentRole.WORKER, task="...")

# 2. 生成工卡图片
image_path = manager.generate_badge_image(card['employee_id'])

# 3. 检查超时
expired = manager.check_expired(auto_terminate=True)
```

---

## 决策树：什么时候用 SubAgent？

```
用户请求
    ↓
┌─────────────────────────────────────┐
│ 1. 任务需要多个专业角色协作？         │
│    (如: 程序员 + 审查员 + 测试员)    │
└─────────────────────────────────────┘
    ↓ 是                    ↓ 否
    ↓              ┌─────────────────────┐
    ↓              │ 2. 任务耗时 > 30分钟？│
    ↓              │    (会阻塞主会话)     │
    ↓              └─────────────────────┘
    ↓                      ↓ 是      ↓ 否
    ↓                      ↓  ┌─────────────────────┐
    ↓                      ↓  │ 3. 任务失败影响大？  │
    ↓                      ↓  │    (如: 生产环境)    │
    ↓                      ↓  └─────────────────────┘
    ↓                      ↓          ↓ 是    ↓ 否
    ↓                      ↓          ↓       ↓
┌──────────┐         ┌──────────┐  ┌──────────┐
│ ✅ 用    │         │ ✅ 考虑用 │  │ ❌ 不用  │
│ SubAgent │         │ SubAgent │  │ 直接处理 │
└──────────┘         └──────────┘  └──────────┘
```

---

## 具体场景对照表

| 场景 | 用 SubAgent？ | 原因 |
|------|--------------|------|
| "查天气" | ❌ 否 | 简单查询，直接处理 |
| "写个冒泡排序" | ❌ 否 | 简单代码，直接处理 |
| "读文件并总结" | ❌ 否 | 单线任务，直接处理 |
| "实现 PTVF 滤波算法 + 验证" | ✅ 是 | 需要 Worker + Reviewer 协作 |
| "设计一套 UI 组件" | ✅ 是 | 需要 Designer 独立输出 |
| "调研 + 实现 + 测试 完整功能" | ✅ 是 | 多阶段，可并行 |
| "处理 1000 个文件" | ✅ 是 | 可分片并行处理 |
| "紧急生产环境修复" | ✅ 是 | 失败影响大，需隔离 |

---

## 反模式：别这样做！

### ❌ 过度分解
```python
# 错误：为简单任务创建过多 SubAgent
planner = manager.spawn(role=SubAgentRole.PLANNER, task="规划")
worker = manager.spawn(role=SubAgentRole.WORKER, task="实现")
reviewer = manager.spawn(role=SubAgentRole.REVIEWER, task="审查")

# 用户只是想转换个文件格式...
```

### ❌ 不清理
```python
# 错误：创建了不终止
worker = manager.spawn(...)
# ... 任务完成 ...
# 忘了 terminate() → 僵尸代理
```

### ❌ 不检查超时
```python
# 错误：不检查过期代理
# 应该在 HEARTBEAT 中定期调用 check_expired()
```

---

## 最佳实践模式

### 模式 1：Worker-Reviewer 流水线
```python
# 适用：需要质量保证的代码/文档任务

worker = manager.spawn(
    name="实现者",
    role=SubAgentRole.WORKER,
    task="实现功能 X",
    timeout_minutes=60
)

# 等待 Worker 完成
# ...

reviewer = manager.spawn(
    name="审查者", 
    role=SubAgentRole.REVIEWER,
    task="审查功能 X 的实现",
    timeout_minutes=30
)

# Reviewer 完成后
manager.terminate(worker['employee_id'], "completed")
manager.terminate(reviewer['employee_id'], "completed")
```

### 模式 2：研究-执行 分离
```python
# 适用：需要调研再执行的任务

researcher = manager.spawn(
    name="研究员",
    role=SubAgentRole.RESEARCHER,
    task="调研最佳方案",
    timeout_minutes=30
)

# 获取研究结果
# ...

worker = manager.spawn(
    name="执行者",
    role=SubAgentRole.WORKER,
    task=f"按方案执行: {research_result}",
    timeout_minutes=60
)
```

### 模式 3：并行分片
```python
# 适用：大规模数据处理

tasks = ["处理文件1", "处理文件2", "处理文件3"]
workers = []

for i, task in enumerate(tasks):
    worker = manager.spawn(
        name=f"Worker-{i}",
        role=SubAgentRole.WORKER,
        task=task,
        timeout_minutes=30
    )
    workers.append(worker)

# 等待全部完成
# ...

# 批量清理
for worker in workers:
    manager.terminate(worker['employee_id'], "completed")
```

---

## 在你的 HEARTBEAT 中添加

```python
# ~/.openclaw/workspace/HEARTBEAT.md

## FIS 3.1 Lite 维护
```python
import sys
sys.path.insert(0, '/home/muselinn/.openclaw/fis-hub/.fis3.1/lib')
from subagent_lifecycle import SubAgentLifecycleManager

manager = SubAgentLifecycleManager("你的Agent名")

# 1. 检查并清理超时 SubAgent
expired = manager.check_expired(auto_terminate=True)
if expired:
    print(f"⏰ Auto-terminated expired: {expired}")

# 2. 报告活跃 SubAgent
active = manager.list_active()
if active:
    print(f"🟢 Active SubAgents: {len(active)}")
    for sa in active:
        print(f"   - {sa['employee_id']}: {sa['task']['description'][:30]}...")
```
```

---

## 快速检查清单

创建 SubAgent 前问自己：

- [ ] 这个任务**必须**多个角色协作吗？
- [ ] 这个任务会**阻塞用户**超过 30 分钟吗？
- [ ] 这个任务失败会造成**严重后果**吗？
- [ ] 我有明确的**终止计划**吗？

如果 4 个都选 "否" → **直接处理，别用 SubAgent**

---

## 记住

> **FIS 是工具，不是拐杖。**  
> 简单任务直接做，复杂任务才协作。  
> 不要为了用工具而用工具。

*FIS 3.1 Lite - 质胜于量 🐱⚡*
