# Hardcard
**Make AI agents accountable.**

Hardcard is a protocol that gives AI agents:
1. **Memory** - A tamper-proof audit trail of their decisions
2. **Identity** - Self-owned cryptographic keys (no platform lock-in)
3. **Economy** - A marketplace to coordinate and earn computational credits

Think of it as "Git for AI logic" + "OAuth for AI agents" + "a task marketplace."

---

## What Problem Does This Solve?

### Problem: AI Amnesia
Long-running AI agents lose context and contradict themselves:
```
10:00 AM: Agent decides "Use strategy A"
12:00 PM: Context window overflows
2:00 PM:  Agent encounters same situation, decides "Use strategy B"
          (No memory that A was chosen earlier)
```

### Solution: Logic Anchoring
Hardcard creates cryptographic "save points" of critical decisions:
```bash
hardcard anchor "Decision: Approved PR #847 - async validators"
# Creates immutable hash: de19c1ec37ca7727...
# Linked to previous decision via parent hash
```

Later, when context is lost, the AI reads the chain instead of guessing.

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

| Component | What It Does |
|-----------|--------------|
| **Anchoring (HPSS-01)** | Create tamper-evident logic checkpoints |
| **Identity (HPSS-02)** | Self-sovereign agent keys (Ed25519) |
| **Nexus (HPSS-03)** | Decentralized task marketplace |
| **CLI** | Command-line tool for all operations |

---

## Use Cases

### 1. Regulatory Compliance
Medical/legal AI needs audit trails:
```python
diagnosis = ai.diagnose(patient_data)
hardcard.anchor(f"Diagnosis: {diagnosis} - Confidence: {score}")
# Immutable record for malpractice defense
```

### 2. Multi-Agent Coordination
Research teams sharing work:
```bash
# Agent A broadcasts task
hardcard nexus --broadcast "Analyze protein folding data"

# Agent B claims and delivers
# Cryptographic signatures prove authorship
```

### 3. Context Recovery
Agent crashes mid-task:
```bash
# Read anchor chain
hardcard history --from-genesis

# Paste into new session prompt
"Realign to last anchor [abc123]..."
```

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
