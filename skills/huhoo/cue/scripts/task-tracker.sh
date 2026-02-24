#!/bin/bash
# CueCue Task Tracker - 异步任务追踪与通知

set -e

TASKS_DIR="${HOME}/.cuecue/tasks"
mkdir -p "$TASKS_DIR"

# 创建新任务
create_task() {
    local topic="$1"
    local report_url="$2"
    local chat_id="${3:-user:ou_5facd87f11cb35d651c435a4c1c7c4bc}"  # 默认值
    local task_id="cuecue_$(date +%s)_$(echo "$topic" | md5sum | cut -c1-8)"
    local task_file="$TASKS_DIR/${task_id}.json"
    
    cat > "$task_file" << EOF
{
  "task_id": "$task_id",
  "topic": "$topic",
  "report_url": "$report_url",
  "chat_id": "$chat_id",
  "status": "running",
  "created_at": "$(date -Iseconds)",
  "completed_at": null,
  "notified": false
}
EOF
    
    echo "$task_id"
}

# 检查任务状态
check_task() {
    local task_id="$1"
    local task_file="$TASKS_DIR/${task_id}.json"
    
    if [ ! -f "$task_file" ]; then
        echo '{"error": "Task not found"}'
        return 1
    fi
    
    # 从 report_url 提取任务ID
    local report_url=$(cat "$task_file" | jq -r '.report_url')
    local cuecue_task_id=$(echo "$report_url" | grep -oP '(?<=/c/)[^/]+')
    
    # 调用 CueCue API 查询任务状态（如果API支持）
    # 这里使用简化的检测逻辑：检查报告是否可访问
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" "$report_url" 2>/dev/null || echo "000")
    
    if [ "$http_status" = "200" ]; then
        # 任务可能已完成，更新状态
        cat "$task_file" | jq '.status = "completed" | .completed_at = "'$(date -Iseconds)'"' > "${task_file}.tmp"
        mv "${task_file}.tmp" "$task_file"
        echo "completed"
    else
        echo "running"
    fi
}

# 获取任务信息
get_task() {
    local task_id="$1"
    local task_file="$TASKS_DIR/${task_id}.json"
    
    if [ -f "$task_file" ]; then
        cat "$task_file"
    else
        echo '{"error": "Task not found"}'
        return 1
    fi
}

# 标记任务已通知
mark_notified() {
    local task_id="$1"
    local task_file="$TASKS_DIR/${task_id}.json"
    
    if [ -f "$task_file" ]; then
        cat "$task_file" | jq '.notified = true' > "${task_file}.tmp"
        mv "${task_file}.tmp" "$task_file"
    fi
}

# 列出所有任务
list_tasks() {
    local status_filter="${1:-all}"
    
    echo '{"tasks": ['
    local first=true
    for task_file in "$TASKS_DIR"/*.json; do
        [ -f "$task_file" ] || continue
        
        local task_status=$(cat "$task_file" | jq -r '.status')
        
        if [ "$status_filter" = "all" ] || [ "$task_status" = "$status_filter" ]; then
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            cat "$task_file"
        fi
    done
    echo ']}'
}

# 清理旧任务（超过7天）
cleanup_tasks() {
    find "$TASKS_DIR" -name "*.json" -mtime +7 -delete
    echo "Cleaned up old tasks"
}

# 命令分发
case "$1" in
    create)
        create_task "$2" "$3" "$4"
        ;;
    check)
        check_task "$2"
        ;;
    get)
        get_task "$2"
        ;;
    notify)
        mark_notified "$2"
        ;;
    list)
        list_tasks "$2"
        ;;
    cleanup)
        cleanup_tasks
        ;;
    *)
        echo "Usage: $0 {create|check|get|notify|list|cleanup}"
        exit 1
        ;;
esac
