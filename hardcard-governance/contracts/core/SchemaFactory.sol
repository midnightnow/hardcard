// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/access/Ownable.sol";

contract SchemaFactory is Ownable {
    struct Schema {
        string name;
        string uri;
        address creator;
        bool active;
    }
    
    mapping(bytes32 => Schema) public schemas;
    uint256 public schemaCount;
    uint256 public freezeUntilTimestamp;
    
    event SchemaCreated(bytes32 indexed schemaId, string name, address indexed creator);
    event SchemaDeactivated(bytes32 indexed schemaId);
    event SchemaReactivated(bytes32 indexed schemaId);
    
    modifier notFrozen() {
        require(block.timestamp >= freezeUntilTimestamp, "SchemaFactory: contract is frozen");
        _;
    }
    
    constructor(address initialOwner) Ownable(initialOwner) {}
    
    function freezeUntil(uint256 timestamp) external onlyOwner {
        freezeUntilTimestamp = timestamp;
    }
    
    function unfreeze() external onlyOwner {
        freezeUntilTimestamp = 0;
    }
    
    function createSchema(string memory name, string memory uri) external notFrozen returns (bytes32) {
        bytes32 schemaId = keccak256(abi.encodePacked(name, uri, block.timestamp, msg.sender));
        require(schemas[schemaId].creator == address(0), "SchemaFactory: schema already exists");
        
        schemas[schemaId] = Schema({
            name: name,
            uri: uri,
            creator: msg.sender,
            active: true
        });
        
        schemaCount++;
        emit SchemaCreated(schemaId, name, msg.sender);
        
        return schemaId;
    }
    
    function deactivateSchema(bytes32 schemaId) external onlyOwner notFrozen {
        require(schemas[schemaId].creator != address(0), "SchemaFactory: schema does not exist");
        require(schemas[schemaId].active, "SchemaFactory: schema already inactive");
        
        schemas[schemaId].active = false;
        emit SchemaDeactivated(schemaId);
    }
    
    function reactivateSchema(bytes32 schemaId) external onlyOwner notFrozen {
        require(schemas[schemaId].creator != address(0), "SchemaFactory: schema does not exist");
        require(!schemas[schemaId].active, "SchemaFactory: schema already active");
        
        schemas[schemaId].active = true;
        emit SchemaReactivated(schemaId);
    }
}