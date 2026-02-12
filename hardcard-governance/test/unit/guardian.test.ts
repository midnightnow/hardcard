import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";
import { time } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("GuardianCouncil", function () {
  async function deployGuardianCouncilFixture() {
    const [rootOwner, guardian1, guardian2, guardian3, guardian4, guardian5, other] = 
      await ethers.getSigners();

    const THRESHOLD = 3;
    const MAX_GUARDIANS = 5;

    const GuardianCouncil = await ethers.getContractFactory("GuardianCouncil");
    const guardianCouncil = await GuardianCouncil.deploy(THRESHOLD, MAX_GUARDIANS, rootOwner.address);

    // Add initial guardians
    await guardianCouncil.connect(rootOwner).addGuardian(guardian1.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian2.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian3.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian4.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian5.address);

    // Deploy a mock freezable contract
    const CredentialRegistry = await ethers.getContractFactory("CredentialRegistry");
    const credentialRegistry = await CredentialRegistry.deploy(guardianCouncil.getAddress());

    return { 
      guardianCouncil, 
      credentialRegistry,
      rootOwner, 
      guardians: [guardian1, guardian2, guardian3, guardian4, guardian5],
      other,
      THRESHOLD,
      MAX_GUARDIANS
    };
  }

  describe("Deployment", function () {
    it("Should set the right threshold and max guardians", async function () {
      const { guardianCouncil, THRESHOLD, MAX_GUARDIANS } = await loadFixture(deployGuardianCouncilFixture);
      
      expect(await guardianCouncil.threshold()).to.equal(THRESHOLD);
      expect(await guardianCouncil.maxGuardians()).to.equal(MAX_GUARDIANS);
    });

    it("Should grant root owner role", async function () {
      const { guardianCouncil, rootOwner } = await loadFixture(deployGuardianCouncilFixture);
      const ROOT_OWNER_ROLE = await guardianCouncil.ROOT_OWNER_ROLE();
      
      expect(await guardianCouncil.hasRole(ROOT_OWNER_ROLE, rootOwner.address)).to.be.true;
    });
  });

  describe("Guardian Management", function () {
    it("Should allow root owner to add guardians", async function () {
      const { guardianCouncil, guardians } = await loadFixture(deployGuardianCouncilFixture);
      
      expect(await guardianCouncil.getGuardianCount()).to.equal(5);
      
      const guardianList = await guardianCouncil.getGuardians();
      expect(guardianList).to.have.lengthOf(5);
    });

    it("Should allow root owner to rotate guardians", async function () {
      const { guardianCouncil, rootOwner, guardians, other } = await loadFixture(deployGuardianCouncilFixture);
      
      await expect(guardianCouncil.connect(rootOwner).rotateGuardian(guardians[0].address, other.address))
        .to.emit(guardianCouncil, "GuardianRemoved")
        .withArgs(guardians[0].address)
        .and.to.emit(guardianCouncil, "GuardianAdded")
        .withArgs(other.address);
      
      expect(await guardianCouncil.isGuardian(guardians[0].address)).to.be.false;
      expect(await guardianCouncil.isGuardian(other.address)).to.be.true;
    });

    it("Should not allow non-root owner to manage guardians", async function () {
      const { guardianCouncil, guardians, other } = await loadFixture(deployGuardianCouncilFixture);
      
      await expect(guardianCouncil.connect(guardians[0]).addGuardian(other.address))
        .to.be.revertedWith("GuardianCouncil: caller is not root owner");
    });
  });

  describe("Freeze Mechanism", function () {
    it("Should require threshold votes to freeze", async function () {
      const { guardianCouncil, credentialRegistry, guardians } = await loadFixture(deployGuardianCouncilFixture);
      const targetAddress = await credentialRegistry.getAddress();
      
      // First vote
      await expect(guardianCouncil.connect(guardians[0]).freeze(targetAddress))
        .to.emit(guardianCouncil, "VoteCast");
      
      // Contract should not be frozen yet
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.false;
      
      // Second vote
      await guardianCouncil.connect(guardians[1]).freeze(targetAddress);
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.false;
      
      // Third vote (reaches threshold)
      await expect(guardianCouncil.connect(guardians[2]).freeze(targetAddress))
        .to.emit(guardianCouncil, "ContractFrozen")
        .and.to.emit(guardianCouncil, "ProposalExecuted");
      
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.true;
    });

    it("Should freeze contract for correct duration", async function () {
      const { guardianCouncil, credentialRegistry, guardians } = await loadFixture(deployGuardianCouncilFixture);
      const targetAddress = await credentialRegistry.getAddress();
      const FREEZE_SECONDS = 7 * 24 * 60 * 60; // 7 days
      
      // Reach threshold to freeze
      await guardianCouncil.connect(guardians[0]).freeze(targetAddress);
      await guardianCouncil.connect(guardians[1]).freeze(targetAddress);
      await guardianCouncil.connect(guardians[2]).freeze(targetAddress);
      
      const freezeTimestamp = await guardianCouncil.frozenUntil(targetAddress);
      const currentTime = await time.latest();
      
      expect(freezeTimestamp).to.be.closeTo(currentTime + FREEZE_SECONDS, 10);
    });

    it("Should not allow duplicate votes", async function () {
      const { guardianCouncil, credentialRegistry, guardians } = await loadFixture(deployGuardianCouncilFixture);
      const targetAddress = await credentialRegistry.getAddress();
      
      await guardianCouncil.connect(guardians[0]).freeze(targetAddress);
      
      // Try to vote again
      await guardianCouncil.connect(guardians[0]).freeze(targetAddress);
      
      // Should still only have 1 vote (no duplicate)
      // Contract should not be frozen
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.false;
    });
  });

  describe("Unfreeze Mechanism", function () {
    it("Should require threshold votes to unfreeze", async function () {
      const { guardianCouncil, credentialRegistry, guardians } = await loadFixture(deployGuardianCouncilFixture);
      const targetAddress = await credentialRegistry.getAddress();
      
      // First freeze the contract
      await guardianCouncil.connect(guardians[0]).freeze(targetAddress);
      await guardianCouncil.connect(guardians[1]).freeze(targetAddress);
      await guardianCouncil.connect(guardians[2]).freeze(targetAddress);
      
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.true;
      
      // Now unfreeze with threshold
      await guardianCouncil.connect(guardians[0]).unfreeze(targetAddress);
      await guardianCouncil.connect(guardians[1]).unfreeze(targetAddress);
      
      // Should still be frozen
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.true;
      
      // Third vote reaches threshold
      await expect(guardianCouncil.connect(guardians[2]).unfreeze(targetAddress))
        .to.emit(guardianCouncil, "ContractUnfrozen");
      
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.false;
    });
  });
});