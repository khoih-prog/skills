#!/bin/bash
# User Manager Wrapper - 调用 Python 版本
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 确保目录存在
python3 "$SCRIPT_DIR/user-manager.py" init 2>/dev/null

# 执行命令（重定向 stderr 到 /dev/null 以避免干扰 JSON 输出）
python3 "$SCRIPT_DIR/user-manager.py" "$@" 2>/dev/null
