#!/bin/bash
# CueCue Report Checker - 统一的报告完成检测模块
# 支持多种检测策略，确保可靠性

REPORT_URL="$1"
MODE="${2:-auto}"  # auto, sync, async
TIMEOUT="${3:-300}"  # 默认5分钟超时

if [ -z "$REPORT_URL" ]; then
    echo '{"error": "Report URL required"}' >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_LOG="/tmp/cuecue-check-$(date +%s).log"

# ============================================
# 检测策略 1: HTTP + 内容检测 (快速)
# ============================================
check_http_content() {
    local url="$1"
    local response=$(curl -s -L "$url" 2>/dev/null)
    local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$status" != "200" ]; then
        echo '{"strategy": "http", "complete": false, "reason": "HTTP status: '$status'"}'
        return 1
    fi
    
    # 提取 body 内容（排除 title 干扰）
    local body_content=$(echo "$response" | sed 's/<title>[^<]*<\/title>//g' | sed 's/<[^>]*>//g')
    
    # 检查是否有完成标志（多种可能）
    local complete_markers=0
    local has_loading=$(echo "$response" | grep -cE "(animate-spin|loading|加载中|请稍候|生成中|思考中)")
    
    # 标志1: 完成按钮（必须在 body 中，不是 title）
    if echo "$body_content" | grep -qE "(转发报告|复制报告|生成搭子|追问|分享报告|下载报告|完成|Finish)"; then
        complete_markers=$((complete_markers + 1))
    fi
    
    # 标志2: 内容关键词（排除 title 后的 body 内容）
    # 要求有多个关键词，避免误判
    local content_keywords=$(echo "$body_content" | grep -oiE "(分析|结论|数据|报告|调研|总结|建议|趋势|竞争|行业|市场|投资|前景)" | wc -l)
    if [ "$content_keywords" -ge 3 ]; then
        complete_markers=$((complete_markers + 1))
    fi
    
    # 标志3: 有明确的报告结构标志（重要！表明是完整报告）
    local structure_marks=$(echo "$body_content" | grep -cE "(一、|二、|三、|1\.|2\.|3\.|第一章|第二章|第三章)")
    if [ "$structure_marks" -ge 2 ]; then
        complete_markers=$((complete_markers + 1))
    fi
    
    # 标志4: 不在加载中（如果内容已充分，轻微加载状态可以接受）
    # 但如果还在重度加载（无内容），则不认为完成
    if [ "$has_loading" -eq 0 ]; then
        complete_markers=$((complete_markers + 1))
    fi
    
    # 判断标准：
    # - 高置信度：有完成按钮 + 有结构标志 + 不在加载中
    # - 中置信度：有结构标志 + 有内容关键词（即使还在轻微加载）
    # - 低置信度：其他情况
    if [ $complete_markers -ge 3 ]; then
        echo '{"strategy": "http", "complete": true, "confidence": "high", "markers": '$complete_markers', "content_keywords": '$content_keywords', "structure_marks": '$structure_marks', "loading": '$has_loading'}'
        return 0
    elif [ $structure_marks -ge 2 ] && [ "$content_keywords" -ge 3 ]; then
        # 有明确的报告结构和内容，即使有轻微加载也认为完成
        echo '{"strategy": "http", "complete": true, "confidence": "medium", "markers": '$complete_markers', "content_keywords": '$content_keywords', "structure_marks": '$structure_marks', "loading": '$has_loading', "note": "content_ready_with_minor_loading"}'
        return 0
    else
        echo '{"strategy": "http", "complete": false, "confidence": "low", "markers": '$complete_markers', "content_keywords": '$content_keywords', "structure_marks": '$structure_marks', "loading": '$has_loading'}'
        return 1
    fi
}

# ============================================
# 检测策略 2: Playwright 浏览器检测 (推荐，针对流式输出优化)
# ============================================
check_playwright() {
    local url="$1"
    local check_script="/tmp/cuecue-playwright-check-$(date +%s).py"
    
    # 创建 Python 检测脚本
    cat > "$check_script" << 'PYTHON_EOF'
import asyncio
import sys
import json

async def check_report(url):
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 访问页面
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 等待流式输出完成（最多30秒，匹配CueCue的流式输出时长）
            max_wait = 30
            check_interval = 2
            elapsed = 0
            last_content = ""
            stable_count = 0
            
            while elapsed < max_wait:
                await asyncio.sleep(check_interval)
                elapsed += check_interval
                
                # 获取当前页面文本内容
                current_content = await page.evaluate("() => document.body.innerText")
                
                # 检查是否有完成按钮（最可靠的标志）
                has_complete_button = await page.evaluate("""() => {
                    const buttons = ['转发报告', '复制报告', '生成搭子', '追问', '分享', '下载'];
                    return buttons.some(text => document.body.innerText.includes(text));
                }
                """)
                
                # 检查是否还在加载中
                is_loading = await page.evaluate("""() => {
                    return document.querySelector('.animate-spin') !== null ||
                           document.body.innerText.includes('加载中') ||
                           document.body.innerText.includes('生成中');
                }
                """)
                
                # 如果发现有完成按钮且不在加载中，立即完成
                if has_complete_button and not is_loading:
                    return {
                        "strategy": "playwright",
                        "complete": True,
                        "confidence": "high",
                        "reason": "complete_buttons_found",
                        "wait_time": elapsed,
                        "has_loading": is_loading
                    }
                
                # 检查内容是否稳定（连续2次相同表示流式输出结束）
                if current_content == last_content and len(current_content) > 500:
                    stable_count += 1
                    if stable_count >= 2 and not is_loading:
                        return {
                            "strategy": "playwright",
                            "complete": True,
                            "confidence": "medium",
                            "reason": "content_stable",
                            "wait_time": elapsed,
                            "content_length": len(current_content),
                            "has_loading": is_loading
                        }
                else:
                    stable_count = 0
                    last_content = current_content
            
            # 超时，返回当前状态
            return {
                "strategy": "playwright",
                "complete": False,
                "confidence": "low",
                "reason": "timeout",
                "wait_time": elapsed,
                "content_length": len(last_content),
                "has_loading": is_loading
            }
            
    except ImportError:
        return {"strategy": "playwright", "complete": False, "error": "playwright not installed"}
    except Exception as e:
        return {"strategy": "playwright", "complete": False, "error": str(e)}

result = asyncio.run(check_report(sys.argv[1]))
print(json.dumps(result, ensure_ascii=False, ensure_ascii=False))
PYTHON_EOF

    result=$(python3 "$check_script" "$url" 2>/dev/null)
    rm -f "$check_script"
    
    echo "$result"
}

# ============================================
# 检测策略 3: API 状态查询 (如果 CueCue 提供)
# ============================================
check_api_status() {
    local url="$1"
    
    # 从 URL 提取任务 ID
    local task_id=$(echo "$url" | grep -oP '(?<=/c/)[^/]+' || echo "")
    
    if [ -z "$task_id" ] || [ -z "$CUECUE_API_KEY" ]; then
        echo '{"strategy": "api", "complete": false, "reason": "missing task_id or api_key"}'
        return 1
    fi
    
    # 尝试调用 CueCue API 查询状态
    local response=$(curl -s -H "Authorization: Bearer $CUECUE_API_KEY" \
        "${CUECUE_BASE_URL:-https://cuecue.cn}/api/v1/tasks/$task_id" 2>/dev/null || echo "{}")
    
    local status=$(echo "$response" | jq -r '.status // .state // "unknown"' 2>/dev/null)
    
    if [ "$status" = "completed" ] || [ "$status" = "done" ] || [ "$status" = "success" ]; then
        echo '{"strategy": "api", "complete": true, "status": "'$status'"}'
        return 0
    else
        echo '{"strategy": "api", "complete": false, "status": "'$status'"}'
        return 1
    fi
}

# ============================================
# 主检测逻辑
# ============================================
check_report() {
    local url="$1"
    local mode="$2"
    
    local result=""
    local complete=false
    
    case "$mode" in
        http)
            result=$(check_http_content "$url")
            ;;
        playwright)
            result=$(check_playwright "$url")
            ;;
        api)
            result=$(check_api_status "$url")
            ;;
        auto|*)
            # 自动选择最佳策略 - 优先使用 Playwright 浏览器检测
            # 因为 CueCue 是流式输出，需要浏览器环境才能准确检测
            
            # 1. 首先尝试 Playwright（最准确，针对流式输出优化）
            result=$(check_playwright "$url")
            complete=$(echo "$result" | jq -r '.complete // false')
            
            # 2. 如果 Playwright 失败（如未安装），降级到 HTTP 检测
            if [ "$complete" != "true" ]; then
                local error=$(echo "$result" | jq -r '.error // empty')
                if [ -n "$error" ]; then
                    # Playwright 出错，使用 HTTP 作为后备
                    result=$(check_http_content "$url")
                fi
            fi
            ;;
    esac
    
    echo "$result"
}

# ============================================
# 同步等待模式 (带超时)
# ============================================
wait_for_completion() {
    local url="$1"
    local timeout="$2"
    local start_time=$(date +%s)
    local check_interval=10  # 每10秒检查一次
    
    echo "⏳ 开始同步等待报告完成..." >&2
    echo "   超时设置: ${timeout}秒" >&2
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -ge $timeout ]; then
            echo '{"complete": false, "error": "timeout", "elapsed": '$elapsed'}'
            return 1
        fi
        
        local result=$(check_report "$url" "auto")
        local complete=$(echo "$result" | jq -r '.complete // false')
        
        if [ "$complete" = "true" ]; then
            echo "$result" | jq '.elapsed = '$elapsed
            return 0
        fi
        
        echo "   已等待 ${elapsed}秒，继续检查..." >&2
        sleep $check_interval
    done
}

# ============================================
# 命令入口
# ============================================
case "${MODE}" in
    check)
        check_report "$REPORT_URL" "auto"
        ;;
    wait)
        wait_for_completion "$REPORT_URL" "$TIMEOUT"
        ;;
    http)
        check_http_content "$REPORT_URL"
        ;;
    playwright)
        check_playwright "$REPORT_URL"
        ;;
    api)
        check_api_status "$REPORT_URL"
        ;;
    *)
        # 默认：单次检测
        check_report "$REPORT_URL" "auto"
        ;;
esac
