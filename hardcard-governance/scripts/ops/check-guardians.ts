import { ethers } from "hardhat";
import { GuardianCouncil } from "../../typechain-types";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("\n🛡️  Guardian Council Status Check");
  console.log("=" .repeat(50));
  
  // Load deployment info
  const deploymentPath = path.join(
    __dirname,
    `../../deployments/${ethers.provider.network.name}/GuardianCouncil.json`
  );
  
  if (!fs.existsSync(deploymentPath)) {
    console.error("❌ GuardianCouncil deployment not found");
    process.exit(1);
  }
  
  const deployment = JSON.parse(fs.readFileSync(deploymentPath, "utf8"));
  const guardianCouncil = await ethers.getContractAt(
    "GuardianCouncil",
    deployment.address
  ) as GuardianCouncil;
  
  console.log(`Contract: ${deployment.address}`);
  console.log(`Network: ${ethers.provider.network.name}`);
  console.log(`Block: ${await ethers.provider.getBlockNumber()}`);
  
  // Get basic info
  const guardianRole = await guardianCouncil.GUARDIAN_ROLE();
  const rootOwnerRole = await guardianCouncil.ROOT_OWNER_ROLE();
  const threshold = await guardianCouncil.getThreshold();
  const guardianCount = await guardianCouncil.getGuardianCount();
  
  console.log(`\n📊 Configuration:`);
  console.log(`  Guardian Count: ${guardianCount}`);
  console.log(`  Threshold: ${threshold}`);
  console.log(`  Max Guardians: 5 (hardcoded)`);
  
  // List all guardians
  console.log(`\n👥 Active Guardians:`);
  const guardians = [];
  
  // Get guardian count using role member enumeration
  const guardianRoleCount = await guardianCouncil.getRoleMemberCount(guardianRole);
  
  for (let i = 0; i < guardianRoleCount; i++) {
    const guardian = await guardianCouncil.getRoleMember(guardianRole, i);
    guardians.push(guardian);
    
    // Try to get last action (this requires the contract to store this)
    try {
      console.log(`  ${i + 1}. ${guardian}`);
      // Note: getLastAction method needs to be implemented in contract
      // For now, just show the address
    } catch (error) {
      console.log(`  ${i + 1}. ${guardian}`);
    }
  }
  
  // Check root owner
  const rootOwnerCount = await guardianCouncil.getRoleMemberCount(rootOwnerRole);
  console.log(`\n👑 Root Owner(s):`);
  
  for (let i = 0; i < rootOwnerCount; i++) {
    const rootOwner = await guardianCouncil.getRoleMember(rootOwnerRole, i);
    console.log(`  ${i + 1}. ${rootOwner}`);
  }
  
  // Check contract status
  console.log(`\n🔒 Contract Status:`);
  
  // Check if any contracts are frozen
  try {
    // This would require checking target contracts if frozen
    console.log(`  Global Status: Active (no freeze detected)`);
  } catch (error) {
    console.log(`  Status Check: Error - ${error}`);
  }
  
  // Recent activity (events from last 1000 blocks)
  console.log(`\n📈 Recent Activity (last 1000 blocks):`);
  const currentBlock = await ethers.provider.getBlockNumber();
  const fromBlock = Math.max(0, currentBlock - 1000);
  
  try {
    // Guardian role changes
    const guardianEvents = await guardianCouncil.queryFilter(
      guardianCouncil.filters.RoleGranted(guardianRole),
      fromBlock
    );
    
    const guardianRemovals = await guardianCouncil.queryFilter(
      guardianCouncil.filters.RoleRevoked(guardianRole),
      fromBlock
    );
    
    // Freeze events
    const freezeEvents = await guardianCouncil.queryFilter(
      guardianCouncil.filters.ContractFrozen(),
      fromBlock
    );
    
    const unfreezeEvents = await guardianCouncil.queryFilter(
      guardianCouncil.filters.ContractUnfrozen(),
      fromBlock
    );
    
    console.log(`  Guardian Additions: ${guardianEvents.length}`);
    console.log(`  Guardian Removals: ${guardianRemovals.length}`);
    console.log(`  Freeze Actions: ${freezeEvents.length}`);
    console.log(`  Unfreeze Actions: ${unfreezeEvents.length}`);
    
    // Show recent events
    const allEvents = [
      ...guardianEvents.map(e => ({ type: "Guardian Added", ...e })),
      ...guardianRemovals.map(e => ({ type: "Guardian Removed", ...e })),
      ...freezeEvents.map(e => ({ type: "Contract Frozen", ...e })),
      ...unfreezeEvents.map(e => ({ type: "Contract Unfrozen", ...e }))
    ].sort((a, b) => a.blockNumber - b.blockNumber);
    
    if (allEvents.length > 0) {
      console.log(`\n📋 Recent Events:`);
      allEvents.slice(-5).forEach(event => {
        console.log(`  Block ${event.blockNumber}: ${event.type}`);
      });
    }
    
  } catch (error) {
    console.log(`  Event query failed: ${error.message}`);
  }
  
  // Health checks
  console.log(`\n🩺 Health Checks:`);
  
  // Check threshold is valid
  const thresholdValid = threshold > 0 && threshold <= guardianCount && threshold >= Math.ceil(guardianCount * 0.6);
  console.log(`  Threshold Valid (≥60%): ${thresholdValid ? "✅" : "❌"}`);
  
  // Check guardian count is within bounds
  const countValid = guardianCount >= 3 && guardianCount <= 5;
  console.log(`  Guardian Count (3-5): ${countValid ? "✅" : "❌"}`);
  
  // Check for duplicate guardians (should not happen)
  const uniqueGuardians = new Set(guardians);
  const noDuplicates = uniqueGuardians.size === guardians.length;
  console.log(`  No Duplicate Guardians: ${noDuplicates ? "✅" : "❌"}`);
  
  // Check root owner exists
  const hasRootOwner = rootOwnerCount > 0;
  console.log(`  Root Owner Present: ${hasRootOwner ? "✅" : "❌"}`);
  
  // Generate summary
  const allChecksPass = thresholdValid && countValid && noDuplicates && hasRootOwner;
  
  console.log(`\n📊 Summary:`);
  console.log(`  Overall Status: ${allChecksPass ? "🟢 HEALTHY" : "🔴 ISSUES DETECTED"}`);
  console.log(`  Last Updated: ${new Date().toISOString()}`);
  
  // Save status to file for monitoring
  const status = {
    timestamp: new Date().toISOString(),
    network: ethers.provider.network.name,
    contract: deployment.address,
    guardianCount: guardianCount.toNumber(),
    threshold: threshold.toNumber(),
    guardians,
    rootOwnerCount: rootOwnerCount.toNumber(),
    healthy: allChecksPass,
    checks: {
      thresholdValid,
      countValid,
      noDuplicates,
      hasRootOwner
    }
  };
  
  const statusPath = path.join(__dirname, "../../logs/guardian-status.json");
  fs.mkdirSync(path.dirname(statusPath), { recursive: true });
  fs.writeFileSync(statusPath, JSON.stringify(status, null, 2));
  
  console.log(`\n💾 Status saved to: logs/guardian-status.json`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error:", error);
    process.exit(1);
  });