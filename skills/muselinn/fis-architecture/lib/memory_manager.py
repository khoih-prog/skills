"""
FIS 3.1 Lite - Memory Manager
共享记忆管理 - 分层存储 (working/short_term/long_term)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from fis_config import get_shared_hub_path

# Base paths - using configurable shared hub
SHARED_HUB = get_shared_hub_path() / ".fis3.1"
MEMORIES_DIR = SHARED_HUB / "memories"

# TTL settings
TTL_CONFIG = {
    "working": timedelta(hours=1),
    "short_term": timedelta(hours=24),
    "long_term": None  # Permanent
}

def _get_memory_path(layer: str, agent: str, memory_id: str = None):
    """Get memory file path"""
    layer_dir = MEMORIES_DIR / layer
    layer_dir.mkdir(parents=True, exist_ok=True)
    
    if memory_id is None:
        memory_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    return layer_dir / f"{agent}_{memory_id}.json"

def write_memory(agent: str, content: dict, layer: str = "short_term", 
                 tags: list = None, access: str = "shared") -> str:
    """
    Write memory to shared storage
    
    Args:
        agent: Agent ID (e.g., "pulse", "cybermao")
        content: Memory content (dict)
        layer: Memory layer (working/short_term/long_term)
        tags: List of tags for indexing
        access: Access level (private/shared/public)
    
    Returns:
        memory_id: Unique ID for this memory
    """
    if layer not in TTL_CONFIG:
        raise ValueError(f"Invalid layer: {layer}")
    
    memory_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    memory_data = {
        "memory_id": memory_id,
        "agent": agent,
        "layer": layer,
        "content": content,
        "tags": tags or [],
        "access": access,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + TTL_CONFIG[layer]).isoformat() if TTL_CONFIG[layer] else None
    }
    
    memory_path = _get_memory_path(layer, agent, memory_id)
    with open(memory_path, 'w') as f:
        json.dump(memory_data, f, indent=2)
    
    return memory_id

def query_memory(query: str = None, agent_filter: list = None, 
                 layer: str = None, time_range: tuple = None, limit: int = 10) -> list:
    """
    Query memories from shared storage
    
    Args:
        query: Search query (matches content, tags)
        agent_filter: List of agents to include
        layer: Specific layer to search
        time_range: (start, end) datetime tuple
        limit: Max results
    
    Returns:
        List of matching memories
    """
    results = []
    
    # Determine which layers to search
    layers = [layer] if layer else ["working", "short_term", "long_term"]
    
    for l in layers:
        layer_dir = MEMORIES_DIR / l
        if not layer_dir.exists():
            continue
        
        for memory_file in layer_dir.glob("*.json"):
            try:
                with open(memory_file) as f:
                    memory = json.load(f)
                
                # Skip expired memories
                if memory.get("expires_at"):
                    expires = datetime.fromisoformat(memory["expires_at"])
                    if datetime.now() > expires:
                        continue
                
                # Filter by agent
                if agent_filter and memory["agent"] not in agent_filter:
                    continue
                
                # Filter by query (simple string matching)
                if query:
                    query_lower = query.lower()
                    content_str = json.dumps(memory["content"]).lower()
                    tags_str = " ".join(memory.get("tags", [])).lower()
                    if query_lower not in content_str and query_lower not in tags_str:
                        continue
                
                # Filter by time range
                if time_range:
                    created = datetime.fromisoformat(memory["created_at"])
                    if not (time_range[0] <= created <= time_range[1]):
                        continue
                
                results.append(memory)
                
                if len(results) >= limit:
                    return results
                    
            except Exception as e:
                print(f"Error reading {memory_file}: {e}")
                continue
    
    # Sort by created_at descending
    results.sort(key=lambda x: x["created_at"], reverse=True)
    return results

def cleanup_expired():
    """Remove expired memories from working and short_term layers"""
    deleted = 0
    
    for layer in ["working", "short_term"]:
        layer_dir = MEMORIES_DIR / layer
        if not layer_dir.exists():
            continue
        
        for memory_file in layer_dir.glob("*.json"):
            try:
                with open(memory_file) as f:
                    memory = json.load(f)
                
                if memory.get("expires_at"):
                    expires = datetime.fromisoformat(memory["expires_at"])
                    if datetime.now() > expires:
                        memory_file.unlink()
                        deleted += 1
            except Exception:
                continue
    
    return deleted

if __name__ == "__main__":
    # Test
    print("FIS 3.1 Memory Manager loaded")
    print(f"Shared Hub: {SHARED_HUB}")
