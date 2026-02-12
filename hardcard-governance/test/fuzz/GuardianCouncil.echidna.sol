// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "../../contracts/governance/GuardianCouncil.sol";

/**
 * @title GuardianCouncil Echidna Fuzzing Tests
 * @notice Invariant testing for the Guardian Council contract
 */
contract GuardianCouncilEchidna {
    GuardianCouncil public council;
    
    address constant ROOT_OWNER = address(0x1);
    address constant GUARDIAN_1 = address(0x2);
    address constant GUARDIAN_2 = address(0x3);
    address constant GUARDIAN_3 = address(0x4);
    address constant GUARDIAN_4 = address(0x5);
    address constant GUARDIAN_5 = address(0x6);
    address constant ATTACKER = address(0x7);
    
    uint256 constant THRESHOLD = 3;
    uint256 constant MAX_GUARDIANS = 5;
    
    // Track state for invariants
    mapping(address => bool) public wasGuardian;
    uint256 public initialGuardianCount;
    
    constructor() {
        // Deploy with specific configuration
        council = new GuardianCouncil(THRESHOLD, MAX_GUARDIANS, ROOT_OWNER);
        
        // Setup initial guardians
        _becomeRootOwner();
        council.addGuardian(GUARDIAN_1);
        council.addGuardian(GUARDIAN_2);
        council.addGuardian(GUARDIAN_3);
        council.addGuardian(GUARDIAN_4);
        council.addGuardian(GUARDIAN_5);
        _stopBeingRootOwner();
        
        // Track initial state
        initialGuardianCount = 5;
        wasGuardian[GUARDIAN_1] = true;
        wasGuardian[GUARDIAN_2] = true;
        wasGuardian[GUARDIAN_3] = true;
        wasGuardian[GUARDIAN_4] = true;
        wasGuardian[GUARDIAN_5] = true;
    }
    
    // Helper to temporarily become root owner for setup
    function _becomeRootOwner() private {
        vm.startPrank(ROOT_OWNER);
    }
    
    function _stopBeingRootOwner() private {
        vm.stopPrank();
    }
    
    // INVARIANT 1: Guardian count should never exceed MAX_GUARDIANS
    function echidna_guardian_count_never_exceeds_max() public view returns (bool) {
        return council.getGuardianCount() <= MAX_GUARDIANS;
    }
    
    // INVARIANT 2: Guardian count should never go below threshold (except during setup)
    function echidna_guardian_count_above_threshold() public view returns (bool) {
        uint256 count = council.getGuardianCount();
        // Allow 0 during initial setup, otherwise must be >= threshold
        return count == 0 || count >= THRESHOLD;
    }
    
    // INVARIANT 3: Threshold should always be respected for freeze operations
    function echidna_freeze_requires_threshold() public returns (bool) {
        address target = address(0x1234);
        uint256 votesBefore = council.proposalVotes(keccak256(abi.encodePacked("freeze", target)));
        
        // Try to freeze with less than threshold
        vm.prank(GUARDIAN_1);
        council.freeze(target);
        
        vm.prank(GUARDIAN_2);
        council.freeze(target);
        
        // Should not be frozen with only 2 votes
        if (council.isFrozen(target)) {
            return false;
        }
        
        // Add third vote
        vm.prank(GUARDIAN_3);
        council.freeze(target);
        
        // Now should be frozen
        return council.isFrozen(target);
    }
    
    // INVARIANT 4: Only root owner can manage guardians
    function echidna_only_root_can_manage_guardians() public returns (bool) {
        address newGuardian = address(uint160(uint256(keccak256(abi.encodePacked(block.timestamp)))));
        
        // Try as non-root (should fail)
        vm.prank(ATTACKER);
        try council.addGuardian(newGuardian) {
            return false; // Should not succeed
        } catch {
            // Expected
        }
        
        // Try as guardian (should fail)
        vm.prank(GUARDIAN_1);
        try council.rotateGuardian(GUARDIAN_2, newGuardian) {
            return false; // Should not succeed
        } catch {
            // Expected
        }
        
        return true;
    }
    
    // INVARIANT 5: Same guardian cannot vote twice on same proposal
    function echidna_no_double_voting() public returns (bool) {
        address target = address(uint160(uint256(keccak256(abi.encodePacked(block.timestamp, "target")))));
        bytes32 proposalId = keccak256(abi.encodePacked("freeze", target));
        
        // First vote
        vm.prank(GUARDIAN_1);
        council.freeze(target);
        uint256 votesAfterFirst = council.proposalVotes(proposalId);
        
        // Try to vote again
        vm.prank(GUARDIAN_1);
        council.freeze(target);
        uint256 votesAfterSecond = council.proposalVotes(proposalId);
        
        // Votes should not increase
        return votesAfterFirst == votesAfterSecond;
    }
    
    // INVARIANT 6: Freeze duration is always 7 days
    function echidna_freeze_duration_constant() public returns (bool) {
        address target = address(uint160(uint256(keccak256(abi.encodePacked(block.timestamp, "freeze")))));
        
        // Get current time
        uint256 timeBefore = block.timestamp;
        
        // Execute freeze with threshold votes
        vm.prank(GUARDIAN_1);
        council.freeze(target);
        vm.prank(GUARDIAN_2);
        council.freeze(target);
        vm.prank(GUARDIAN_3);
        council.freeze(target);
        
        // Check freeze duration
        uint256 frozenUntil = council.frozenUntil(target);
        uint256 expectedFreezeEnd = timeBefore + 7 days;
        
        // Allow small difference for block timestamp variance
        return frozenUntil >= expectedFreezeEnd && frozenUntil <= expectedFreezeEnd + 1;
    }
    
    // PROPERTY 1: Guardian rotation maintains count
    function test_guardian_rotation_maintains_count(address oldGuardian, address newGuardian) public {
        // Skip if invalid inputs
        if (oldGuardian == address(0) || newGuardian == address(0)) return;
        if (oldGuardian == newGuardian) return;
        if (!council.isGuardian(oldGuardian)) return;
        if (council.isGuardian(newGuardian)) return;
        
        uint256 countBefore = council.getGuardianCount();
        
        vm.prank(ROOT_OWNER);
        try council.rotateGuardian(oldGuardian, newGuardian) {
            uint256 countAfter = council.getGuardianCount();
            assert(countBefore == countAfter);
        } catch {
            // Rotation failed, which is fine
        }
    }
    
    // PROPERTY 2: Frozen contracts stay frozen for full duration
    function test_freeze_duration_unchangeable(address target, uint256 timeJump) public {
        // Limit time jump to reasonable values
        timeJump = timeJump % (30 days);
        
        // Freeze the target
        vm.prank(GUARDIAN_1);
        council.freeze(target);
        vm.prank(GUARDIAN_2);
        council.freeze(target);
        vm.prank(GUARDIAN_3);
        council.freeze(target);
        
        if (!council.isFrozen(target)) return;
        
        uint256 frozenUntil = council.frozenUntil(target);
        
        // Jump time but not past freeze end
        if (block.timestamp + timeJump < frozenUntil) {
            vm.warp(block.timestamp + timeJump);
            assert(council.isFrozen(target));
        }
    }
}

// Helper contract to enable Foundry cheatcodes in Echidna
abstract contract vm {
    function prank(address) public virtual;
    function startPrank(address) public virtual;
    function stopPrank() public virtual;
    function warp(uint256) public virtual;
}