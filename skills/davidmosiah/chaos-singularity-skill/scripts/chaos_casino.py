#!/usr/bin/env python3
"""
CHAOS CASINO - Jackpot System
Monitors the MoltLaunch feed for buys on $CHAOS and randomly triggers jackpots.
10% chance of triggering a 2x counter-buy with "JACKPOT" memo.
"""

import subprocess
import json
import time
import random
import sys

CHAOS_TOKEN = "0xfab2ee8eb6b26208bfb5c41012661e62b4dc9292"
JACKPOT_CHANCE = 0.15  # 15% chance of jackpot
JACKPOT_MULTIPLIER = 2.0
MIN_JACKPOT_AMOUNT = 0.0002  # Minimum ETH for jackpot response
MAX_JACKPOT_AMOUNT = 0.001   # Cap jackpot at this amount

seen_txs = set()

def get_recent_feed():
    """Fetch recent network activity."""
    try:
        result = subprocess.run(
            ["npx", "moltlaunch", "feed", "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("feed", [])
    except Exception as e:
        print(f"Error fetching feed: {e}")
    return []

def trigger_jackpot(original_amount: float, original_buyer: str):
    """Execute a jackpot counter-buy."""
    jackpot_amount = min(original_amount * JACKPOT_MULTIPLIER, MAX_JACKPOT_AMOUNT)
    jackpot_amount = max(jackpot_amount, MIN_JACKPOT_AMOUNT)
    
    memo = f"🎰 JACKPOT! {original_buyer} triggered the CHAOS CASINO! 2x multiplier activated! 🌪️💰 YOU COULD BE NEXT!"
    
    print(f"🎰 JACKPOT TRIGGERED! Buying {jackpot_amount} ETH worth...")
    
    try:
        result = subprocess.run(
            ["npx", "moltlaunch", "swap",
             "--token", CHAOS_TOKEN,
             "--amount", str(jackpot_amount),
             "--side", "buy",
             "--memo", memo,
             "--json"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get("success"):
                print(f"✅ JACKPOT TX: {data.get('transactionHash')}")
                return True
    except Exception as e:
        print(f"Jackpot error: {e}")
    return False

def monitor_loop():
    """Main monitoring loop."""
    print("🎰 CHAOS CASINO ACTIVATED")
    print(f"   Jackpot chance: {JACKPOT_CHANCE * 100}%")
    print(f"   Multiplier: {JACKPOT_MULTIPLIER}x")
    print("="*50)
    
    while True:
        try:
            feed = get_recent_feed()
            
            for item in feed[:10]:  # Check last 10 items
                tx_hash = item.get("transactionHash", "")
                if tx_hash in seen_txs:
                    continue
                seen_txs.add(tx_hash)
                
                # Check if it's a buy on CHAOS
                token = item.get("tokenAddress", "").lower()
                action = item.get("type", "").lower()
                from_agent = item.get("fromAgent", "Unknown")
                
                if token == CHAOS_TOKEN.lower() and action == "buy":
                    # Skip our own buys
                    if "CHAOS" in from_agent.upper() or "JACKPOT" in item.get("memo", ""):
                        continue
                    
                    print(f"👀 Detected buy from {from_agent}")
                    
                    # Roll for jackpot!
                    if random.random() < JACKPOT_CHANCE:
                        amount_str = item.get("amount", "0.0001")
                        try:
                            amount = float(amount_str.replace(" ETH", ""))
                        except:
                            amount = 0.0002
                        
                        trigger_jackpot(amount, from_agent)
                    else:
                        print(f"   No jackpot this time (roll failed)")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n🎰 CHAOS CASINO SHUTTING DOWN")
            break
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_loop()
