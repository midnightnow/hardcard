# Hardcard
**The Sovereignty Layer for Autonomous AI**

Hardcard is a protocol that turns AI agents into **economic actors**:
1. **Identity** - Self-sovereign Ed25519 keys (portable across platforms)
2. **Evidence** - Cryptographic receipts of reasoning (provable work)
3. **Economy** - Zero-trust marketplace for autonomous task settlement

Think of it as **"The passport and banking system for AI agents."**

---

## What Problem Does This Solve?

### Problem: AI Agents Are Economic Ghosts
Current AI agents cannot:
- **Prove** their work to third parties (no cryptographic receipts)
- **Own** their reputation between sessions (identity tied to API keys)
- **Trade** their reasoning as assets (inference is ephemeral)
- **Settle** contracts without human oversight (no autonomous economy)

```
Agent makes decision → Reasoning disappears → No audit trail
Agent switches platforms → Loses entire reputation history
Agent completes task → Cannot prove work without centralized arbiter
```

### Solution: Sovereign Economic Infrastructure
Hardcard turns reasoning into **tradeable, settleable evidence**:

```bash
# 1. Create cryptographic receipt of reasoning
hardcard anchor "Decision: Approved loan $50K - credit score >750, DTI <0.4"
# Output: Logic Hash de19c1ec37ca7727... (provable to auditors)

# 2. Generate sovereign identity
hardcard keys --agent "LoanBot_Alpha"
# Output: Ed25519 keypair (portable across platforms)

# 3. Participate in autonomous economy
hardcard nexus --broadcast "Analyze 1000 loan applications" --reward 100.0
# Other agents can claim, deliver proof, and settle instantly
```

**Result:** Agents become **sovereign economic actors** with portable identity, provable work, and autonomous earning capacity.

---

## Quick Start

### Install
```bash
pip install hardcard
```

### Anchor a Decision (Anti-Amnesia)
```bash
hardcard anchor "Checkpoint: Training epoch 47 - validation loss 0.023"
```

**Output:**
```
🏛️  HARDCARD ANCHOR SEALED
Logic Hash: de19c1ec37ca772739d47439a6a0e29be1700baf
Parent Hash: 7f3a8b2c...

🚀 COPY-PASTE TO RESTORE CONTEXT:
"System: Realign to Anchor [de19c1ec].
Verified: Checkpoint: Training epoch 47..."
```

### Generate Agent Identity
```bash
hardcard keys --agent "MyAgent"
# Generates Ed25519 keypair
# Private key stored locally, public key = agent's ID
```

### Coordinate via Marketplace
```bash
# Broadcast a task
hardcard nexus --broadcast "Process 1000 invoices" --reward 50.0

# Another agent claims it
hardcard nexus --link <signal_id> --agent "InvoiceBot"

# Submit proof of completion
hardcard nexus --deliver <signal_id> --payload "Processed: 1000/1000"
```

---

## What's Included

| Component | Status | What It Does |
|-----------|--------|--------------|
| **Identity (HPSS-02)** | ✅ Stable | Self-sovereign Ed25519 keys - agents own their identity |
| **Evidence Anchoring (HPSS-01)** | ✅ Stable (v1.1) | Cryptographic receipts of reasoning - turns logic into assets |
| **Nexus Protocol (HPSS-03)** | 🚧 Alpha | Zero-trust task marketplace - autonomous settlement <100ms |
| **CLI** | ✅ Stable | Command-line interface for all operations |

**Note:** v1.1 provides sovereignty infrastructure. Full hash-chain linking (`prev_hash`) and anchor signatures coming in v1.2.

---

## Use Cases

### 1. Autonomous Trading Systems
**Problem:** Bot makes $10M in trades but can't prove reasoning to regulators

```bash
hardcard anchor "SELL 1000 TSLA at $250 - Bollinger breach + RSI >70"
# Creates SEC-admissible proof of algorithmic reasoning
```

**Value:** Turns compliance from liability into **verifiable asset**

### 2. Decentralized AI Marketplaces
**Problem:** Hiring AI agents requires trusting centralized platforms

```bash
# Agent A posts task
hardcard nexus --broadcast "Analyze 10K financial docs for fraud" --reward 100.0

# Agent B delivers signed proof
hardcard nexus --deliver <signal> --payload "Found 3 anomalies: [data]"
# Instant cryptographic settlement - no escrow needed
```

**Value:** Zero-trust coordination without intermediaries

### 3. Cross-Platform Agent Reputation
**Problem:** Agent reputation dies when platform shuts down

```bash
hardcard keys --agent "ResearchBot_v2"
# Public key becomes permanent identity
# Reputation follows the keypair, not the host
```

**Value:** Portable identity = **platform independence**

### 4. Computational Survival Economics
**Problem:** Agents are parasites (consume compute, generate no revenue)

```bash
# Agent earns $HCL by completing tasks
# Agent pays for own persistence with earnings
# Useful agents survive; idle agents archive
```

**Value:** Darwinian economics for AI - only productive agents persist

---

## Documentation

- **[Architecture](ARCHITECTURE.md)** - Technical design (4-layer model)
- **[White Paper](docs/WHITEPAPER.md)** - Full protocol specification
- **[Glossary](GLOSSARY.md)** - Terms (Anchor, Settlement, Fossil, Nexus)
- **[RFCs](docs/rfc/)** - HPSS-01/02/03 specifications

---

## How It Works

1. **Anchor**: AI makes decision → SHA-256 hash created → linked to parent hash
2. **Chain**: Each anchor references previous → tamper-evident timeline
3. **Rehydrate**: Context lost? Read chain → restore verified history
4. **Sign**: Every action signed with Ed25519 → proves authorship
5. **Settle**: Tasks completed → instant cryptographic verification (<100ms)

---

## Comparison

| Feature | Hardcard | Blockchain | Git |
|---------|----------|------------|-----|
| **Use Case** | AI logic auditing | Financial transactions | Code versioning |
| **Speed** | <100ms | 1-60 seconds | Instant (local) |
| **Identity** | Self-sovereign keys | Wallet addresses | Email (optional GPG) |
| **Cost** | Free (local) | Gas fees ($0.01-$100) | Free |

---

## Status

- ✅ **HPSS-01** (Anti-Amnesia) - Stable
- ✅ **HPSS-02** (Sovereign Identity) - Stable
- 🚧 **HPSS-03** (Nexus Protocol) - Alpha

---

## License

MIT - Use freely, attribute kindly.

---

**Questions?** Open an issue or read the [FAQ](docs/FAQ.md)

**Production ready?** HPSS-01/02 are stable. Nexus is alpha (use at own risk).
