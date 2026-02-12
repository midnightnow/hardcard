# Ed25519 Integration Patch for RealTBlock

> Created: 2026-01-02
> Author: Claude Opus 4.5 (Red Zen Audit Session)
> Status: Ready to Apply

## Summary

This patch wires real Ed25519 cryptographic signatures into RealTBlock, replacing
the simulated hash-based signatures with actual cryptographic non-repudiation.

## Prerequisites

1. Crypto module must exist at `/backend/app/apis/crypto/__init__.py`
2. Module must contain: `MathMessengerCrypto`, `get_server_crypto`, `SignatureBundle`

## Files to Modify

### 1. `/backend/app/apis/realtblock/__init__.py`

#### Change 1: Add Import (Line 8)

```python
# ADD after line 7:
from app.apis.crypto import MathMessengerCrypto, get_server_crypto, SignatureBundle
```

#### Change 2: Update Integration Comment (Lines 11-13)

```python
# REPLACE lines 11-13 with:
# RealTBlock trust model implementation
# A pure mathematics–based, consensus-free ledger using high-precision timestamps
# and cryptographic hash chaining
#
# INTEGRATION STATUS (2026-01-02):
# - Ed25519 signatures: WIRED via app.apis.crypto
# - Hash chain: WORKING
# - Formal verification: WORKING
```

#### Change 3: Replace Hardcard Integration (Lines 164-187)

```python
# REPLACE everything from line 164 to end of file with:

# Hardcard integration with REAL Ed25519 signatures
class HardcardSignRequest(BaseModel):
    """Request to sign data with a Hardcard"""
    hardcard_id: str
    data: Dict[str, Any]

class HardcardSignResponse(BaseModel):
    """Response from signing data with a Hardcard - now with REAL Ed25519"""
    algorithm: str = "Ed25519"
    signature_b64: str
    public_key_b64: str
    data_hash: str
    timestamp: float
    hardcard_id: str

class VerifySignatureRequest(BaseModel):
    """Request to verify a signature"""
    data: Dict[str, Any]
    signature_b64: str
    public_key_b64: str

class VerifySignatureResponse(BaseModel):
    """Response from signature verification"""
    valid: bool
    error: Optional[str] = None

@router.post("/hardcard/sign", response_model=HardcardSignResponse)
def sign_with_hardcard(request: HardcardSignRequest) -> HardcardSignResponse:
    """Sign data with a Hardcard using REAL Ed25519 signatures.

    INTEGRATION STATUS: REAL CRYPTO (as of 2026-01-02)

    This now uses actual Ed25519 digital signatures via the crypto module.
    The server maintains a signing key (ephemeral by default, or from
    MATHMESSENGER_SIGNING_KEY environment variable for persistence).

    Note: Physical Hardcard hardware integration is still pending.
    Current implementation uses software keys as a stepping stone.
    """
    # Get the server's crypto instance (real Ed25519)
    crypto = get_server_crypto()

    # Serialize data for signing
    data_str = str(request.data)
    data_bytes = data_str.encode('utf-8')
    data_hash = hashlib.sha256(data_bytes).hexdigest()

    # Sign with REAL Ed25519 (not simulated!)
    signature_bundle = crypto.sign(data_bytes, data_hash)

    return HardcardSignResponse(
        algorithm=signature_bundle.algorithm,
        signature_b64=signature_bundle.signature_b64,
        public_key_b64=signature_bundle.public_key_b64,
        data_hash=signature_bundle.signed_data_hash,
        timestamp=time.time(),
        hardcard_id=request.hardcard_id
    )

@router.post("/hardcard/verify", response_model=VerifySignatureResponse)
def verify_hardcard_signature(request: VerifySignatureRequest) -> VerifySignatureResponse:
    """Verify a signature using Ed25519.

    This verifies that the signature was created by the holder of the
    private key corresponding to the provided public key.

    Note: This proves WHAT was signed, not WHO signed it (that requires
    additional PKI infrastructure to map public keys to identities).
    """
    # Serialize data the same way it was signed
    data_str = str(request.data)
    data_bytes = data_str.encode('utf-8')

    # Verify with Ed25519
    valid, error = MathMessengerCrypto.verify(
        data_bytes,
        request.signature_b64,
        request.public_key_b64
    )

    return VerifySignatureResponse(valid=valid, error=error)
```

## Verification

After applying patch, run:

```bash
cd /Users/studio/hardcard/backend
python3 -c "
from app.apis.crypto import MathMessengerCrypto
import hashlib

crypto = MathMessengerCrypto()
data = b'Hello, Hardcard!'
data_hash = hashlib.sha256(data).hexdigest()
bundle = crypto.sign(data, data_hash)
print(f'Signed with Ed25519: {bundle.algorithm}')

valid, error = MathMessengerCrypto.verify(data, bundle.signature_b64, bundle.public_key_b64)
print(f'Verification: {\"PASSED\" if valid else \"FAILED\"}')"
```

Expected output:
```
Signed with Ed25519: Ed25519
Verification: PASSED
```

## New Endpoints After Patch

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/realtblock/hardcard/sign` | Sign with Ed25519 (returns full bundle) |
| POST | `/realtblock/hardcard/verify` | Verify Ed25519 signature |

## Breaking Changes

The `HardcardSignResponse` model changes from:
```python
{ "signature": str, "timestamp": float }
```

To:
```python
{ "algorithm": "Ed25519", "signature_b64": str, "public_key_b64": str, "data_hash": str, "timestamp": float, "hardcard_id": str }
```

Clients using the old response format will need to be updated.

---

*This patch was created during Red Zen audit session when file edits were being reverted by parallel processes.*
