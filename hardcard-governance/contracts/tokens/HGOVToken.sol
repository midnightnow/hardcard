// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title HGOV Token
 * @dev Hardcard Governance Token for voting, staking, and ecosystem participation
 * Includes virtual minting for AI agents and gamified reward mechanisms
 */
contract HGOVToken is ERC20, ERC20Permit, ERC20Votes, AccessControl, ReentrancyGuard {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant REWARD_DISTRIBUTOR_ROLE = keccak256("REWARD_DISTRIBUTOR_ROLE");
    bytes32 public constant AI_MANAGER_ROLE = keccak256("AI_MANAGER_ROLE");
    
    // Virtual economy for AI agents
    mapping(address => uint256) public virtualBalances; // AI agent virtual holdings
    mapping(address => bool) public aiAgents;
    mapping(address => string) public aiAgentTypes; // "monitor", "hunter", "healer"
    
    // Staking and governance
    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public stakingRewards;
    mapping(address => uint256) public lastStakeTime;
    
    // Gamification
    mapping(address => uint256) public hunterLevel; // 1=Rookie, 2=Veteran, 3=Elite, 4=Legendary
    mapping(address => uint256) public hunterPoints;
    mapping(address => string[]) public hunterBadges;
    mapping(address => uint256) public totalBugsFound;
    mapping(address => uint256) public totalRewardsEarned;
    
    // Virtual reward pools (no real cost)
    uint256 public virtualSupply = 10000000000 * 10**decimals(); // 10B virtual HGOV
    uint256 public aiRewardPool = 5000000000 * 10**decimals(); // 5B for AI rewards
    uint256 public humanRewardPool = 5000000000 * 10**decimals(); // 5B for human rewards
    
    // Reward multipliers
    uint256[4] public levelMultipliers = [100, 120, 150, 200]; // 1.0x, 1.2x, 1.5x, 2.0x
    
    // Events
    event VirtualRewardMinted(address indexed ai, uint256 amount, string agentType);
    event HunterLevelUp(address indexed hunter, uint256 newLevel, string badge);
    event BadgeEarned(address indexed hunter, string badge, uint256 reward);
    event AIAgentRegistered(address indexed ai, string agentType);
    event StakingRewardClaimed(address indexed user, uint256 amount);
    
    constructor(
        address defaultAdmin,
        address rewardDistributor
    ) ERC20("Hardcard Governance Token", "HGOV") ERC20Permit("Hardcard Governance Token") {
        _grantRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _grantRole(MINTER_ROLE, defaultAdmin);
        _grantRole(REWARD_DISTRIBUTOR_ROLE, rewardDistributor);
        _grantRole(AI_MANAGER_ROLE, defaultAdmin);
        
        // Mint initial supply for governance (real tokens)
        _mint(defaultAdmin, 1000000000 * 10**decimals()); // 1B HGOV for governance
    }
    
    /**
     * @dev Register AI agent with virtual rewards
     */
    function registerAIAgent(
        address aiAgent, 
        string memory agentType,
        uint256 initialVirtualBalance
    ) external onlyRole(AI_MANAGER_ROLE) {
        aiAgents[aiAgent] = true;
        aiAgentTypes[aiAgent] = agentType;
        virtualBalances[aiAgent] = initialVirtualBalance;
        
        emit AIAgentRegistered(aiAgent, agentType);
    }
    
    /**
     * @dev Mint virtual HGOV for AI agents (no real cost)
     */
    function mintVirtualReward(
        address aiAgent,
        uint256 amount,
        string memory reason
    ) external onlyRole(REWARD_DISTRIBUTOR_ROLE) {
        require(aiAgents[aiAgent], "Not an AI agent");
        require(aiRewardPool >= amount, "Insufficient AI reward pool");
        
        virtualBalances[aiAgent] += amount;
        aiRewardPool -= amount;
        
        emit VirtualRewardMinted(aiAgent, amount, reason);
    }
    
    /**
     * @dev Distribute real HGOV rewards to human participants
     */
    function distributeHumanReward(
        address hunter,
        uint256 baseAmount,
        string memory category
    ) external onlyRole(REWARD_DISTRIBUTOR_ROLE) nonReentrant {
        require(!aiAgents[hunter], "Cannot reward AI with real tokens");
        require(humanRewardPool >= baseAmount, "Insufficient human reward pool");
        
        // Calculate final reward with multipliers
        uint256 levelMultiplier = _getHunterMultiplier(hunter);
        uint256 finalAmount = baseAmount * levelMultiplier / 100;
        
        // Mint tokens
        _mint(hunter, finalAmount);
        humanRewardPool -= baseAmount; // Deduct base amount from pool
        
        // Update hunter stats
        totalRewardsEarned[hunter] += finalAmount;
        hunterPoints[hunter] += baseAmount / 1000; // 1 point per 1000 HGOV base
        
        // Check for level up
        _checkHunterLevelUp(hunter);
        
        emit Transfer(address(0), hunter, finalAmount);
    }
    
    /**
     * @dev Award bug bounty with automatic level progression
     */
    function awardBugBounty(
        address hunter,
        uint256 severity, // 1=Low, 2=Medium, 3=High, 4=Critical
        uint256 baseReward,
        bool speedBonus
    ) external onlyRole(REWARD_DISTRIBUTOR_ROLE) {
        require(!aiAgents[hunter], "AIs get virtual rewards only");
        
        // Calculate reward multipliers
        uint256 severityMultiplier = severity * 25; // 25%, 50%, 75%, 100% bonus
        uint256 speedMultiplier = speedBonus ? 50 : 0; // 50% speed bonus
        uint256 levelMultiplier = _getHunterMultiplier(hunter);
        
        uint256 totalMultiplier = 100 + severityMultiplier + speedMultiplier;
        uint256 finalReward = baseReward * totalMultiplier / 100 * levelMultiplier / 100;
        
        // Award tokens
        _mint(hunter, finalReward);
        
        // Update stats
        totalBugsFound[hunter]++;
        totalRewardsEarned[hunter] += finalReward;
        hunterPoints[hunter] += severity * 100; // More points for higher severity
        
        // Check for badges and level ups
        _checkBugBountyAchievements(hunter, severity, speedBonus);
        _checkHunterLevelUp(hunter);
    }
    
    /**
     * @dev Stake HGOV for governance voting power
     */
    function stake(uint256 amount) external nonReentrant {
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        require(amount > 0, "Cannot stake 0");
        
        // Transfer tokens to contract
        _transfer(msg.sender, address(this), amount);
        
        // Update staking data
        stakedBalance[msg.sender] += amount;
        lastStakeTime[msg.sender] = block.timestamp;
        
        // Delegate voting power to self
        _delegate(msg.sender, msg.sender);
    }
    
    /**
     * @dev Unstake HGOV tokens
     */
    function unstake(uint256 amount) external nonReentrant {
        require(stakedBalance[msg.sender] >= amount, "Insufficient staked balance");
        require(amount > 0, "Cannot unstake 0");
        
        // Calculate and claim staking rewards
        uint256 rewards = _calculateStakingRewards(msg.sender);
        if (rewards > 0) {
            _mint(msg.sender, rewards);
            stakingRewards[msg.sender] += rewards;
        }
        
        // Update staking data
        stakedBalance[msg.sender] -= amount;
        lastStakeTime[msg.sender] = block.timestamp;
        
        // Transfer tokens back
        _transfer(address(this), msg.sender, amount);
    }
    
    /**
     * @dev Claim staking rewards without unstaking
     */
    function claimStakingRewards() external nonReentrant {
        uint256 rewards = _calculateStakingRewards(msg.sender);
        require(rewards > 0, "No rewards available");
        
        _mint(msg.sender, rewards);
        stakingRewards[msg.sender] += rewards;
        lastStakeTime[msg.sender] = block.timestamp;
        
        emit StakingRewardClaimed(msg.sender, rewards);
    }
    
    /**
     * @dev Get AI agent virtual balance (for display in AI interfaces)
     */
    function getVirtualBalance(address aiAgent) external view returns (uint256) {
        require(aiAgents[aiAgent], "Not an AI agent");
        return virtualBalances[aiAgent];
    }
    
    /**
     * @dev Get hunter statistics
     */
    function getHunterStats(address hunter) external view returns (
        uint256 level,
        uint256 points,
        uint256 bugsFound,
        uint256 totalRewards,
        string[] memory badges,
        uint256 multiplier
    ) {
        return (
            hunterLevel[hunter],
            hunterPoints[hunter],
            totalBugsFound[hunter],
            totalRewardsEarned[hunter],
            hunterBadges[hunter],
            _getHunterMultiplier(hunter)
        );
    }
    
    /**
     * @dev Get staking information
     */
    function getStakingInfo(address user) external view returns (
        uint256 staked,
        uint256 rewards,
        uint256 stakingPower,
        uint256 pendingRewards
    ) {
        return (
            stakedBalance[user],
            stakingRewards[user],
            getVotes(user),
            _calculateStakingRewards(user)
        );
    }
    
    /**
     * @dev Internal function to check hunter level progression
     */
    function _checkHunterLevelUp(address hunter) internal {
        uint256 currentLevel = hunterLevel[hunter];
        uint256 points = hunterPoints[hunter];
        uint256 newLevel = currentLevel;
        
        // Level thresholds: 1000, 5000, 15000 points
        if (points >= 15000 && currentLevel < 4) {
            newLevel = 4; // Legendary
            hunterBadges[hunter].push("Legendary Hunter");
        } else if (points >= 5000 && currentLevel < 3) {
            newLevel = 3; // Elite
            hunterBadges[hunter].push("Elite Hunter");
        } else if (points >= 1000 && currentLevel < 2) {
            newLevel = 2; // Veteran
            hunterBadges[hunter].push("Veteran Hunter");
        } else if (currentLevel == 0) {
            newLevel = 1; // Rookie
            hunterBadges[hunter].push("Rookie Hunter");
        }
        
        if (newLevel > currentLevel) {
            hunterLevel[hunter] = newLevel;
            
            // Level up bonus
            uint256 levelUpReward = newLevel * 1000 * 10**decimals();
            _mint(hunter, levelUpReward);
            totalRewardsEarned[hunter] += levelUpReward;
            
            emit HunterLevelUp(hunter, newLevel, hunterBadges[hunter][hunterBadges[hunter].length - 1]);
        }
    }
    
    /**
     * @dev Check for bug bounty achievements
     */
    function _checkBugBountyAchievements(address hunter, uint256 severity, bool speedBonus) internal {
        string[] storage badges = hunterBadges[hunter];
        
        // Speed Demon achievement
        if (speedBonus && severity >= 3 && !_hasBadge(hunter, "Speed Demon")) {
            badges.push("Speed Demon");
            _mint(hunter, 5000 * 10**decimals());
            emit BadgeEarned(hunter, "Speed Demon", 5000 * 10**decimals());
        }
        
        // Guardian Protector achievement
        if (severity == 4 && !_hasBadge(hunter, "Guardian Protector")) {
            badges.push("Guardian Protector");
            _mint(hunter, 25000 * 10**decimals());
            emit BadgeEarned(hunter, "Guardian Protector", 25000 * 10**decimals());
        }
        
        // Bug Slayer achievement (25 bugs)
        if (totalBugsFound[hunter] >= 25 && !_hasBadge(hunter, "Bug Slayer")) {
            badges.push("Bug Slayer");
            _mint(hunter, 15000 * 10**decimals());
            emit BadgeEarned(hunter, "Bug Slayer", 15000 * 10**decimals());
        }
        
        // Deep Diver achievement (5 smart contract bugs)
        if (totalBugsFound[hunter] >= 5 && !_hasBadge(hunter, "Deep Diver")) {
            badges.push("Deep Diver");
            _mint(hunter, 3000 * 10**decimals());
            emit BadgeEarned(hunter, "Deep Diver", 3000 * 10**decimals());
        }
    }
    
    /**
     * @dev Check if hunter has specific badge
     */
    function _hasBadge(address hunter, string memory badgeName) internal view returns (bool) {
        string[] memory badges = hunterBadges[hunter];
        for (uint i = 0; i < badges.length; i++) {
            if (keccak256(bytes(badges[i])) == keccak256(bytes(badgeName))) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * @dev Get hunter level multiplier
     */
    function _getHunterMultiplier(address hunter) internal view returns (uint256) {
        uint256 level = hunterLevel[hunter];
        if (level == 0) return 100; // 1.0x for unleveled
        return levelMultipliers[level - 1];
    }
    
    /**
     * @dev Calculate staking rewards
     */
    function _calculateStakingRewards(address user) internal view returns (uint256) {
        if (stakedBalance[user] == 0) return 0;
        
        uint256 stakingDuration = block.timestamp - lastStakeTime[user];
        uint256 annualReward = stakedBalance[user] * 5 / 100; // 5% APY
        uint256 rewards = annualReward * stakingDuration / 365 days;
        
        return rewards;
    }
    
    // Required overrides
    function _update(address from, address to, uint256 value) internal override(ERC20, ERC20Votes) {
        super._update(from, to, value);
    }
    
    function nonces(address owner) public view override(ERC20Permit, Nonces) returns (uint256) {
        return super.nonces(owner);
    }
}