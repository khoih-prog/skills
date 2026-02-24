#!/bin/bash
# CueCue Monitor - 创建实际监控项

set -e

MONITOR_CONFIG="$1"
OUTPUT_FILE="${2:-/tmp/monitor_create_result.json}"

if [ -z "$MONITOR_CONFIG" ]; then
    echo '{"error": "Monitor configuration is required"}' >&2
    exit 1
fi

# 检查环境变量
if [ -z "$CUECUE_API_KEY" ]; then
    echo '{"error": "CUECUE_API_KEY not configured"}' >&2
    exit 1
fi

# 如果是文件路径，读取内容
if [ -f "$MONITOR_CONFIG" ]; then
    MONITOR_CONFIG=$(cat "$MONITOR_CONFIG")
fi

echo "🔧 正在创建监控项..." >&2

# 解析监控配置
TITLE=$(echo "$MONITOR_CONFIG" | jq -r '.title // "未命名监控"')
SYMBOL=$(echo "$MONITOR_CONFIG" | jq -r '.related_asset_symbol // ""')
CATEGORY=$(echo "$MONITOR_CONFIG" | jq -r '.category // "Data"')
SIGNIFICANCE=$(echo "$MONITOR_CONFIG" | jq -r '.significance // "Structural"')
SOURCE=$(echo "$MONITOR_CONFIG" | jq -r '.target_source // ""')
CRON=$(echo "$MONITOR_CONFIG" | jq -r '.frequency_cron // "0 9 * * 1-5"')
START_DATE=$(echo "$MONITOR_CONFIG" | jq -r '.start_date // ""')
TRIGGER=$(echo "$MONITOR_CONFIG" | jq -r '.semantic_trigger // ""')
REASON=$(echo "$MONITOR_CONFIG" | jq -r '.reason_for_user // ""')

echo "  📊 监控: $TITLE" >&2
echo "  🏷️  标的: $SYMBOL" >&2
echo "  📅 频率: $CRON" >&2

# 构建 API 请求体
REQUEST_BODY=$(jq -n \
    --arg title "$TITLE" \
    --arg symbol "$SYMBOL" \
    --arg category "$CATEGORY" \
    --arg significance "$SIGNIFICANCE" \
    --arg source "$SOURCE" \
    --arg cron "$CRON" \
    --arg start_date "$START_DATE" \
    --arg trigger "$TRIGGER" \
    --arg reason "$REASON" \
    '{
        title: $title,
        symbol: $symbol,
        category: $category,
        significance: $significance,
        source: $source,
        frequency: $cron,
        startDate: $start_date,
        triggerCondition: $trigger,
        description: $reason
    }')

# 调用 CueCue API 创建监控
RESPONSE=$(curl -s -X POST "${CUECUE_BASE_URL}/api/v1/monitors" \
    -H "Authorization: Bearer ${CUECUE_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_BODY" 2>/dev/null || echo '{"error": "API request failed"}')

# 检查响应
if echo "$RESPONSE" | jq -e '.error' >/dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
    echo "  ❌ 创建失败: $ERROR_MSG" >&2
    echo "$RESPONSE" > "$OUTPUT_FILE"
    exit 1
fi

# 保存结果
echo "$RESPONSE" > "$OUTPUT_FILE"

MONITOR_ID=$(echo "$RESPONSE" | jq -r '.id // .monitorId // "unknown"')
echo "  ✅ 监控创建成功！ID: $MONITOR_ID" >&2

echo "$RESPONSE"
