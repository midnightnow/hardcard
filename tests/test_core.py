"""Tests for Hardcard core primitives."""

import pytest
from hardcard import anchor, verify, Chain, Identity

def test_anchor_deterministic():
    """Same input should produce same hash."""
    data = {"test": "data", "number": 123}
    h1 = anchor(data)
    h2 = anchor(data)
    assert h1 == h2

def test_anchor_different():
    """Different inputs should produce different hashes."""
    h1 = anchor({"a": 1})
    h2 = anchor({"a": 2})
    assert h1 != h2

def test_verify():
    """Verification should work for matching content."""
    data = {"x": 42}
    h = anchor(data)
    assert verify(h, data) == True
    assert verify(h, {"x": 43}) == False

def test_chain():
    """Chain should maintain integrity."""
    chain = Chain()
    h1 = chain.add("first")
    h2 = chain.add("second")
    assert chain.verify() == True
    assert len(chain) == 2

def test_identity():
    """Ed25519 signatures should work."""
    id = Identity()
    msg = b"test message"
    sig = id.sign(msg)
    assert id.verify(msg, sig, id.public_key) == True
    assert id.verify(b"wrong", sig, id.public_key) == False
