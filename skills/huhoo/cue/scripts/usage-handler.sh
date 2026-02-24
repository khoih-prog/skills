#!/bin/bash
# 配额查询命令处理
# /usage

CHAT_ID="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_MANAGER="$SCRIPT_DIR/user-manager.sh"

# 确保用户存在并获取配额状态
QUOTA_STATUS=$($USER_MANAGER quota "$CHAT_ID")
USER_TYPE=$(echo "$QUOTA_STATUS" | jq -r '.type')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 配额使用情况"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$USER_TYPE" = "registered" ]; then
    echo "👤 用户类型：注册用户"
    echo ""
    echo "✅ 深度研究：无限制"
    echo "✅ 快速搜索：无限制"
    echo ""
    echo "💡 使用您自己的 API Key，不受本地配额限制"
    echo ""
else
    RESEARCH_REMAINING=$(echo "$QUOTA_STATUS" | jq -r '.research_remaining')
    RESEARCH_LIMIT=$(echo "$QUOTA_STATUS" | jq -r '.research_limit')
    SEARCH_REMAINING=$(echo "$QUOTA_STATUS" | jq -r '.search_remaining')
    SEARCH_LIMIT=$(echo "$QUOTA_STATUS" | jq -r '.search_limit')
    
    echo "👤 用户类型：体验用户"
    echo ""
    echo "📊 深度研究：${RESEARCH_REMAINING}/${RESEARCH_LIMIT} 次"
    echo "📊 快速搜索：${SEARCH_REMAINING}/${SEARCH_LIMIT} 次"
    echo ""
    
    # 进度条显示
    RESEARCH_USED=$((RESEARCH_LIMIT - RESEARCH_REMAINING))
    echo -n "研究配额：["
    for i in $(seq 1 $RESEARCH_USED); do echo -n "█"; done
    for i in $(seq 1 $RESEARCH_REMAINING); do echo -n "░"; done
    echo "]"
    echo ""
    
    if [ "$RESEARCH_REMAINING" -eq 0 ]; then
        echo "⚠️ 今日研究配额已用完"
        echo ""
        echo "💡 获取更多配额："
        echo "   输入 /register <api_key> 绑定自己的 Key"
        echo "   去 https://cuecue.cn 注册获取 API Key"
    else
        echo "✅ 今日还可进行 ${RESEARCH_REMAINING} 次深度研究"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📅 配额每日 0:00 自动重置"
echo ""
echo "---"
echo "*使用 /help 查看所有命令*"
