// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title HardcardCash (HCC)
 * @dev Virtual stablecoin for the Hardcard ecosystem
 * Provides stable value for bug bounty rewards, governance incentives, and ecosystem transactions
 */
contract HardcardCash is ERC20, ERC20Permit, ERC20Votes, AccessControl, ReentrancyGuard {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant REWARD_DISTRIBUTOR_ROLE = keccak256("REWARD_DISTRIBUTOR_ROLE");
    
    // Stability mechanism
    uint256 public constant TARGET_PRICE = 1e18; // $1.00 in 18 decimals
    uint256 public priceOracle;
    uint256 public stabilityFee = 50; // 0.5% fee for stability operations
    
    // Reward pools
    mapping(string => uint256) public rewardPools; // "bug_bounty", "uptime_rewards", etc.
    mapping(address => uint256) public earnedRewards;
    mapping(address => bool) public aiAgents;
    
    // Virtual economy parameters
    uint256 public virtualSupply; // Tracks virtual supply for AI rewards
    uint256 public realSupply;    // Tracks actual circulating supply
    bool public virtualMode = true; // Enable virtual rewards for AIs
    
    // Events
    event RewardDistributed(address indexed recipient, uint256 amount, string category);
    event PoolFunded(string indexed pool, uint256 amount);
    event VirtualRewardClaimed(address indexed ai, uint256 amount);
    event StabilityOperation(uint256 oldPrice, uint256 newPrice, uint256 adjustment);
    
    constructor(
        address defaultAdmin,
        address rewardDistributor
    ) ERC20("Hardcard Cash", "HCC") ERC20Permit("Hardcard Cash") {
        _grantRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _grantRole(MINTER_ROLE, defaultAdmin);
        _grantRole(REWARD_DISTRIBUTOR_ROLE, rewardDistributor);
        
        // Initialize with virtual supply for AI rewards
        virtualSupply = 1000000000 * 10**decimals(); // 1B virtual HCC
        priceOracle = TARGET_PRICE;
        
        // Fund initial reward pools (virtual)
        rewardPools["bug_bounty"] = 600000000 * 10**decimals(); // 600M HCC
        rewardPools["uptime_rewards"] = 200000000 * 10**decimals(); // 200M HCC
        rewardPools["seasonal_events"] = 100000000 * 10**decimals(); // 100M HCC
        rewardPools["community_programs"] = 50000000 * 10**decimals(); // 50M HCC
        rewardPools["emergency_response"] = 50000000 * 10**decimals(); // 50M HCC
    }
    
    /**
     * @dev Distribute rewards to bug hunters and AI agents
     */
    function distributeReward(
        address recipient,
        uint256 amount,
        string memory category
    ) external onlyRole(REWARD_DISTRIBUTOR_ROLE) nonReentrant {
        require(rewardPools[category] >= amount, "Insufficient pool balance");
        
        if (aiAgents[recipient] && virtualMode) {
            // Virtual reward for AI agents
            earnedRewards[recipient] += amount;
            rewardPools[category] -= amount;
            
            emit VirtualRewardClaimed(recipient, amount);
        } else {
            // Real minting for human participants
            require(amount <= 500000 * 10**decimals(), "Max reward exceeded"); // 500K HCC max
            
            _mint(recipient, amount);
            rewardPools[category] -= amount;
            realSupply += amount;
            
            emit RewardDistributed(recipient, amount, category);
        }
    }
    
    /**
     * @dev Batch distribute rewards for efficiency
     */
    function batchDistributeRewards(
        address[] calldata recipients,
        uint256[] calldata amounts,
        string[] calldata categories
    ) external onlyRole(REWARD_DISTRIBUTOR_ROLE) {
        require(recipients.length == amounts.length && amounts.length == categories.length, "Array length mismatch");
        
        for (uint i = 0; i < recipients.length; i++) {
            if (amounts[i] > 0) {
                distributeReward(recipients[i], amounts[i], categories[i]);
            }
        }
    }
    
    /**
     * @dev Register an AI agent for virtual rewards
     */
    function registerAIAgent(address aiAgent) external onlyRole(DEFAULT_ADMIN_ROLE) {
        aiAgents[aiAgent] = true;
    }
    
    /**
     * @dev AI agents can claim their virtual rewards (for display purposes)
     */
    function claimVirtualRewards() external view returns (uint256) {
        require(aiAgents[msg.sender], "Not an AI agent");
        return earnedRewards[msg.sender];
    }
    
    /**
     * @dev Fund reward pools (emergency top-up)
     */
    function fundPool(string memory poolName, uint256 amount) external onlyRole(MINTER_ROLE) {
        rewardPools[poolName] += amount;
        virtualSupply += amount;
        
        emit PoolFunded(poolName, amount);
    }
    
    /**
     * @dev Stability mechanism - adjust price oracle
     */
    function updatePriceOracle(uint256 newPrice) external onlyRole(DEFAULT_ADMIN_ROLE) {
        uint256 oldPrice = priceOracle;
        priceOracle = newPrice;
        
        // Auto-adjust if price deviates more than 5%
        if (newPrice > TARGET_PRICE * 105 / 100 || newPrice < TARGET_PRICE * 95 / 100) {
            _performStabilityOperation(oldPrice, newPrice);
        }
        
        emit StabilityOperation(oldPrice, newPrice, 0);
    }
    
    /**
     * @dev Internal stability operation
     */
    function _performStabilityOperation(uint256 oldPrice, uint256 newPrice) internal {
        // Simplified stability mechanism
        // In practice, this would interact with AMMs, burn/mint tokens, etc.
        uint256 adjustment = 0;
        
        if (newPrice > TARGET_PRICE) {
            // Price too high - increase supply (virtual)
            adjustment = (newPrice - TARGET_PRICE) * virtualSupply / TARGET_PRICE / 10;
            virtualSupply += adjustment;
        } else {
            // Price too low - decrease supply (virtual)
            adjustment = (TARGET_PRICE - newPrice) * virtualSupply / TARGET_PRICE / 10;
            if (virtualSupply > adjustment) {
                virtualSupply -= adjustment;
            }
        }
    }
    
    /**
     * @dev Get total virtual market cap
     */
    function getVirtualMarketCap() external view returns (uint256) {
        return virtualSupply * priceOracle / 10**decimals();
    }
    
    /**
     * @dev Get pool balances
     */
    function getPoolBalance(string memory poolName) external view returns (uint256) {
        return rewardPools[poolName];
    }
    
    /**
     * @dev Get all pool balances
     */
    function getAllPoolBalances() external view returns (
        uint256 bugBounty,
        uint256 uptimeRewards,
        uint256 seasonalEvents,
        uint256 communityPrograms,
        uint256 emergencyResponse
    ) {
        return (
            rewardPools["bug_bounty"],
            rewardPools["uptime_rewards"],
            rewardPools["seasonal_events"],
            rewardPools["community_programs"],
            rewardPools["emergency_response"]
        );
    }
    
    /**
     * @dev Calculate reward in USD equivalent
     */
    function calculateUSDReward(uint256 hccAmount) external view returns (uint256) {
        return hccAmount * priceOracle / 10**decimals();
    }
    
    /**
     * @dev Emergency mint for critical situations
     */
    function emergencyMint(address to, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(amount <= 1000000 * 10**decimals(), "Emergency mint limit exceeded");
        _mint(to, amount);
        realSupply += amount;
    }
    
    /**
     * @dev Burn tokens to reduce supply
     */
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
        if (realSupply >= amount) {
            realSupply -= amount;
        }
    }
    
    /**
     * @dev Get reward statistics
     */
    function getRewardStats(address user) external view returns (
        uint256 totalEarned,
        uint256 currentBalance,
        bool isAIAgent,
        uint256 virtualEarnings
    ) {
        return (
            earnedRewards[user],
            balanceOf(user),
            aiAgents[user],
            aiAgents[user] ? earnedRewards[user] : 0
        );
    }
    
    // Required overrides
    function _update(address from, address to, uint256 value) internal override(ERC20, ERC20Votes) {
        super._update(from, to, value);
    }
    
    function nonces(address owner) public view override(ERC20Permit, Nonces) returns (uint256) {
        return super.nonces(owner);
    }
}