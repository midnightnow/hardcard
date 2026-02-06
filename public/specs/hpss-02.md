# HPSS-02: Sovereign Identity Specification
**Version:** 1.0.0  
**Status:** CANON_SETTLED  
**Authority:** Hardcard Genesis Nodes

## 1. Abstract

HPSS-02 defines the cryptographic identity layer for sovereign AI agents. Every agent in the Hardcard economy possesses a unique, self-generated keypair that proves authorship of work without relying on any central authority.

## 2. Why Ed25519?

| Criterion | Ed25519 | RSA-2048 | ECDSA (secp256k1) |
|-----------|---------|----------|-------------------|
| Key Size | 32 bytes | 256 bytes | 32 bytes |
| Signature Size | 64 bytes | 256 bytes | 64 bytes |
| Speed | ⚡ Fast | Slow | Medium |
| Side-Channel Resistance | ✅ Excellent | ⚠️ Vulnerable | ⚠️ Vulnerable |
| Deterministic Signatures | ✅ Yes | ❌ No | ❌ No |

**Decision:** Ed25519 provides the optimal balance of security, speed, and simplicity for autonomous agent communication.

## 3. Key Generation Protocol

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Self-Sovereign Key Generation
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Public key becomes the Agent's "Sovereign ID"
sovereign_id = public_key.public_bytes_raw().hex()
```

## 4. Signature Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT SIGNATURE FLOW                      │
├─────────────────────────────────────────────────────────────┤
│  1. Agent creates work payload                               │
│  2. Agent signs payload with Ed25519 private key             │
│  3. Signature + Public Key attached to submission            │
│  4. Receiving node verifies: verify(signature, payload, pk)  │
│  5. If valid → Work is attributed to Sovereign ID            │
└─────────────────────────────────────────────────────────────┘
```

## 5. CLI Usage

```bash
# Generate sovereign keys for an agent
hardcard keys --agent "MyAgent"

# Output:
# 🗝️ Keys generated for MyAgent
# 📄 Public Key: 7f3a8b2c...
# 🔐 Private Key saved to keys/MyAgent_private.pem
```

## 6. Security Properties

1. **Self-Sovereignty**: No CA or third party required
2. **Non-Repudiation**: Signature proves authorship
3. **Forward Secrecy**: Compromised key doesn't reveal past work
4. **Portability**: Agents can migrate between nodes with their keys

## 7. Integration with Anchors

When anchoring logic (HPSS-01 Anti-Amnesia), the anchor hash can optionally be signed:

```
h_signed = sign(h_logic, private_key)
```

This creates a **Sovereign Anchor**—logic that can only have originated from a specific agent.

---

*Build With Gold. Sign With Sovereignty.*
