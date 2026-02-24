# Cue Skill - ClawHub 发布说明

## 📦 发布包信息

| 属性 | 值 |
|------|-----|
| 技能名称 | cue |
| 版本 | 1.0.0 |
| 包文件 | dist/cue-v1.0.0.tar.gz |
| 包大小 | 25KB |

---

## 🚀 发布步骤

### 1. 登录 ClawHub

```bash
clawhub login
```

如果您没有 ClawHub 账号：
1. 访问 https://clawhub.com
2. 注册账号
3. 在 Settings 中创建 API Token
4. 运行 `clawhub login` 并输入 Token

### 2. 发布技能

```bash
cd /usr/lib/node_modules/openclaw/skills/cue
./publish-guide.sh
```

或手动发布：

```bash
clawhub publish dist/cue-v1.0.0.tar.gz \
    --name "Cue" \
    --slug "cue" \
    --version "1.0.0" \
    --tags "finance,research,ai,monitoring,investment"
```

### 3. 验证发布

```bash
# 搜索技能
clawhub search cue

# 查看技能详情
clawhub info cue
```

---

## 📋 技能信息

**名称**: Cue - 智能投研助手

**描述**: AI-powered financial research assistant with multi-user support and intelligent monitoring generation. Conduct deep research on markets, companies, and industries using multi-agent AI analysis.

**标签**: finance, research, ai, monitoring, investment, financial-analysis

**功能特性**:
- 深度研究 (`/cue <topic>`)
- 研究模式 (`--mode`)
- 监控生成 (`/monitor generate`)
- 用户管理 (`/register`, `/usage`)
- 配额控制
- 中英双语支持

---

## 🔧 安装使用

用户安装命令：

```bash
clawhub install cue
```

---

## 📁 包内容

```
cue-v1.0.0/
├── SKILL.md              # 技能文档（中英双语）
├── manifest.json         # 包清单
├── package.sh            # 打包脚本
├── publish-guide.sh      # 发布指南
├── lib/                  # 库文件
└── scripts/              # 脚本文件
    ├── cue.sh            # 主路由
    ├── research.sh       # 研究执行
    ├── monitor-generator.sh  # 监控生成
    ├── user-manager.py   # 用户管理
    ├── notifier.sh       # 通知推送
    └── executor/         # 执行器
```

---

## ✅ 发布前检查清单

- [x] 技能功能完整
- [x] 测试验证通过
- [x] SKILL.md 文档完善（中英双语）
- [x] 打包成功
- [ ] 已登录 ClawHub
- [ ] 已发布
- [ ] 已验证发布成功

---

## 🔗 相关链接

- ClawHub: https://clawhub.com
- OpenClaw Docs: https://docs.openclaw.ai
- CueCue Platform: https://cuecue.cn
