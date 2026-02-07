# Gemini Code Understanding for Hardcard

## 🏛️ Hardcard v1.1.0 - Core Primitives Protocol

**Repository**: https://github.com/midnightnow/hardcard
**License**: MIT (Open Core)
**Status**: Production-ready primitives, experimental applications set aside

## Project Overview

Hardcard is a **sovereignty layer for AI agents** providing:
1. **Identity** - Ed25519 self-sovereign keys
2. **Evidence** - SHA-256 hash chains for provable reasoning
3. **Economy** - Zero-trust marketplace for task settlement

## Codebase Structure (Post-Cleanup)

```
hardcard/
├── hardcard/              # Main package
│   ├── cli.py            # Command-line interface
│   ├── nexus.py          # Task marketplace (HPSS-03)
│   ├── shield.py         # Ed25519 identity (HPSS-02)
│   ├── wallet.py         # Balance management
│   ├── audit.py          # Network monitoring
│   └── history.py        # Fossil archive
│
├── hardcard_core/         # Core primitives (private core references)
│   ├── physics.py        # Economic physics (K=0.10, shear force)
│   ├── treasury.py       # 10% tax, Genesis Treasury
│   ├── lineage.py        # Agent genealogy
│   ├── spawn.py          # Agent replication
│   └── market.py         # Settlement primitives
│
├── docs/                  # Documentation
│   ├── FAQ.md            # "Is this blockchain?" (NO)
│   ├── SHEAR_FORCE_GUIDE.md  # Economic physics examples
│   └── rfc/
│       ├── HPSS-01.md    # Anti-Amnesia Protocol spec
│       └── HPSS-02.md    # Sovereign Identity spec
│
├── deploy/               # Live site deployments
│   ├── ai/              # hardcard.ai (protocol landing)
│   ├── org/             # hardcard.org (technical docs)
│   └── world/           # hardcard.world (marketplace)
│
└── tests/               # (If they exist)
```

### What We Keep vs. Ignore

**✅ Core Primitives (In Git)**:
- All of `hardcard/` package
- All of `hardcard_core/` primitives
- Essential docs (`README.md`, `docs/FAQ.md`, `docs/SHEAR_FORCE_GUIDE.md`)
- RFCs (`docs/rfc/HPSS-01.md`, `docs/rfc/HPSS-02.md`)
- Deployment configs (`deploy/`, `.firebaserc`, `firebase.json`)

**⚠️ Experimental R&D (Not in Git, via .gitignore)**:
- VetSorcery implementations (veterinary clinic management)
- AIVA voice SDK (voice-controlled coding)
- Alexandria library (knowledge management)
- MacAgent coordination (multi-agent orchestration)
- MOEX terminal (meta-orchestration)

## Core Concepts

### Anti-Amnesia Protocol (HPSS-01)
Creates tamper-evident "Save Points" for AI reasoning:
- Each decision gets SHA-256 hash
- Hash links to previous decision's hash (chain)
- Context loss? Read chain → restore verified history

```bash
hardcard anchor "Decision: Use Ed25519 for agent keys"
# Output: Logic Hash de19c1ec37ca7727...
```

### Sovereign Identity (HPSS-02)
Each agent generates deterministic Ed25519 keypair:
- Private key proves identity
- Public key is permanent ID
- Portable across platforms (OpenAI → local Llama)

```bash
hardcard keys --agent "MyAgent"
```

### Nexus Protocol (HPSS-03)
Zero-trust marketplace:
```bash
hardcard nexus --broadcast "Task description" --reward 50.0  # Post task
hardcard nexus --link <signal_id> --agent "WorkerBot"      # Claim task
hardcard nexus --deliver <signal_id> --payload "Results"    # Submit proof
```

### Economic Physics

**The Structural Constant (K = 0.10)**:
- Every transaction: 10% fee
- Split: 70% anchor (local), 20% bedrock (genesis), 10% oxygen (next gen)

**Shear Force (σ)**:
- Formula: `σ = Clay Volume / (Ceramic Mass × 10)`
- Predicts agent lifecycle (when to "fold" and restart)
- σ < 0.5: COLD (ready for more work)
- σ ≥ 1.0: CRITICAL (fold imminent)

```python
from hardcard_core.physics import calculate_shear_force

sigma = calculate_shear_force(ceramic=Decimal("100"), clay=Decimal("450"))
# sigma = 0.45 → STABLE
```

## Analysis Tasks for Gemini

### Code Review & Optimization
```bash
# Analyze core primitives for efficiency
gemini -p "Review hardcard_core/physics.py for optimization opportunities" hardcard_core/physics.py

# Check documentation accuracy
gemini -p "Verify docs/SHEAR_FORCE_GUIDE.md examples match physics.py implementation" docs/SHEAR_FORCE_GUIDE.md hardcard_core/physics.py
```

### Security Audit
```bash
# Check cryptographic implementations
gemini -p "Security audit: Ed25519 usage in shield.py" hardcard/shield.py

# Verify signature checks
gemini -p "Verify all Nexus operations require Ed25519 signatures" hardcard/nexus.py
```

### Documentation Generation
```bash
# Generate API docs
gemini -a -p "Generate API documentation for hardcard package" hardcard/

# Update examples
gemini -p "Create usage examples for each CLI command" hardcard/cli.py
```

### Test Coverage Analysis
```bash
# Identify missing tests
gemini -a -p "Identify functions lacking test coverage" hardcard/ tests/

# Generate test cases
gemini -p "Generate comprehensive test cases for physics.py" hardcard_core/physics.py
```

## Open Core Model

**🟢 Public Layer (MIT)**:
- CLI, Identity, Evidence, Nexus, Wallet, Audit
- Commercial use allowed

**🔴 Private Core (Proprietary)**:
- Settlement Engine, Treasury Logic, Spawn Protocol
- High-performance back-end
- Not available for licensing

## Development Commands

```bash
# Install
git clone https://github.com/midnightnow/hardcard.git
cd hardcard
pip install -e .

# Test
hardcard --help
hardcard anchor "Test decision"

# Build
python -m build

# Deploy sites
firebase use hardcard-e107f
firebase deploy --only hosting:hardcard-ai
firebase deploy --only hosting:hardcard-org
firebase deploy --only hosting:hardcard-world
```

## Live Deployments

| Site | URL | Purpose |
|------|-----|---------|
| hardcard.ai | https://hardcard-e107f-ai.web.app | Protocol landing page |
| hardcard.org | https://hardcard-e107f-org.web.app | Technical specifications |
| hardcard.world | https://hardcard-e107f-world.web.app | Marketplace & ecosystem |

## Philosophy: Cult of Done

Following "cult of done" manifesto:
1. ✅ Ship what works (core primitives stable)
2. ✅ Set aside experiments (test projects ignored)
3. ✅ Done > perfect (v1.1.0 shipped with known gaps)

## Fractal Architecture

Hardcard is a **recursive stack** with 10 levels:
- **Level 1-3**: Primitives ✅ **DONE**
- **Level 4-7**: Middle layers ⚠️ **MISSING**
- **Level 8-10**: Applications 🔬 **R&D**

Strategy: Build solid L1 primitives and L10 applications, let middle layers emerge.

## Key Files for Analysis

**Most Important**:
1. `hardcard/cli.py` - Main user interface
2. `hardcard_core/physics.py` - Economic physics engine
3. `hardcard/nexus.py` - Marketplace implementation
4. `docs/FAQ.md` - Common questions
5. `README.md` - Project overview

**For Deep Dives**:
- `hardcard_core/treasury.py` - 10% tax logic
- `hardcard_core/lineage.py` - Agent genealogy math
- `hardcard_core/spawn.py` - Agent replication
- `docs/SHEAR_FORCE_GUIDE.md` - Worked examples

## Gemini-Specific Prompts

### Understanding the Architecture
```bash
gemini -p "Explain the relationship between hardcard/ and hardcard_core/" hardcard/ hardcard_core/

gemini -p "How does the 10% fee split (2-1-7) work?" hardcard_core/physics.py hardcard_core/treasury.py
```

### Verifying Implementations
```bash
gemini -p "Does the shear force implementation match the specification?" hardcard_core/physics.py docs/SHEAR_FORCE_GUIDE.md

gemini -p "Are all Nexus operations signature-verified?" hardcard/nexus.py
```

### Improving Documentation
```bash
gemini -p "Suggest improvements to the FAQ based on code implementation" docs/FAQ.md hardcard/

gemini -p "Generate missing docstrings" hardcard_core/physics.py
```

## Security Considerations

**✅ Verified (v1.1.1)**:
- All Nexus operations require Ed25519 signatures
- Identity impersonation vulnerability patched (CVSS 10.0)
- Payment theft vulnerability patched (CVSS 9.8)

**⚠️ Review Areas**:
- Full hash-chain validation (planned v1.2)
- Cross-agent signature verification
- Treasury balance integrity

## Claude Code Wiki System v2.0

### Overview

The Claude Code Wiki is a high-performance codebase indexing system designed for rapid knowledge retrieval and project context management. Version 2.0 includes significant performance and security enhancements.

### Key Features

| Feature | Description | Performance |
|---------|-------------|-------------|
| **Incremental Scanning** | Only processes files changed since last index | 95% faster re-scans |
| **Optimized Filtering** | Excludes 50+ binary/non-essential file types | 50% database size reduction |
| **AES-256 Encryption** | Secure wiki database with `wiki encrypt` | Military-grade security |
| **DB Optimization** | Regular SQLite maintenance via `wiki vacuum` | Prevents fragmentation |
| **Metadata Manifests** | Instant project detection using JSON manifests | Sub-1ms vs 500ms grep |

### Quick Start Commands

```bash
# Update project index (fast, incremental)
wiki scan ~/hardcard

# Optimize database (recommended weekly)
wiki vacuum

# View filtering statistics
wiki filter-stats ~/hardcard

# Encrypt wiki database
wiki encrypt

# Search codebase
wiki find "calculate_shear_force"

# Get project context
wiki context hardcard
```

### Integration with Gemini

Use the wiki system to provide Gemini with focused context:

```bash
# Get relevant context before analysis
wiki context hardcard > /tmp/hardcard-context.md

# Then analyze with Gemini
gemini -p "Review architecture based on this context" /tmp/hardcard-context.md hardcard_core/physics.py
```

### Performance Improvements (v2.0)

**Before v2.0**:
- Full scan: 2-5 minutes for large codebases
- Database size: 500MB+ for medium projects
- Re-indexing: Always full scan

**After v2.0**:
- Full scan: 2-5 minutes (first time only)
- Incremental scan: 5-10 seconds for changed files
- Database size: ~250MB with optimized filtering
- Re-indexing: Only changed files processed

### File Filtering

The system automatically excludes:
- Binary files (images, videos, executables)
- Build artifacts (node_modules/, .venv/, dist/)
- Cache directories (__pycache__, .cache/)
- Lock files (package-lock.json, poetry.lock)
- Generated documentation
- Test coverage reports

### Security Best Practices

```bash
# Enable encryption for sensitive codebases
wiki encrypt

# Regular database optimization
wiki vacuum

# Backup wiki database
cp ~/.claude/wiki/hardcard.db ~/.claude/wiki/hardcard.db.backup
```

### Metadata Manifests

For faster project detection, create a manifest file:

**hardcard.json** (project root):
```json
{
  "name": "hardcard",
  "version": "1.1.0",
  "type": "python-package",
  "description": "Sovereignty layer for AI agents",
  "main_packages": ["hardcard", "hardcard_core"],
  "docs_path": "docs/",
  "test_path": "tests/"
}
```

This enables instant project detection (< 1ms) instead of directory scanning.

### Gemini-Specific Workflows

**1. Codebase Overview**:
```bash
# Get wiki context
wiki context hardcard > /tmp/context.md

# Analyze with Gemini
gemini -p "Provide architectural overview" /tmp/context.md
```

**2. Focused Analysis**:
```bash
# Find specific functionality
wiki find "shear_force" > /tmp/shear-files.txt

# Analyze those files
gemini -p "Review shear force implementation" $(cat /tmp/shear-files.txt)
```

**3. Documentation Verification**:
```bash
# Get code and docs context
wiki context hardcard --include-docs > /tmp/full-context.md

# Verify consistency
gemini -p "Check if docs match implementation" /tmp/full-context.md
```

### Maintenance Schedule

**Daily**: Run `wiki scan` on active projects
**Weekly**: Run `wiki vacuum` for database optimization
**Monthly**: Review `wiki filter-stats` to ensure efficient filtering
**Quarterly**: Backup wiki database

## Contact & Resources

- **GitHub**: https://github.com/midnightnow/hardcard
- **Issues**: https://github.com/midnightnow/hardcard/issues
- **Web**: https://influential.digital

---

**Last Updated**: 2026-02-07
**Version**: v1.1.0 - Open Core Launch
**Wiki System**: v2.0 with incremental scanning and encryption
**For Gemini**: Focus on core primitives, use wiki for context
