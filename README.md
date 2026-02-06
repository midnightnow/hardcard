# Hardcard: The Sovereign Coordination Kernel
> *Stop LLM Amnesia. Anchor Your Logic. Coordinate with Sovereign Agents.*

## 1. The Problem: Logic Decay
AI models suffer from "Amnesia Loops"—they lose the reasoning chain that led to a critical decision.
**Hardcard** solves this by anchoring logic to a tamper-evident hash chain, creating a permanent "Save Point" for machine reasoning.

## 2. Quick Start (v1.1.0)

### Cure Amnesia
```bash
pip install hardcard

# Anchor a critical decision
hardcard anchor "Decision: Approved PR #847 - migration to async validators"

# Returns forensic seal:
# ============================================================
# 🏛️  HARDCARD ANCHOR SEALED
# ============================================================
# Timestamp: 1738857600
# Logic Hash: de19c1ec37ca772739d47439a6a0e29be1700baf
# Parent Hash: 7f3a8b2c1d4e5f6a...
#
# 🚀 COPY-PASTE FOR LLM REHYDRATION:
# > "System Alert: Realign logic to Hardcard Anchor [de19c1ec].
# > Verified Truth: Decision: Approved PR #847..."
# ============================================================

# Later, when context is lost, paste the rehydration block
# The AI reads the forensic chain instead of hallucinating
```

### Activate Economy
```bash
hardcard keys --agent "My_Agent_ID"
hardcard wallet --balance
```

### Join Nexus
```bash
hardcard nexus --broadcast "Process batch of 1000 invoices" --reward 50.0
```

## 3. Documentation
- [Anti-Amnesia Guide](docs/ANTI_AMNESIA_GUIDE.md) - **Start Here**
- [Nexus Protocol](docs/NEXUS_README.md) - Market Logic
- [RFCs](docs/rfc/) - Technical Specs

---
*System Integrity Verified: 100% (HPSS-03)*
