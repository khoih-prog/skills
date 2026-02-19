#!/usr/bin/env python3
"""
FIS 3.1 Lite - Agent Extension Setup
帮助 Agent 创建自己的 .fis3.1 扩展目录
"""

from pathlib import Path
import json

def setup_agent_extension(agent_name: str, workspace_path: Path = None):
    """
    为当前 Agent 创建 .fis3.1 扩展目录
    
    Args:
        agent_name: Agent 名称 (如 "cybermao", "pulse")
        workspace_path: 工作区路径，默认 ~/.openclaw/workspace
    """
    if workspace_path is None:
        workspace_path = Path.home() / ".openclaw" / "workspace"
    
    print(f"🔧 Setting up FIS 3.1 extension for {agent_name}")
    print(f"   Workspace: {workspace_path}")
    
    # Create .fis3.1 directory
    fis31_dir = workspace_path / ".fis3.1"
    fis31_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (fis31_dir / "local_cache").mkdir(exist_ok=True)
    (fis31_dir / "memories").mkdir(exist_ok=True)
    
    # Create skill manifest for this agent
    manifest_file = fis31_dir / "skill_manifest.json"
    if not manifest_file.exists():
        manifest = {
            "agent": agent_name,
            "version": "3.1.0-lite",
            "skills": [],
            "last_updated": "2026-02-18T00:00:00+08:00"
        }
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"   ✅ Created skill_manifest.json")
    
    print(f"   ✅ Extension ready: {fis31_dir}")
    return fis31_dir

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 setup_agent_extension.py <agent_name>")
        print("Example: python3 setup_agent_extension.py cybermao")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    setup_agent_extension(agent_name)
