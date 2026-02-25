# AdGuard Home Skill 发布流程指南

本文档记录 AdGuard Home Skill 的标准发布流程，确保 ClawHub 和 GitHub 两个平台保持一致。

---

## 📋 发布前准备

### 1. 更新版本号

修改以下文件的版本号（遵循 SemVer 规范）：

- `clawhub.json` - `"version": "x.y.z"`
- `index.js` - 文件头部注释中的版本
- `README.md` - Version 部分
- `SKILL.md` / `SKILL.en.md` / `SKILL.zh-CN.md` - Version History 部分

### 2. 更新文档内容

**必须修改的文件：**

- `SKILL.en.md` - 英文版本（用于 ClawHub）
- `SKILL.zh-CN.md` - 中英文双语版本（用于 GitHub）
- `README.md` - 保持中英文双语
- `clawhub.json` - 更新 security.notes 和 changelog

**可能修改的文件：**

- `index.js` - 代码更新时
- 其他文档（SECURITY_AUDIT.md, TEST_REPORT.md 等）

---

## 🚀 发布步骤

### 步骤 1：准备 ClawHub 版本（英文）

```bash
cd /home/foxleoly/.openclaw/workspace/skills/adguard-home

# 复制英文版本到 SKILL.md
cp SKILL.en.md SKILL.md
```

### 步骤 2：发布到 ClawHub

```bash
# 发布新版本（等待前一次发布 60 秒后再试，避免 Rate Limit）
clawhub publish . --slug adguard-home --version x.y.z --changelog "更新说明（英文，简洁）"

# 如果 Rate limit exceeded，等待 10-60 秒后重试
```

**Changelog 编写规范：**
- 使用英文
- 简洁明了（50-100 字符）
- 突出主要变更（安全改进、新功能、Bug 修复）

**示例：**
```bash
--changelog "v1.2.4: English-only SKILL.md for ClawHub. Security: env vars or 1Password only."
--changelog "v1.2.3: Removed file loading from code. Env vars or 1Password only."
--changelog "v1.2.2: Removed file-based credential storage. Env vars only."
```

### 步骤 3：恢复 GitHub 版本（双语）

```bash
# 恢复中英文双语版本
cp SKILL.zh-CN.md SKILL.md
```

### 步骤 4：提交到 Git

```bash
# 检查变更
git status

# 添加所有变更
git add -A

# 提交（使用英文 commit message）
git commit -m "v1.2.4 Security Hardening

- SKILL.md: Bilingual (Chinese + English) for GitHub
- SKILL.en.md: English-only version for ClawHub publishing
- [主要变更说明 1]
- [主要变更说明 2]

Security: [安全相关说明]"

# 推送到 GitHub
git pull origin master --no-edit
git push origin master
```

**处理合并冲突：**
```bash
# 如果有冲突，优先使用本地版本
git checkout --ours SKILL.md SKILL.en.md SKILL.zh-CN.md README.md clawhub.json index.js
git add -A
git commit -m "v1.2.4 Security Hardening - Keep local version"
git push origin master
```

---

## 📝 版本发布清单

发布前检查：

- [ ] 版本号已更新（所有文件保持一致）
- [ ] SKILL.en.md 已更新（英文，用于 ClawHub）
- [ ] SKILL.zh-CN.md 已更新（双语，用于 GitHub）
- [ ] clawhub.json 已更新（version, changelog, security.notes）
- [ ] README.md 已更新（Version 部分）
- [ ] index.js 已更新（如代码有修改）
- [ ] 测试过新功能/修复（本地测试）
- [ ] 无敏感信息泄露（凭证、密钥等）

发布后检查：

- [ ] ClawHub 发布成功（记录 Skill ID）
- [ ] GitHub 推送成功
- [ ] 本地 SKILL.md 已恢复为双语版本

---

## 🔑 关键要点

### 1. 双版本策略

| 平台 | SKILL.md 内容 | 目的 |
|------|--------------|------|
| **ClawHub** | 英文 only | 国际化用户，避免编码问题 |
| **GitHub** | 中英文双语 | 中文用户友好，完整文档 |

### 2. 文件用途

| 文件 | 用途 |
|------|------|
| `SKILL.en.md` | ClawHub 发布源文件（纯英文） |
| `SKILL.zh-CN.md` | GitHub 备份（中英文双语） |
| `SKILL.md` | 工作文件（发布时切换） |

### 3. 安全要求

- ❌ **禁止**在代码或文档中存储明文凭证示例
- ✅ **只推荐**环境变量或 1Password CLI
- ✅ 文档明确说明文件配置已弃用
- ✅ 代码强制执行安全配置方式

### 4. Rate Limit 处理

ClawHub 有发布频率限制：
- 如果 `Rate limit exceeded`，等待 10-60 秒后重试
- 不要连续快速发布多个版本
- 建议单次发布完成所有变更

---

## 📊 版本历史模板

在 `SKILL.md` / `SKILL.en.md` / `SKILL.zh-CN.md` 中添加：

```markdown
## Version History

### v1.2.4 (2026-02-25) - [简短标题]

**[分类，如 Security Improvements]:**
- ✅ [变更 1]
- ✅ [变更 2]

### v1.2.3 (2026-02-25) - [简短标题]

...
```

---

## 🛠️ 快速命令参考

```bash
# 完整发布流程（替换 x.y.z 为实际版本号）
cd /home/foxleoly/.openclaw/workspace/skills/adguard-home
cp SKILL.en.md SKILL.md
clawhub publish . --slug adguard-home --version x.y.z --changelog "更新说明"
cp SKILL.zh-CN.md SKILL.md
git add -A
git commit -m "v1.2.4 [标题]"
git pull origin master --no-edit
git push origin master
```

---

## 📞 问题排查

### ClawHub 发布失败

**错误：`SKILL.md required`**
- 检查 SKILL.md 是否存在
- 检查文件权限（可读）
- 使用绝对路径：`clawhub publish /完整/路径/adguard-home ...`

**错误：`Rate limit exceeded`**
- 等待 10-60 秒后重试
- 不要连续发布

**错误：`version must be valid semver`**
- 版本号格式：`x.y.z`（如 `1.2.4`）
- 不要带 `v` 前缀

### Git 推送失败

**错误：`Updates were rejected`**
```bash
git pull origin master --no-edit
git push origin master
```

**错误：合并冲突**
```bash
git checkout --ours [文件名]
git add [文件名]
git commit -m "解决冲突"
git push
```

---

**最后更新**: 2026-02-25  
**版本**: v1.2.4  
**作者**: Leo Li (@foxleoly)
