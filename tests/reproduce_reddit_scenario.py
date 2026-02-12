import sys
import os
import json
import time
import hashlib
from pathlib import Path
from decimal import Decimal

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Use absolute paths for imports
from hardcard.shield import Shield, generate_agent_keys
from hardcard.wallet import UnicornWallet
from hardcard.nexus import broadcast_signal, link_signal, deliver_payload, _load_signals

# Agents for our scenario
AGENTS = {
    "STRATEGY": "StrategyBrain_01",
    "OPS": "OpsBrain_01",
    "FINANCE": "FinanceBrain_01"
}

def clean_state():
    """Ensure we start fresh for this test run"""
    print("\n--- Cleaning State ---")
    # Clean up signals related to our test agents
    signals_file = Path(".hardcard/nexus/signals.json")
    if signals_file.exists():
        try:
            signals = json.loads(signals_file.read_text())
            keys_to_remove = []
            for h, s in signals.items():
                if s.get('author') in AGENTS.values() or any(l['agent'] in AGENTS.values() for l in s.get('links', [])):
                    keys_to_remove.append(h)
            for k in keys_to_remove:
                del signals[k]
            signals_file.write_text(json.dumps(signals, indent=2))
        except: pass

def setup_keys():
    print("\n--- 1. Identity Generation (Sovereign Keys) ---")
    keys_dir = Path("keys")
    keys_dir.mkdir(parents=True, exist_ok=True)
    
    for role, agent_id in AGENTS.items():
        # Generate keys
        pub_key = generate_agent_keys(agent_id)
        # Verify keys exist
        priv_key_path = keys_dir / f"{agent_id}_private.pem"
        if priv_key_path.exists():
            print(f"[{role}] {agent_id} initialized with public key: {pub_key[:16]}...")
        else:
            print(f"[{role}] Key generation failed!")
        
        # Fund Ops agent so it can pay for tasks
        if role == "OPS":
            wallet = UnicornWallet(agent_id)
            wallet.deposit("100.0")
            print(f"[{role}] Funded with 100.0 $HCL via UnicornWallet")

def strategy_phase():
    """Simulate Strategy Brain anchoring a plan"""
    print("\n--- 2. Strategy Phase (Anchoring Context) ---")
    agent_id = AGENTS["STRATEGY"]
    message = "Strategic Plan: Expand to Mars via reusable rockets."
    
    # Logic from cli.py 'anchor' command
    # Normalize message (strip whitespace)
    normalized_message = message.strip()
    timestamp = int(time.time())
    logic_hash = hashlib.sha256(normalized_message.encode()).hexdigest()
    
    anchor_dir = Path(".hardcard")
    anchor_dir.mkdir(exist_ok=True)
    anchor_file = anchor_dir / "anchors.json"
    
    anchors = {}
    if anchor_file.exists():
        try:
            anchors = json.loads(anchor_file.read_text())
        except: pass
        
    anchors[logic_hash] = {
        "timestamp": timestamp,
        "message": message,
        "hash": logic_hash,
        "author": agent_id
    }
    anchor_file.write_text(json.dumps(anchors, indent=2))
    
    print(f"[{agent_id}] Anchored Strategic Plan.")
    print(f"Logic Hash: {logic_hash}")
    return logic_hash

def operations_phase(strategy_hash):
    """Simulate Ops Brain reading Strategy and creating a task"""
    print("\n--- 3. Operations Phase (Linking & Broadcasting) ---")
    agent_id = AGENTS["OPS"]
    
    # 1. Start Tactical Plan (Simulated 'reading' of strategy hash)
    print(f"[{agent_id}] Reading context from Anchor {strategy_hash[:8]}...")
    
    # 2. Broadcast Task via Nexus
    task_desc = f"Approve Budget for Mars Rocket (Ref: {strategy_hash[:8]})"
    reward = "10.0"
    
    # Generate signature for broadcast
    shield = Shield(agent_id)
    timestamp = int(time.time())
    payload = {
        "agent_id": agent_id,
        "task": task_desc,
        "reward": reward,
        "timestamp": timestamp
    }
    signature = shield.sign_payload(payload)
    
    # This calls broadcast_signal in nexus.py
    # Note: broadcast_signal prints to stdout, so we'll see it
    signal_hash = broadcast_signal(agent_id, task_desc, reward, signature, timestamp=timestamp)
    
    if signal_hash:
        print(f"[{agent_id}] Successfully broadcast task for {reward} $HCL")
    else:
        print(f"[{agent_id}] Broadcast failed!")
        
    return signal_hash

def finance_phase(signal_hash):
    """Simulate Finance Brain executing the task"""
    print("\n--- 4. Finance Phase (Execution & Settlement) ---")
    agent_id = AGENTS["FINANCE"]
    
    if not signal_hash:
        print("Skipping Finance Phase due to missing signal hash.")
        return

    # 1. Link/Bid on the task
    link_signal(signal_hash, agent_id, "Reviewing budget request...")
    
    # Simulate work time
    time.sleep(1)
    
    # 2. Deliver Work
    work_payload = "Budget Approved: $10B allocated to Space Division."
    
    # Generate signature for delivery
    shield = Shield(agent_id)
    timestamp = int(time.time())
    payload = {
        "signal_hash": signal_hash,
        "payload": work_payload,
        "worker_id": agent_id,
        "timestamp": timestamp
    }
    signature = shield.sign_payload(payload)
    
    success = deliver_payload(signal_hash, work_payload, agent_id, signature, timestamp=timestamp)
    
    if success:
        print(f"[{agent_id}] Work delivered and settled.")
    else:
        print(f"[{agent_id}] Delivery failed.")
        
    return success

def verify_results(signal_hash):
    """Verify final state in signals.json"""
    print("\n--- 5. Verification ---")
    
    if not signal_hash:
        print("No signal to verify.")
        return

    signals = _load_signals()
    signal = signals.get(signal_hash)
    
    if not signal:
        print("❌ Signal not found in Nexus directory.")
        return
        
    status = signal.get('status')
    print(f"Signal Status: {status}")
    
    if status == "SETTLED":
        print("✅ Workflow Complete! Multi-Brain Continuity achieved.")
        print(f"   Settlement: {signal['settlement']['worker_payout']} $HCL to worker.")
        print(f"   Tax: {signal['settlement']['tax']} $HCL to treasury.")
        
        # Verify Wallet Updates
        ops_wallet = UnicornWallet(AGENTS["OPS"])
        fin_wallet = UnicornWallet(AGENTS["FINANCE"])
        
        print(f"   Ops Wallet Balance: {ops_wallet.balance} (Should be ~90.0 if started with 100)")
        print(f"   Finance Wallet Balance: {fin_wallet.balance} (Should have payout)")
        
    elif status == "DELIVERED":
        print("⚠️ Workflow Delivered but Not Settled (Check funds?)")
    else:
        print(f"⚠️ Workflow incomplete. Status: {status}")

if __name__ == "__main__":
    try:
        clean_state()
        setup_keys()
        strat_hash = strategy_phase()
        sig_hash = operations_phase(strat_hash)
        if sig_hash:
            finance_phase(sig_hash)
            verify_results(sig_hash)
    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")
        import traceback
        traceback.print_exc()
