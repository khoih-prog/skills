#!/usr/bin/env python3
"""
User Manager - 用户管理系统
管理用户配置、API Key、配额跟踪
"""

import os
import sys
import json
import re
from datetime import datetime, date
from pathlib import Path

# 配置路径
CUECUE_DIR = Path.home() / ".cuecue"
USERS_DIR = CUECUE_DIR / "users"
DEFAULT_CONFIG_FILE = CUECUE_DIR / "default.conf"

def init_dirs():
    """初始化目录结构"""
    USERS_DIR.mkdir(parents=True, exist_ok=True)
    return True

def get_safe_id(chat_id: str) -> str:
    """将 chat_id 转换为安全的文件名"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', chat_id)

def get_user_config_file(chat_id: str) -> Path:
    """获取用户配置文件路径"""
    safe_id = get_safe_id(chat_id)
    return USERS_DIR / f"{safe_id}.json"

def get_user_workspace(chat_id: str) -> Path:
    """获取用户工作目录"""
    safe_id = get_safe_id(chat_id)
    workspace = USERS_DIR / safe_id
    (workspace / "tasks").mkdir(parents=True, exist_ok=True)
    return workspace

def get_default_api_key() -> str:
    """读取默认 API Key"""
    if DEFAULT_CONFIG_FILE.exists():
        try:
            with open(DEFAULT_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('default_api_key', '')
        except:
            pass
    return os.environ.get('CUECUE_API_KEY', '')

def create_user(chat_id: str):
    """创建新用户"""
    config_file = get_user_config_file(chat_id)
    default_key = get_default_api_key()
    today = date.today().isoformat()
    
    user_config = {
        "chat_id": chat_id,
        "created_at": datetime.now().isoformat(),
        "type": "guest",
        "api_key": default_key,
        "custom_key": None,
        "quota": {
            "research_daily_limit": 3,
            "research_used_today": 0,
            "search_daily_limit": 10,
            "search_used_today": 0,
            "last_reset_date": today
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(user_config, f, indent=2)
    
    # 输出到 stderr 避免干扰 JSON 输出
    print(f"Created user config: {config_file}", file=sys.stderr)

def reset_quota_if_needed(chat_id: str):
    """检查并重置配额（新的一天）"""
    config_file = get_user_config_file(chat_id)
    
    if not config_file.exists():
        return
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        today = date.today().isoformat()
        last_reset = config.get('quota', {}).get('last_reset_date', '')
        
        if last_reset != today:
            config['quota']['research_used_today'] = 0
            config['quota']['search_used_today'] = 0
            config['quota']['last_reset_date'] = today
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
    except:
        pass

def ensure_user(chat_id: str):
    """确保用户存在，不存在则创建"""
    config_file = get_user_config_file(chat_id)
    
    if not config_file.exists():
        create_user(chat_id)
    else:
        reset_quota_if_needed(chat_id)

def get_user_info(chat_id: str) -> dict:
    """获取用户信息"""
    ensure_user(chat_id)
    config_file = get_user_config_file(chat_id)
    
    with open(config_file, 'r') as f:
        return json.load(f)

def get_user_type(chat_id: str) -> str:
    """获取用户类型"""
    ensure_user(chat_id)
    config_file = get_user_config_file(chat_id)
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config.get('type', 'guest')

def get_api_key(chat_id: str) -> str:
    """获取用户的 API Key"""
    ensure_user(chat_id)
    config_file = get_user_config_file(chat_id)
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # 优先使用自定义 Key
    custom_key = config.get('custom_key')
    if custom_key and custom_key != 'null':
        return custom_key
    
    return config.get('api_key', '')

def check_quota(chat_id: str, operation: str) -> dict:
    """检查配额"""
    ensure_user(chat_id)
    config_file = get_user_config_file(chat_id)
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    user_type = config.get('type', 'guest')
    
    # 注册用户无本地配额限制
    if user_type == 'registered':
        return {"allowed": True, "reason": "registered_user"}
    
    quota = config.get('quota', {})
    
    if operation == 'research':
        used_limit = quota.get('research_daily_limit', 3)
        used = quota.get('research_used_today', 0)
    else:
        used_limit = quota.get('search_daily_limit', 10)
        used = quota.get('search_used_today', 0)
    
    remaining = used_limit - used
    
    if used >= used_limit:
        return {"allowed": False, "reason": "quota_exceeded", "limit": used_limit, "used": used, "remaining": 0}
    else:
        return {"allowed": True, "reason": "quota_ok", "limit": used_limit, "used": used, "remaining": remaining}

def use_quota(chat_id: str, operation: str):
    """使用配额"""
    ensure_user(chat_id)
    config_file = get_user_config_file(chat_id)
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    user_type = config.get('type', 'guest')
    
    # 注册用户不记录配额
    if user_type == 'registered':
        return
    
    quota = config.get('quota', {})
    
    if operation == 'research':
        quota['research_used_today'] = quota.get('research_used_today', 0) + 1
    else:
        quota['search_used_today'] = quota.get('search_used_today', 0) + 1
    
    config['quota'] = quota
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def register_user(chat_id: str, api_key: str):
    """注册用户（绑定自己的 API Key）"""
    ensure_user(chat_id)
    config_file = get_user_config_file(chat_id)
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    config['type'] = 'registered'
    config['custom_key'] = api_key
    config['registered_at'] = datetime.now().isoformat()
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"User {chat_id} registered with custom API key")

def get_quota_status(chat_id: str) -> dict:
    """获取配额状态"""
    ensure_user(chat_id)
    config_file = get_user_config_file(chat_id)
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    user_type = config.get('type', 'guest')
    
    if user_type == 'registered':
        return {
            "type": "registered",
            "research_remaining": "unlimited",
            "search_remaining": "unlimited",
            "note": "Using custom API key, no local quota limit"
        }
    
    quota = config.get('quota', {})
    research_used = quota.get('research_used_today', 0)
    research_limit = quota.get('research_daily_limit', 3)
    search_used = quota.get('search_used_today', 0)
    search_limit = quota.get('search_daily_limit', 10)
    
    return {
        "type": "guest",
        "research_remaining": research_limit - research_used,
        "research_limit": research_limit,
        "search_remaining": search_limit - search_used,
        "search_limit": search_limit,
        "note": "Using shared API key"
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: user-manager.py {init|ensure|info|type|apikey|check-quota|use-quota|register|quota|workspace} [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_dirs()
    elif command == 'ensure' and len(sys.argv) >= 3:
        ensure_user(sys.argv[2])
    elif command == 'info' and len(sys.argv) >= 3:
        print(json.dumps(get_user_info(sys.argv[2])))
    elif command == 'type' and len(sys.argv) >= 3:
        print(get_user_type(sys.argv[2]))
    elif command == 'apikey' and len(sys.argv) >= 3:
        print(get_api_key(sys.argv[2]))
    elif command == 'check-quota' and len(sys.argv) >= 4:
        print(json.dumps(check_quota(sys.argv[2], sys.argv[3])))
    elif command == 'use-quota' and len(sys.argv) >= 4:
        use_quota(sys.argv[2], sys.argv[3])
    elif command == 'register' and len(sys.argv) >= 4:
        register_user(sys.argv[2], sys.argv[3])
    elif command == 'quota' and len(sys.argv) >= 3:
        print(json.dumps(get_quota_status(sys.argv[2])))
    elif command == 'workspace' and len(sys.argv) >= 3:
        print(get_user_workspace(sys.argv[2]))
    else:
        print("Usage: user-manager.py {init|ensure|info|type|apikey|check-quota|use-quota|register|quota|workspace} [args...]")
        sys.exit(1)

if __name__ == '__main__':
    main()
