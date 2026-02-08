# Cross-Project Ledger

> Mike's awareness of all Spokes in the Constellation

---

## Active Spokes

### vetsorcery 🏥
**Status**: Active development
**Last significant update**: 2026-02-07
**Current focus**: Frontend polishing, ValleyVet integration
**Key decisions**:
- AIVA voice integration planned
- PII scrubber verified
- Staging → Production path defined

**Open items:**
- [ ] UI mockups pending
- [ ] Final production certification

---

### hardcard 🛡️
**Status**: v1.1.0 shipped
**Last significant update**: 2026-02-07
**Current focus**: Public pillar preparation
**Key decisions**:
- Open Core model (MIT public, proprietary core)
- Anti-Amnesia Protocol (HPSS-01) specified
- Sovereign Identity (HPSS-02) implemented

**Open items:**
- [ ] PyPI publication
- [ ] Firebase deployment verification

---

### macagent 🖥️
**Status**: Model updates
**Last significant update**: 2026-02-07
**Current focus**: Gemini 3.0 migration
**Key decisions**:
- Purged legacy 2.0/1.5 models
- Sovereign Standard: gemini-3.0-pro/flash, gemma-3

**Open items:**
- [ ] Binary recompilation
- [ ] LM Studio engine timeout fixes

---

### mathman 🧮
**Status**: Dormant
**Last significant update**: Unknown
**Current focus**: N/A
**Key decisions**: N/A

---

### aiva 🎙️
**Status**: R&D
**Last significant update**: Unknown
**Current focus**: Voice SDK for coding
**Key decisions**: N/A

---

## Cross-Project Dependencies

| From | To | Dependency |
|------|-----|------------|
| vetsorcery | hardcard | Could use anchor pattern for clinical decision logging |
| macagent | hardcard | Shares identity/signing patterns |
| mike | hardcard | Decision anchoring for audit trail |
| mike | all | State management protocol |

---

## Pending Routes

*Entries here are waiting to be processed by the target spoke*

### → vetsorcery
*(none)*

### → hardcard
*(none)*

### → macagent
*(none)*

---

## Update Protocol

When a spoke has significant updates:
1. Update the spoke's section in this ledger
2. Check for cross-project implications
3. Add any new dependencies
4. Clear processed routes

**Mike maintains this ledger. Spokes contribute via State Exports.**
