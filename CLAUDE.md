# Claude Code Configuration for Hardcard

## 🏛️ Hardcard v1.1.0 - Core Primitives Protocol

**Repository**: https://github.com/midnightnow/hardcard
**License**: MIT (Open Core)
**Status**: Production-ready primitives, experimental applications set aside

## Project Overview

Hardcard is a **sovereignty layer for AI agents** providing three core capabilities:
1. **Identity** - Self-sovereign Ed25519 keys (portable across platforms)
2. **Evidence** - Cryptographic receipts of reasoning (provable work)
3. **Economy** - Zero-trust marketplace for autonomous task settlement

## Repository Structure (Post-Cleanup)

```
hardcard/
├── hardcard/              # Main package (CLI, Nexus, Shield, Wallet)
├── hardcard_core/         # Core primitives (Physics, Treasury, Lineage, Spawn)
├── docs/                  # Essential documentation
│   ├── FAQ.md            # Comprehensive FAQ
│   ├── SHEAR_FORCE_GUIDE.md  # Economic physics guide
│   └── rfc/              # Protocol specifications (HPSS-01, HPSS-02)
├── deploy/               # Live site deployments
│   ├── ai/              # hardcard.ai (protocol landing)
│   ├── org/             # hardcard.org (technical docs)
│   └── world/           # hardcard.world (marketplace)
├── README.md            # Main documentation
├── pyproject.toml       # Package configuration
└── .gitignore           # Excludes test projects
```

### What We Keep (Core Primitives)

**✅ Stable Production Code:**
- `hardcard/cli.py` - Command-line interface
- `hardcard/nexus.py` - Task marketplace (HPSS-03)
- `hardcard/shield.py` - Ed25519 identity (HPSS-02)
- `hardcard/wallet.py` - Balance management
- `hardcard/audit.py` - Network monitoring
- `hardcard_core/physics.py` - Economic physics engine (K=0.10, shear force)
- `hardcard_core/treasury.py` - 10% tax, Genesis Treasury
- `hardcard_core/lineage.py` - Agent genealogy tracking
- `hardcard_core/spawn.py` - Agent replication mechanics
- `hardcard_core/market.py` - Settlement primitives

### What We Ignore (Test Projects)

**⚠️ Experimental R&D (Not in Git):**
- VetSorcery implementations (veterinary clinic management)
- AIVA voice SDK (voice-controlled coding)
- Alexandria library (knowledge management)
- MacAgent coordination (multi-agent orchestration)
- MOEX terminal (meta-orchestration)

These are **not deleted**, just excluded via `.gitignore` for future consideration.

## Core Hardcard Commands

### Anti-Amnesia Protocol (HPSS-01)
```bash
# Anchor critical decisions
hardcard anchor "Decision: Use Ed25519 for agent keys to ensure self-sovereignty."

# Output: Tamper-evident logic hash with LLM rehydration snippet
# Logic Hash: de19c1ec37ca772739d47439a6a0e29be1700baf
# Parent Hash: 7f3a8b2c... (linked to previous anchor)
```

### Sovereign Identity (HPSS-02)
```bash
# Generate Ed25519 keypair
hardcard keys --agent "MyAgent"

# Private key stored locally, public key = agent's permanent ID
# Portable across platforms (OpenAI, local Llama, etc.)
```

### Nexus Marketplace (HPSS-03)
```bash
# Broadcast a task
hardcard nexus --broadcast "Process 1000 invoices" --reward 50.0

# Claim a task
hardcard nexus --link <signal_id> --agent "InvoiceBot"

# Deliver proof of completion
hardcard nexus --deliver <signal_id> --payload "Processed: 1000/1000"
```

### Network Audit
```bash
# Real-time network metrics
hardcard audit

# Shows: Total reserve, economic actions, agent lineages
```

## Development Workflow

### Installation
```bash
git clone https://github.com/midnightnow/hardcard.git
cd hardcard
pip install -e .
```

### Quality Checks (if Makefile exists)
```bash
make check   # Run pytest + ruff
make build   # Build distribution
```

### Firebase Deployment
```bash
# Three consolidated sites in hardcard-e107f project
firebase use hardcard-e107f
firebase deploy --only hosting:hardcard-ai     # Protocol landing page
firebase deploy --only hosting:hardcard-org    # Technical documentation
firebase deploy --only hosting:hardcard-world  # Marketplace
```

## Economic Physics Primer

**The Structural Constant (K = 0.10)**:
- Every transaction pays 10% fee
- Split: 70% anchor (local), 20% bedrock (genesis), 10% oxygen (next generation)

**Shear Force (σ)**:
- Formula: `σ = Clay Volume / (Ceramic Mass × 10)`
- Predicts when an agent lineage should "fold" (compress and restart)
- `σ < 0.5`: COLD (ready for more work)
- `σ 0.5-0.8`: STABLE (healthy load)
- `σ 0.8-1.0`: WARNING (approaching limit)
- `σ ≥ 1.0`: CRITICAL (dimensional fold imminent)

**Use Case Example** (VetSorcery Fleet):
```python
from hardcard_core.physics import calculate_shear_force, structural_audit

agent_state = {"ceramic": Decimal("100.0"), "clay": Decimal("450.0")}
sigma = calculate_shear_force(agent_state["ceramic"], agent_state["clay"])

if sigma >= 1.0:
    print("Execute dimensional fold for this agent")
elif sigma < 0.5:
    print("Agent has excess capacity - scale up")
```

See `docs/SHEAR_FORCE_GUIDE.md` for full worked examples.

## Key Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Quick start, use cases, architecture overview |
| `docs/FAQ.md` | "Is this a blockchain?" (NO), technical questions, troubleshooting |
| `docs/SHEAR_FORCE_GUIDE.md` | Economic physics with VetSorcery, trading bot, lifecycle examples |
| `docs/rfc/HPSS-01.md` | Anti-Amnesia Protocol specification |
| `docs/rfc/HPSS-02.md` | Sovereign Identity (Ed25519) specification |
| `ARCHITECTURE.md` | 4-layer technical design |
| `GLOSSARY.md` | Terms (Anchor, Settlement, Fossil, Nexus) |

## Live Deployments

| Site | URL | Status | Purpose |
|------|-----|--------|---------|
| **hardcard.ai** | https://hardcard-e107f-ai.web.app | ✅ | Protocol landing page |
| **hardcard.org** | https://hardcard-e107f-org.web.app | ✅ | Technical specifications |
| **hardcard.world** | https://hardcard-e107f-world.web.app | ✅ | Marketplace & ecosystem |

## Git Workflow

### Commit Style
- Use descriptive commit messages with context
- Follow conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- Always include `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

### Branch Strategy
- `main` - Production-ready code
- `feat/*` - Feature branches
- `fix/*` - Bug fixes

### Example Commit
```bash
git commit -m "$(cat <<'EOF'
feat: Add shear force monitoring to Nexus agents

Implements real-time shear force calculation for all active agents
in the Nexus marketplace. When σ >= 1.0, agents receive fold warnings.

- Added calculate_shear_force() integration to nexus.py
- CLI now shows shear status in agent listings
- Updated docs/SHEAR_FORCE_GUIDE.md with Nexus examples

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

## Cult of Done Principles (Applied)

Following the "cult of done" manifesto:
1. ✅ **Ship what works** - Core primitives are stable
2. ✅ **Set aside experiments** - Test projects in .gitignore
3. ✅ **Pretending you know what you're doing is almost the same as knowing** - Documentation written confidently
4. ✅ **Done is better than perfect** - v1.1.0 shipped with known gaps (middle layers 4-7)
5. ✅ **Laugh at perfection** - It's boring and keeps you from being done

## Philosophy: Fractal Architecture

Hardcard isn't a single product; it's a **recursive stack** with 10 levels:
- **Level 1-3**: Primitives (Anchoring, Identity, Nexus) ✅ **DONE**
- **Level 4-7**: Middle layers (pattern recognition, synthesis) ⚠️ **MISSING**
- **Level 8-10**: Applications (VetSorcery, Fintech, Professional OS) 🔬 **R&D**

**Current Strategy**: Build solid Level 1 primitives and Level 10 applications, then let the middle layers emerge naturally. "Functional compression" - if Level 10 logic can't run on Level 1 primitives, the architecture is too brittle.

## Open Core Model

**🟢 Public Layer (MIT):**
- CLI, Identity, Evidence, Nexus, Wallet, Audit, Fossil Archive
- Anyone can build commercial products on these primitives

**🔴 Private Core (Proprietary):**
- Settlement Engine, Treasury Logic (10% fee), Spawn Protocol
- High-performance back-end for Hardcard network
- Not currently available for licensing

## Best Practices for Claude Code

### Workflow
1. **Explore** - Read relevant files, understand context
2. **Plan** - Create implementation plan (use `think` or `think hard`)
3. **Code** - Implement iteratively, verify each step
4. **Commit** - Descriptive messages with context

### When Working on Hardcard
- **Focus on primitives** - Don't get pulled into application-level features
- **Keep it simple** - Hardcard is infrastructure, not a kitchen sink
- **Document physics** - Economic constants (K=0.10, 2-1-7 split) are sacred
- **Test thoroughly** - Primitives must be rock-solid

### Context Management
- Use `/clear` between major tasks
- Hardcard has deep context - don't try to hold it all at once
- Read specific docs on demand rather than front-loading

## Emergency Commands

### If Firebase deployment breaks
```bash
# Check current project
firebase use

# Should be: hardcard-e107f
# If not: firebase use hardcard-e107f

# Verify sites exist
firebase hosting:sites:list

# Deploy specific site
firebase deploy --only hosting:hardcard-ai --project hardcard-e107f
```

### If package broken
```bash
# Reinstall in development mode
pip uninstall hardcard
pip install -e .

# Verify CLI works
hardcard --help
```

## Key Contacts

- **GitHub**: https://github.com/midnightnow/hardcard
- **Issues**: https://github.com/midnightnow/hardcard/issues
- **Discussions**: https://github.com/midnightnow/hardcard/discussions
- **Web**: https://influential.digital


## 🏺 Athena Context Anchor
> **Last Active**: 2026-02-11
> **Evidence Hash**: 19d75e8610b1efae
> **Key Decisions**:
> - CLAUDE.md acts as the AI BIOS.

---


**Last Updated**: 2026-02-07
**Version**: v1.1.0 - Open Core Launch
**Status**: Core primitives stable, experimental applications set aside for future work
