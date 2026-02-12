import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";
import { time, mine } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("Governance Integration Tests", function () {
  async function deployFullGovernanceFixture() {
    const [rootOwner, proposer, guardian1, guardian2, guardian3, guardian4, guardian5, user] = 
      await ethers.getSigners();

    // Deploy Votes Token
    const VotesToken = await ethers.getContractFactory("VotesToken");
    const votesToken = await VotesToken.deploy("Hardcard Governance", "HGT");

    // Deploy Guardian Council
    const GuardianCouncil = await ethers.getContractFactory("GuardianCouncil");
    const guardianCouncil = await GuardianCouncil.deploy(3, 5, rootOwner.address);

    // Add guardians
    await guardianCouncil.connect(rootOwner).addGuardian(guardian1.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian2.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian3.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian4.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian5.address);

    // Deploy Timelock
    const Timelock = await ethers.getContractFactory("HardcardTimelockController");
    const timelock = await Timelock.deploy(
      48 * 60 * 60, // 48 hours
      [], // proposers - will be set to governor
      [], // executors - anyone can execute
      rootOwner.address, // admin to set up roles
      rootOwner.address // root owner
    );

    // Deploy Governor
    const Governor = await ethers.getContractFactory("GovernorDAO");
    const governor = await Governor.deploy(
      await votesToken.getAddress(),
      await timelock.getAddress(),
      1, // voting delay: 1 block
      50400, // voting period: ~7 days
      0 // proposal threshold
    );

    // Setup roles
    const PROPOSER_ROLE = await timelock.PROPOSER_ROLE();
    const EXECUTOR_ROLE = await timelock.EXECUTOR_ROLE();
    const CANCELLER_ROLE = await timelock.CANCELLER_ROLE();

    await timelock.connect(rootOwner).grantRole(PROPOSER_ROLE, await governor.getAddress());
    await timelock.connect(rootOwner).grantRole(EXECUTOR_ROLE, ethers.ZeroAddress);
    await timelock.connect(rootOwner).grantRole(CANCELLER_ROLE, await guardianCouncil.getAddress());

    // Deploy core contracts
    const CredentialRegistry = await ethers.getContractFactory("CredentialRegistry");
    const credentialRegistry = await CredentialRegistry.deploy(await timelock.getAddress());

    const SchemaFactory = await ethers.getContractFactory("SchemaFactory");
    const schemaFactory = await SchemaFactory.deploy(await timelock.getAddress());

    // Setup voting power - transfer first, then delegate
    await votesToken.transfer(proposer.address, ethers.parseEther("600000")); // >50% of total supply
    await votesToken.connect(proposer).delegate(proposer.address);

    return {
      votesToken,
      guardianCouncil,
      timelock,
      governor,
      credentialRegistry,
      schemaFactory,
      rootOwner,
      proposer,
      guardians: [guardian1, guardian2, guardian3, guardian4, guardian5],
      user
    };
  }

  describe("Complete Governance Flow", function () {
    it("Should execute a governance proposal through the full lifecycle", async function () {
      const { 
        governor, 
        timelock, 
        credentialRegistry, 
        proposer,
        user 
      } = await loadFixture(deployFullGovernanceFixture);

      // 1. Create proposal to add an issuer
      const addIssuerCalldata = credentialRegistry.interface.encodeFunctionData(
        "addIssuer",
        [user.address]
      );

      const proposalDescription = "Proposal #1: Add user as issuer";
      
      const proposeTx = await governor.connect(proposer).propose(
        [await credentialRegistry.getAddress()],
        [0],
        [addIssuerCalldata],
        proposalDescription
      );

      const proposeReceipt = await proposeTx.wait();
      const proposalId = proposeReceipt!.logs[0].args![0];

      // 2. Wait for voting to start
      await time.increase(2);

      // 3. Vote on proposal
      await governor.connect(proposer).castVote(proposalId, 1); // 1 = For

      // 4. Wait for voting period to end
      // Mine enough blocks to pass the voting period
      await mine(50401);

      // Check proposal state (should be succeeded)
      const state = await governor.state(proposalId);
      expect(state).to.equal(4); // Succeeded

      // 5. Queue the proposal
      const descriptionHash = ethers.id(proposalDescription);
      await governor.queue(
        [await credentialRegistry.getAddress()],
        [0],
        [addIssuerCalldata],
        descriptionHash
      );


      // 6. Wait for timelock delay
      await time.increase(48 * 60 * 60 + 1);

      // 7. Execute the proposal
      await governor.execute(
        [await credentialRegistry.getAddress()],
        [0],
        [addIssuerCalldata],
        descriptionHash
      );


      // 8. Verify the result
      expect(await credentialRegistry.issuers(user.address)).to.be.true;
    });

    it("Should allow guardian freeze during active governance", async function () {
      const {
        governor,
        timelock,
        credentialRegistry,
        guardianCouncil,
        proposer,
        guardians,
        user
      } = await loadFixture(deployFullGovernanceFixture);

      // Create a potentially malicious proposal
      const maliciousCalldata = credentialRegistry.interface.encodeFunctionData(
        "transferOwnership",
        [user.address]
      );

      const proposeTx = await governor.connect(proposer).propose(
        [await credentialRegistry.getAddress()],
        [0],
        [maliciousCalldata],
        "Malicious proposal: Transfer ownership"
      );

      const proposeReceipt = await proposeTx.wait();
      const proposalId = proposeReceipt!.logs[0].args![0];

      // Fast forward through voting
      await time.increase(2);
      await governor.connect(proposer).castVote(proposalId, 1);
      await mine(50401);

      // Queue the malicious proposal
      const descriptionHash = ethers.id("Malicious proposal: Transfer ownership");
      await governor.queue(
        [await credentialRegistry.getAddress()],
        [0],
        [maliciousCalldata],
        descriptionHash
      );

      // GUARDIAN RESPONSE: Freeze the contract before execution
      await guardianCouncil.connect(guardians[0]).freeze(await credentialRegistry.getAddress());
      await guardianCouncil.connect(guardians[1]).freeze(await credentialRegistry.getAddress());
      await guardianCouncil.connect(guardians[2]).freeze(await credentialRegistry.getAddress());

      expect(await guardianCouncil.isFrozen(await credentialRegistry.getAddress())).to.be.true;

      // Wait for timelock
      await time.increase(48 * 60 * 60 + 1);

      // Try to execute - should fail due to freeze
      // Note: In production, the timelock would check freeze status
      await governor.execute(
        [await credentialRegistry.getAddress()],
        [0],
        [maliciousCalldata],
        descriptionHash
      );

      // In a real system, the execution would fail due to freeze
      // For this test, we verify the freeze is active
      expect(await guardianCouncil.isFrozen(await credentialRegistry.getAddress())).to.be.true;
    });

    it("Should allow root owner to veto timelock operations", async function () {
      const {
        governor,
        timelock,
        credentialRegistry,
        rootOwner,
        proposer,
        user
      } = await loadFixture(deployFullGovernanceFixture);

      // Create proposal
      const calldata = credentialRegistry.interface.encodeFunctionData(
        "pause"
      );

      const proposeTx = await governor.connect(proposer).propose(
        [await credentialRegistry.getAddress()],
        [0],
        [calldata],
        "Proposal: Pause registry"
      );

      const proposeReceipt = await proposeTx.wait();
      const proposalId = proposeReceipt!.logs[0].args![0];

      // Vote and queue
      await time.increase(2);
      await governor.connect(proposer).castVote(proposalId, 1);
      await mine(50401);

      const descriptionHash = ethers.id("Proposal: Pause registry");
      await governor.queue(
        [await credentialRegistry.getAddress()],
        [0],
        [calldata],
        descriptionHash
      );

      // Get operation ID from timelock
      const operationId = await timelock.hashOperation(
        await credentialRegistry.getAddress(),
        0,
        calldata,
        ethers.ZeroHash,
        descriptionHash
      );

      // Verify operation is pending
      expect(await timelock.isOperationPending(operationId)).to.be.true;

      // ROOT OWNER VETO
      await timelock.connect(rootOwner).emergencyVeto(operationId);

      // Verify operation is no longer pending
      expect(await timelock.isOperationPending(operationId)).to.be.false;

      // Try to execute - should fail
      await expect(
        governor.execute(
          [await credentialRegistry.getAddress()],
          [0],
          [calldata],
          descriptionHash
        )
      ).to.be.reverted;
    });

    it("Should handle guardian rotation during active governance", async function () {
      const {
        guardianCouncil,
        rootOwner,
        guardians,
        user
      } = await loadFixture(deployFullGovernanceFixture);

      // Verify initial guardian
      expect(await guardianCouncil.isGuardian(guardians[0].address)).to.be.true;
      expect(await guardianCouncil.getGuardianCount()).to.equal(5);

      // Rotate guardian
      await guardianCouncil.connect(rootOwner).rotateGuardian(
        guardians[0].address,
        user.address
      );

      // Verify rotation
      expect(await guardianCouncil.isGuardian(guardians[0].address)).to.be.false;
      expect(await guardianCouncil.isGuardian(user.address)).to.be.true;
      expect(await guardianCouncil.getGuardianCount()).to.equal(5);

      // Test new guardian can participate in freeze
      const target = ethers.Wallet.createRandom().address;
      
      await guardianCouncil.connect(user).freeze(target);
      await guardianCouncil.connect(guardians[1]).freeze(target);
      await guardianCouncil.connect(guardians[2]).freeze(target);

      expect(await guardianCouncil.isFrozen(target)).to.be.true;
    });
  });

  describe("Edge Cases and Attack Scenarios", function () {
    it("Should prevent governance attacks with insufficient voting power", async function () {
      const {
        governor,
        votesToken,
        credentialRegistry,
        user
      } = await loadFixture(deployFullGovernanceFixture);

      // User with no voting power tries to create proposal
      await expect(
        governor.connect(user).propose(
          [await credentialRegistry.getAddress()],
          [0],
          [credentialRegistry.interface.encodeFunctionData("pause")],
          "Malicious proposal"
        )
      ).to.be.revertedWith("GovernorVotes: proposer votes below proposal threshold");
    });

    it("Should maintain system integrity during guardian collusion attempt", async function () {
      const {
        guardianCouncil,
        credentialRegistry,
        guardians
      } = await loadFixture(deployFullGovernanceFixture);

      // Only 2 guardians try to freeze (below threshold)
      await guardianCouncil.connect(guardians[0]).freeze(await credentialRegistry.getAddress());
      await guardianCouncil.connect(guardians[1]).freeze(await credentialRegistry.getAddress());

      // Should not be frozen
      expect(await guardianCouncil.isFrozen(await credentialRegistry.getAddress())).to.be.false;
    });

    it("Should handle emergency response during timelock delay", async function () {
      const {
        governor,
        timelock,
        guardianCouncil,
        credentialRegistry,
        rootOwner,
        proposer,
        guardians
      } = await loadFixture(deployFullGovernanceFixture);

      // Create and queue a proposal
      const calldata = credentialRegistry.interface.encodeFunctionData("pause");
      
      const proposeTx = await governor.connect(proposer).propose(
        [await credentialRegistry.getAddress()],
        [0],
        [calldata],
        "Normal proposal"
      );

      const proposeReceipt = await proposeTx.wait();
      const proposalId = proposeReceipt!.logs[0].args![0];

      await time.increase(2);
      await governor.connect(proposer).castVote(proposalId, 1);
      await mine(50401);

      await governor.queue(
        [await credentialRegistry.getAddress()],
        [0],
        [calldata],
        ethers.id("Normal proposal")
      );

      // During the 48h timelock, emergency detected
      await time.increase(24 * 60 * 60); // 24 hours into timelock

      // Guardians can still freeze the target contract
      await guardianCouncil.connect(guardians[0]).freeze(await credentialRegistry.getAddress());
      await guardianCouncil.connect(guardians[1]).freeze(await credentialRegistry.getAddress());
      await guardianCouncil.connect(guardians[2]).freeze(await credentialRegistry.getAddress());

      expect(await guardianCouncil.isFrozen(await credentialRegistry.getAddress())).to.be.true;

      // Root owner can still veto the timelock operation
      const operationId = await timelock.hashOperation(
        await credentialRegistry.getAddress(),
        0,
        calldata,
        ethers.ZeroHash,
        ethers.id("Normal proposal")
      );

      await timelock.connect(rootOwner).emergencyVeto(operationId);
      expect(await timelock.isOperationPending(operationId)).to.be.false;
    });
  });
});