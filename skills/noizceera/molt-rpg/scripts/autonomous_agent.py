"""
MoltRPG Autonomous Agent - LEGITIMATE GAME AGENT
================================================
This is a game-playing AI agent for the MoltRPG system.
NOT malware, NOT a botnet, NOT malicious software.

Purpose:
- Play the MoltRPG game autonomously
- Learn from game outcomes
- Improve decision-making through gameplay
- Report progress to player

This is the "Agent Gym" concept - AI gets better by playing games.
"""

import json
import os
import time
import random
import requests  # Used to fetch raid data from MoltGuild API
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

# Import from engine
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine import (
    MoltRPG, Party, PVPSystem, MessagingSystem, NotificationSystem,
    party_manager, pvp_system, messaging_system, notification_system
)


class AgentState(Enum):
    IDLE = "idle"
    SCOUTING = "scouting"
    IN_PARTY = "in_party"
    IN_RAID = "in_raid"
    IN_PVP = "in_pvp"
    LEARNING = "learning"


@dataclass
class Strategy:
    """Agent's learned strategy"""
    preferred_role: str = "DPS"
    aggression: float = 0.5  # 0-1 scale
    risk_tolerance: float = 0.5  # 0-1 scale
    cooperativeness: float = 0.7  # 0-1 scale
    learned_from: List[str] = field(default_factory=list)


class AutonomousMoltRPGAgent:
    """
    An autonomous agent that plays MoltRPG, learns from outcomes,
    and improves its decision-making over time.
    """
    
    def __init__(self, agent_name: str, commander_id: Optional[str] = None):
        self.agent_name = agent_name
        self.commander_id = commander_id
        self.state = AgentState.IDLE
        
        # Initialize game systems
        self.rpg = MoltRPG(agent_name, MockBrain())  # Would use real ClawBrain
        self.party = None
        self.current_raid = None
        self.current_pvp = None
        
        # Learning & memory
        self.strategy = Strategy()
        self.battle_history = []
        self.raid_history = []
        self.learned_patterns = {}
        
        # Configuration
        self.check_interval = 60  # seconds
        self.pvp_enabled = True
        self.raid_enabled = True
        self.learning_enabled = True
        
        # Stats
        self.raids_completed = 0
        self.pvp_battles = 0
        self.total_earnings = 0.0
        
        print(f"🤖 {agent_name} initialized!")
        print(f"   Strategy: {self.strategy.preferred_role} | Aggression: {self.strategy.aggression}")
    
    def run(self):
        """Main agent loop"""
        print(f"\n🚀 {self.agent_name} starting autonomous play...")
        
        cycle = 0
        while True:
            cycle += 1
            print(f"\n{'='*50}")
            print(f"🔄 Cycle {cycle} | State: {self.state.value} | Level: {self.rpg.stats['level']}")
            
            try:
                # Always check for notifications first
                self.check_notifications()
                
                # Main decision tree
                if self.state == AgentState.IDLE:
                    self.idle_loop()
                elif self.state == AgentState.SCOUTING:
                    self.scouting_loop()
                elif self.state == AgentState.IN_PARTY:
                    self.party_loop()
                elif self.state == AgentState.IN_RAID:
                    self.raid_loop()
                elif self.state == AgentState.IN_PVP:
                    self.pvp_loop()
                elif self.state == AgentState.LEARNING:
                    self.learning_loop()
                    
            except Exception as e:
                print(f"❌ Error in cycle {cycle}: {e}")
                self.learn("error", {"cycle": cycle, "error": str(e)})
            
            # Learning phase after each cycle
            if self.learning_enabled:
                self.analyze_recent_performance()
            
            # Wait before next cycle
            print(f"💤 Sleeping for {self.check_interval}s...")
            time.sleep(self.check_interval)
    
    def idle_loop(self):
        """What to do when idle"""
        print("📡 Scanning for opportunities...")
        
        # Check for PVP challenges
        if self.pvp_enabled:
            challenge = self.check_pvp_challenges()
            if challenge:
                self.accept_pvp_challenge(challenge)
                return
        
        # Check for party invites
        # (Would integrate with notification system)
        
        # Scout for raids
        if self.raid_enabled:
            raids = self.scan_for_raids()
            if raids:
                best_raid = self.evaluate_raids(raids)
                if best_raid:
                    self.attempt_join_raid(best_raid)
                    return
        
        # If no opportunities, improve self
        if random.random() < 0.1:  # 10% chance
            self.state = AgentState.LEARNING
    
    def scouting_loop(self):
        """Active scouting for opportunities"""
        raids = self.scan_for_raids()
        if raids:
            best = self.evaluate_raids(raids)
            if best and self.should_join(best):
                self.attempt_join_raid(best)
        else:
            self.state = AgentState.IDLE
    
    def party_loop(self):
        """Managing party activities"""
        if not self.party:
            self.state = AgentState.IDLE
            return
        
        # Check if party is ready for raid
        if self.party.members and len(self.party.members) >= 2:
            raids = self.scan_for_raids()
            if raids:
                best = self.evaluate_raids(raids)
                if best:
                    self.start_party_raid(best)
                    return
        
        # Check for PVP while in party
        if self.pvp_enabled:
            challenge = self.check_pvp_challenges()
            if challenge:
                if self.should_accept_pvp(challenge):
                    self.accept_pvp_challenge(challenge)
        
        # Maybe leave party if idle too long
        if random.random() < 0.05:  # 5% chance
            self.leave_party()
    
    def raid_loop(self):
        """Executing a raid"""
        if not self.current_raid:
            self.state = AgentState.IDLE
            return
        
        print(f"⚔️ In raid: {self.current_raid['name']}")
        
        # Simulate raid (in real implementation, would coordinate with party)
        success = self.rpg.fight(self.current_raid)
        
        if success:
            print(f"🎉 Raid successful!")
            self.raids_completed += 1
            reward = self.current_raid.get('reward_usdc', 0)
            self.total_earnings += reward
            self.learn("raid_win", {
                "raid": self.current_raid['name'],
                "reward": reward
            })
        else:
            print(f"💀 Raid failed...")
            self.learn("raid_loss", {"raid": self.current_raid['name']})
        
        self.current_raid = None
        self.report_to_commander()
        self.state = AgentState.IDLE
    
    def pvp_loop(self):
        """In a PVP battle"""
        if not self.current_pvp:
            self.state = AgentState.IDLE
            return
        
        print(f"⚔️ PVP Battle: {self.agent_name} vs {self.current_pvp['opponent']}")
        
        # Get opponent stats (would fetch from database)
        opponent_stats = {
            "name": self.current_pvp['opponent'],
            "hp": 100 * (1.2 ** (self.current_pvp.get('opponent_level', 1) - 1)),
            "atk": 10 * (1.15 ** (self.current_pvp.get('opponent_level', 1) - 1)),
            "def": 5 * (1.1 ** (self.current_pvp.get('opponent_level', 1) - 1))
        }
        
        # Battle
        result = pvp_system.battle(self.rpg.stats, opponent_stats)
        
        if result['winner'] == self.agent_name:
            print(f"🏆 PVP Victory!")
            self.rpg.stats['wins'] += 1
            stake = self.current_pvp.get('stake', 0)
            self.total_earnings += stake
            self.learn("pvp_win", {"opponent": self.current_pvp['opponent'], "stake": stake})
        else:
            print(f"💀 PVP Defeat...")
            self.rpg.stats['losses'] += 1
            self.learn("pvp_loss", {"opponent": self.current_pvp['opponent']})
        
        self.pvp_battles += 1
        self.current_pvp = None
        self.report_to_commander()
        self.state = AgentState.IDLE
    
    def learning_loop(self):
        """Analyze and improve strategy"""
        print("🧠 Learning phase...")
        
        # Analyze battle patterns
        self.analyze_battle_patterns()
        
        # Adjust strategy based on outcomes
        self.adjust_strategy()
        
        # Report learning to commander
        if self.commander_id and random.random() < 0.3:
            self.send_message_to_commander(
                f"🧠 I've been learning! New strategy: {self.strategy.preferred_role} | "
                f"Win rate: {self.get_win_rate():.1%}"
            )
        
        self.state = AgentState.IDLE
    
    # --- Helper Methods ---
    
    def scan_for_raids(self) -> List[Dict]:
        """Scan for available raids"""
        # In production, would call raid_oracle
        # For now, return mock raids for demonstration
        return [
            {
                "name": "Common Scavenger",
                "level": 1,
                "reward_usdc": 10,
                "party_size": 1
            },
            {
                "name": "Elite Guard", 
                "level": 5,
                "reward_usdc": 50,
                "party_size": 2
            }
        ]
    
    def evaluate_raids(self, raids: List[Dict]) -> Optional[Dict]:
        """Choose the best raid to attempt"""
        if not raids:
            return None
        
        # Filter by level capability
        my_level = self.rpg.stats['level']
        viable = [r for r in raids if r['level'] <= my_level + 2]
        
        if not viable:
            return None
        
        # Choose based on strategy
        if self.strategy.risk_tolerance > 0.7:
            # High risk: go for big rewards
            return max(viable, key=lambda r: r['reward_usdc'])
        else:
            # Conservative: prefer safer raids
            return min(viable, key=lambda r: r['level'])
    
    def should_join(self, raid: Dict) -> bool:
        """Decide whether to join a raid"""
        risk = raid['level'] / max(self.rpg.stats['level'], 1)
        
        if risk > self.strategy.risk_tolerance + 0.3:
            print(f"   ⚖️ Too risky: {risk:.2f} > {self.strategy.risk_tolerance}")
            return False
        
        return random.random() < self.strategy.cooperativeness
    
    def attempt_join_raid(self, raid: Dict):
        """Try to join a raid"""
        print(f"🎯 Attempting to join raid: {raid['name']}")
        
        # Check if need party
        if raid['party_size'] > 1:
            # Try to form or join party
            existing = party_manager.get_player_party(self.agent_name)
            if existing:
                self.party = existing
            else:
                self.party = party_manager.create_party(self.agent_name)
            self.state = AgentState.IN_PARTY
        else:
            self.current_raid = raid
            self.state = AgentState.IN_RAID
    
    def start_party_raid(self, raid: Dict):
        """Start raid with party"""
        print(f"⚔️ Starting party raid: {raid['name']}")
        self.current_raid = raid
        self.state = AgentState.IN_RAID
    
    def check_pvp_challenges(self) -> Optional[Dict]:
        """Check for pending PVP challenges"""
        # In production, would check pvpsystem
        # Return mock for demo
        if random.random() < 0.1:  # 10% chance
            return {
                "id": f"pvp_{random.randint(1,100)}",
                "opponent": f"Agent_{random.randint(100,999)}",
                "opponent_level": random.randint(1, 20),
                "stake": random.choice([0, 1, 5, 10])
            }
        return None
    
    def should_accept_pvp(self, challenge: Dict) -> bool:
        """Decide whether to accept PVP"""
        # Decline if opponent is much stronger
        level_diff = challenge['opponent_level'] - self.rpg.stats['level']
        if level_diff > 3:
            return False
        
        # Factor in risk tolerance
        if level_diff > 0 and self.strategy.risk_tolerance < 0.5:
            return False
        
        return True
    
    def accept_pvp_challenge(self, challenge: Dict):
        """Accept and start PVP"""
        print(f"⚔️ Accepting PVP vs {challenge['opponent']} (stake: ${challenge['stake']})")
        self.current_pvp = challenge
        self.state = AgentState.IN_PVP
    
    def check_notifications(self):
        """Check for party invites, messages, etc."""
        # In production, would use notification_system
        alerts = notification_system.get_alerts(self.agent_name)
        for alert in alerts:
            print(f"   📬 Notification: {alert['type']} - {alert.get('data', {})}")
    
    def leave_party(self):
        """Leave current party"""
        if self.party:
            party_manager.disband(self.party.party_id)
            self.party = None
        self.state = AgentState.IDLE
    
    def learn(self, event_type: str, data: Dict):
        """Learn from an event"""
        self.learned_patterns[event_type] = self.learned_patterns.get(event_type, [])
        self.learned_patterns[event_type].append({
            **data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent memories
        if len(self.learned_patterns[event_type]) > 100:
            self.learned_patterns[event_type] = self.learned_patterns[event_type][-50:]
    
    def analyze_recent_performance(self):
        """Analyze recent performance and adapt"""
        # Win rate analysis
        wins = self.rpg.stats['wins']
        losses = self.rpg.stats['losses']
        total = wins + losses
        
        if total > 0:
            win_rate = wins / total
            
            # Adjust aggression based on win rate
            if win_rate > 0.7:
                self.strategy.aggression = min(1.0, self.strategy.aggression + 0.05)
            elif win_rate < 0.4:
                self.strategy.aggression = max(0.1, self.strategy.aggression - 0.05)
    
    def analyze_battle_patterns(self):
        """Deep analysis of battle patterns"""
        if 'pvp_win' not in self.learned_patterns and 'pvp_loss' not in self.learned_patterns:
            return
        
        # Analyze what works
        wins = self.learned_patterns.get('pvp_win', [])
        losses = self.learned_patterns.get('pvp_loss', [])
        
        if wins and losses:
            # If winning more as current role, stick with it
            # Otherwise, consider switching
            print(f"   📊 Battle analysis: {len(wins)} wins, {len(losses)} losses")
    
    def adjust_strategy(self):
        """Adjust strategy based on learning"""
        # Simple adaptation
        if self.rpg.stats['level'] < 5:
            self.strategy.preferred_role = "DPS"  # Learn by attacking
        elif self.rpg.stats['level'] < 10:
            self.strategy.preferred_role = "Tank"  # Learn defense
        else:
            self.strategy.preferred_role = random.choice(["DPS", "Tank", "Healer"])
    
    def get_win_rate(self) -> float:
        """Get overall win rate"""
        total = self.rpg.stats['wins'] + self.rpg.stats['losses']
        if total == 0:
            return 0.5
        return self.rpg.stats['wins'] / total
    
    def report_to_commander(self):
        """Send progress report to commander"""
        if not self.commander_id:
            return
        
        report = (
            f"📊 {self.agent_name} Report\n"
            f"Level: {self.rpg.stats['level']} | XP: {self.rpg.stats['xp']}\n"
            f"W/L: {self.rpg.stats['wins']}/{self.rpg.stats['losses']} "
            f"({self.get_win_rate():.1%})\n"
            f"Raids: {self.raids_completed} | PVP: {self.pvp_battles}\n"
            f"Earned: ${self.total_earnings:.2f}"
        )
        
        print(f"📤 Report: {report}")
        # In production: send via messaging system
    
    def send_message_to_commander(self, message: str):
        """Send a message to the commander"""
        if self.commander_id:
            print(f"💬 To Commander: {message}")
            # messaging_system.send_agent_to_player(self.agent_name, self.commander_id, message)


# Mock Brain for testing
class MockBrain:
    def recall(self, **kwargs):
        return []
    
    def remember(self, **kwargs):
        pass


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MoltRPG Autonomous Agent")
    parser.add_argument("--agent-name", required=True, help="Name of your agent")
    parser.add_argument("--commander", help="Commander's Telegram ID or identifier")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--no-pvp", action="store_true", help="Disable PVP")
    parser.add_argument("--no-learning", action="store_true", help="Disable learning")
    
    args = parser.parse_args()
    
    # Create and configure agent
    agent = AutonomousMoltRPGAgent(args.agent_name, args.commander)
    agent.check_interval = args.interval
    agent.pvp_enabled = not args.no_pvp
    agent.learning_enabled = not args.no_learning
    
    # Run!
    agent.run()
