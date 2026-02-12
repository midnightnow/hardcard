// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

contract CredentialRegistry is Ownable, Pausable {
    mapping(bytes32 => bool) public credentials;
    mapping(address => bool) public issuers;
    
    uint256 public freezeUntilTimestamp;
    
    event CredentialIssued(bytes32 indexed credentialId, address indexed issuer);
    event CredentialRevoked(bytes32 indexed credentialId, address indexed revoker);
    event IssuerAdded(address indexed issuer);
    event IssuerRemoved(address indexed issuer);
    
    modifier notFrozen() {
        require(block.timestamp >= freezeUntilTimestamp, "CredentialRegistry: contract is frozen");
        _;
    }
    
    modifier onlyIssuer() {
        require(issuers[msg.sender], "CredentialRegistry: caller is not an issuer");
        _;
    }
    
    constructor(address initialOwner) Ownable(initialOwner) {}
    
    function freezeUntil(uint256 timestamp) external onlyOwner {
        freezeUntilTimestamp = timestamp;
    }
    
    function unfreeze() external onlyOwner {
        freezeUntilTimestamp = 0;
    }
    
    function addIssuer(address issuer) external onlyOwner notFrozen {
        issuers[issuer] = true;
        emit IssuerAdded(issuer);
    }
    
    function removeIssuer(address issuer) external onlyOwner notFrozen {
        issuers[issuer] = false;
        emit IssuerRemoved(issuer);
    }
    
    function issueCredential(bytes32 credentialId) external onlyIssuer notFrozen whenNotPaused {
        require(!credentials[credentialId], "CredentialRegistry: credential already exists");
        credentials[credentialId] = true;
        emit CredentialIssued(credentialId, msg.sender);
    }
    
    function revokeCredential(bytes32 credentialId) external onlyIssuer notFrozen {
        require(credentials[credentialId], "CredentialRegistry: credential does not exist");
        credentials[credentialId] = false;
        emit CredentialRevoked(credentialId, msg.sender);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
}