// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

interface IFreezable {
    function freezeUntil(uint256 timestamp) external;
    function unfreeze() external;
}

contract GuardianCouncil is AccessControl {
    using EnumerableSet for EnumerableSet.AddressSet;

    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");
    bytes32 public constant ROOT_OWNER_ROLE = keccak256("ROOT_OWNER_ROLE");
    
    uint256 public constant FREEZE_SECONDS = 7 days;
    uint256 public immutable threshold;
    uint256 public immutable maxGuardians;
    
    EnumerableSet.AddressSet private guardians;
    
    mapping(bytes32 => uint256) public proposalVotes;
    mapping(bytes32 => mapping(address => bool)) public hasVoted;
    mapping(address => uint256) public frozenUntil;
    
    event ContractFrozen(address indexed target, uint256 until);
    event ContractUnfrozen(address indexed target);
    event GuardianAdded(address indexed guardian);
    event GuardianRemoved(address indexed guardian);
    event ProposalCreated(bytes32 indexed proposalId, address proposer, string action);
    event ProposalExecuted(bytes32 indexed proposalId);
    event VoteCast(bytes32 indexed proposalId, address indexed voter);
    
    modifier onlyGuardian() {
        require(hasRole(GUARDIAN_ROLE, msg.sender), "GuardianCouncil: caller is not a guardian");
        _;
    }
    
    modifier onlyRootOwner() {
        require(hasRole(ROOT_OWNER_ROLE, msg.sender), "GuardianCouncil: caller is not root owner");
        _;
    }
    
    constructor(uint256 _threshold, uint256 _maxGuardians, address _rootOwner) {
        require(_threshold > 0 && _threshold <= _maxGuardians, "GuardianCouncil: invalid threshold");
        require(_maxGuardians > 0, "GuardianCouncil: invalid max guardians");
        
        threshold = _threshold;
        maxGuardians = _maxGuardians;
        
        _grantRole(DEFAULT_ADMIN_ROLE, _rootOwner);
        _grantRole(ROOT_OWNER_ROLE, _rootOwner);
    }
    
    function freeze(address _target) external onlyGuardian {
        bytes32 proposalId = keccak256(abi.encodePacked("freeze", _target));
        
        if (!hasVoted[proposalId][msg.sender]) {
            hasVoted[proposalId][msg.sender] = true;
            proposalVotes[proposalId]++;
            emit VoteCast(proposalId, msg.sender);
            
            if (proposalVotes[proposalId] == 1) {
                emit ProposalCreated(proposalId, msg.sender, "freeze");
            }
        }
        
        if (proposalVotes[proposalId] >= threshold) {
            uint256 freezeUntil = block.timestamp + FREEZE_SECONDS;
            frozenUntil[_target] = freezeUntil;
            
            try IFreezable(_target).freezeUntil(freezeUntil) {} catch {}
            
            emit ContractFrozen(_target, freezeUntil);
            emit ProposalExecuted(proposalId);
            
            // Clean up votes for this proposal
            _cleanupProposal(proposalId);
        }
    }
    
    function unfreeze(address _target) external onlyGuardian {
        bytes32 proposalId = keccak256(abi.encodePacked("unfreeze", _target));
        
        if (!hasVoted[proposalId][msg.sender]) {
            hasVoted[proposalId][msg.sender] = true;
            proposalVotes[proposalId]++;
            emit VoteCast(proposalId, msg.sender);
            
            if (proposalVotes[proposalId] == 1) {
                emit ProposalCreated(proposalId, msg.sender, "unfreeze");
            }
        }
        
        if (proposalVotes[proposalId] >= threshold) {
            frozenUntil[_target] = 0;
            
            try IFreezable(_target).unfreeze() {} catch {}
            
            emit ContractUnfrozen(_target);
            emit ProposalExecuted(proposalId);
            
            // Clean up votes for this proposal
            _cleanupProposal(proposalId);
        }
    }
    
    function rotateGuardian(address oldGuardian, address newGuardian) external onlyRootOwner {
        require(hasRole(GUARDIAN_ROLE, oldGuardian), "GuardianCouncil: old address is not a guardian");
        require(!hasRole(GUARDIAN_ROLE, newGuardian), "GuardianCouncil: new address is already a guardian");
        require(newGuardian != address(0), "GuardianCouncil: new guardian is zero address");
        
        _revokeRole(GUARDIAN_ROLE, oldGuardian);
        guardians.remove(oldGuardian);
        emit GuardianRemoved(oldGuardian);
        
        _grantRole(GUARDIAN_ROLE, newGuardian);
        guardians.add(newGuardian);
        emit GuardianAdded(newGuardian);
    }
    
    function addGuardian(address guardian) external onlyRootOwner {
        require(!hasRole(GUARDIAN_ROLE, guardian), "GuardianCouncil: address is already a guardian");
        require(guardian != address(0), "GuardianCouncil: guardian is zero address");
        require(guardians.length() < maxGuardians, "GuardianCouncil: max guardians reached");
        
        _grantRole(GUARDIAN_ROLE, guardian);
        guardians.add(guardian);
        emit GuardianAdded(guardian);
    }
    
    function removeGuardian(address guardian) external onlyRootOwner {
        require(hasRole(GUARDIAN_ROLE, guardian), "GuardianCouncil: address is not a guardian");
        require(guardians.length() > threshold, "GuardianCouncil: cannot go below threshold");
        
        _revokeRole(GUARDIAN_ROLE, guardian);
        guardians.remove(guardian);
        emit GuardianRemoved(guardian);
    }
    
    function getGuardians() external view returns (address[] memory) {
        return guardians.values();
    }
    
    function getGuardianCount() external view returns (uint256) {
        return guardians.length();
    }
    
    function isGuardian(address account) external view returns (bool) {
        return hasRole(GUARDIAN_ROLE, account);
    }
    
    function isFrozen(address target) external view returns (bool) {
        return frozenUntil[target] > block.timestamp;
    }
    
    function _cleanupProposal(bytes32 proposalId) private {
        delete proposalVotes[proposalId];
        // Note: we don't clean up hasVoted to prevent double voting on the same proposal
    }
}