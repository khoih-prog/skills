#!/bin/bash
# Cue - 智能投研助手
# 统一入口：深度研究、用户管理、监控生成

set -e

USER_INPUT="$1"
CHAT_ID="${2:-user:default}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_MANAGER="$SCRIPT_DIR/user-manager.sh"

if [ -z "$USER_INPUT" ]; then
    echo '{"error": "Empty input"}'
    exit 1
fi

# 初始化用户管理器
$USER_MANAGER init 2>/dev/null || true

# 提取命令和参数
COMMAND=""
ARGS=""

# 检查是否是显式命令
if [[ "$USER_INPUT" =~ ^/([a-zA-Z]+)[[:space:]]*(.*)$ ]]; then
    COMMAND="${BASH_REMATCH[1]}"
    ARGS="${BASH_REMATCH[2]}"
else
    COMMAND="auto"
fi

# 路由决策
case "$COMMAND" in
    cue)
        # 核心命令：深度研究
        if [ -z "$ARGS" ]; then
            cat << 'EOF'
⚠️ 请提供研究主题

用法: /cue <研究主题>

示例:
  /cue 特斯拉 2024 财务分析
  /cue 新能源电池行业竞争格局
  /cue --mode 基金经理 宁德时代

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 可选模式：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
--mode 理财顾问  → 投资建议导向
--mode 研究员    → 产业分析导向
--mode 基金经理  → 投资决策导向
EOF
            exit 0
        fi
        
        # 检查配额
        QUOTA_CHECK=$($USER_MANAGER check-quota "$CHAT_ID" research 2>/dev/null)
        ALLOWED=$(echo "$QUOTA_CHECK" | jq -r '.allowed // false')
        
        if [ "$ALLOWED" != "true" ]; then
            cat << 'EOF'
⚠️ 今日研究配额已用完

💡 获取更多配额：
1. 访问 https://cuecue.cn 注册账号
2. 获取 API Key
3. 输入：/register sk-您的APIKey
EOF
            exit 1
        fi
        
        # 获取模式
        MODE=""
        if [[ "$ARGS" =~ --mode[[:space:]]+([^[:space:]]+) ]]; then
            MODE="${BASH_REMATCH[1]}"
            ARGS=$(echo "$ARGS" | sed 's/--mode[[:space:]]*[^[:space:]]*//')
        fi
        
        # 应用模式
        if [ -n "$MODE" ]; then
            case "$MODE" in
                advisor|理财顾问)
                    ARGS="【理财顾问视角】${ARGS}"
                    ;;
                researcher|研究员)
                    ARGS="【行业研究员视角】${ARGS}"
                    ;;
                manager|基金经理)
                    ARGS="【基金经理视角】${ARGS}"
                    ;;
            esac
        fi
        
        # 执行研究
        export OPENCLAW_CHAT_ID="$CHAT_ID"
        exec "$SCRIPT_DIR/research.sh" "$ARGS" "$CHAT_ID"
        ;;
        
    register)
        # 注册命令
        if [ -z "$ARGS" ]; then
            cat << 'EOF'
⚠️ 请提供 API Key

用法: /register sk-您的Key

1. 访问 https://cuecue.cn 注册
2. 在 Settings → API Keys 创建 Key
EOF
            exit 0
        fi
        
        exec "$SCRIPT_DIR/register-handler.sh" "$CHAT_ID" "$ARGS"
        ;;
        
    monitor)
        # 监控命令
        SUBCOMMAND=$(echo "$ARGS" | awk '{print $1}')
        
        case "$SUBCOMMAND" in
            generate|create)
                echo "🔔 从研究报告生成监控项..." >&2
                # 查找用户最近完成的任务
                USER_WORKSPACE=$($USER_MANAGER workspace "$CHAT_ID")
                LATEST_TASK=$(ls -t "$USER_WORKSPACE/tasks/"/*.json 2>/dev/null | head -1)
                
                if [ -z "$LATEST_TASK" ]; then
                    echo "⚠️ 未找到最近的研究报告"
                    echo "请先完成一个深度研究任务：/cue <研究主题>"
                    exit 1
                fi
                
                echo "📄 找到最近任务: $(basename "$LATEST_TASK")"
                echo "🎯 开始生成监控项..."
                
                # 调用监控生成器
                exec "$SCRIPT_DIR/monitor-generator.sh" "$LATEST_TASK" "$CHAT_ID"
                ;;
            *)
                cat << 'EOF'
📊 监控功能

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
可用子命令：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/monitor generate  - 从最近报告生成监控项

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
工作流：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 完成深度研究：/cue <主题>
2. 输入 /monitor generate
3. 系统自动提取监控指标
4. 监控项激活并定期执行

EOF
                ;;
        esac
        ;;
        
    usage)
        # 查看配额
        exec "$SCRIPT_DIR/usage-handler.sh" "$CHAT_ID"
        ;;
        
    help)
        # 帮助信息
        USER_TYPE=$($USER_MANAGER type "$CHAT_ID" 2>/dev/null)
        
        if [ "$USER_TYPE" = "registered" ]; then
            cat << 'EOF'
📚 Cue - 智能投研助手

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 账户状态：注册用户 ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ 核心命令：
/cue <主题>       深度研究
/cue --mode <角色> <主题>  指定模式

📊 监控功能：
/monitor generate  从报告生成监控项

📋 其他命令：
/usage            查看配额
/register         重新绑定 Key
/help             显示帮助

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
        else
            RESEARCH_REMAINING=$($USER_MANAGER quota "$CHAT_ID" 2>/dev/null | jq -r '.research_remaining // 3')
            cat << EOF
📚 Cue - 智能投研助手

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 账户状态：体验用户
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 深度研究：${RESEARCH_REMAINING}/3 次今日剩余

⭐ 核心命令：
/cue <主题>       深度研究

📊 监控功能：
/monitor generate  从报告生成监控项

💡 获取无限制配额：
/register sk-您的Key

📋 其他命令：
/usage            查看配额
/help             显示帮助

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
        fi
        ;;
        
    auto)
        # 自然语言处理
        echo "🤔 分析需求..." >&2
        
        # 首次使用检测
        USER_EXISTS=$($USER_MANAGER ensure "$CHAT_ID" 2>&1)
        IS_NEW=$(echo "$USER_EXISTS" | grep -q "Created" && echo "true" || echo "false")
        
        if [ "$IS_NEW" = "true" ]; then
            exec "$SCRIPT_DIR/welcome-handler.sh" "$CHAT_ID"
            exit 0
        fi
        
        # 检查配额
        QUOTA_CHECK=$($USER_MANAGER check-quota "$CHAT_ID" research 2>/dev/null)
        ALLOWED=$(echo "$QUOTA_CHECK" | jq -r '.allowed // false')
        
        if [ "$ALLOWED" != "true" ]; then
            cat << 'EOF'
⚠️ 今日研究配额已用完

💡 获取更多配额：
/register sk-您的APIKey
EOF
            exit 0
        fi
        
        # 意图识别
        if [[ "$USER_INPUT" =~ (分析|研究|深度|报告|趋势|前景|竞争|格局|产业链|投资|调研) ]]; then
            echo "📊 识别为深度研究需求" >&2
            
            # 检测模式
            if [[ "$USER_INPUT" =~ (投资建议|理财|配置) ]]; then
                USER_INPUT="【理财顾问视角】${USER_INPUT}"
            elif [[ "$USER_INPUT" =~ (产业链|竞争格局|行业) ]]; then
                USER_INPUT="【行业研究员视角】${USER_INPUT}"
            elif [[ "$USER_INPUT" =~ (估值|财报|投资策略) ]]; then
                USER_INPUT="【基金经理视角】${USER_INPUT}"
            fi
            
            export OPENCLAW_CHAT_ID="$CHAT_ID"
            exec "$SCRIPT_DIR/research.sh" "$USER_INPUT" "$CHAT_ID"
        else
            echo "💡 请输入研究主题，例如：" >&2
            echo "   /cue 分析一下新能源行业" >&2
            echo "   或直接输入：新能源行业竞争格局分析" >&2
        fi
        ;;
        
    *)
        echo "❓ 未知命令: /$COMMAND"
        echo ""
        echo "可用命令:"
        echo "  /cue <主题>       - 深度研究"
        echo "  /monitor generate  - 从报告生成监控项"
        echo "  /register         - 绑定 API Key"
        echo "  /usage            - 查看配额"
        echo "  /help             - 显示帮助"
        exit 1
        ;;
esac
