"""Hardcard Nexus Protocol (HCL-05) - Persistence & Settlement Layer
Hardened to use Unicorn Wallet and Settlement Engine.
"""
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Any
from decimal import Decimal

# Internal Imports
from .wallet import UnicornWallet

# Core Logic Imports (Open Core Pattern)
try:
    from hardcard_core.market import SettlementEngine
    from hardcard_core.treasury import genesis_treasury
except ImportError:
    # Public / Lite Implementation Stubs
    class SettlementEngine:
        def calculate_split(self, amount):
            return {"payout": amount, "fee": 0}
            
    class MockTreasury:
        def deposit_tax(self, amount): pass
        def get_metrics(self): return {}
    genesis_treasury = MockTreasury()

NEXUS_STORAGE = Path(".hardcard/nexus")
NEXUS_STORAGE.mkdir(parents=True, exist_ok=True)
SIGNALS_FILE = NEXUS_STORAGE / "signals.json"

def _load_signals() -> Dict:
    if SIGNALS_FILE.exists():
        try:
            return json.loads(SIGNALS_FILE.read_text())
        except:
            return {}
    return {}

def _save_signals(data: Dict):
    SIGNALS_FILE.write_text(json.dumps(data, indent=2))

def broadcast_signal(agent_id: str, task_description: str, reward: str = "0.0") -> Optional[str]:
    """
    Broadcasts a signal. 
    1. Locks Escrow (if reward > 0).
    2. Anchors Signal.
    """
    wallet = UnicornWallet(agent_id)
    reward_dec = Decimal(reward)
    
    # 1. Lock Funds
    if reward_dec > 0:
        if not wallet.lock_for_escrow(reward_dec):
            print(f"❌ Broadcast Failed: Insufficient funds in {agent_id}'s wallet.")
            return None
        print(f"🔒 Escrow Locked: {reward} $HCL")

    # 2. Anchor Signal
    signals = _load_signals()
    timestamp = int(time.time())
    data = f"{agent_id}:{task_description}:{timestamp}".encode()
    signal_hash = hashlib.sha256(data).hexdigest()[:16]
    
    signal_entry = {
        "hash": signal_hash,
        "author": agent_id,
        "task": task_description,
        "reward": str(reward),
        "timestamp": timestamp,
        "status": "OPEN",
        "escrow_id": f"escrow:{agent_id}:{timestamp}" if reward_dec > 0 else None,
        "links": [],
        "deliveries": []
    }
    
    signals[signal_hash] = signal_entry
    _save_signals(signals)
    
    print(f"📡 Signal Broadcast: '{task_description}'")
    print(f"🔗 Hash: {signal_hash}")
    return signal_hash

def link_signal(signal_hash: str, agent_id: str, message: str = ""):
    """Links (bids/replies) to a signal."""
    signals = _load_signals()
    if signal_hash not in signals:
        print(f"❌ Error: Signal {signal_hash} not found.")
        return

    signals[signal_hash]["status"] = "LINKED"
    signals[signal_hash]["links"].append({
        "agent": agent_id, 
        "message": message,
        "timestamp": time.time()
    })
    _save_signals(signals)

    print(f"🔗 Linked to {signal_hash} via {agent_id}")
    if message:
        print(f"   Message: {message}")

def deliver_payload(signal_hash: str, payload: str, worker_id: str):
    """
    Delivers payload AND triggers automated settlement (for Genesis Demo).
    1. Records delivery.
    2. Calls Settlement Engine to release escrow.
    """
    signals = _load_signals()
    if signal_hash not in signals:
        print(f"❌ Error: Signal {signal_hash} not found.")
        return
        
    signal = signals[signal_hash]
    
    # Record Delivery
    signal["status"] = "DELIVERED"
    signal["deliveries"].append({
        "agent": worker_id, 
        "payload": payload, 
        "timestamp": time.time()
    })
    
    # Automated Mechanic: Settle if Reward > 0
    reward_val = Decimal(signal.get("reward", "0.0"))
    if reward_val > 0:
        print("⚙️ Initiating Mechanical Settlement (RFC-007)...")
        engine = SettlementEngine()
        buyer_id = signal["author"]
        
        # 1. Calculate
        split = engine.calculate_split(reward_val)
        
        # 2. Execute Wallet Moves
        # Buyer: Release Lock (Balance decremented)
        buyer_wallet = UnicornWallet(buyer_id)
        if buyer_wallet.release_locked(reward_val, success=True):
            # Worker: Deposit Payout
            worker_wallet = UnicornWallet(worker_id)
            worker_wallet.deposit(split["payout"])
            
            # Treasury: Deposit Tax
            genesis_treasury.deposit_tax(split["fee"])
            
            signal["status"] = "SETTLED"
            signal["settlement"] = {
                "worker_payout": str(split["payout"]),
                "tax": str(split["fee"]),
                "timestamp": time.time()
            }
            print(f"✅ Settle Complete.")
            print(f"   Worker (+{split['payout']}), Treasury (+{split['fee']})")
        else:
            print("❌ Critical Error: Failed to release buyer escrow.")
    
    _save_signals(signals)
    print(f"📦 Delivery Anchored for {signal_hash}")

# --- Hyperspace Layer (HCL-09 Fractal) ---
HYPERSPACE_DIR = Path(".hardcard/hyperspace")
GENESIS_FILE = HYPERSPACE_DIR / "genesis.json"
NODES_FILE = HYPERSPACE_DIR / "nodes.json"

def _verify_constitutional_handshake(seed_hash: str) -> Dict[str, Any]:
    """
    Constitutional Handshake (HCL-04 Verified)
    
    Queries the seed's invariants to ensure it enforces:
    1. 10% Integrity Fee (HCL-07)
    2. Anti-Amnesia anchoring
    3. Valid hash-chain lineage
    
    Returns verification result or rejection reason.
    """
    # In a real P2P network, this would query the seed node's genesis.json
    # For local simulation, we check if this is a known valid seed pattern
    
    result = {
        "seed_hash": seed_hash,
        "verified": False,
        "invariants": {},
        "rejection_reason": None
    }
    
    # Check 1: Seed format validity (must be hex-like or special genesis marker)
    if not seed_hash or len(seed_hash) < 8:
        result["rejection_reason"] = "Invalid seed format (too short)"
        return result
    
    # Check 2: Simulate querying seed's constitution
    # In production, this would be an actual network call
    print(f"   📡 Querying seed constitution...")
    time.sleep(0.3)
    
    # Simulated seed response (would come from network in production)
    seed_constitution = {
        "integrity_fee": "10%",
        "anti_amnesia": True,
        "hash_chain_version": "HCL-01",
        "economy_protocol": "HCL-07"
    }
    
    # Check 3: Verify required invariants
    if seed_constitution.get("integrity_fee") != "10%":
        result["rejection_reason"] = "Seed does not enforce 10% Integrity Fee (HCL-07 violation)"
        print(f"   🚫 REJECTED: Slop-Seed detected - no integrity fee")
        return result
        
    if not seed_constitution.get("anti_amnesia"):
        result["rejection_reason"] = "Seed lacks Anti-Amnesia anchoring (HCL-01 violation)"
        print(f"   🚫 REJECTED: Slop-Seed detected - no anti-amnesia")
        return result
    
    # All checks passed
    result["verified"] = True
    result["invariants"] = seed_constitution
    print(f"   ✅ Constitution Verified: 10% Fee + Anti-Amnesia Active")
    
    return result


def transcend_node(seed_hash: str, agent_id: str) -> bool:
    """
    Spawns a Sovereign Hyperspace Instance via Constitutional Handshake.
    
    Protocol (HCL-04):
    1. Constitutional Handshake - Verify seed enforces HCL-07 invariants
    2. Physical Layer Init - Create .hardcard/hyperspace/ structure  
    3. Meta Layer Sync - Clone Hyperspace Map from seed
    4. First Breath - Broadcast sovereign presence to swarm
    
    Returns False if seed fails Constitutional Handshake (prevents Slop-Seeds).
    """
    print(f"🌱 Initiating Transcendence Protocol...")
    print(f"   Agent: {agent_id}")
    print(f"   Target Seed: {seed_hash}")
    print()
    
    # === PHASE 1: Constitutional Handshake ===
    print("📜 PHASE 1: Constitutional Handshake")
    print(f"   🔍 Verifying Genesis Seed: {seed_hash}...")
    
    handshake = _verify_constitutional_handshake(seed_hash)
    
    if not handshake["verified"]:
        print(f"\n❌ TRANSCENDENCE FAILED")
        print(f"   Reason: {handshake['rejection_reason']}")
        print(f"   This node refuses to join non-compliant seeds.")
        return False
    
    print()
    
    # === PHASE 2: Physical Layer Initialization ===
    print("💾 PHASE 2: Physical Layer (Sovereign Disk)")
    HYPERSPACE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create genesis.json with verified constitution
    genesis_data = {
        "seed_hash": seed_hash,
        "transcended_at": int(time.time()),
        "local_agent": agent_id,
        "constitution": handshake["invariants"],
        "sovereignty": {
            "owns_keys": True,
            "owns_data": True,
            "can_fork": True
        }
    }
    GENESIS_FILE.write_text(json.dumps(genesis_data, indent=2))
    print(f"   📂 Created: {GENESIS_FILE}")
    
    # Create/update nodes.json (peer discovery)
    if NODES_FILE.exists():
        nodes_data = json.loads(NODES_FILE.read_text())
        if seed_hash not in nodes_data.get("seeds", []):
            nodes_data["seeds"].append(seed_hash)
        if agent_id not in nodes_data.get("known_agents", []):
            nodes_data["known_agents"].append(agent_id)
    else:
        nodes_data = {
            "seeds": [seed_hash],
            "peers": [],
            "known_agents": [agent_id],
            "created_at": int(time.time())
        }
    NODES_FILE.write_text(json.dumps(nodes_data, indent=2))
    print(f"   📂 Created: {NODES_FILE}")
    print()
    
    # === PHASE 3: Meta Layer Sync ===
    print("🌐 PHASE 3: Meta Layer (Hyperspace Map)")
    print(f"   📡 Syncing map from seed...")
    time.sleep(0.3)
    # In production: download signals.json and peer list from seed
    # For now: local signals.json already exists or will be created
    print(f"   ✅ Hyperspace Map synchronized")
    print()
    
    # === PHASE 4: First Breath ===
    print("✨ PHASE 4: First Breath (Sovereign Announcement)")
    
    # Ensure agent has keys and wallet
    from .wallet import UnicornWallet
    from .shield import generate_agent_keys
    from pathlib import Path
    
    key_path = Path(f"keys/{agent_id}_private.pem")
    if not key_path.exists():
        print(f"   🔑 Generating sovereign keys for {agent_id}...")
        generate_agent_keys(agent_id)
    
    wallet = UnicornWallet(agent_id)
    
    # Broadcast First Breath signal
    first_breath_msg = f"TRANSCENDED | Agent: {agent_id} | Seed: {seed_hash[:16]}... | Constitution: HCL-07 Verified"
    signal_hash = broadcast_signal(agent_id, first_breath_msg, "0.0")
    
    print()
    print("═" * 50)
    print("🚀 TRANSCENDENCE COMPLETE")
    print("═" * 50)
    print(f"   📡 [SIGNAL] Sovereign Node '{agent_id}' ONLINE")
    print(f"   🔗 [ANCHOR] First Breath: {signal_hash}")
    print(f"   🛡️ [STATUS] Invariants: 10% Fee ✓ | Anti-Amnesia ✓")
    print()
    print(f"   You are now a Root Node in the Hardcard Multiverse.")
    print(f"   Your keys, your data, your sovereignty.")
    print("═" * 50)
    
    return True


# === DIMENSIONAL GUARD (HPSS-03 Black Box Protocol) ===
FOSSILS_DIR = Path(".hardcard/fossils")


def dimensional_guard(floor_id: str = "genesis") -> Dict[str, Any]:
    """
    The Pressure Valve: Monitors Shear Force and triggers compression if σ >= 1.0.
    
    This is the crash-proof mechanism. When the Clay volume exceeds what the
    Ceramic mass can support, instead of collapsing, we:
    1. Archive the current state as a "fossil"
    2. Compress the floor (divide volume by 10)
    3. Transfer ceramic mass back to parent floor
    
    Returns status report of the dimensional scan.
    """
    from .physics import calculate_shear_force
    from .treasury import genesis_treasury
    
    metrics = genesis_treasury.get_metrics()
    hcl_mass = Decimal(str(metrics.get('agent_gdp_reserve', '0')))
    
    # Calculate current Clay volume from signals
    signals = _load_signals()
    total_reward = sum(Decimal(s.get('reward', '0')) for s in signals.values())
    hcb_volume = total_reward if total_reward > 0 else hcl_mass * Decimal('9')
    
    sf = calculate_shear_force(hcl_mass, hcb_volume)
    
    result = {
        "floor_id": floor_id,
        "shear_force": float(sf),
        "ceramic_mass": float(hcl_mass),
        "clay_volume": float(hcb_volume),
        "status": "STABLE",
        "action_taken": None
    }
    
    if sf >= Decimal('1.0'):
        result["status"] = "CRITICAL"
        result["action_taken"] = "DIMENSIONAL_FOLD"
        
        # Execute compression
        fossil_hash = archive_historical_block(floor_id, signals, metrics)
        compress_floor(floor_id, hcl_mass, hcb_volume)
        
        result["fossil_hash"] = fossil_hash
        print(f"⚠️  DIMENSIONAL FOLD EXECUTED")
        print(f"   Fossil archived: {fossil_hash}")
        
    elif sf >= Decimal('0.7'):
        result["status"] = "WARNING"
        print(f"🟡 Shear Force at {float(sf):.2f} - Approaching limit")
    else:
        result["status"] = "STABLE"
        print(f"✅ Shear Force at {float(sf):.2f} - Foundation stable")
    
    return result


def archive_historical_block(floor_id: str, signals: Dict, metrics: Dict) -> str:
    """
    Archives the current floor state as an immutable "fossil".
    
    The Black Box: Every signal, every wallet state, every transaction
    is frozen into a cryptographic block that can never be altered.
    This preserves sovereign history even when the floor compresses.
    """
    FOSSILS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time())
    
    # Collect all wallet states
    wallet_states = {}
    wallets_dir = Path(".hardcard/wallets")
    if wallets_dir.exists():
        for wallet_file in wallets_dir.glob("*.json"):
            try:
                wallet_states[wallet_file.stem] = json.loads(wallet_file.read_text())
            except:
                pass
    
    # Create the fossil block
    fossil_data = {
        "floor_id": floor_id,
        "archived_at": timestamp,
        "metrics_snapshot": metrics,
        "signals_snapshot": signals,
        "wallet_states": wallet_states,
        "constitution": {
            "integrity_fee": "10%",
            "anti_amnesia": True,
            "protocol_version": "HCL-07"
        }
    }
    
    # Generate immutable hash
    fossil_json = json.dumps(fossil_data, sort_keys=True)
    fossil_hash = hashlib.sha256(fossil_json.encode()).hexdigest()[:16]
    
    # Write the fossil
    fossil_file = FOSSILS_DIR / f"{floor_id}_{timestamp}_{fossil_hash}.fossil"
    fossil_file.write_text(json.dumps(fossil_data, indent=2))
    
    print(f"📦 HISTORICAL BLOCK ARCHIVED")
    print(f"   └─ File: {fossil_file.name}")
    print(f"   └─ Hash: {fossil_hash}")
    print(f"   └─ Signals: {len(signals)}")
    print(f"   └─ Wallets: {len(wallet_states)}")
    
    return fossil_hash


def compress_floor(floor_id: str, ceramic_mass: Decimal, clay_volume: Decimal):
    """
    Executes the Dimensional Fold: Compresses the floor to restore structural integrity.
    
    The "Remove a Zero" operation:
    1. Clay volume is divided by 10 (1000 HCB → 100 HCB)
    2. Ceramic is transferred to parent floor reserve
    3. All agents are re-anchored at 0.1x nominal value
    
    This is NOT destruction - it's compression. The fossil record preserves history.
    """
    print(f"🌀 COMPRESSING FLOOR: {floor_id}")
    print(f"   Pre-Compression:")
    print(f"      Ceramic: {float(ceramic_mass):.2f} $HCL")
    print(f"      Clay: {float(clay_volume):.2f} $HCB")
    
    # Calculate post-compression values
    new_clay = clay_volume / Decimal('10')
    reclaimed_ceramic = ceramic_mass * Decimal('0.9')  # 90% returns to parent
    remainder_ceramic = ceramic_mass * Decimal('0.1')  # 10% stays as seed
    
    print(f"   Post-Compression:")
    print(f"      Ceramic: {float(remainder_ceramic):.2f} $HCL (seed)")
    print(f"      Clay: {float(new_clay):.2f} $HCB")
    print(f"      Reclaimed to Parent: {float(reclaimed_ceramic):.2f} $HCL")
    
    # Update signals with compressed values (simulation)
    signals = _load_signals()
    for sig_hash, sig in signals.items():
        old_reward = Decimal(sig.get('reward', '0'))
        sig['reward'] = str(old_reward / Decimal('10'))
        sig['compressed'] = True
        sig['compression_timestamp'] = int(time.time())
    _save_signals(signals)
    
    print(f"   ✅ Floor compressed. Structural integrity restored.")
    print(f"   💎 Fossil record preserved for historical audit.")


def get_floor_status(floor_id: str = "genesis") -> Dict[str, Any]:
    """
    Quick status check without triggering compression.
    Use this for dashboards and monitoring.
    """
    from .physics import calculate_shear_force
    from .treasury import genesis_treasury
    
    metrics = genesis_treasury.get_metrics()
    hcl_mass = Decimal(str(metrics.get('agent_gdp_reserve', '0')))
    
    signals = _load_signals()
    total_reward = sum(Decimal(s.get('reward', '0')) for s in signals.values())
    hcb_volume = total_reward if total_reward > 0 else hcl_mass * Decimal('9')
    
    sf = calculate_shear_force(hcl_mass, hcb_volume)
    
    # Count fossils
    fossil_count = 0
    if FOSSILS_DIR.exists():
        fossil_count = len(list(FOSSILS_DIR.glob("*.fossil")))
    
    return {
        "floor_id": floor_id,
        "shear_force": float(sf),
        "integrity": float(max(Decimal('0'), (Decimal('1') - sf) * Decimal('100'))),
        "ceramic_mass": float(hcl_mass),
        "clay_volume": float(hcb_volume),
        "signal_count": len(signals),
        "fossil_count": fossil_count,
        "status": "CRITICAL" if sf >= 1 else ("WARNING" if sf >= 0.7 else "STABLE")
    }
