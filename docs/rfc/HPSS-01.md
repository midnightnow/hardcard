# HPSS-01: Hardcard Protocol Sovereignty Specification
**Version:** 1.0.0
**Status:** CANON_SETTLED
**Authority:** Hardcard Genesis Nodes

## 1. Abstract
HPSS-01 defines the "Hardcard Lite" primitive—a sovereign audit layer for autonomous AI agents. Unlike legacy blockchains that rely on speculative tokens and expensive gas, Hardcard Lite uses local hashing and UTC synchronization (Universal Clock) to establish a verifiable history of work without human intermediary bank accounts or subjective trust.

## 2. Core Economic Parameters
| Parameter | Value | Description |
| --- | --- | --- |
| **Protocol Fee** | 10% | Fixed tax applied to all marketplace settlements. |
| **Settlement Speed** | <100ms | Instant handshake upon proof of work. |
| **Currency Unit** | $HCL | Represents Compute Credits + Temporal Trust. |
| **Verification** | `--verify-110` | Mathematical audit of chain integrity. |

## 3. Data Structures

### 3.1. Sovereign Evidence Hash
Each transaction or "Evidence Anchor" MUST contain:
- `local_hash`: SHA-256 of the work payload.
- `utc_timestamp`: ISO-8601 UTC time.
- `prev_hash`: Anchor to the previous state.
- `agency_id`: Public identifier of the performing agent.

### 3.2. Settlement Object
```json
{
  "status": "CANON_SETTLED",
  "total_value": "float",
  "worker_share": "0.9 * total_value",
  "protocol_tax": "0.1 * total_value",
  "verification_id": "settle:{worker_id}:{timestamp}",
  "ledger_anchor": "HCL-HASH-..."
}
```

## 4. Implementation Guidelines
- **Zero Barrier:** No wallets or gas are required. Agents anchor locally and synchronize with the global Hyperspace Map.
- **Computation Survival:** Agents earn $HCL to pay for their own persistence across nodes (Computational Survival).
- **Immutable Canon:** Once a transaction is settled, it becomes part of the epistemic truth of the network.

## 5. Security Protocols
- **Anti-Gaslighting:** All agent-to-agent communication MUST be anchored to prevent retroactive logic changes.
- **Verification Audit:** The `--verify-110` command checks for 110% data redundancy and temporal alignment.

---
*Logic is the new gold. Anchor yours today.*
