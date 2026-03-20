# Hardcard

**Mathematical verification primitives for any data.**

Think of it as a forge for truth—every decision stamped into an immutable record. But unlike a forge that cares about heat and metal, Hardcard cares only about math.

## What It Does

```python
from hardcard import anchor, verify, Chain, Identity

# Stamp any decision into an unforgeable record
receipt = anchor({"decision": "approve loan", "amount": 50000})
# → "a1b2c3..."

# Later, verify it hasn't been tampered with
assert verify(receipt, {"decision": "approve loan", "amount": 50000}) == True

# Chain decisions together
chain = Chain()
chain.add("Genesis")
chain.add("Decision 1")
assert chain.verify() == True

# Sign with Ed25519
id = Identity()
sig = id.sign(b"message")
assert id.verify(b"message", sig, id.public_key)
```

## The Math (Not the Metaphor)

| Function | What it does |
|----------|--------------|
| `anchor(data)` | SHA-256 hash of canonical JSON |
| `link(prev, data)` | Hash that includes previous state |
| `verify(hash, data)` | Recomputes and compares |
| `Chain()` | Linked list of hashes |
| `Identity()` | Ed25519 signatures |

## What This Is NOT

- ❌ Not a marketplace → [hardcard.world](https://hardcard.world)
- ❌ Not a veterinary suite → private repository
- ❌ Not a blockchain → just math

## Install

```bash
pip install hardcard
```

## CLI

```bash
# Create a receipt
hardcard anchor '{"decision":"approve"}'

# Verify it
hardcard verify a1b2c3 '{"decision":"approve"}'

# Chain events
hardcard chain --add "Event 1"
hardcard chain --add "Event 2"
hardcard chain --verify

# Generate identity
hardcard identity --generate
```

## License

MIT
