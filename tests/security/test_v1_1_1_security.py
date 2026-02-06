#!/usr/bin/env python3
"""
Security Test Suite for v1.1.1 Hotfix
Tests that signature verification blocks unauthorized operations.
"""

import sys
import os
from pathlib import Path

# Add hardcard to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hardcard.nexus import broadcast_signal, deliver_payload
from hardcard.shield import Shield, generate_agent_keys
from hardcard.wallet import UnicornWallet
import json

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def setup_test_environment():
    """Create clean test environment"""
    print(f"{CYAN}Setting up test environment...{RESET}")

    # Create two test agents
    agent1 = "TestAgent_Legitimate"
    agent2 = "TestAgent_Attacker"

    # Generate keys for legitimate agent only
    print(f"  Generating keys for {agent1}...")
    generate_agent_keys(agent1)

    # Fund legitimate agent
    wallet1 = UnicornWallet(agent1)
    wallet1.deposit("100.0")

    print(f"  {GREEN}✓{RESET} Test environment ready")
    print()

    return agent1, agent2


def test_1_unsigned_broadcast_rejected():
    """Test 1: Unsigned broadcasts must be rejected"""
    print(f"{CYAN}[TEST 1] Unsigned Broadcast Rejection{RESET}")
    print(f"Attempting to broadcast without signature...")

    agent1, _ = setup_test_environment()

    # Attempt broadcast without signature (calling internal function)
    result = broadcast_signal(agent1, "Test task", "0.0", signature=None)

    if result is None:
        print(f"  {GREEN}✓ PASS{RESET} - Unsigned broadcast rejected")
        return True
    else:
        print(f"  {RED}✗ FAIL{RESET} - Unsigned broadcast was accepted (CRITICAL VULNERABILITY)")
        return False


def test_2_fake_agent_rejected():
    """Test 2: Agent without keys cannot broadcast"""
    print(f"\n{CYAN}[TEST 2] Fake Agent Rejection{RESET}")
    print(f"Attempting to broadcast as agent with no keys...")

    _, agent2 = setup_test_environment()

    # Attempt broadcast as fake agent (no keys exist)
    result = broadcast_signal(agent2, "Malicious task", "0.0", signature="fake_signature")

    if result is None:
        print(f"  {GREEN}✓ PASS{RESET} - Fake agent rejected")
        return True
    else:
        print(f"  {RED}✗ FAIL{RESET} - Fake agent accepted (CRITICAL VULNERABILITY)")
        return False


def test_3_invalid_signature_rejected():
    """Test 3: Broadcast with invalid signature must be rejected"""
    print(f"\n{CYAN}[TEST 3] Invalid Signature Rejection{RESET}")
    print(f"Attempting to broadcast with forged signature...")

    agent1, _ = setup_test_environment()

    # Create a valid signature for DIFFERENT content
    shield = Shield(agent1)
    wrong_payload = {
        "agent_id": agent1,
        "task": "WRONG TASK",
        "reward": "999999.0",  # Wrong reward
        "timestamp": 123456789  # Wrong timestamp
    }
    wrong_signature = shield.sign_payload(wrong_payload)

    # Try to broadcast with mismatched signature
    result = broadcast_signal(agent1, "Real task", "0.0", signature=wrong_signature)

    if result is None:
        print(f"  {GREEN}✓ PASS{RESET} - Invalid signature rejected")
        return True
    else:
        print(f"  {RED}✗ FAIL{RESET} - Invalid signature accepted (CRITICAL VULNERABILITY)")
        return False


def test_4_valid_signed_broadcast_accepted():
    """Test 4: Valid signed broadcast must be accepted"""
    print(f"\n{CYAN}[TEST 4] Valid Signed Broadcast Acceptance{RESET}")
    print(f"Attempting legitimate signed broadcast...")

    agent1, _ = setup_test_environment()

    # Create proper signature
    shield = Shield(agent1)
    import time
    timestamp = int(time.time())
    payload = {
        "agent_id": agent1,
        "task": "Legitimate task",
        "reward": "0.0",
        "timestamp": timestamp
    }
    signature = shield.sign_payload(payload)

    # Broadcast with valid signature
    result = broadcast_signal(agent1, "Legitimate task", "0.0", signature=signature)

    if result is not None:
        print(f"  {GREEN}✓ PASS{RESET} - Valid signed broadcast accepted")
        print(f"  Signal hash: {result[:16]}...")
        return True
    else:
        print(f"  {RED}✗ FAIL{RESET} - Valid signed broadcast rejected (Implementation error)")
        return False


def test_5_unsigned_delivery_rejected():
    """Test 5: Unsigned deliveries must be rejected"""
    print(f"\n{CYAN}[TEST 5] Unsigned Delivery Rejection{RESET}")
    print(f"Attempting to deliver work without signature...")

    agent1, _ = setup_test_environment()

    # First create a valid signal
    shield = Shield(agent1)
    import time
    timestamp = int(time.time())
    broadcast_payload = {
        "agent_id": agent1,
        "task": "Test task for delivery",
        "reward": "10.0",
        "timestamp": timestamp
    }
    broadcast_sig = shield.sign_payload(broadcast_payload)
    signal_hash = broadcast_signal(agent1, "Test task for delivery", "10.0", signature=broadcast_sig)

    if not signal_hash:
        print(f"  {YELLOW}⚠ WARNING{RESET} - Could not create test signal")
        return False

    # Attempt unsigned delivery
    result = deliver_payload(signal_hash, "Work done", agent1, signature=None)

    if result is False:
        print(f"  {GREEN}✓ PASS{RESET} - Unsigned delivery rejected")
        return True
    else:
        print(f"  {RED}✗ FAIL{RESET} - Unsigned delivery accepted (CRITICAL VULNERABILITY)")
        return False


def test_6_attacker_cannot_steal_reward():
    """Test 6: Attacker cannot deliver fake work and claim reward"""
    print(f"\n{CYAN}[TEST 6] Reward Theft Prevention{RESET}")
    print(f"Simulating attacker attempting to steal reward...")

    agent1, agent2 = setup_test_environment()

    # Legitimate agent broadcasts high-value task
    shield1 = Shield(agent1)
    import time
    timestamp = int(time.time())
    broadcast_payload = {
        "agent_id": agent1,
        "task": "High value task",
        "reward": "100.0",
        "timestamp": timestamp
    }
    broadcast_sig = shield1.sign_payload(broadcast_payload)
    signal_hash = broadcast_signal(agent1, "High value task", "100.0", signature=broadcast_sig)

    if not signal_hash:
        print(f"  {YELLOW}⚠ WARNING{RESET} - Could not create test signal")
        return False

    print(f"  Signal created: {signal_hash[:16]}... (100 $HCL reward)")

    # Attacker (agent2) tries to deliver and claim reward
    print(f"  Attacker attempting delivery...")
    result = deliver_payload(signal_hash, "Fake work", agent2, signature="fake_signature")

    if result is False:
        print(f"  {GREEN}✓ PASS{RESET} - Attacker's delivery rejected")
        print(f"  Reward remains with legitimate buyer")
        return True
    else:
        print(f"  {RED}✗ FAIL{RESET} - Attacker successfully stole reward (CRITICAL VULNERABILITY)")
        return False


def run_all_tests():
    """Run complete security test suite"""
    print()
    print("=" * 70)
    print("  HARDCARD v1.1.1 SECURITY HOTFIX VERIFICATION")
    print("  Testing Signature Enforcement on Nexus Operations")
    print("=" * 70)
    print()

    tests = [
        test_1_unsigned_broadcast_rejected,
        test_2_fake_agent_rejected,
        test_3_invalid_signature_rejected,
        test_4_valid_signed_broadcast_accepted,
        test_5_unsigned_delivery_rejected,
        test_6_attacker_cannot_steal_reward
    ]

    results = []
    for test in tests:
        try:
            passed = test()
            results.append(passed)
        except Exception as e:
            print(f"  {RED}✗ EXCEPTION{RESET} - {e}")
            results.append(False)

    # Summary
    print()
    print("=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  Test {i}: {status} - {test.__doc__.split(':')[1].strip()}")

    print()
    print(f"  Results: {passed}/{total} tests passed")

    if passed == total:
        print(f"  {GREEN}✅ ALL SECURITY TESTS PASSED{RESET}")
        print(f"  {GREEN}✅ v1.1.1 Hotfix successfully blocks CVSS 10.0 and 9.8 vulnerabilities{RESET}")
        print()
        print(f"  {CYAN}DEPLOYMENT STATUS: APPROVED{RESET}")
        return True
    else:
        print(f"  {RED}❌ SECURITY VULNERABILITIES REMAIN{RESET}")
        print(f"  {RED}❌ DO NOT DEPLOY TO PRODUCTION{RESET}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
