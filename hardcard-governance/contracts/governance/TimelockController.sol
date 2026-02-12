// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/governance/TimelockController.sol";

contract HardcardTimelockController is TimelockController {
    uint256 public constant DEFAULT_DELAY = 48 hours;
    
    address public rootOwner;
    
    event EmergencyVeto(bytes32 indexed proposalId, address indexed vetoer);
    event RootOwnerTransferred(address indexed previousOwner, address indexed newOwner);
    
    modifier onlyRootOwner() {
        require(msg.sender == rootOwner, "TimelockController: caller is not root owner");
        _;
    }
    
    constructor(
        uint256 minDelay,
        address[] memory proposers,
        address[] memory executors,
        address admin,
        address _rootOwner
    ) TimelockController(minDelay, proposers, executors, admin) {
        require(_rootOwner != address(0), "TimelockController: root owner is zero address");
        rootOwner = _rootOwner;
    }
    
    function emergencyVeto(bytes32 id) external onlyRootOwner {
        require(isOperationPending(id), "TimelockController: operation is not pending");
        cancel(id);
        emit EmergencyVeto(id, msg.sender);
    }
    
    function transferRootOwnership(address newOwner) external onlyRootOwner {
        require(newOwner != address(0), "TimelockController: new owner is zero address");
        address previousOwner = rootOwner;
        rootOwner = newOwner;
        emit RootOwnerTransferred(previousOwner, newOwner);
    }
    
    function emergencyUpdateDelay(uint256 newDelay) external onlyRootOwner {
        require(newDelay >= DEFAULT_DELAY, "TimelockController: delay less than minimum");
        // Root owner can force delay update in emergency situations
        // This bypasses the normal timelock process
        emit MinDelayChange(getMinDelay(), newDelay);
        
        // We need to call updateDelay from the timelock address
        (bool success,) = address(this).call(
            abi.encodeWithSelector(TimelockController.updateDelay.selector, newDelay)
        );
        require(success, "TimelockController: emergency delay update failed");
    }
}