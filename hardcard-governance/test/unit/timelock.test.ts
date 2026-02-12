import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";
import { time } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("TimelockController", function () {
  async function deployTimelockFixture() {
    const [rootOwner, proposer, executor, other] = await ethers.getSigners();
    
    const MIN_DELAY = 48 * 60 * 60; // 48 hours
    
    const TimelockController = await ethers.getContractFactory("HardcardTimelockController");
    const timelock = await TimelockController.deploy(
      MIN_DELAY,
      [proposer.address],
      [executor.address],
      ethers.ZeroAddress,
      rootOwner.address
    );
    
    // Deploy a target contract
    const CredentialRegistry = await ethers.getContractFactory("CredentialRegistry");
    const credentialRegistry = await CredentialRegistry.deploy(await timelock.getAddress());
    
    return { timelock, credentialRegistry, rootOwner, proposer, executor, other, MIN_DELAY };
  }
  
  describe("Deployment", function () {
    it("Should set the correct minimum delay", async function () {
      const { timelock, MIN_DELAY } = await loadFixture(deployTimelockFixture);
      
      expect(await timelock.getMinDelay()).to.equal(MIN_DELAY);
    });
    
    it("Should set the root owner", async function () {
      const { timelock, rootOwner } = await loadFixture(deployTimelockFixture);
      
      expect(await timelock.rootOwner()).to.equal(rootOwner.address);
    });
  });
  
  describe("Proposal Lifecycle", function () {
    it("Should enforce minimum delay on operations", async function () {
      const { timelock, credentialRegistry, proposer, executor } = await loadFixture(deployTimelockFixture);
      
      const target = await credentialRegistry.getAddress();
      const value = 0;
      const data = credentialRegistry.interface.encodeFunctionData("pause");
      const predecessor = ethers.ZeroHash;
      const salt = ethers.randomBytes(32);
      
      // Schedule operation
      await timelock.connect(proposer).schedule(
        target,
        value,
        data,
        predecessor,
        salt,
        48 * 60 * 60
      );
      
      const id = await timelock.hashOperation(target, value, data, predecessor, salt);
      
      // Try to execute immediately (should fail)
      await expect(
        timelock.connect(executor).execute(target, value, data, predecessor, salt)
      ).to.be.revertedWith("TimelockController: operation is not ready");
      
      // Fast forward time
      await time.increase(48 * 60 * 60);
      
      // Now execution should succeed
      await expect(
        timelock.connect(executor).execute(target, value, data, predecessor, salt)
      ).to.not.be.reverted;
      
      // Verify the operation was executed
      expect(await credentialRegistry.paused()).to.be.true;
    });
  });
  
  describe("Root Owner Veto", function () {
    it("Should allow root owner to veto pending operations", async function () {
      const { timelock, credentialRegistry, rootOwner, proposer } = await loadFixture(deployTimelockFixture);
      
      const target = await credentialRegistry.getAddress();
      const value = 0;
      const data = credentialRegistry.interface.encodeFunctionData("pause");
      const predecessor = ethers.ZeroHash;
      const salt = ethers.randomBytes(32);
      
      // Schedule operation
      await timelock.connect(proposer).schedule(
        target,
        value,
        data,
        predecessor,
        salt,
        48 * 60 * 60
      );
      
      const id = await timelock.hashOperation(target, value, data, predecessor, salt);
      
      // Verify operation is pending
      expect(await timelock.isOperationPending(id)).to.be.true;
      
      // Root owner vetoes
      await expect(timelock.connect(rootOwner).emergencyVeto(id))
        .to.emit(timelock, "EmergencyVeto")
        .withArgs(id, rootOwner.address);
      
      // Operation should no longer be pending
      expect(await timelock.isOperationPending(id)).to.be.false;
    });
    
    it("Should not allow non-root owner to veto", async function () {
      const { timelock, credentialRegistry, proposer, other } = await loadFixture(deployTimelockFixture);
      
      const target = await credentialRegistry.getAddress();
      const value = 0;
      const data = credentialRegistry.interface.encodeFunctionData("pause");
      const predecessor = ethers.ZeroHash;
      const salt = ethers.randomBytes(32);
      
      await timelock.connect(proposer).schedule(
        target,
        value,
        data,
        predecessor,
        salt,
        48 * 60 * 60
      );
      
      const id = await timelock.hashOperation(target, value, data, predecessor, salt);
      
      await expect(timelock.connect(other).emergencyVeto(id))
        .to.be.revertedWith("TimelockController: caller is not root owner");
    });
  });
  
  describe("Delay Updates", function () {
    it("Should enforce minimum delay when updating delay", async function () {
      const { timelock, rootOwner } = await loadFixture(deployTimelockFixture);
      const DEFAULT_DELAY = 48 * 60 * 60;
      
      // Try to set delay below minimum
      await expect(timelock.connect(rootOwner).updateDelay(24 * 60 * 60))
        .to.be.revertedWith("TimelockController: delay less than minimum");
      
      // Setting delay at or above minimum should work
      await expect(timelock.connect(rootOwner).updateDelay(72 * 60 * 60))
        .to.not.be.reverted;
      
      expect(await timelock.getMinDelay()).to.equal(72 * 60 * 60);
    });
  });
  
  describe("Root Owner Transfer", function () {
    it("Should allow root owner to transfer ownership", async function () {
      const { timelock, rootOwner, other } = await loadFixture(deployTimelockFixture);
      
      await expect(timelock.connect(rootOwner).transferRootOwnership(other.address))
        .to.emit(timelock, "RootOwnerTransferred")
        .withArgs(rootOwner.address, other.address);
      
      expect(await timelock.rootOwner()).to.equal(other.address);
    });
    
    it("Should not allow non-root owner to transfer", async function () {
      const { timelock, other } = await loadFixture(deployTimelockFixture);
      
      await expect(timelock.connect(other).transferRootOwnership(other.address))
        .to.be.revertedWith("TimelockController: caller is not root owner");
    });
  });
});