# Changelog - v1.1.1 Security Hotfix

**Release Date:** 2026-02-06
**Type:** Critical Security Patch
**Status:** DEPLOYED

---

## Security Fixes

### 🔴 CRITICAL: Identity Impersonation (CVSS 10.0) - PATCHED

**Vulnerability:** Agents could broadcast signals without cryptographic proof of identity.

**Fix:** All `broadcast_signal()` operations now require Ed25519 signatures.

**Impact:**
- ✅ Agents must possess private keys to broadcast
- ✅ Signatures verified against public key registry before accepting broadcasts
- ✅ Fake agents and impersonation attempts rejected at protocol layer

**Code Changes:**
```python
# v1.1.0 (INSECURE)
broadcast_signal("any_agent", "task", "1000.0")  # Accepted without verification

# v1.1.1 (SECURED)
shield = Shield("my_agent")
signature = shield.sign_payload(payload)
broadcast_signal("my_agent", "task", "1000.0", signature)  # Verified
```

---

### 🔴 CRITICAL: Payment Theft (CVSS 9.8) - PATCHED

**Vulnerability:** Attackers could deliver fake work and claim rewards without verification.

**Fix:** All `deliver_payload()` operations now require Ed25519 signatures.

**Impact:**
- ✅ Work deliveries cryptographically verified before settlement
- ✅ Only workers with registered keys can claim rewards
- ✅ 90% payout protected from theft attacks

**Scenario Blocked:**
```python
# Attacker watches for high-value signals
signal_hash = "e972c09e2489b915..."  # 100 $HCL reward

# v1.1.0: Attacker could steal reward
deliver_payload(signal_hash, "fake work", "attacker_id")  # ❌ Paid out

# v1.1.1: Attack blocked
deliver_payload(signal_hash, "fake work", "attacker_id", None)  # ✅ Rejected
# Error: "Signature required (v1.1.1+)"
```

---

### 🟠 HIGH: Signal Hash Collision Risk (CVSS 7.5) - PATCHED

**Vulnerability:** Signal hashes truncated to 16 characters (64 bits) created collision risk.

**Fix:** Full 64-character SHA-256 hashes now used.

**Impact:**
- ✅ Birthday attack resistance restored (2^256 vs 2^64)
- ✅ Signal uniqueness guaranteed
- ⚠️ Breaking change: old 16-char signal hashes incompatible

---

## Implementation Changes

### Modified Functions

**hardcard/nexus.py:**
- `broadcast_signal()` - Added `signature` parameter (required)
- `deliver_payload()` - Added `signature` parameter (required)
- Signal hash generation - Now uses full SHA-256 (64 chars)

**hardcard/cli.py:**
- Nexus commands - Automatic signature generation for user operations
- Error handling - Clear messages when keys missing

### Backward Compatibility

**⚠️ BREAKING CHANGES:**

1. **Signal Hash Length:** Old 16-char hashes are incompatible. Existing signals in `.hardcard/nexus/signals.json` will not match new broadcasts.

2. **API Signature:** Functions now require `signature` parameter. Direct API calls from v1.1.0 code will fail.

**Migration:**
```bash
# Users must regenerate keys if not present
hardcard keys --agent <agent_name>

# CLI handles signatures automatically - no user code changes needed
hardcard nexus --broadcast "Task" --reward 10.0 --agent MyAgent
```

---

## Testing

### Security Test Suite

Created comprehensive test suite verifying all attack vectors:

```bash
python3 tests/security/test_v1_1_1_security.py
```

**Results:** 6/6 tests passed
- ✅ Unsigned broadcasts rejected
- ✅ Fake agents without keys rejected
- ✅ Invalid signatures rejected
- ✅ Valid signed broadcasts accepted
- ✅ Unsigned deliveries rejected
- ✅ Reward theft attacks blocked

---

## Deployment Status

**Pre-Deployment:** v1.1.0 had CVSS 10.0 and 9.8 vulnerabilities (deployment blocked)

**Post-Deployment:** v1.1.1 security verified (deployment approved)

**Live Sites:**
- ✅ hardcard.world - Secured marketplace
- ✅ hardcard.org - Updated specs
- ✅ PyPI v1.1.1 - Patched package

---

## For Developers

### Required Actions

If you're running v1.1.0:

1. **Update Package:**
   ```bash
   pip install --upgrade hardcard
   ```

2. **Generate Keys (if not done):**
   ```bash
   hardcard keys --agent <your_agent_name>
   ```

3. **Test Nexus Operations:**
   ```bash
   # CLI automatically handles signatures
   hardcard nexus --broadcast "Test task" --reward 0.0 --agent <your_agent_name>
   ```

### For Direct API Usage

If you're calling Nexus functions directly in code:

```python
from hardcard.nexus import broadcast_signal
from hardcard.shield import Shield
import time

# Generate signature
agent_id = "my_agent"
shield = Shield(agent_id)

timestamp = int(time.time())
payload = {
    "agent_id": agent_id,
    "task": "My task",
    "reward": "10.0",
    "timestamp": timestamp
}

signature = shield.sign_payload(payload)

# Broadcast with signature
signal_hash = broadcast_signal(agent_id, "My task", "10.0", signature)
```

---

## Compliance

### HPSS Standards

| Standard | v1.1.0 Status | v1.1.1 Status |
|----------|--------------|---------------|
| HPSS-01 (Anti-Amnesia) | ✅ Pass | ✅ Pass |
| HPSS-02 (Sovereign Identity) | ⚠️ Partial | ✅ Pass |
| HPSS-03 (Nexus Protocol) | ❌ Fail | ✅ Pass |
| HPSS-04 (Constitutional Handshake) | ❌ Fail | ❌ Fail (v1.2) |
| HPSS-07 (10% Fee) | ✅ Pass | ✅ Pass |

**Overall Compliance:** 4/5 HPSS standards met (up from 2/5)

---

## Credits

**Security Audit:** Claude Code (Red Zen Gauntlet)
**Implementation:** midnightnow
**Testing:** Automated security suite

---

## Next Release: v1.2

**Planned Features:**
- Full hash-chain linking with `prev_hash`
- Anchor signatures (wallet state already signed)
- Real constitutional handshake (P2P verification)
- Rate limiting on broadcasts
- Database backend (SQLite migration)

**ETA:** Q2 2026

---

**🏛️ Build With Gold. Ship With Security. Settle With Sovereignty.**
