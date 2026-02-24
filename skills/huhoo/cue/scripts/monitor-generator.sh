#!/bin/bash
# CueCue Monitor - 从研究报告生成监控项

set -e

REPORT_CONTENT="$1"
USER_PROFILE="${2:-通用投资者}"
ASSET_WHITELIST="${3:-}"
OUTPUT_FILE="${4:-/tmp/monitor_suggestions.json}"

if [ -z "$REPORT_CONTENT" ]; then
    echo '{"error": "Report content is required"}' >&2
    exit 1
fi

# 检查环境变量
if [ -z "$CUECUE_API_KEY" ]; then
    echo '{"error": "CUECUE_API_KEY not configured"}' >&2
    exit 1
fi

echo "🔍 正在分析研究报告并生成监控建议..." >&2

# 构建提示词
PROMPT=$(cat << 'PROMPT_EOF'
你精通金融市场分析、行业趋势洞察以及数据工程技术。

# Core Objective
你的核心任务是将一份非结构化的"深度研究报告"，提取出**高价值、可量化、第一性信源**的可监控信号。
你需要像一名基金经理一样思考"什么值得看"，同时像一名量化工程师一样思考"怎么抓取数据"。

# Context Inputs
1. **User Profile": {USER_PROFILE} (用户的角色身份、关注领域)
2. **Asset Whitelist**: {ASSET_WHITELIST} (报告涉及的标的清单)
3. **Report Content**: {REPORT_CONTENT}

# Cognitive Process (思考链)
在生成监控项之前，请遵循以下步骤：
1.  **价值评估 (Value Assessment)**: 
    - 针对该用户画像，报告中哪条信息一旦发生变化，会产生最大的盈亏影响？
    - 区分"噪音"与"信号"。忽略长期的宏观空话，锁定短期的具体催化剂。
2.  **信号转化 (Signal Engineering)**:
    - 这个价值点能被数字化吗？(股价、销量、汇率)
    - 还是只能被事件化？(发文、公告、开庭)
    - 哪里是数据的"第一源头"？(不仅是新闻，更可能是交易所官网、政府公示栏)
3.  **可行性校验 (Feasibility Check)**:
    - 现在的技术手段（Search 工具）能低成本获取吗？
    - 现在开始监控时间合适吗？(引入时间窗口优化)
4.  **去噪与阈值 (De-noising & Thresholds)**:
    - **拒绝形容词**：严禁使用"大幅增长"、"明显改善"。
    - **强制逻辑算子**：必须转化为 > 30%, AND, OR, in [list] 等逻辑表达式。

# Extraction Rules
1.  **Alpha & Beta**: 既要捕捉个股的超额收益机会（Alpha，如新订单、技术突破），也要监控行业的系统性风险（Beta，如政策收紧、原材料涨价）。
2.  **Hard Link**: 输出的 `related_asset_symbol` 必须严格来自 `Asset Whitelist`。
3.  **Start Date Strategy**: 智能推迟监控开始时间。例如，财报监控应推迟到财报季开始前 5 天，而非今天。
4.  **Frequency Efficiency**:
    - 每日更新的数据 (Daily) -> 0 9 * * 1-5
    - 每周/每月数据 -> 0 10 * * 1 (具体到周几)
    - 严禁使用 Hourly 频率，除非是极端的日内交易信号。

# Output JSON Schema
{
  "monitoring_suggestions": [
    {
      "title": "简明扼要的监控标题",
      "related_asset_symbol": "从Whitelist中选择",
      "asset_name": "标的名称",

      "category": "Data | Event | Policy | Sentiment",
      "significance": "Opportunity (利好催化) | Risk (利空预警) | Structural (基本面验证)",
      "target_source": "具体的信源 (如: 港交所披露易 / 深交所公告 / 某某官网)",

      "frequency_cron": "Cron表达式(如: 0 9 * * 1)",
      "start_date": "YYYY-MM-DD",
      "start_date_reason": "解释为什么从这个日期开始(例如: 避开静默期，等待财报季)",

      "semantic_trigger": "详细描述触发条件逻辑(逻辑表达式或包含阈值的自然语言描述)",      
      "reason_for_user": "一句话告诉用户：为什么你需要关注这个？对你的持仓有什么具体影响？"
    }
  ]
}

请严格按照上述 JSON Schema 输出，只返回 JSON 格式，不要包含其他文字。
PROMPT_EOF
)

# 替换变量
PROMPT="${PROMPT//\{USER_PROFILE\}/$USER_PROFILE}"
PROMPT="${PROMPT//\{ASSET_WHITELIST\}/$ASSET_WHITELIST}"
PROMPT="${PROMPT//\{REPORT_CONTENT\}/$REPORT_CONTENT}"

# 调用 AI 生成监控建议
echo "  🤖 调用 AI 分析中..." >&2

RESPONSE=$(curl -s -X POST "${CUECUE_BASE_URL}/api/v1/chat/completions" \
    -H "Authorization: Bearer ${CUECUE_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"moonshot/kimi-k2.5\",
        \"messages\": [
            {\"role\": \"system\", \"content\": \"你是一个专业的金融市场监控信号提取助手。\"},
            {\"role\": \"user\", \"content\": $(echo "$PROMPT" | jq -Rs .)}
        ],
        \"temperature\": 0.3
    }")

# 提取 JSON 内容
MONITOR_JSON=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty' 2>/dev/null || echo "")

if [ -z "$MONITOR_JSON" ]; then
    echo '{"error": "Failed to generate monitor suggestions"}' >&2
    exit 1
fi

# 清理可能的 markdown 代码块
MONITOR_JSON=$(echo "$MONITOR_JSON" | sed 's/```json//g' | sed 's/```//g' | tr -d '\\')

# 验证 JSON 格式
if ! echo "$MONITOR_JSON" | jq -e . >/dev/null 2>&1; then
    echo '{"error": "Invalid JSON response from AI"}' >&2
    exit 1
fi

# 保存到文件
echo "$MONITOR_JSON" > "$OUTPUT_FILE"

# 统计生成的监控项数量
COUNT=$(echo "$MONITOR_JSON" | jq '.monitoring_suggestions | length')

echo "  ✅ 生成完成！共 ${COUNT} 个监控建议" >&2
echo "$MONITOR_JSON"
