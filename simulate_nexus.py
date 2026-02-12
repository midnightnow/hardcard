"""
simulate_nexus.py
Simulates a full Hardcard Nexus transaction lifecycle with HPSS-02 Identity check.

Roles:
1. "ClientAgent" (Broadcasts task)
2. "ExpertNode" (Links and Delivers work)

Flow:
1. Key Generation (Ed25519)
2. Broadcast Signal
3. Link (Bid)
4. Deliver (Signed Payload)
5. Settlement Verification
"""

import sys
import json
import time
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519

# Utility: Simulate CLI Key Gen
def generate_keys(agent_name):
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    pub_hex = pub.public_bytes_raw().hex()
    print(f"[{agent_name}] 🗝️  Keypair Generated. ID: {pub_hex[:8]}...")
    return priv, pub, pub_hex

# Utility: Sign Payload
def sign_payload(private_key, data):
    signature = private_key.sign(data.encode())
    return signature.hex()

def run_simulation():
    print("\n🚀 STARTING NEXUS SIMULATION (HPSS-02)\n" + "="*50)
    
    # 1. Identity Setup
    client_priv, client_pub, client_id = generate_keys("ClientAgent")
    worker_priv, worker_pub, worker_id = generate_keys("ExpertNode")
    
    # 2. Broadcast (Client)
    task_desc = "Optimize diagnosis chain for feline hyperthyroidism"
    reward = 50.0
    signal_hash = hashlib.sha256(f"{client_id}:{task_desc}:{time.time()}".encode()).hexdigest()
    
    print(f"\n📡 BROADCAST: {task_desc}")
    print(f"   Reward: {reward} $HCL")
    print(f"   Signal Hash: {signal_hash[:16]}...")
    
    # 3. Link (Worker)
    print(f"\n🔗 LINK: ExpertNode ({worker_id[:8]}) bidding on signal.")
    
    # 4. Deliver (Worker Signs Work)
    # The worker performs the task and signs the result
    work_result = "Diagnosis: T4 > 5.0 indicates hyperthyroidism. Confidence: 98%."
    signature = sign_payload(worker_priv, work_result)
    
    print(f"\n📦 DELIVER:")
    print(f"   Payload: \"{work_result}\"")
    print(f"   Signature: {signature[:16]}... (Ed25519)")
    
    # 5. Settlement Verification (The Architecture Check)
    print(f"\n⚖️  SETTLEMENT ENGINE VERIFICATION:")
    
    try:
        # Verify signature using worker's public key
        worker_pub.verify(bytes.fromhex(signature), work_result.encode())
        print("   ✅ Signature VALID. Identity confirmed.")
        
        # Calculate Splits
        fee = reward * 0.10
        payout = reward * 0.90
        print(f"   💰 Treasury Fee (10%): {fee} $HCL")
        print(f"   🦄 Worker Payout (90%): {payout} $HCL")
        print("\n✅ TRANSACTION SETTLED. COMMITTED TO FOSSIL.")
        
    except Exception as e:
        print(f"   ❌ VERIFICATION FAILED: {e}")

if __name__ == "__main__":
    try:
        run_simulation()
    except ImportError:
        print("Error: 'cryptography' library not found. Install with: pip install cryptography")
