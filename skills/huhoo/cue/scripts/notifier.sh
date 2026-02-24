#!/bin/bash
# CueCue Notifier - 研究完成通知器 (v3.0 - Playwright版)
# 使用 Playwright 浏览器检测，针对流式输出优化

TASK_ID="$1"
RESEARCH_PID="$2"
OUTPUT_FILE="$3"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_TRACKER="$SCRIPT_DIR/task-tracker.sh"

# 等待研究进程完成
wait $RESEARCH_PID
EXIT_CODE=$?

# 获取任务信息
TASK_INFO=$($TASK_TRACKER get "$TASK_ID")
CHAT_ID=$(echo "$TASK_INFO" | jq -r '.chat_id // empty')
TOPIC=$(echo "$TASK_INFO" | jq -r '.topic // "未知主题"')
REPORT_URL=$(echo "$TASK_INFO" | jq -r '.report_url // empty')

if [ -z "$CHAT_ID" ]; then
    echo "[$(date)] 任务 $TASK_ID 缺少 chat_id，无法发送通知" >> /tmp/cuecue-notifier.log
    exit 1
fi

# ============================================
# Playwright 检测函数
# ============================================
check_with_playwright() {
    local url="$1"
    local max_wait="${2:-60}"  # 默认最多等待60秒
    
    python3 << EOF
import asyncio
from playwright.async_api import async_playwright
import json

async def check():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 访问页面
            await page.goto("$url", wait_until="domcontentloaded", timeout=30000)
            
            # 等待流式输出（最多${max_wait}秒）
            for i in range(${max_wait} // 2):
                await asyncio.sleep(2)
                
                # 检测完成按钮
                has_button = await page.evaluate("""() => {
                    const buttons = ['转发报告', '复制报告', '生成搭子', '追问'];
                    return buttons.some(t => document.body.innerText.includes(t));
                }""")
                
                # 检测加载状态
                is_loading = await page.evaluate("""() => {
                    return document.querySelector('.animate-spin') !== null ||
                           document.body.innerText.includes('加载中');
                }""")
                
                # 获取内容长度
                content = await page.evaluate("() => document.body.innerText")
                
                # 完成条件：有完成按钮且不在加载中
                if has_button and not is_loading:
                    await browser.close()
                    return json.dumps({
                        "complete": True,
                        "confidence": "high",
                        "wait_time": (i + 1) * 2,
                        "content_length": len(content)
                    })
                
                # 如果内容稳定且较长，也认为完成
                if len(content) > 10000 and not is_loading:
                    await browser.close()
                    return json.dumps({
                        "complete": True,
                        "confidence": "medium",
                        "wait_time": (i + 1) * 2,
                        "content_length": len(content),
                        "note": "content_stable"
                    })
            
            await browser.close()
            return json.dumps({
                "complete": False,
                "confidence": "low",
                "reason": "timeout",
                "content_length": len(content) if 'content' in locals() else 0
            })
            
    except Exception as e:
        return json.dumps({
            "complete": False,
            "error": str(e)
        })

result = asyncio.run(check())
print(result)
EOF
}

# ============================================
# 主检测逻辑
# ============================================
echo "[$(date)] 任务 $TASK_ID - 开始 Playwright 检测" >> /tmp/cuecue-notifier.log

# 使用 Playwright 检测（最多等待60秒）
CHECK_RESULT=$(check_with_playwright "$REPORT_URL" 60)
IS_COMPLETE=$(echo "$CHECK_RESULT" | jq -r '.complete // false')
CONFIDENCE=$(echo "$CHECK_RESULT" | jq -r '.confidence // "low"')
WAIT_TIME=$(echo "$CHECK_RESULT" | jq -r '.wait_time // 0')
CONTENT_LENGTH=$(echo "$CHECK_RESULT" | jq -r '.content_length // 0')

echo "[$(date)] 任务 $TASK_ID - 检测结果: complete=$IS_COMPLETE, confidence=$CONFIDENCE, wait_time=${WAIT_TIME}s, content_length=$CONTENT_LENGTH" >> /tmp/cuecue-notifier.log

# ============================================
# 构建通知消息
# ============================================
if [ "$IS_COMPLETE" = "true" ]; then
    MESSAGE=$(cat << EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 研究完成：$TOPIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 完整报告：
$REPORT_URL

⏱️ 流式输出耗时：${WAIT_TIME} 秒
📝 报告长度：$(echo "$CONTENT_LENGTH" | awk '{printf "%.1fK", $1/1000}') 字符

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 后续操作
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 查看报告后，可要求我从报告中提取关键监控指标
• 输入 /usage 查看剩余研究配额

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 小贴士
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
如需基于此报告创建持续监控，请告诉我：
"从这个报告中提取监控项"

---
*任务ID: $TASK_ID | Playwright检测*
EOF
)
    REPORT_AVAILABLE=true
else
    # 检测未完成，但进程成功退出
    if [ $EXIT_CODE -eq 0 ]; then
        MESSAGE=$(cat << EOF
⏳ **研究进行中：$TOPIC**

研究进程已结束，但报告可能仍在最终渲染中。

📄 **查看进度：**
$REPORT_URL

请稍后刷新页面查看最新内容。

---
*任务ID: $TASK_ID | 检测状态: ${CONFIDENCE}*
EOF
)
    else
        MESSAGE=$(cat << EOF
⚠️ **研究进程异常：$TOPIC**

研究进程退出码: $EXIT_CODE

📄 **查看进度：**
$REPORT_URL

建议稍后手动检查报告状态。

---
*任务ID: $TASK_ID*
EOF
)
    fi
    REPORT_AVAILABLE=false
fi

# ============================================
# 发送通知
# ============================================
NOTIFICATION_SENT=false

# 方式1: 使用 message 工具
if command -v message &> /dev/null; then
    message send --channel feishu --target "$CHAT_ID" --message "$MESSAGE" 2>/dev/null && NOTIFICATION_SENT=true
fi

# 方式2: 使用 openclaw CLI
if [ "$NOTIFICATION_SENT" = false ] && command -v openclaw &> /dev/null; then
    echo "$MESSAGE" | openclaw message send --channel feishu --target "$CHAT_ID" 2>/dev/null && NOTIFICATION_SENT=true
fi

# 记录结果
if [ "$NOTIFICATION_SENT" = true ]; then
    echo "[$(date)] 成功发送通知到 $CHAT_ID (任务: $TASK_ID)" >> /tmp/cuecue-notifier.log
else
    echo "[$(date)] 发送通知到 $CHAT_ID 失败 (任务: $TASK_ID)" >> /tmp/cuecue-notifier.log
    echo "$MESSAGE" > "/tmp/notification_${TASK_ID}.txt"
fi

# 更新任务状态
$TASK_TRACKER notify "$TASK_ID" > /dev/null 2>&1

exit 0
