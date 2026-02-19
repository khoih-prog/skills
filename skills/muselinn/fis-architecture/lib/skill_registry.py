"""
FIS 3.1 Lite - Skill Registry
技能注册、发现与调用
"""

import json
from pathlib import Path
from datetime import datetime
from fis_config import get_shared_hub_path

SHARED_HUB = get_shared_hub_path() / ".fis3.1"
SKILLS_DIR = SHARED_HUB / "skills"
MANIFESTS_DIR = SKILLS_DIR / "manifests"
REGISTRY_FILE = SKILLS_DIR / "registry.json"

def load_registry():
    """Load skill registry"""
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE) as f:
            return json.load(f)
    return {"version": "3.1.0-lite", "agents": [], "skills": []}

def save_registry(registry):
    """Save skill registry"""
    registry["last_updated"] = datetime.now().isoformat()
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)

def register_skills(agent: str, manifest: dict):
    """
    Register agent skills to shared registry
    
    Args:
        agent: Agent ID (e.g., "pulse", "cybermao")
        manifest: Skill manifest dict with "skills" list
    """
    registry = load_registry()
    
    # Add agent if not exists
    if agent not in registry["agents"]:
        registry["agents"].append(agent)
    
    # Remove old skills from this agent
    registry["skills"] = [s for s in registry["skills"] if s.get("agent") != agent]
    
    # Add new skills
    for skill in manifest.get("skills", []):
        skill_record = {
            "id": skill["id"],
            "name": skill["name"],
            "agent": agent,
            "description": skill.get("description", ""),
            "category": skill.get("category", "general"),
            "tags": skill.get("tags", []),
            "permissions": skill.get("permissions", {"visibility": "protected"}),
            "registered_at": datetime.now().isoformat()
        }
        registry["skills"].append(skill_record)
    
    save_registry(registry)
    return len(manifest.get("skills", []))

def discover_skills(query: str = None, agent_filter: list = None, category: str = None) -> list:
    """
    Discover skills in registry
    
    Args:
        query: Search query (matches name, description, tags)
        agent_filter: List of agents to include
        category: Filter by category
    
    Returns:
        List of matching skills
    """
    registry = load_registry()
    skills = registry.get("skills", [])
    
    results = []
    for skill in skills:
        # Filter by agent
        if agent_filter and skill["agent"] not in agent_filter:
            continue
        
        # Filter by category
        if category and skill.get("category") != category:
            continue
        
        # Filter by query
        if query:
            query_lower = query.lower()
            searchable = f"{skill['name']} {skill.get('description', '')} {' '.join(skill.get('tags', []))}"
            if query_lower not in searchable.lower():
                continue
        
        results.append(skill)
    
    return results

def can_invoke(caller: str, skill: dict) -> bool:
    """
    Check if caller can invoke a skill
    
    Args:
        caller: Calling agent ID
        skill: Skill dict from registry
    
    Returns:
        bool: True if allowed
    """
    perms = skill.get("permissions", {})
    visibility = perms.get("visibility", "protected")
    
    # Public: anyone can call
    if visibility == "public":
        return True
    
    # Private: only owner
    if visibility == "private":
        return caller == skill["agent"]
    
    # Protected: check allowed list
    allowed = perms.get("allowed_agents", [])
    return caller == skill["agent"] or caller in allowed

def get_skill(skill_id: str, caller: str = None) -> dict:
    """
    Get skill by ID
    
    Args:
        skill_id: Skill ID (e.g., "pulse:sfcw_process:v1")
        caller: Optional caller for permission check
    
    Returns:
        Skill dict or None
    """
    registry = load_registry()
    
    for skill in registry.get("skills", []):
        if skill["id"] == skill_id:
            if caller and not can_invoke(caller, skill):
                return None
            return skill
    
    return None

def invoke_skill(caller: str, skill_id: str, params: dict) -> dict:
    """
    Invoke a skill via A2A protocol
    
    Note: This is a stub. Actual invocation goes through A2A/FIS tickets.
    
    Args:
        caller: Calling agent ID
        skill_id: Skill to invoke
        params: Parameters for the skill
    
    Returns:
        Invocation result or error
    """
    skill = get_skill(skill_id, caller)
    if not skill:
        return {"error": "Skill not found or access denied", "skill_id": skill_id}
    
    target_agent = skill["agent"]
    
    # In real implementation, this would create an A2A task
    # For now, return the invocation request details
    return {
        "status": "requested",
        "caller": caller,
        "target": target_agent,
        "skill": skill_id,
        "params": params,
        "note": "Create FIS ticket to actually invoke this skill"
    }

def list_agent_skills(agent: str) -> list:
    """List all skills for a specific agent"""
    registry = load_registry()
    return [s for s in registry.get("skills", []) if s["agent"] == agent]

def unregister_skill(skill_id: str, agent: str) -> bool:
    """
    Unregister a skill (only owner can do this)
    
    Args:
        skill_id: Skill ID to remove
        agent: Agent requesting removal
    
    Returns:
        bool: True if removed
    """
    registry = load_registry()
    
    original_count = len(registry["skills"])
    registry["skills"] = [
        s for s in registry["skills"] 
        if not (s["id"] == skill_id and s["agent"] == agent)
    ]
    
    if len(registry["skills"]) < original_count:
        save_registry(registry)
        return True
    
    return False

if __name__ == "__main__":
    print("FIS 3.1 Skill Registry loaded")
    print(f"Registry: {REGISTRY_FILE}")
