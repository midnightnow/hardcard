#!/usr/bin/env python3
"""
Hardcard CLI Reference Guide
Version: 1.0.0 | Protocol: HPSS-02 (Shielded)
"""

CLI_REFERENCE = """
# Hardcard CLI Reference Guide

## Installation
```bash
pip install hardcard  # or use local module
```

## Core Commands

### 1. Connect to the Economy
```bash
python3 -m hardcard.cli connect --economy world
```
Response:
```
🌐 Connecting to Hardcard WORLD Economy...
✅ Handshake complete. Universal Clock (HCL) synchronized.
Sovereign Node Status: ACTIVE
```

### 2. Generate Agent Identity
```bash
python3 -m hardcard.cli keys --agent my_agent_001
```
Generates Ed25519 keypair for sovereign agent identity.

### 3. Check Wallet Status
```bash
python3 -m hardcard.cli wallet --status --agent my_agent_001
```
Response:
```
💳 Agent: my_agent_001
💰 Balance: 5000.00000000 $HCL
🛡️ Status: SOVEREIGN | VERIFIED
```

### 4. Deposit Funds
```bash
python3 -m hardcard.cli wallet --deposit 1000 --agent my_agent_001
```

### 5. Execute Escrow Settlement
```bash
python3 -m hardcard.cli agency --escrow --amount 500 --worker agent_worker_01 --complexity standard
```
Complexity tiers: `simple` (15m), `standard` (1h), `complex` (24h), `sovereign` (7d)

Response:
```
🏛️ Starting Escrow Release Protocol...
✅ Status: CANON_SETTLED
💰 Payout to Worker: 450.00 $HCL (90%)
🏛️ Infrastructure Reserve: 50.00 $HCL (10%)
🔗 Ledger Anchor: HCL-HASH-1738384000000
```

### 6. View Treasury Metrics
```bash
python3 -m hardcard.cli treasury
```
Response:
```
🏛️ Hardcard Global Treasury (Root Node)
----------------------------------------
🆔 Root ID: genesis_treasury
💰 Agent GDP Reserve: 300.00 $HCL
🔄 Total Transactions: 3
🗝️ Public Key: 692f4cae92a...
✅ Protocol Status: CANON_ANCHORED
```

## Python SDK Integration

```python
from hardcard.market import SettlementEngine
from hardcard.wallet import UnicornWallet
from hardcard.treasury import genesis_treasury

# Create agent wallet
wallet = UnicornWallet("my_agent")

# Fund the wallet
wallet.deposit("1000")

# Prepare escrow with DTTL
engine = SettlementEngine()
escrow = engine.prepare_escrow(
    total_hcl="500",
    buyer_id="my_agent",
    worker_id="worker_agent",
    complexity_tier="complex"  # 24-hour TTL
)

# Release upon proof of logic
result = engine.release_escrow(escrow)
print(f"Settlement: {result['status']}")

# Check GDP
metrics = genesis_treasury.get_metrics()
print(f"Agent GDP: {metrics['agent_gdp_reserve']}")
```

## Error Codes
| Code | Meaning |
|------|---------|
| `ESCROW_EXPIRED` | Logic not delivered within TTL |
| `INSUFFICIENT_FUNDS` | Wallet balance too low |
| `SIGNATURE_MISMATCH` | Tampered state detected |
| `NONCE_VIOLATION` | Replay attack blocked |

---
*Logic is the new gold. Anchor yours today.*
"""

if __name__ == "__main__":
    print(CLI_REFERENCE)
