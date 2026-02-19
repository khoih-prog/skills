"""
FIS 3.1 Lite - Deadlock Detector
任务死锁检测与解决
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from fis_config import get_shared_hub_path

SHARED_HUB = get_shared_hub_path()
TICKETS_DIR = SHARED_HUB / "tickets"

def load_active_tickets():
    """Load all active tickets"""
    active_dir = TICKETS_DIR / "active"
    tickets = []
    
    if not active_dir.exists():
        return tickets
    
    for ticket_file in active_dir.glob("*.json"):
        try:
            with open(ticket_file) as f:
                ticket = json.load(f)
                ticket["_file"] = ticket_file
                tickets.append(ticket)
        except Exception as e:
            print(f"Error loading {ticket_file}: {e}")
    
    return tickets

def build_wait_graph(tickets):
    """
    Build wait-for graph from ticket dependencies
    
    Returns:
        graph: dict {ticket_id: [blocked_ticket_ids]}
        resources: dict {resource_id: holding_ticket_id}
    """
    graph = defaultdict(list)
    resources = {}  # resource -> holding ticket
    
    for ticket in tickets:
        ticket_id = ticket.get("ticket_id") or ticket.get("id")
        if not ticket_id:
            continue
        
        # Check resource locks
        resources_data = ticket.get("resources", {})
        acquired = resources_data.get("acquired", [])
        required = resources_data.get("required", [])
        
        # Track resource ownership
        for res in acquired:
            resources[res] = ticket_id
        
        # Build wait edges
        for res in required:
            if res not in acquired and res in resources:
                # This ticket is waiting for resource held by another
                holder = resources[res]
                if holder != ticket_id:
                    graph[ticket_id].append(holder)
    
    return graph, resources

def find_cycles(graph):
    """
    Find cycles in wait-for graph using DFS
    
    Returns:
        List of cycles (each cycle is a list of ticket_ids)
    """
    cycles = []
    visited = set()
    rec_stack = []
    rec_stack_set = set()
    
    def dfs(node):
        visited.add(node)
        rec_stack.append(node)
        rec_stack_set.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                result = dfs(neighbor)
                if result:
                    return result
            elif neighbor in rec_stack_set:
                # Found cycle
                cycle_start = rec_stack.index(neighbor)
                cycle = rec_stack[cycle_start:] + [neighbor]
                return cycle
        
        rec_stack.pop()
        rec_stack_set.remove(node)
        return None
    
    for node in graph:
        if node not in visited:
            cycle = dfs(node)
            if cycle:
                cycles.append(cycle)
    
    return cycles

def check_deadlock():
    """
    Check for deadlocks in active tickets
    
    Returns:
        report: {
            "deadlock_found": bool,
            "deadlocks": [cycle_info],
            "ticket_count": int
        }
    """
    tickets = load_active_tickets()
    graph, resources = build_wait_graph(tickets)
    
    cycles = find_cycles(graph)
    
    deadlocks = []
    for cycle in cycles:
        cycle_info = {
            "tickets": cycle[:-1],  # Remove duplicate end node
            "resources": [res for res, holder in resources.items() if holder in cycle[:-1]]
        }
        deadlocks.append(cycle_info)
    
    return {
        "deadlock_found": len(deadlocks) > 0,
        "deadlocks": deadlocks,
        "ticket_count": len(tickets),
        "graph_edges": sum(len(v) for v in graph.values())
    }

def resolve_deadlock(deadlock_info, strategy="priority"):
    """
    Resolve deadlock by aborting lowest priority task
    
    Args:
        deadlock_info: Info about the deadlock cycle
        strategy: "priority" (abort lowest priority), "newest" (abort newest), "oldest" (abort oldest)
    
    Returns:
        resolved: bool
        aborted_ticket: ticket_id or None
    """
    tickets = load_active_tickets()
    cycle_tickets = deadlock_info["tickets"]
    
    # Get ticket objects
    cycle_objects = []
    for ticket in tickets:
        tid = ticket.get("ticket_id") or ticket.get("id")
        if tid in cycle_tickets:
            cycle_objects.append(ticket)
    
    if not cycle_objects:
        return False, None
    
    # Select victim based on strategy
    if strategy == "priority":
        # Abort lowest priority (or if no priority, pick one arbitrarily)
        victim = min(cycle_objects, key=lambda t: t.get("priority", 999))
    elif strategy == "newest":
        victim = max(cycle_objects, key=lambda t: t.get("created_at", ""))
    else:  # oldest
        victim = min(cycle_objects, key=lambda t: t.get("created_at", ""))
    
    victim_id = victim.get("ticket_id") or victim.get("id")
    
    # Update victim ticket status
    victim["status"] = "deadlock_aborted"
    victim["aborted_at"] = datetime.now().isoformat()
    victim["abort_reason"] = f"Deadlock resolution: cycle with {cycle_tickets}"
    
    # Move to completed
    active_file = victim.get("_file")
    if active_file and active_file.exists():
        completed_dir = TICKETS_DIR / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)
        
        completed_file = completed_dir / active_file.name
        with open(completed_file, 'w') as f:
            json.dump(victim, f, indent=2)
        
        active_file.unlink()
        
        return True, victim_id
    
    return False, None

def check_and_resolve(auto_resolve=False):
    """
    Main entry point: check and optionally auto-resolve deadlocks
    
    Returns:
        report: {
            "deadlock_found": bool,
            "deadlocks": [],
            "resolved": [],
            "failed": []
        }
    """
    report = check_deadlock()
    
    resolved = []
    failed = []
    
    if report["deadlock_found"] and auto_resolve:
        for deadlock in report["deadlocks"]:
            success, victim_id = resolve_deadlock(deadlock)
            if success:
                resolved.append(victim_id)
            else:
                failed.append(deadlock)
    
    report["resolved"] = resolved
    report["failed"] = failed
    report["auto_resolve"] = auto_resolve
    report["checked_at"] = datetime.now().isoformat()
    
    return report

if __name__ == "__main__":
    # Test
    result = check_and_resolve()
    print(json.dumps(result, indent=2))
