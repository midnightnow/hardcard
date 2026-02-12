import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("Guardian Safety Tests", function () {
  async function deployFullSystemFixture() {
    const [rootOwner, guardian1, guardian2, guardian3, guardian4, guardian5, attacker] = 
      await ethers.getSigners();

    // Deploy Guardian Council
    const GuardianCouncil = await ethers.getContractFactory("GuardianCouncil");
    const guardianCouncil = await GuardianCouncil.deploy(3, 5, rootOwner.address);

    // Add guardians
    await guardianCouncil.connect(rootOwner).addGuardian(guardian1.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian2.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian3.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian4.address);
    await guardianCouncil.connect(rootOwner).addGuardian(guardian5.address);

    // Deploy core contracts
    const CredentialRegistry = await ethers.getContractFactory("CredentialRegistry");
    const credentialRegistry = await CredentialRegistry.deploy(guardianCouncil.getAddress());

    const SchemaFactory = await ethers.getContractFactory("SchemaFactory");
    const schemaFactory = await SchemaFactory.deploy(guardianCouncil.getAddress());

    return {
      guardianCouncil,
      credentialRegistry,
      schemaFactory,
      rootOwner,
      guardians: [guardian1, guardian2, guardian3, guardian4, guardian5],
      attacker
    };
  }

  describe("Attack Scenarios", function () {
    it("Should prevent single guardian from freezing contracts", async function () {
      const { guardianCouncil, credentialRegistry, guardians } = await loadFixture(deployFullSystemFixture);
      const targetAddress = await credentialRegistry.getAddress();

      // Single guardian tries to freeze
      await guardianCouncil.connect(guardians[0]).freeze(targetAddress);
      
      // Contract should not be frozen
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.false;
    });

    it("Should prevent guardian collusion below threshold", async function () {
      const { guardianCouncil, credentialRegistry, guardians } = await loadFixture(deployFullSystemFixture);
      const targetAddress = await credentialRegistry.getAddress();

      // Two guardians collude (below threshold of 3)
      await guardianCouncil.connect(guardians[0]).freeze(targetAddress);
      await guardianCouncil.connect(guardians[1]).freeze(targetAddress);
      
      // Contract should still not be frozen
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.false;
    });

    it("Should prevent non-guardian from voting", async function () {
      const { guardianCouncil, credentialRegistry, attacker } = await loadFixture(deployFullSystemFixture);
      const targetAddress = await credentialRegistry.getAddress();

      await expect(guardianCouncil.connect(attacker).freeze(targetAddress))
        .to.be.revertedWith("GuardianCouncil: caller is not a guardian");
    });

    it("Should prevent guardian removal below threshold", async function () {
      const { guardianCouncil, rootOwner, guardians } = await loadFixture(deployFullSystemFixture);

      // Remove guardians down to threshold (3)
      await guardianCouncil.connect(rootOwner).removeGuardian(guardians[0].address);
      await guardianCouncil.connect(rootOwner).removeGuardian(guardians[1].address);

      // Should have exactly 3 guardians now
      expect(await guardianCouncil.getGuardianCount()).to.equal(3);

      // Try to remove one more (would go below threshold)
      await expect(guardianCouncil.connect(rootOwner).removeGuardian(guardians[2].address))
        .to.be.revertedWith("GuardianCouncil: cannot go below threshold");
    });
  });

  describe("Emergency Response", function () {
    it("Should allow legitimate freeze with threshold", async function () {
      const { guardianCouncil, credentialRegistry, guardians } = await loadFixture(deployFullSystemFixture);
      const targetAddress = await credentialRegistry.getAddress();

      // Three guardians vote to freeze (meets threshold)
      await guardianCouncil.connect(guardians[0]).freeze(targetAddress);
      await guardianCouncil.connect(guardians[1]).freeze(targetAddress);
      await guardianCouncil.connect(guardians[2]).freeze(targetAddress);

      // Contract should be frozen
      expect(await guardianCouncil.isFrozen(targetAddress)).to.be.true;
      
      // Verify the credential registry recognizes the freeze
      const freezeTimestamp = await credentialRegistry.freezeUntilTimestamp();
      expect(freezeTimestamp).to.be.gt(0);
    });

    it("Should allow root owner to rotate compromised guardian", async function () {
      const { guardianCouncil, rootOwner, guardians, attacker } = await loadFixture(deployFullSystemFixture);
      
      // Simulate guardian compromise - rotate to new address
      const compromisedGuardian = guardians[0].address;
      const newGuardian = attacker.address; // Using attacker address as new guardian for test

      await expect(guardianCouncil.connect(rootOwner).rotateGuardian(compromisedGuardian, newGuardian))
        .to.emit(guardianCouncil, "GuardianRemoved")
        .withArgs(compromisedGuardian)
        .and.to.emit(guardianCouncil, "GuardianAdded")
        .withArgs(newGuardian);

      // Verify rotation
      expect(await guardianCouncil.isGuardian(compromisedGuardian)).to.be.false;
      expect(await guardianCouncil.isGuardian(newGuardian)).to.be.true;
      expect(await guardianCouncil.getGuardianCount()).to.equal(5);
    });
  });

  describe("System Invariants", function () {
    it("Should maintain guardian count invariants", async function () {
      const { guardianCouncil } = await loadFixture(deployFullSystemFixture);

      const count = await guardianCouncil.getGuardianCount();
      const threshold = await guardianCouncil.threshold();
      const maxGuardians = await guardianCouncil.maxGuardians();

      // Count should be between threshold and max
      expect(count).to.be.gte(threshold);
      expect(count).to.be.lte(maxGuardians);
    });

    it("Should prevent zero address operations", async function () {
      const { guardianCouncil, rootOwner, guardians } = await loadFixture(deployFullSystemFixture);

      // Try to add zero address as guardian
      await expect(guardianCouncil.connect(rootOwner).addGuardian(ethers.ZeroAddress))
        .to.be.revertedWith("GuardianCouncil: guardian is zero address");

      // Try to rotate to zero address
      await expect(guardianCouncil.connect(rootOwner).rotateGuardian(guardians[0].address, ethers.ZeroAddress))
        .to.be.revertedWith("GuardianCouncil: new guardian is zero address");
    });
  });
});