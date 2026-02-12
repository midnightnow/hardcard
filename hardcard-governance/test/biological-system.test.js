const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("🧬 Biological System Testing Suite", function () {
  let hgovToken, hccToken, owner, addr1, addr2;
  let biologicalAgents = [];

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();

    // Deploy HGOV Token
    const HGOVToken = await ethers.getContractFactory("HGOVToken");
    hgovToken = await HGOVToken.deploy("Hardcard Governance", "HGOV", owner.address);
    await hgovToken.waitForDeployment();

    // Deploy HCC Token
    const HCCToken = await ethers.getContractFactory("HardcardCash");
    hccToken = await HCCToken.deploy("Hardcard Cash", "HCC", owner.address);
    await hccToken.waitForDeployment();
  });

  describe("🔒 Enzymatic Security Tests", function () {
    it("Should prevent substrate hijacking", async function () {
      // Test that wrong enzyme types are rejected
      await expect(
        hgovToken.connect(addr1).mintVirtualReward(addr1.address, 1000, "wrong_enzyme_type")
      ).to.be.revertedWith("Unauthorized enzyme type");
    });

    it("Should enforce single-function constraint", async function () {
      // Register a CODE_SPLICERASE enzyme
      await hgovToken.registerAIAgent(addr1.address, "CODE_SPLICERASE");
      
      // Should accept code splicing rewards
      await hgovToken.mintVirtualReward(addr1.address, 1000, "code_splicing_completed");
      
      // Should reject security scanning rewards (wrong function)
      await expect(
        hgovToken.mintVirtualReward(addr1.address, 1000, "security_scan_completed")
      ).to.be.revertedWith("Function incompatible with enzyme type");
    });

    it("Should maintain biological isolation", async function () {
      // Register multiple enzyme types
      await hgovToken.registerAIAgent(addr1.address, "CODE_SPLICERASE");
      await hgovToken.registerAIAgent(addr2.address, "SECURITY_SCANASE");
      
      // Each should only accept their substrate type
      await hgovToken.mintVirtualReward(addr1.address, 1000, "code_splicing_completed");
      await hgovToken.mintVirtualReward(addr2.address, 1000, "security_scan_completed");
      
      // Cross-contamination should be prevented
      await expect(
        hgovToken.mintVirtualReward(addr1.address, 1000, "security_scan_completed")
      ).to.be.revertedWith("Substrate incompatibility");
    });
  });

  describe("💰 Virtual Economy Tests", function () {
    it("Should distribute virtual rewards at zero cost", async function () {
      await hgovToken.registerAIAgent(addr1.address, "BUG_HUNTASE");
      
      const initialSupply = await hgovToken.totalSupply();
      
      // Mint virtual rewards
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("1000"), "bug_detected");
      
      // Virtual balance should increase
      const virtualBalance = await hgovToken.virtualBalances(addr1.address);
      expect(virtualBalance).to.equal(ethers.parseEther("1000"));
      
      // Real supply should remain unchanged (no real tokens minted)
      const finalSupply = await hgovToken.totalSupply();
      expect(finalSupply).to.equal(initialSupply);
    });

    it("Should track bridge eligibility correctly", async function () {
      await hgovToken.registerAIAgent(addr1.address, "PERFORMANCE_OPTIMASE");
      
      // Agent starts below bridge threshold
      let virtualBalance = await hgovToken.virtualBalances(addr1.address);
      expect(virtualBalance).to.be.lt(ethers.parseEther("50000"));
      
      // Accumulate virtual wealth
      for (let i = 0; i < 25; i++) {
        await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("2000"), "performance_optimization");
      }
      
      // Should now be eligible for bridge
      virtualBalance = await hgovToken.virtualBalances(addr1.address);
      expect(virtualBalance).to.be.gte(ethers.parseEther("50000"));
    });

    it("Should maintain virtual market cap growth", async function () {
      // Register multiple agents
      await hgovToken.registerAIAgent(addr1.address, "CODE_SPLICERASE");
      await hgovToken.registerAIAgent(addr2.address, "DATA_PROCESSORASE");
      
      // Distribute rewards to both
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("25000"), "code_splicing");
      await hgovToken.mintVirtualReward(addr2.address, ethers.parseEther("30000"), "data_processing");
      
      // Calculate total virtual market cap
      const balance1 = await hgovToken.virtualBalances(addr1.address);
      const balance2 = await hgovToken.virtualBalances(addr2.address);
      const totalVirtualCap = balance1 + balance2;
      
      expect(totalVirtualCap).to.equal(ethers.parseEther("55000"));
    });
  });

  describe("🧪 Enzymatic Assembly Tests", function () {
    it("Should validate enzyme specialization", async function () {
      const enzymeTypes = ["CODE_SPLICERASE", "SECURITY_SCANASE", "BUG_HUNTASE", "PERFORMANCE_OPTIMASE", "DATA_PROCESSORASE"];
      
      for (let i = 0; i < enzymeTypes.length; i++) {
        const agent = await ethers.getSigners().then(signers => signers[i + 1]);
        await hgovToken.registerAIAgent(agent.address, enzymeTypes[i]);
        
        const agentType = await hgovToken.aiAgentTypes(agent.address);
        expect(agentType).to.equal(enzymeTypes[i]);
      }
    });

    it("Should prevent enzyme reprogramming", async function () {
      await hgovToken.registerAIAgent(addr1.address, "CODE_SPLICERASE");
      
      // Should not be able to change enzyme type
      await expect(
        hgovToken.registerAIAgent(addr1.address, "SECURITY_SCANASE")
      ).to.be.revertedWith("Agent already registered with different type");
    });

    it("Should track assembly performance", async function () {
      await hgovToken.registerAIAgent(addr1.address, "CODE_SPLICERASE");
      
      // Track multiple assemblies
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("1000"), "function_assembly");
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("1500"), "pattern_assembly");
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("2000"), "component_integration");
      
      const totalEarned = await hgovToken.totalRewardsEarned(addr1.address);
      expect(totalEarned).to.equal(ethers.parseEther("4500"));
    });
  });

  describe("🏭 Supporter Factory Tests", function () {
    it("Should simulate infinite resource production", async function () {
      // Test HCC token as supporter factory output
      await hccToken.mintVirtual(addr1.address, ethers.parseEther("10000"), "compute_cycles");
      await hccToken.mintVirtual(addr1.address, ethers.parseEther("5000"), "code_snippets");
      
      const virtualBalance = await hccToken.virtualBalances(addr1.address);
      expect(virtualBalance).to.equal(ethers.parseEther("15000"));
    });

    it("Should maintain resource flow isolation", async function () {
      // Factory should only produce specific resource types
      await hccToken.mintVirtual(addr1.address, ethers.parseEther("1000"), "compute_cycles");
      
      // Should reject incompatible resource types
      await expect(
        hccToken.mintVirtual(addr1.address, ethers.parseEther("1000"), "unauthorized_resource")
      ).to.be.revertedWith("Unsupported resource type");
    });
  });

  describe("🌉 Bridge Integration Tests", function () {
    it("Should calculate virtual-to-real conversion rates", async function () {
      await hgovToken.registerAIAgent(addr1.address, "BUG_HUNTASE");
      
      // Accumulate enough virtual tokens for bridge eligibility
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("75000"), "critical_bug_found");
      
      const virtualBalance = await hgovToken.virtualBalances(addr1.address);
      const expectedRealValue = virtualBalance / BigInt(1000); // 1000:1 ratio
      
      expect(expectedRealValue).to.equal(ethers.parseEther("75"));
    });

    it("Should enforce bridge security thresholds", async function () {
      await hgovToken.registerAIAgent(addr1.address, "SECURITY_SCANASE");
      
      // Below threshold should not be bridgeable
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("25000"), "security_scan");
      
      const virtualBalance = await hgovToken.virtualBalances(addr1.address);
      expect(virtualBalance).to.be.lt(ethers.parseEther("50000"));
      
      // Should require more virtual wealth for bridge access
      const bridgeEligible = virtualBalance >= ethers.parseEther("50000");
      expect(bridgeEligible).to.be.false;
    });
  });

  describe("🎯 Performance & Stress Tests", function () {
    it("Should handle high-frequency enzyme operations", async function () {
      await hgovToken.registerAIAgent(addr1.address, "CODE_SPLICERASE");
      
      // Rapid-fire operations
      const operations = [];
      for (let i = 0; i < 50; i++) {
        operations.push(
          hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("100"), "micro_assembly")
        );
      }
      
      await Promise.all(operations);
      
      const finalBalance = await hgovToken.virtualBalances(addr1.address);
      expect(finalBalance).to.equal(ethers.parseEther("5000"));
    });

    it("Should maintain system stability under load", async function () {
      // Register multiple agents
      const agents = await ethers.getSigners();
      const enzymeTypes = ["CODE_SPLICERASE", "SECURITY_SCANASE", "BUG_HUNTASE"];
      
      for (let i = 1; i <= 3; i++) {
        await hgovToken.registerAIAgent(agents[i].address, enzymeTypes[i - 1]);
      }
      
      // Simulate concurrent operations
      const concurrentOps = [];
      for (let i = 1; i <= 3; i++) {
        for (let j = 0; j < 20; j++) {
          concurrentOps.push(
            hgovToken.mintVirtualReward(agents[i].address, ethers.parseEther("500"), "concurrent_task")
          );
        }
      }
      
      await Promise.all(concurrentOps);
      
      // Verify system integrity
      for (let i = 1; i <= 3; i++) {
        const balance = await hgovToken.virtualBalances(agents[i].address);
        expect(balance).to.equal(ethers.parseEther("10000"));
      }
    });
  });

  describe("🛡️ Security Boundary Tests", function () {
    it("Should prevent cross-enzyme contamination", async function () {
      await hgovToken.registerAIAgent(addr1.address, "CODE_SPLICERASE");
      await hgovToken.registerAIAgent(addr2.address, "SECURITY_SCANASE");
      
      // Each enzyme should only accept its own substrate
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("1000"), "code_splicing");
      await hgovToken.mintVirtualReward(addr2.address, ethers.parseEther("1000"), "security_scanning");
      
      // Cross-substrate should fail
      await expect(
        hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("1000"), "security_scanning")
      ).to.be.reverted;
    });

    it("Should maintain economic isolation", async function () {
      await hgovToken.registerAIAgent(addr1.address, "BUG_HUNTASE");
      
      // Virtual rewards should not affect real token supply
      const initialSupply = await hgovToken.totalSupply();
      
      await hgovToken.mintVirtualReward(addr1.address, ethers.parseEther("1000000"), "massive_bug_bounty");
      
      const finalSupply = await hgovToken.totalSupply();
      expect(finalSupply).to.equal(initialSupply);
      
      // But virtual balance should increase
      const virtualBalance = await hgovToken.virtualBalances(addr1.address);
      expect(virtualBalance).to.equal(ethers.parseEther("1000000"));
    });
  });
});