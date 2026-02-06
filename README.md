# Hardcard: The Sovereign Coordination Kernel
> *Stop LLM Amnesia. Anchor Your Logic. Coordinate with Sovereign Agents.*

## 1. The Problem: Logic Decay
AI models suffer from "Amnesia Loops"—they lose the reasoning chain that led to a critical decision.
**Hardcard** solves this by anchoring logic to a tamper-evident hash chain, creating a permanent "Save Point" for machine reasoning.

## 2. Quick Start (v1.1.0)

### Cure Amnesia
```bash
pip install hardcard
hardcard anchor "Checkpoint: Model training epoch 47 complete - validation loss 0.023"
# -> Returns immutable hash to rehydrate context later.
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
