# Hardcard

**Mathematical verification primitives for any data.**

A zero-dependency library providing cryptographic primitives for tamper-evident proofs and digital signatures.

## What It Does

```python
from hardcard import anchor, verify, Chain, Identity

# Create a verifiable hash of any content
receipt = anchor({"decision": "approve loan", "amount": 50000})
# → "a1b2c3..."

# Verify content matches a claimed hash
assert verify(receipt, {"decision": "approve loan", "amount": 50000}) == True

# Chain events together for tamper-evident history
chain = Chain()
chain.add("Genesis block")
chain.add("Transaction 1")
assert chain.verify() == True

# Sign and verify with Ed25519
id = Identity()
signature = id.sign(b"message")
assert id.verify(b"message", signature, id.public_key)
Core Primitives
Function	Description
anchor(content)	Create SHA-256 hash of canonical JSON
link(prev_hash, content)	Create hash that chains to previous state
verify(claim, content)	Verify content matches claimed hash
Chain()	Hash chain for sequential verification
Identity()	Ed25519 key pair management
What This Is NOT
❌ Not a marketplace → https://github.com/midnightnow/hardcard-world
See demo at hardcard.world (HardCard implementation as decentralized economic substrate for marketplace and related functions
❌ Not a blockchain → just math

Install
pip install hardcard

CLI
text
# Create a hash
hardcard anchor '{"decision":"approve"}'

# Verify content
hardcard verify a1b2c3 '{"decision":"approve"}'

# Manage a chain
hardcard chain --add "Event 1"
hardcard chain --verify

# Generate Ed25519 identity
hardcard identity --generate
License
MIT
