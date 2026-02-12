// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "../../contracts/governance/TimelockController.sol";

/**
 * @title Timelock Echidna Fuzzing Tests
 * @notice Invariant testing for the Timelock Controller
 */
contract TimelockEchidna {
    HardcardTimelockController public timelock;
    
    address constant ROOT_OWNER = address(0x1);
    address constant PROPOSER = address(0x2);
    address constant EXECUTOR = address(0x3);
    address constant ATTACKER = address(0x4);
    
    uint256 constant MIN_DELAY = 48 hours;
    uint256 constant DEFAULT_DELAY = 48 hours;
    
    // Track operations for invariant checking
    mapping(bytes32 => bool) public wasScheduled;
    mapping(bytes32 => uint256) public scheduleTime;
    mapping(bytes32 => bool) public wasExecuted;
    
    constructor() {
        // Deploy timelock
        address[] memory proposers = new address[](1);
        proposers[0] = PROPOSER;
        
        address[] memory executors = new address[](1);
        executors[0] = EXECUTOR;
        
        timelock = new HardcardTimelockController(
            MIN_DELAY,
            proposers,
            executors,
            ROOT_OWNER,
            ROOT_OWNER
        );
    }
    
    // INVARIANT 1: Minimum delay is always respected
    function echidna_min_delay_enforced() public view returns (bool) {
        return timelock.getMinDelay() >= DEFAULT_DELAY;
    }
    
    // INVARIANT 2: Only scheduled operations can be executed
    function echidna_only_scheduled_can_execute() public returns (bool) {
        bytes32 id = keccak256(abi.encodePacked(block.timestamp, "test"));
        address target = address(uint160(uint256(id)));
        bytes memory data = abi.encodeWithSignature("test()");
        
        // Try to execute without scheduling
        vm.prank(EXECUTOR);
        try timelock.execute(target, 0, data, bytes32(0), bytes32(0)) {
            return false; // Should not succeed
        } catch {
            return true; // Expected failure
        }
    }
    
    // INVARIANT 3: Operations cannot be executed before delay
    function echidna_delay_enforced_for_execution() public returns (bool) {
        address target = address(uint160(uint256(keccak256(abi.encodePacked(block.timestamp)))));
        bytes memory data = "";
        bytes32 predecessor = bytes32(0);
        bytes32 salt = keccak256(abi.encodePacked(block.timestamp));
        
        // Schedule operation
        vm.prank(PROPOSER);
        timelock.schedule(target, 0, data, predecessor, salt, MIN_DELAY);
        
        bytes32 id = timelock.hashOperation(target, 0, data, predecessor, salt);
        
        // Try immediate execution (should fail)
        vm.prank(EXECUTOR);
        try timelock.execute(target, 0, data, predecessor, salt) {
            return false; // Should not succeed
        } catch {
            // Expected - cannot execute before delay
        }
        
        // Fast forward time
        vm.warp(block.timestamp + MIN_DELAY + 1);
        
        // Now execution should work
        vm.prank(EXECUTOR);
        try timelock.execute(target, 0, data, predecessor, salt) {
            return true; // Should succeed after delay
        } catch {
            return false; // Unexpected failure
        }
    }
    
    // INVARIANT 4: Only root owner can veto
    function echidna_only_root_can_veto() public returns (bool) {
        // Schedule an operation
        address target = address(uint160(uint256(keccak256(abi.encodePacked(block.timestamp, "veto")))));
        bytes memory data = "";
        bytes32 salt = keccak256(abi.encodePacked(block.timestamp));
        
        vm.prank(PROPOSER);
        timelock.schedule(target, 0, data, bytes32(0), salt, MIN_DELAY);
        
        bytes32 id = timelock.hashOperation(target, 0, data, bytes32(0), salt);
        
        // Try veto as attacker (should fail)
        vm.prank(ATTACKER);
        try timelock.emergencyVeto(id) {
            return false; // Should not succeed
        } catch {
            // Expected
        }
        
        // Try veto as proposer (should fail)
        vm.prank(PROPOSER);
        try timelock.emergencyVeto(id) {
            return false; // Should not succeed
        } catch {
            // Expected
        }
        
        // Veto as root owner (should succeed)
        vm.prank(ROOT_OWNER);
        try timelock.emergencyVeto(id) {
            return !timelock.isOperationPending(id); // Should no longer be pending
        } catch {
            return false; // Unexpected failure
        }
    }
    
    // INVARIANT 5: Executed operations cannot be re-executed
    function echidna_no_double_execution() public returns (bool) {
        address target = address(uint160(uint256(keccak256(abi.encodePacked(block.timestamp, "double")))));
        bytes memory data = "";
        bytes32 salt = keccak256(abi.encodePacked(block.timestamp, "unique"));
        
        // Schedule
        vm.prank(PROPOSER);
        timelock.schedule(target, 0, data, bytes32(0), salt, MIN_DELAY);
        
        // Wait for delay
        vm.warp(block.timestamp + MIN_DELAY + 1);
        
        // Execute once
        vm.prank(EXECUTOR);
        try timelock.execute(target, 0, data, bytes32(0), salt) {
            // First execution succeeded
        } catch {
            return true; // If first fails, test is invalid
        }
        
        // Try to execute again
        vm.prank(EXECUTOR);
        try timelock.execute(target, 0, data, bytes32(0), salt) {
            return false; // Should not succeed
        } catch {
            return true; // Expected failure
        }
    }
    
    // PROPERTY 1: Delay updates maintain minimum
    function test_delay_update_maintains_minimum(uint256 newDelay) public {
        vm.prank(ROOT_OWNER);
        try timelock.emergencyUpdateDelay(newDelay) {
            assert(timelock.getMinDelay() >= DEFAULT_DELAY);
        } catch {
            // Update failed, which is fine if newDelay < DEFAULT_DELAY
        }
    }
    
    // PROPERTY 2: Cancelled operations cannot be executed
    function test_cancelled_operations_fail(address target, uint256 value, bytes memory data) public {
        bytes32 salt = keccak256(abi.encodePacked(block.timestamp, target, value, data));
        
        // Schedule
        vm.prank(PROPOSER);
        try timelock.schedule(target, value, data, bytes32(0), salt, MIN_DELAY) {
            bytes32 id = timelock.hashOperation(target, value, data, bytes32(0), salt);
            
            // Cancel
            vm.prank(ROOT_OWNER);
            timelock.emergencyVeto(id);
            
            // Wait and try to execute
            vm.warp(block.timestamp + MIN_DELAY + 1);
            
            vm.prank(EXECUTOR);
            try timelock.execute(target, value, data, bytes32(0), salt) {
                assert(false); // Should never succeed
            } catch {
                assert(true); // Expected
            }
        } catch {
            // Schedule failed, skip test
        }
    }
}

// Helper contract to enable Foundry cheatcodes in Echidna
abstract contract vm {
    function prank(address) public virtual;
    function warp(uint256) public virtual;
}