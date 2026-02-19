#!/usr/bin/env python3
"""
FIS 3.1 Lite - 初始化脚本
一键部署 FIS 3.1 环境 (共享中心 + Agent 分形结构)
"""

import sys
from pathlib import Path

# Add skill lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

def init_shared_hub(hub_name: str = None):
    """初始化共享中心 (Shared Hub)"""
    from fis_config import get_shared_hub_path, set_shared_hub_name
    
    print("\n📦 Step 1: Initialize Shared Hub")
    print("-" * 40)
    
    # Allow custom hub name
    if hub_name:
        set_shared_hub_name(hub_name)
        print(f"Using custom hub name: {hub_name}")
    
    openclaw_dir = Path.home() / ".openclaw"
    fis31_dir = get_shared_hub_path() / ".fis3.1"
    
    # Create structure
    dirs = [
        fis31_dir / "memories" / "working",
        fis31_dir / "memories" / "short_term", 
        fis31_dir / "memories" / "long_term",
        fis31_dir / "skills" / "manifests",
        fis31_dir / "lib",
        fis31_dir / "heartbeat"
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d.relative_to(openclaw_dir)}")
    
    # Create registries
    import json
    
    registry_file = fis31_dir / "skills" / "registry.json"
    if not registry_file.exists():
        registry = {
            "version": "3.1.0-lite",
            "agents": [],
            "skills": [],
            "last_updated": "2026-02-18T00:00:00+08:00"
        }
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        print(f"  ✅ Created skills/registry.json")
    
    subagent_file = fis31_dir / "subagent_registry.json"
    if not subagent_file.exists():
        registry = {
            "version": "3.1.0-lite",
            "subagents": [],
            "id_counter": 0
        }
        with open(subagent_file, 'w') as f:
            json.dump(registry, f, indent=2)
        print(f"  ✅ Created subagent_registry.json")
    
    return fis31_dir

def init_agent_extension(agent_name: str):
    """初始化单个 Agent 的分形扩展"""
    from fis_config import get_shared_hub_path
    
    print(f"\n🔧 Step 2: Initialize Agent Extension for '{agent_name}'")
    print("-" * 40)
    
    openclaw_dir = Path.home() / ".openclaw"
    
    # Map agent names to workspace directories
    agent_dirs = {
        "cybermao": "workspace",
        "pulse": "workspace-radar",
        "painter": "workspace-painter",
        "formatter": "workspace-formatter",
        "hardware": "workspace-hardware"
    }
    
    workspace_name = agent_dirs.get(agent_name, f"workspace-{agent_name}")
    workspace_path = openclaw_dir / workspace_name
    
    if not workspace_path.exists():
        print(f"  ⚠️  Workspace not found: {workspace_path}")
        print(f"  💡 Please create it first or use a different name")
        return None
    
    # Create .fis3.1 directory
    fis31_dir = workspace_path / ".fis3.1"
    fis31_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (fis31_dir / "local_cache").mkdir(exist_ok=True)
    (fis31_dir / "memories").mkdir(exist_ok=True)
    
    # Create skill manifest
    import json
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
        print(f"  ✅ Created skill_manifest.json")
    
    print(f"  ✅ Extension ready: {fis31_dir}")
    return fis31_dir

def init_fis31():
    """Initialize FIS 3.1 Lite environment"""
    
    print("🚀 FIS 3.1 Lite Initialization")
    print("=" * 50)
    print("\nThis will set up:")
    print("  1. Shared Hub (fis-hub/.fis3.1/ or custom name)")
    print("  2. Agent Extensions (workspace*/.fis3.1/)")
    
    # Ask for custom hub name
    hub_name = input("\nEnter shared hub name (press Enter for default 'fis-hub'): ").strip()
    if not hub_name:
        hub_name = None
    
    # Step 1: Shared Hub
    shared_hub = init_shared_hub(hub_name)
    
    # Step 2: Ask for agent extensions
    print("\n" + "=" * 50)
    print("\n💡 Now let's set up Agent extensions.")
    print("Available agents: cybermao, pulse, painter, formatter, hardware")
    
    response = input("\nSetup extensions for which agents? (comma-separated, or 'all', or 'skip'): ").strip().lower()
    
    if response == 'skip':
        print("\n⏭️  Skipping agent extensions.")
    elif response == 'all':
        for agent in ["cybermao", "pulse", "painter", "formatter", "hardware"]:
            init_agent_extension(agent)
    else:
        agents = [a.strip() for a in response.split(",")]
        for agent in agents:
            if agent:
                init_agent_extension(agent)
    
    print("\n" + "=" * 50)
    print("✅ FIS 3.1 Lite initialized successfully!")
    print("\n📚 Next steps:")
    print("  1. Read AGENT_GUIDE.md - Learn when to use SubAgents")
    print("  2. Try examples/subagent_pipeline.py")
    print("  3. Add FIS checks to your HEARTBEAT.md")
    print("\n⚠️  Remember:")
    print("  - Simple tasks: Handle directly")
    print("  - Complex tasks: Use SubAgents with proper cleanup")

if __name__ == "__main__":
    init_fis31()
