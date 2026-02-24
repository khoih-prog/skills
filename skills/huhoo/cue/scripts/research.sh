#!/bin/bash
# CueCue Deep Research - 异步研究执行器 (v2.2 - 用户管理集成)
# 特点：支持多用户配额管理，首次使用欢迎

set -e

TOPIC="$1"
CHAT_ID="${2:-}"
OUTPUT_FORMAT="${3:-markdown}"

# 脚本路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_TRACKER="$SCRIPT_DIR/task-tracker.sh"
NOTIFIER="$SCRIPT_DIR/notifier.sh"
REPORT_CHECKER="$SCRIPT_DIR/report-checker.sh"
USER_MANAGER="$SCRIPT_DIR/user-manager.sh"

# 初始化用户管理
$USER_MANAGER init 2>/dev/null || true

# 检查参数
if [ -z "$TOPIC" ]; then
  echo '{"error": "Research topic is required"}' >&2
  exit 1
fi

# 确保用户存在（首次使用会创建用户）
USER_INFO=$($USER_MANAGER info "$CHAT_ID" 2>/dev/null)
if [ -z "$USER_INFO" ]; then
    # 首次使用，创建用户并显示欢迎
    $USER_MANAGER ensure "$CHAT_ID" 2>/dev/null
    $SCRIPT_DIR/welcome-handler.sh "$CHAT_ID"
    exit 0
fi

# 检查配额
QUOTA_CHECK=$($USER_MANAGER check-quota "$CHAT_ID" research 2>/dev/null)
ALLOWED=$(echo "$QUOTA_CHECK" | jq -r '.allowed // false')

if [ "$ALLOWED" != "true" ]; then
    REMAINING=$(echo "$QUOTA_CHECK" | jq -r '.remaining // 0')
    cat << EOF
⚠️ 今日研究配额已用完

今日已使用：3/3 次
剩余配额：0 次

💡 获取更多配额：
1. 访问 https://cuecue.cn 注册账号
2. 获取 API Key（Settings → API Keys）
3. 输入：/register sk-您的APIKey

绑定后可享受：
✓ 无本地配额限制
✓ 独立 API Key
EOF
    exit 1
fi

# 获取用户的 API Key
USER_API_KEY=$($USER_MANAGER apikey "$CHAT_ID" 2>/dev/null)

if [ -z "$USER_API_KEY" ]; then
    echo '{"error": "API Key not configured. Please set CUECUE_API_KEY or register with /register"}' >&2
    exit 1
fi

# 获取配额信息用于显示
QUOTA_REMAINING=$(echo "$QUOTA_CHECK" | jq -r '.remaining // 0')
USER_TYPE=$($USER_MANAGER type "$CHAT_ID" 2>/dev/null)

# 创建持久化日志文件
LOG_DIR="${HOME}/.cuecue/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESEARCH_LOG="$LOG_DIR/research_${TIMESTAMP}_$(echo "$TOPIC" | md5sum | cut -c1-8).log"
TEMP_OUTPUT=$(mktemp)

KEEP_RESEARCH_LOG="${KEEP_RESEARCH_LOG:-false}"

cleanup() {
    if [ "$KEEP_RESEARCH_LOG" = "true" ] && [ -f "$TEMP_OUTPUT" ]; then
        cp "$TEMP_OUTPUT" "$RESEARCH_LOG"
        echo "📄 研究过程日志已保存: $RESEARCH_LOG" >&2
    fi
    rm -f "$TEMP_OUTPUT"
}
trap cleanup EXIT

# ============================================
# 启动研究
# ============================================
echo "🔍 正在启动深度研究..." >&2

# 使用用户的 API Key 启动研究
export CUECUE_API_KEY="$USER_API_KEY"
cuecue-research "$TOPIC" --verbose > "$TEMP_OUTPUT" 2>&1 &
RESEARCH_PID=$!

# 等待并提取进度链接
REPORT_URL=""
LINK_WAIT_TIME=0
MAX_LINK_WAIT=30

while [ $LINK_WAIT_TIME -lt $MAX_LINK_WAIT ]; do
    if grep -q "cuecue.cn/c/" "$TEMP_OUTPUT" 2>/dev/null; then
        REPORT_URL=$(grep -oP 'https://cuecue.cn/c/[^ ]+' "$TEMP_OUTPUT" | head -1)
        break
    fi
    sleep 1
    LINK_WAIT_TIME=$((LINK_WAIT_TIME + 1))
done

if [ -z "$REPORT_URL" ]; then
    echo "❌ 无法获取研究进度链接" >&2
    kill $RESEARCH_PID 2>/dev/null || true
    wait $RESEARCH_PID || true
    exit 1
fi

# ============================================
# 同步验证：确保链接可访问
# ============================================
echo "🔗 验证研究链接..." >&2

VERIFY_ATTEMPTS=3
VERIFY_SUCCESS=false

for i in $(seq 1 $VERIFY_ATTEMPTS); do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$REPORT_URL" 2>/dev/null || echo "000")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        VERIFY_SUCCESS=true
        echo "✅ 链接验证通过" >&2
        break
    else
        echo "   验证尝试 $i/$VERIFY_ATTEMPTS: HTTP $HTTP_STATUS" >&2
        sleep 2
    fi
done

if [ "$VERIFY_SUCCESS" = "false" ]; then
    echo "⚠️ 链接验证失败，但研究可能仍在进行" >&2
    echo "   报告地址: $REPORT_URL" >&2
fi

# ============================================
# 记录配额使用
# ============================================
$USER_MANAGER use-quota "$CHAT_ID" research 2>/dev/null || true

# ============================================
# 创建任务记录
# ============================================
TASK_ID=$($TASK_TRACKER create "$TOPIC" "$REPORT_URL" "$CHAT_ID")

# ============================================
# 输出启动结果
# ============================================
echo "" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo "✅ 深度研究已启动" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo "" >&2
echo "📋 研究主题：$TOPIC" >&2
echo "🆔 任务ID：$TASK_ID" >&2
echo "" >&2
echo "🔗 实时进度：$REPORT_URL" >&2
echo "" >&2
echo "⏱️ 预计耗时：5-10 分钟" >&2

# 显示配额信息
if [ "$USER_TYPE" = "registered" ]; then
    echo "💳 账户类型：注册用户（无限制）" >&2
else
    NEW_REMAINING=$((QUOTA_REMAINING - 1))
    echo "📊 今日剩余：${NEW_REMAINING}/3 次研究" >&2
fi

echo "🔔 完成后将自动推送结果到当前对话" >&2
echo "" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo "💡 提示：研究进行中，您无需等待，可以继续其他工作" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2

# ============================================
# 启动后台监控进程
# ============================================
nohup "$NOTIFIER" "$TASK_ID" "$RESEARCH_PID" "$TEMP_OUTPUT" > /dev/null 2>&1 &
NOTIFIER_PID=$!
echo "[$(date)] 后台监控已启动 (PID: $NOTIFIER_PID)" >> /tmp/cuecue-async.log

# 可选：启动即时预检
(
    sleep 15
    PRE_CHECK=$($REPORT_CHECKER "$REPORT_URL" "check" 2>/dev/null)
    IS_LOADING=$(echo "$PRE_CHECK" | jq -r '.is_loading // false')
    
    if [ "$IS_LOADING" = "true" ]; then
        echo "[$(date)] 任务 $TASK_ID 预检：研究正在正常进行" >> /tmp/cuecue-async.log
    fi
) &

# ============================================
# 输出 JSON 结果
# ============================================
cat << EOF
{
  "success": true,
  "task_id": "$TASK_ID",
  "topic": "$TOPIC",
  "report_url": "$REPORT_URL",
  "status": "running",
  "verified": $VERIFY_SUCCESS,
  "quota_remaining": $NEW_REMAINING,
  "user_type": "$USER_TYPE",
  "message": "研究已启动，预计5-10分钟完成"
}
EOF
