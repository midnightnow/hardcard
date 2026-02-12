# Hardcard Trust Model: The Native Number Registry

> **Status**: v1.0 IMPLEMENTED (Software)
> **Hardware Status**: PENDING (Physical Card not built)

## 1. The Core Concept
Hardcard is a **Native Number Registry**. It assigns a unique, strictly ordered real number timestamp to every registered event, creating a mathematical "arrow of time" that cannot be forged.

Unlike traditional blockchains that rely on "Consensus" (voting), Hardcard relies on **"Proof"** (Math).
- **Consensus**: "We all agree this happened." (Bitcoin)
- **Proof**: "Here is the cryptographic chain derived from the event." (Hardcard)

## 2. Architecture: Reality vs Vision

The Hardcard trust model relies on **RealTBlock** (Real-Time Block), a verifiable, append-only hash chain ledger.

| Component | Status | Implementation Location |
|-----------|--------|-------------------------|
| **RealTBlock Ledger** | ✅ **IMPLEMENTED** | `backend/app/apis/realtblock` |
| **Formal Verification** | ✅ **IMPLEMENTED** | `backend/app/apis/realtblock_formal` |
| **Ed25519 Signatures** | ✅ **IMPLEMENTED** | `mathmessenger_codec/crypto.py` |
| **Physical Hardcard** | ❌ **MISSING** | Hardware not yet manufactured |
| **Time Oracle** | ⚠️ **PARTIAL** | Uses system time; needs RFC 3161 integration |

### 2.1 The RealTBlock Ledger (Implemented)

RealTBlock is NOT a cryptocurrency blockchain. It is a **native number registry** where:

1.  **Strict Ordering**: Every event $E_i$ has a real-number timestamp $t_i$ such that $t_i > t_{i-1}$.
2.  **Cryptographic Integrity**: $h_i = H(h_{i-1} || t_i || data)$.
3.  **Formal Verification**: The system implements run-time verification of these mathematical properties.

Current Implementation Status:
- **Core Ledger**: Fully implemented in `realtblock/`.
- **Formal Verification**: Mathematical proofs implemented in `realtblock_formal/`.
- **Signatures**: Ed25519 crypto implemented in `mathmessenger_codec/crypto.py`.

### 2.2 What is Missing (Hardware Gap)

While the software ledger exists, the **physical hardware anchors** described in the vision (The Hardcard) do not yet exist.

- **Physical Card**: ❌ Not built.
- **Hardware Secure Element**: ❌ Simulated in software.
- **External Time Oracle**: ❌ Uses system time (needs RFC 3161).

## 3. Trust Layers

### Layer 1: Mathematical Integrity (The Chain)
*Status: Active*
The hash chain ensures that history cannot be rewritten without breaking the cryptographic links.
- **Verification**: `POST /realtblock/verify` runs the formal proof against the current chain.

### Layer 2: Identity (The Keys)
*Status: Partial*
- **Software**: Ed25519 keys are generated and used for signatures.
- **Hardware**: Keys should be locked in a secure element (Hardcard). Currently they are software-managed.

### Layer 3: Time (The Registry)
*Status: Simulated*
- **Current**: Server clock + Monotonic Counter.
- **Target**: GPS/Atomic Clock Oracle via RFC 3161.

## 4. Verification Process

To verify a Hardcard entry:
1.  **Fetch**: Retrieve the entry `E_i` and its predecessor `E_{i-1}`.
2.  **Compute**: `h_calculated = SHA256(h_{i-1} || t_i || data_i)`
3.  **Compare**: `h_calculated == E_i.hash`
4.  **Verify Time**: `t_i > t_{i-1}`

This logic is fully enforced by the code in `realtblock_formal`.
