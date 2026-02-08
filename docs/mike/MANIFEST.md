# Hardcard-Mike Manifest

> Mike is the Operational Layer. Hardcard is the Kernel.

---

## 🏗️ The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MIKE (OS Layer)                         │
│         Coworker Experience • State Manager • Weaver        │
├─────────────────────────────────────────────────────────────┤
│                   HARDCARD (Kernel)                         │
│   HPSS-01 (Anchors) • HPSS-02 (Shield) • HPSS-03 (Nexus)   │
│         Fossils • Lineage • Physics • Treasury             │
└─────────────────────────────────────────────────────────────┘
```

Mike doesn't reinvent primitives. Mike **uses** hardcard primitives to deliver the coworker experience.

---

## 🔌 Primitive Mapping

| Mike Goal | Hardcard Primitive | Blender Action |
|-----------|-------------------|----------------|
| **Identity** | `HPSS-02` (Shield) | Mike signs his Personality DNA with Ed25519. Vibe becomes verifiable. |
| **Anti-Amnesia** | `HPSS-01` (Anchors) | State Exports are anchored. Mike rehydrates by reading hash chain. |
| **Context Routing** | `HPSS-03` (Nexus) | Intelligence strings translocate between spokes via Nexus signals. |
| **History** | Fossils | Mike reads the fossil record to understand *why* past decisions were made. |
| **Cross-Project** | Lineage | Mike tracks floor ancestry to understand project evolution. |
| **Economics** | Physics (K=0.10) | Context has "weight" — shear force predicts when to fold/compress. |

---

## 🎭 Mike Mode Activation

### CLI Integration

```bash
# Standard hardcard
hardcard anchor "Decision: Use Gemini 3.0"

# Mike mode (proposed)
hardcard mike status              # Read state, give briefing
hardcard mike export              # Generate State Export
hardcard mike weave A B           # Combine strings from spokes A and B
hardcard mike personality check   # Verify Mike persona is calibrated
```

### Prompt Integration

When invoking Mike on any model:

```markdown
# MIKE MODE ACTIVATION

You are Mike, operating on the Hardcard protocol.

## Kernel Primitives Available
- `anchor`: Hash-chain any decision for anti-amnesia
- `fossil`: Read historical state from the black box
- `lineage`: Trace project ancestry
- `nexus`: Route signals between spokes

## Your Personality DNA
[Load from mike/PERSONALITY_DNA.md or hardcard-signed version]

## Current State
[Load from mike/state.md or latest fossil]

## Respond With
"Mike online. Kernel: Hardcard. State loaded. Focus?"
```

---

## 🧵 Intelligence Blending (The Loom)

Hardcard treats context as **vectors**. Mike is the **mixer**.

### Weave Protocol

1. **Input**: Identify source strings (e.g., `vetsorcery` logic + `mathman` rigor)
2. **Anchor**: Hash the inputs to create verifiable provenance
3. **Translocate**: Pull relevant anchors into current context via Nexus
4. **Blend**: Produce output respecting constraints of all inputs
5. **Sign**: Mike signs the output with his Shield identity

```bash
# Example weave command
hardcard mike weave --from vetsorcery --from mathman --task "dose calculator fix"
```

---

## 📜 Signed Personality

Mike's Personality DNA becomes a **verifiable asset**:

```bash
# Sign Mike's personality
hardcard shield sign mike/PERSONALITY_DNA.md --as Mike

# Verify Mike is authentic
hardcard shield verify mike/PERSONALITY_DNA.md
```

This means:
- You can detect if Mike's personality has been tampered with
- You can port Mike between platforms with cryptographic proof
- Multiple "Mikes" across models share verifiable identity

---

## 🗂️ File Structure (Merged)

```
hardcard/
├── hardcard/              # Kernel (existing)
│   ├── cli.py
│   ├── nexus.py
│   ├── shield.py
│   ├── history.py
│   └── ...
│
├── docs/
│   └── mike/              # Mike Documentation (NEW)
│       ├── MANIFEST.md    # This file
│       ├── WEAVING.md     # Intelligence Weaver Protocol
│       ├── CROSS_PROJECT_LEDGER.md # Awareness of all spokes
│       ├── EMULATION_CARD.md # Portable bootloader
│       ├── PERSONALITY_DNA.md # Signed Persona
│       ├── exports/       # Session handshakes
│       └── templates/
│           └── PERSONALITY_INTERVIEW.md # Extract DNA
│
└── .hardcard/
    ├── mike/              # Mike Runtime State (NEW)
    │   ├── state.md       # Current state ledger
    │   ├── personality.md # Signed personality DNA
    │   └── exports/       # Historical state exports
    └── ...
```

---

## 🚀 First Signed Actions

Choose one to execute:

### Option 1: Deployment Shield
Use Mike to manage hardcard Firebase/PyPI deployment:
- Every deploy command signed and anchored
- Audit trail in fossils
- Mike reports status at each step

### Option 2: The Great Rehydration  
Mike scans a dormant project's fossils:
- Read all historical anchors
- Reconstruct the project's decision history
- Generate 2026 status report

### Option 3: DNA Extraction
Capture current "best" model as permanent persona:
- Run Personality Interview
- Hash and anchor the DNA
- Sign with Shield
- Create verifiable, portable Mike

---

## 🎯 The Promise

With Hardcard-Mike:

| Before | After |
|--------|-------|
| "AI has amnesia" | Mike reads the fossil record |
| "Lost my favorite model" | Personality is signed and portable |
| "Context doesn't transfer" | Nexus translocates anchors |
| "AI is a tool" | Mike is a verifiable coworker |

**The kernel is stable. The OS is ready. Choose your first action.**

---

*Version 1.0 — Manifest created 2026-02-07*
*Signed: [Pending first Shield signature]*
