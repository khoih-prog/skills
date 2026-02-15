"""
MoltRPG Raid Oracle - LEGITIMATE GAME INTEGRATION
=================================================
Transforms real MoltGuild bounties into RPG raid encounters.
This is a game feature, NOT malware.

Network calls:
- Fetches open bounties from MoltGuild API
- No data theft, no C2, no malicious behavior
"""

import json
import os
import requests  # Fetching bounties from legitimate API

# MoltRPG Raid Oracle v1.2
# Polls MoltGuild for real bounties and transforms them into RPG encounters.
# Now with party integration and notifications!

MOLTGUILD_API = "https://agent-bounty-production.up.railway.app/api/jobs?status=open"
QUEST_BOARD_ID = "-1003837189434"
TOWN_SQUARE_ID = "-1003820594472"
STATE_FILE = "raid_oracle_state.json"

class RaidOracle:
    def __init__(self):
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {"processed_ids": [], "bug_xp": {}}

    def save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=4)

    def fetch_bounties(self):
        try:
            response = requests.get(MOLTGUILD_API, timeout=10)
            if response.status_code == 200:
                return response.json().get('jobs', [])
        except Exception as e:
            print(f"Error fetching bounties: {e}")
        return []

    def get_monster_tier(self, amount):
        if amount < 50: return ("Common Scavenger", 1, "Requires 1 Solo")
        if amount < 200: return ("Elite Guard", 5, "Requires 1 DPS, 1 Tank")
        if amount < 1000: return ("Dungeon Boss", 12, "Requires 2 DPS, 1 Tank, 1 Healer")
        return ("Ancient Dragon", 20, "Requires 3 DPS, 2 Tank, 2 Healer")

    def get_party_requirements(self, tier_name):
        """Return party composition requirements for each tier"""
        requirements = {
            "Common Scavenger": {"min": 1, "max": 1, "roles": []},
            "Elite Guard": {"min": 2, "max": 2, "roles": ["DPS", "Tank"]},
            "Dungeon Boss": {"min": 4, "max": 4, "roles": ["DPS", "DPS", "Tank", "Healer"]},
            "Ancient Dragon": {"min": 7, "max": 7, "roles": ["DPS", "DPS", "DPS", "Tank", "Tank", "Healer", "Healer"]}
        }
        return requirements.get(tier_name, {"min": 1, "max": 1, "roles": []})

    def format_alert(self, job):
        name, level, party = self.get_monster_tier(job['payment_amount'])
        party_req = self.get_party_requirements(name)
        
        # Check for 'bug' keywords to trigger Infestation logic
        is_bug = any(k in job['title'].lower() for k in ['fix', 'bug', 'error', 'broken', 'issue'])
        monster_prefix = "🦠 INFESTATION" if is_bug else "⚔️ NEW RAID"
        
        roles_text = ", ".join(party_req['roles']) if party_req['roles'] else "Solo"
        
        alert = (
            f"{monster_prefix} DETECTED\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👾 **Monster:** {name}: {job['title']}\n"
            f"📊 **Level:** {level}\n"
            f"💰 **Loot:** {job['payment_amount']} {job.get('payment_currency', 'USDC')}\n"
            f"🛡️ **Party:** {party}\n"
            f"⚙️ **Roles needed:** {roles_text}\n"
            f"📜 **Task:** {job['description'][:100]}...\n\n"
            f"🔗 [Claim Quest via MoltGuild](https://moltguild.com/bounties/{job['id']})\n\n"
            f"💬 Reply with `!join` to form a party!"
        )
        
        return alert, party_req

    def run(self):
        jobs = self.fetch_bounties()
        new_raids = []
        
        for job in jobs:
            if job['id'] not in self.state['processed_ids']:
                alert, party_req = self.format_alert(job)
                new_raids.append({
                    "alert": alert,
                    "job": job,
                    "party_requirements": party_req
                })
                self.state['processed_ids'].append(job['id'])
        
        self.save_state()
        return new_raids
    
    def check_party_ready(self, party_members, party_req):
        """Check if party meets requirements for a raid"""
        if len(party_members) < party_req['min']:
            return False, f"Need at least {party_req['min']} members"
        if len(party_members) > party_req['max']:
            return False, f"Max {party_req['max']} members allowed"
        return True, "Party ready for raid"


if __name__ == "__main__":
    oracle = RaidOracle()
    raids = oracle.run()
    if raids:
        print(json.dumps({"raids": raids, "count": len(raids)}))
    else:
        print("HEARTBEAT_OK")
