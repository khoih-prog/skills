#!/bin/bash
# ClawHub Publish Guide for Cue Skill

VERSION="1.0.0"
PKG_FILE="/usr/lib/node_modules/openclaw/skills/cue/dist/cue-v${VERSION}.tar.gz"

echo "📤 ClawHub 发布指南 | Publish Guide"
echo "===================================="
echo ""

# Check if logged in
if ! clawhub whoami &> /dev/null; then
    echo "⚠️  需要登录 ClawHub | Login Required"
    echo ""
    echo "请先登录 | Please login first:"
    echo "  clawhub login"
    echo ""
    echo "如果您没有账号 | If you don't have an account:"
    echo "  1. 访问 Visit: https://clawhub.com"
    echo "  2. 注册账号 Register"
    echo "  3. 获取 API Token Get API Token"
    echo "  4. 运行 Run: clawhub login"
    echo ""
    exit 1
fi

echo "✅ 已登录 | Logged in as:"
clawhub whoami
echo ""

echo "📦 发布信息 | Publish Info:"
echo "  名称 Name: cue"
echo "  版本 Version: ${VERSION}"
echo "  包文件 Package: ${PKG_FILE}"
echo ""

echo "🚀 开始发布 | Starting publish..."
clawhub publish "${PKG_FILE}" \
    --name "Cue" \
    --slug "cue" \
    --version "${VERSION}" \
    --tags "finance,research,ai,monitoring,investment,financial-analysis"

echo ""
echo "✅ 发布完成！| Publish Complete!"
echo ""
echo "查看技能 | View skill:"
echo "  https://clawhub.com/skills/cue"
