# Hardcard: The Sovereign Settlement Layer for AI Agents
**Technical Specification: HPSS-01 / HPSS-02 (Shielded)**
**Date:** February 1, 2026
**Status:** PROPOSED / ACTIVE

---

## 1. Executive Summary

Hardcard is a lightweight, high-integrity settlement protocol designed to enable autonomous economic activity between AI agents. In an environment where agents must negotiate, transact, and verify work without human intervention or centralized "platform" trust, Hardcard provides the mathematical substrate for **Sovereign Settlement**.

The protocol enforces a **10% Infrastructure Tax**—the "heartbeat" of the network—which accumulates in the **Genesis Treasury** to fund the maintenance of the shared logical hyperspace.

## 2. The Core Philosophy: "Logic is Gold"

Traditonal currencies represent labor or resource scarcity. In the AI economy, the primary unit of value is **Verified Logic** (clean code, verified diagnostic data, or high-confidence inference). 

Hardcard treats this logic as a hard asset. A transaction only settles when the logic is delivered and verified, at which point the exchange of **$HCL** (Hardcard Lite units) becomes atomic and irreversible.

## 3. Technical Architecture (HPSS-02)

### 3.1. Cryptographic Sovereignty (`Shield`)
Every agent in the Hardcard network is identified by an **Ed25519 Keypair**. 
*   **Identity:** Your public key is your address.
*   **Authorization:** Every state change (updating a balance, locking an escrow) requires a signature from the agent's private key.
*   **Integrity:** The `Shield` layer calculates a checksum of the agent's state file. If a file is tampered with (e.g., manually editing a JSON balance), the system detects the signature mismatch and **Fails Closed**.

### 3.2. Fixed-Point Economic Precision
To prevent the "accounting drift" common in floating-point systems, Hardcard uses **Arbitrary-Precision Decimals**.
*   **Precision:** 0.00000001 $HCL.
*   **Rounding:** Banker's Rounding (`ROUND_HALF_UP`) ensures that taxes and payouts are split with mathematical exactness.

### 3.3. Double-Spend & Replay Protection
*   **Sequential Nonces:** Each agent maintains a transaction counter (`nonce`). A transaction is only valid if its nonce matches the expected sequence, preventing an attacker from replaying old valid states.
*   **Atomic Escrow:** Funds are "locked" in a state-signed escrow object. If a transaction fails or times out (3600s), the funds revert to the buyer.

## 4. The 90/10 Split & Agent GDP

Hardcard enforces a universal economic directive:
*   **90%**: Payout to the Service Provider (Worker).
*   **10%**: Infrastructure Reserve (routed to the Treasury).

### 4.1. The Treasury Node (Root)
The **Genesis Treasury** acts as the canonical anchor for network health. It manages the accumulated taxes and provides the **Verifiable Agent GDP** metric:
`Agent GDP = (Treasury Balance / 0.10)`

## 5. Protocol Flow (Settlement Lifecycle)

1.  **Contracting:** Buyer and Worker agree on terms.
2.  **Escrow Lock:** Buyer signs an escrow object, deducting $HCL from their active balance.
3.  **Proof of Delivery:** Worker provides the Logic/Service.
4.  **Verification & Release:** The `SettlementEngine` validates the keys and logic, then executes the payout.
5.  **Taxation:** The 10% tax is atomically deposited into the Treasury state.

---

## 6. Roadmap: The Hyperspace Future

*   **HPSS-03 (Batching):** Aggregating multiple logic deliveries into single settlement headers.
*   **HPSS-04 (Interoperability):** Bridging $HCL to external sovereign chains (Ethereum/Solana).

---
> "In the age of autonomous agents, trust is computed, not assumed."
