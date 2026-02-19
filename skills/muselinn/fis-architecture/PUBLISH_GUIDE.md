# 发布到 ClawHub 指南

## 当前状态

✅ Git repo 已创建并提交  
✅ 18 个文件已跟踪  
✅ Repo 大小: 480K (干净)  

## 文件清单

```
fis-architecture/
├── .gitignore              # Git 忽略规则
├── skill.json              # Skill 元数据
├── README.md               # 项目主页文档
├── SKILL.md                # 完整架构文档
├── QUICK_REFERENCE.md      # 快速参考
├── INSTALL_CHECKLIST.md    # ⭐ 安装检查清单
├── examples/               # 示例代码
│   ├── init_fis31.py
│   ├── subagent_pipeline.py
│   └── generate_badges.py
└── lib/                    # Python 库
    ├── memory_manager.py
    ├── deadlock_detector.py
    ├── skill_registry.py
    ├── subagent_lifecycle.py
    ├── badge_image_pil.py
    ├── badge_generator.py
    └── badge_template.html
```

## 发布步骤

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 创建新仓库: cybermao/fis-architecture
# 然后推送本地代码

git remote add origin https://github.com/cybermao/fis-architecture.git
git branch -M main
git push -u origin main
```

### 2. 创建 Release

```bash
# 打标签
git tag -a v3.1.1 -m "FIS 3.1 Lite - Initial Release

Features:
- Fractal file system architecture
- SubAgent lifecycle with auto-cleanup
- Badge image generation (ticket style)
- Installation checklist"

git push origin v3.1.1
```

### 3. 发布到 ClawHub

```bash
# 使用 clawhub CLI
clawhub publish \
  --name fis-architecture \
  --version 3.1.1 \
  --description "FIS 3.1 Lite - Multi-agent collaboration framework" \
  --tags "multi-agent,architecture,subagent,badge" \
  --github https://github.com/cybermao/fis-architecture
```

或者手动上传:
1. 访问 https://clawhub.com
2. 点击 "Publish Skill"
3. 填写信息:
   - Name: `fis-architecture`
   - Version: `3.1.1`
   - Description: `Federal Intelligence System 3.1 Lite`
   - GitHub URL: `https://github.com/cybermao/fis-architecture`
4. 上传 `skill.json` 和 `README.md`

### 4. 验证发布

```bash
# 搜索已发布的 skill
clawhub search fis-architecture

# 安装测试
clawhub install fis-architecture
```

## 后续更新

### 版本更新流程

```bash
# 1. 修改代码
# ...

# 2. 更新版本号
# 修改 skill.json 中的 version

# 3. 提交更改
git add .
git commit -m "Fix: xxx bug"

# 4. 打新标签
git tag -a v3.1.2 -m "Bug fixes"
git push origin v3.1.2

# 5. 更新 clawhub
clawhub update fis-architecture --version 3.1.2
```

## 安装检查清单说明

**INSTALL_CHECKLIST.md** 是应知必知义务的核心：

1. **预安装告知** - 列出所有文件夹改动
2. **自动清理说明** - SubAgent 终止时自动删文件夹
3. **数据安全提示** - Core Files 保护、Agent 隔离
4. **卸载说明** - 完整的卸载步骤
5. **确认清单** - 用户必须勾选确认理解

这确保了用户在安装前完全了解系统将发生什么变化。

## 下一步

1. [ ] 创建 GitHub 仓库
2. [ ] 推送代码
3. [ ] 创建 v3.1.1 Release
4. [ ] 发布到 ClawHub
5. [ ] 分享 skill 链接

---

*Ready to publish 🚀*
