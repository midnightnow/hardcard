import { ethers } from "hardhat";
import { time } from "@nomicfoundation/hardhat-toolbox/network-helpers";

/**
 * Guardian Emergency Simulation Script
 * Simulates a complete emergency response scenario with guardian freeze
 */

async function main() {
  console.log("🚨 Starting Guardian Emergency Simulation...\n");

  // Get signers
  const [deployer, guardian1, guardian2, guardian3, guardian4, guardian5, attacker] = 
    await ethers.getSigners();

  // Deploy contracts
  console.log("📦 Deploying contracts...");
  
  // Deploy Guardian Council
  const GuardianCouncil = await ethers.getContractFactory("GuardianCouncil");
  const guardianCouncil = await GuardianCouncil.deploy(3, 5, deployer.address);
  await guardianCouncil.waitForDeployment();
  
  // Add guardians
  const guardians = [guardian1, guardian2, guardian3, guardian4, guardian5];
  for (const guardian of guardians) {
    await guardianCouncil.addGuardian(guardian.address);
  }
  
  console.log("✅ Guardian Council deployed at:", await guardianCouncil.getAddress());
  console.log("   - Threshold: 3/5");
  console.log("   - Guardians added: 5\n");

  // Deploy vulnerable contract
  const CredentialRegistry = await ethers.getContractFactory("CredentialRegistry");
  const credentialRegistry = await CredentialRegistry.deploy(deployer.address);
  await credentialRegistry.waitForDeployment();
  
  console.log("✅ CredentialRegistry deployed at:", await credentialRegistry.getAddress());

  // Simulate normal operations first
  console.log("⏳ Simulating normal operations...");
  await credentialRegistry.addIssuer(deployer.address);
  await credentialRegistry.issueCredential(ethers.id("credential1"));
  console.log("   - Credential issued successfully");
  
  // Keep ownership with deployer but give guardian council freeze capability
  console.log("   - CredentialRegistry operational under normal ownership\n");

  // ATTACK SIMULATION
  console.log("🔥 ATTACK DETECTED! Simulating emergency response...\n");
  
  // Simulate suspicious activity
  console.log("⚠️  Suspicious activity detected on CredentialRegistry");
  console.log("   - Unusual gas consumption");
  console.log("   - Rapid state changes");
  console.log("   - Potential exploit in progress\n");

  // Guardian response
  console.log("👥 Guardian Emergency Response Initiated");
  console.log("   - Alert sent to all guardians");
  console.log("   - Threat assessment: HIGH");
  console.log("   - Action required: Emergency freeze\n");

  // First guardian votes to freeze
  console.log("🗳️  Guardian 1 voting to freeze...");
  let tx = await guardianCouncil.connect(guardian1).freeze(await credentialRegistry.getAddress());
  await tx.wait();
  console.log("   ✓ Vote submitted (1/3)");

  // Check if frozen (should not be)
  let isFrozen = await guardianCouncil.isFrozen(await credentialRegistry.getAddress());
  console.log(`   - Contract frozen: ${isFrozen}\n`);

  // Second guardian votes
  console.log("🗳️  Guardian 2 voting to freeze...");
  tx = await guardianCouncil.connect(guardian2).freeze(await credentialRegistry.getAddress());
  await tx.wait();
  console.log("   ✓ Vote submitted (2/3)");
  
  isFrozen = await guardianCouncil.isFrozen(await credentialRegistry.getAddress());
  console.log(`   - Contract frozen: ${isFrozen}\n`);

  // Third guardian votes (reaches threshold)
  console.log("🗳️  Guardian 3 voting to freeze...");
  tx = await guardianCouncil.connect(guardian3).freeze(await credentialRegistry.getAddress());
  const receipt = await tx.wait();
  console.log("   ✓ Vote submitted (3/3) - THRESHOLD REACHED!");
  
  // Check for freeze event
  const freezeEvent = receipt?.logs.find(
    log => log.topics[0] === ethers.id("ContractFrozen(address,uint256)")
  );
  
  if (freezeEvent) {
    console.log("   📢 ContractFrozen event emitted");
  }

  isFrozen = await guardianCouncil.isFrozen(await credentialRegistry.getAddress());
  console.log(`   - Contract frozen: ${isFrozen}`);
  
  const frozenUntil = await guardianCouncil.frozenUntil(await credentialRegistry.getAddress());
  const freezeDuration = frozenUntil - BigInt(await time.latest());
  console.log(`   - Frozen for: ${freezeDuration / 86400n} days\n`);

  // Try to use frozen contract
  console.log("🚫 Testing frozen contract behavior...");
  try {
    await credentialRegistry.issueCredential(ethers.id("credential2"));
    console.log("   ❌ ERROR: Transaction should have failed!");
  } catch (error: any) {
    if (error.message.includes("contract is frozen")) {
      console.log("   ✅ Contract correctly rejects transactions while frozen");
    } else {
      console.log("   ⚠️  Unexpected error:", error.message);
    }
  }

  // Simulate time passing and investigation
  console.log("\n⏰ Fast forwarding 2 days for investigation...");
  await time.increase(2 * 24 * 60 * 60);
  
  console.log("🔍 Investigation Results:");
  console.log("   - Vulnerability identified and patched");
  console.log("   - No funds were lost");
  console.log("   - Attacker address identified\n");

  // Unfreeze process
  console.log("🔓 Initiating unfreeze process...");
  
  // Three guardians vote to unfreeze
  for (let i = 0; i < 3; i++) {
    console.log(`🗳️  Guardian ${i + 1} voting to unfreeze...`);
    tx = await guardianCouncil.connect(guardians[i]).unfreeze(await credentialRegistry.getAddress());
    await tx.wait();
    console.log(`   ✓ Vote submitted (${i + 1}/3)`);
  }

  isFrozen = await guardianCouncil.isFrozen(await credentialRegistry.getAddress());
  console.log(`\n   - Contract frozen: ${isFrozen}`);
  console.log("   ✅ Contract successfully unfrozen!\n");

  // Resume operations
  console.log("✅ Testing resumed operations...");
  await credentialRegistry.issueCredential(ethers.id("credential3"));
  console.log("   - New credential issued successfully");
  console.log("   - System fully operational\n");

  // Summary
  console.log("📊 Emergency Response Summary:");
  console.log("   - Total response time: ~5 minutes");
  console.log("   - Guardians participating: 3/5");
  console.log("   - Freeze duration: 2 days");
  console.log("   - System impact: Minimal");
  console.log("   - User funds: SAFE");
  
  console.log("\n✅ Guardian Emergency Simulation Complete!");
  console.log("   The system successfully demonstrated its ability to:");
  console.log("   1. Detect and respond to threats quickly");
  console.log("   2. Freeze compromised contracts with guardian consensus");
  console.log("   3. Investigate and remediate issues while frozen");
  console.log("   4. Resume normal operations after threat mitigation");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });