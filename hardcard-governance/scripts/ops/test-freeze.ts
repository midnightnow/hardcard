import { ethers } from "hardhat";
import { GuardianCouncil } from "../../typechain-types";
import * as fs from "fs";
import * as path from "path";

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const guardiansIndex = args.findIndex(arg => arg === "--guardians");
  const targetIndex = args.findIndex(arg => arg === "--target");
  
  if (guardiansIndex === -1 || targetIndex === -1) {
    console.error("Usage: npx hardhat run scripts/ops/test-freeze.ts --guardians <indices> --target <address> --network <network>");
    console.error("Example: --guardians 1,2,3 --target 0x123...");
    process.exit(1);
  }
  
  const guardianIndices = args[guardiansIndex + 1].split(",").map(n => parseInt(n.trim()) - 1);
  const targetContract = args[targetIndex + 1];
  
  console.log("\n🧊 Guardian Freeze Test");
  console.log("=" .repeat(50));
  console.log(`Voting Guardians: ${guardianIndices.map(i => i + 1).join(", ")}`);
  console.log(`Target Contract: ${targetContract}`);
  console.log(`Network: ${ethers.provider.network.name}`);
  
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
  
  // Get guardian addresses
  const guardianRole = await guardianCouncil.GUARDIAN_ROLE();
  const totalGuardians = await guardianCouncil.getRoleMemberCount(guardianRole);
  const threshold = await guardianCouncil.getThreshold();
  
  console.log(`\nConfiguration:`);
  console.log(`  Total Guardians: ${totalGuardians}`);
  console.log(`  Threshold: ${threshold}`);
  console.log(`  Voting Count: ${guardianIndices.length}`);
  
  if (guardianIndices.length < threshold) {
    console.error(`❌ Insufficient guardians (need ${threshold}, have ${guardianIndices.length})`);
    process.exit(1);
  }
  
  // Get guardian addresses
  const guardianAddresses = [];
  for (let i = 0; i < totalGuardians; i++) {
    const guardian = await guardianCouncil.getRoleMember(guardianRole, i);
    guardianAddresses.push(guardian);
  }
  
  console.log(`\nGuardian Addresses:`);
  guardianAddresses.forEach((addr, i) => {
    const voting = guardianIndices.includes(i) ? "🗳️  VOTING" : "   idle";
    console.log(`  ${i + 1}. ${addr} ${voting}`);
  });
  
  // Check if target is already frozen
  try {
    const isFrozen = await guardianCouncil.isFrozen(targetContract);
    if (isFrozen) {
      console.log(`\n⚠️  Target contract is already frozen!`);
      
      // Show when it was frozen
      const freezeTimestamp = await guardianCouncil.getFreezeTimestamp(targetContract);
      const freezeDate = new Date(freezeTimestamp.toNumber() * 1000);
      console.log(`   Frozen at: ${freezeDate.toISOString()}`);
      
      // Calculate unfreeze time (7 days later)
      const unfreezeTime = new Date(freezeDate.getTime() + 7 * 24 * 60 * 60 * 1000);
      console.log(`   Auto-unfreeze: ${unfreezeTime.toISOString()}`);
      
      return;
    }
  } catch (error) {
    // Contract might not have freeze tracking yet
    console.log(`   Freeze status unknown (${error.message})`);
  }
  
  // Get available signers
  const signers = await ethers.getSigners();
  const votingSigners = [];
  
  // Try to match guardian addresses to available signers
  for (const index of guardianIndices) {
    if (index >= guardianAddresses.length) {
      console.error(`❌ Invalid guardian index: ${index + 1}`);
      process.exit(1);
    }
    
    const guardianAddr = guardianAddresses[index];
    const signer = signers.find(s => s.address.toLowerCase() === guardianAddr.toLowerCase());
    
    if (!signer) {
      console.error(`❌ No signer available for guardian ${index + 1} (${guardianAddr})`);
      console.log(`Available signers:`);
      signers.forEach((s, i) => console.log(`  ${i}: ${s.address}`));
      process.exit(1);
    }
    
    votingSigners.push(signer);
  }
  
  console.log(`\n✅ Found signers for ${votingSigners.length} guardians`);
  
  // Estimate gas for freeze operation
  const firstSigner = votingSigners[0];
  const guardianContract = guardianCouncil.connect(firstSigner);
  
  try {
    const estimatedGas = await guardianContract.estimateGas.freeze(targetContract);
    console.log(`   Estimated gas per vote: ${estimatedGas.toString()}`);
  } catch (error) {
    console.log(`   Gas estimation failed: ${error.message}`);
  }
  
  // Confirm test
  console.log("\n⚠️  This will attempt to freeze the target contract");
  console.log("Press ENTER to continue or CTRL+C to cancel...");
  await new Promise(resolve => process.stdin.once("data", resolve));
  
  // Execute freeze votes
  console.log("\n🗳️  Executing freeze votes...");
  const transactions = [];
  
  for (let i = 0; i < votingSigners.length; i++) {
    const signer = votingSigners[i];
    const guardianIndex = guardianIndices[i];
    
    console.log(`\n  Vote ${i + 1}/${votingSigners.length} - Guardian ${guardianIndex + 1}`);
    console.log(`  Signer: ${signer.address}`);
    
    try {
      const contract = guardianCouncil.connect(signer);
      const tx = await contract.freeze(targetContract);
      console.log(`  Transaction: ${tx.hash}`);
      
      const receipt = await tx.wait();
      console.log(`  ✅ Confirmed in block ${receipt.blockNumber}`);
      
      transactions.push({
        guardian: guardianIndex + 1,
        signer: signer.address,
        hash: tx.hash,
        block: receipt.blockNumber,
        gasUsed: receipt.gasUsed.toString()
      });
      
      // Check if freeze is now active
      try {
        const isFrozen = await guardianCouncil.isFrozen(targetContract);
        if (isFrozen) {
          console.log(`  🧊 FREEZE ACTIVATED!`);
          break;
        } else {
          const currentVotes = await guardianCouncil.getFreezeVotes(targetContract);
          console.log(`  Current votes: ${currentVotes}/${threshold}`);
        }
      } catch (error) {
        console.log(`  Vote count check failed: ${error.message}`);
      }
      
    } catch (error) {
      console.log(`  ❌ Vote failed: ${error.message}`);
      
      // Continue with remaining votes unless it's a fatal error
      if (error.message.includes("already voted")) {
        console.log(`  (Guardian ${guardianIndex + 1} already voted)`);
      }
    }
  }
  
  // Final status check
  console.log("\n📊 Final Status:");
  
  try {
    const isFrozen = await guardianCouncil.isFrozen(targetContract);
    console.log(`  Target Frozen: ${isFrozen ? "✅ YES" : "❌ NO"}`);
    
    if (isFrozen) {
      const freezeTimestamp = await guardianCouncil.getFreezeTimestamp(targetContract);
      const freezeDate = new Date(freezeTimestamp.toNumber() * 1000);
      const unfreezeTime = new Date(freezeDate.getTime() + 7 * 24 * 60 * 60 * 1000);
      
      console.log(`  Freeze Time: ${freezeDate.toISOString()}`);
      console.log(`  Auto-Unfreeze: ${unfreezeTime.toISOString()}`);
      console.log(`  Duration: 7 days`);
    }
    
    const currentVotes = await guardianCouncil.getFreezeVotes(targetContract);
    console.log(`  Vote Count: ${currentVotes}/${threshold}`);
    
  } catch (error) {
    console.log(`  Status check failed: ${error.message}`);
  }
  
  // Save test results
  const testResults = {
    timestamp: new Date().toISOString(),
    network: ethers.provider.network.name,
    target: targetContract,
    votingGuardians: guardianIndices.map(i => i + 1),
    threshold: threshold.toNumber(),
    transactions,
    success: transactions.length > 0
  };
  
  const resultsPath = path.join(__dirname, "../../logs/freeze-tests.json");
  const results = fs.existsSync(resultsPath) 
    ? JSON.parse(fs.readFileSync(resultsPath, "utf8"))
    : [];
  
  results.push(testResults);
  fs.mkdirSync(path.dirname(resultsPath), { recursive: true });
  fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));
  
  console.log(`\n💾 Test results saved to: logs/freeze-tests.json`);
  console.log(`\n✅ Freeze test complete!`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error:", error);
    process.exit(1);
  });