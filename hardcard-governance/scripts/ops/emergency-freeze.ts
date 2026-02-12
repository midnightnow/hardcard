import { ethers } from "hardhat";
import { GuardianCouncil } from "../../typechain-types";
import * as fs from "fs";
import * as path from "path";

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const targetIndex = args.findIndex(arg => arg === "--target");
  const guardianIndex = args.findIndex(arg => arg === "--guardian-index");
  const reasonIndex = args.findIndex(arg => arg === "--reason");
  
  if (targetIndex === -1 || guardianIndex === -1) {
    console.error("Usage: npx hardhat run scripts/ops/emergency-freeze.ts --target <address> --guardian-index <number> [--reason <string>] --network <network>");
    process.exit(1);
  }
  
  const targetContract = args[targetIndex + 1];
  const guardianIdx = parseInt(args[guardianIndex + 1]);
  const reason = reasonIndex !== -1 ? args[reasonIndex + 1] : "Emergency freeze";
  
  console.log("\n🚨 EMERGENCY FREEZE ACTIVATION");
  console.log("=" .repeat(50));
  console.log(`Target Contract: ${targetContract}`);
  console.log(`Guardian Index: ${guardianIdx}`);
  console.log(`Reason: ${reason}`);
  console.log(`Network: ${ethers.provider.network.name}`);
  console.log(`Timestamp: ${new Date().toISOString()}`);
  
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
  
  // Get guardian information
  const guardianRole = await guardianCouncil.GUARDIAN_ROLE();
  const totalGuardians = await guardianCouncil.getRoleMemberCount(guardianRole);
  const threshold = await guardianCouncil.getThreshold();
  
  console.log(`\nGuardian Council Status:`);
  console.log(`  Total Guardians: ${totalGuardians}`);
  console.log(`  Threshold: ${threshold}`);
  
  if (guardianIdx >= totalGuardians) {
    console.error(`❌ Invalid guardian index: ${guardianIdx} (max: ${totalGuardians - 1})`);
    process.exit(1);
  }
  
  // Get guardian address
  const guardianAddress = await guardianCouncil.getRoleMember(guardianRole, guardianIdx);
  console.log(`  Guardian ${guardianIdx}: ${guardianAddress}`);
  
  // Check if this guardian has already voted
  try {
    const currentVotes = await guardianCouncil.getFreezeVotes(targetContract);
    console.log(`  Current Votes: ${currentVotes}/${threshold}`);
  } catch (error) {
    console.log(`  Current votes: Unable to determine`);
  }
  
  // Check if already frozen
  try {
    const isFrozen = await guardianCouncil.isFrozen(targetContract);
    if (isFrozen) {
      console.log(`\n⚠️  Contract is already frozen!`);
      const freezeTimestamp = await guardianCouncil.getFreezeTimestamp(targetContract);
      const freezeDate = new Date(freezeTimestamp.toNumber() * 1000);
      console.log(`   Frozen at: ${freezeDate.toISOString()}`);
      return;
    }
  } catch (error) {
    console.log(`   Freeze status: Unable to determine`);
  }
  
  // Get available signers
  const signers = await ethers.getSigners();
  const guardianSigner = signers.find(s => s.address.toLowerCase() === guardianAddress.toLowerCase());
  
  if (!guardianSigner) {
    console.error(`❌ No signer available for guardian ${guardianIdx} (${guardianAddress})`);
    console.log(`Available signers:`);
    signers.forEach((s, i) => console.log(`  ${i}: ${s.address}`));
    process.exit(1);
  }
  
  console.log(`\n✅ Using signer: ${guardianSigner.address}`);
  
  // Estimate gas
  const guardianContract = guardianCouncil.connect(guardianSigner);
  
  try {
    const estimatedGas = await guardianContract.estimateGas.freeze(targetContract);
    console.log(`   Estimated gas: ${estimatedGas.toString()}`);
  } catch (error) {
    console.log(`   Gas estimation failed: ${error.message}`);
  }
  
  // Log the emergency action
  const emergencyLog = {
    timestamp: new Date().toISOString(),
    action: "emergency_freeze_vote",
    guardian: guardianAddress,
    guardianIndex: guardianIdx,
    target: targetContract,
    reason: reason,
    network: ethers.provider.network.name
  };
  
  const logPath = path.join(__dirname, "../../logs/emergency-actions.json");
  const logs = fs.existsSync(logPath) 
    ? JSON.parse(fs.readFileSync(logPath, "utf8"))
    : [];
  
  logs.push(emergencyLog);
  fs.mkdirSync(path.dirname(logPath), { recursive: true });
  fs.writeFileSync(logPath, JSON.stringify(logs, null, 2));
  
  // Confirm action
  console.log("\n⚠️  This will cast an EMERGENCY FREEZE vote");
  console.log("This action should only be taken in genuine emergencies");
  console.log("Press ENTER to continue or CTRL+C to cancel...");
  await new Promise(resolve => process.stdin.once("data", resolve));
  
  // Execute freeze vote
  console.log("\n🗳️  Casting emergency freeze vote...");
  
  try {
    const tx = await guardianContract.freeze(targetContract);
    console.log(`Transaction: ${tx.hash}`);
    
    console.log("Waiting for confirmation...");
    const receipt = await tx.wait();
    console.log(`✅ Vote confirmed in block ${receipt.blockNumber}`);
    
    // Check if freeze is now active
    try {
      const isFrozen = await guardianCouncil.isFrozen(targetContract);
      const currentVotes = await guardianCouncil.getFreezeVotes(targetContract);
      
      console.log(`\n📊 Post-Vote Status:`);
      console.log(`  Current Votes: ${currentVotes}/${threshold}`);
      console.log(`  Freeze Active: ${isFrozen ? "🧊 YES" : "❌ NO"}`);
      
      if (isFrozen) {
        console.log(`\n🚨 EMERGENCY FREEZE ACTIVATED!`);
        console.log(`Target contract ${targetContract} is now FROZEN`);
        
        const freezeTimestamp = await guardianCouncil.getFreezeTimestamp(targetContract);
        const freezeDate = new Date(freezeTimestamp.toNumber() * 1000);
        const unfreezeTime = new Date(freezeDate.getTime() + 7 * 24 * 60 * 60 * 1000);
        
        console.log(`Freeze Time: ${freezeDate.toISOString()}`);
        console.log(`Auto-Unfreeze: ${unfreezeTime.toISOString()}`);
        console.log(`Duration: 7 days`);
        
        // Send emergency notifications
        console.log(`\n📢 Sending emergency notifications...`);
        // This would integrate with your notification system
        
      } else {
        console.log(`\n⏳ Freeze not yet active (need ${threshold - currentVotes} more votes)`);
      }
      
    } catch (error) {
      console.log(`Post-vote status check failed: ${error.message}`);
    }
    
    // Update emergency log with result
    emergencyLog.transactionHash = tx.hash;
    emergencyLog.blockNumber = receipt.blockNumber;
    emergencyLog.gasUsed = receipt.gasUsed.toString();
    emergencyLog.success = true;
    
    logs[logs.length - 1] = emergencyLog;
    fs.writeFileSync(logPath, JSON.stringify(logs, null, 2));
    
    // Generate emergency report
    const reportPath = path.join(__dirname, `../../logs/emergency-freeze-${Date.now()}.md`);
    const report = `# Emergency Freeze Report

**Timestamp**: ${emergencyLog.timestamp}
**Guardian**: ${guardianAddress} (Index: ${guardianIdx})
**Target**: ${targetContract}
**Reason**: ${reason}
**Network**: ${ethers.provider.network.name}

## Transaction Details
- **Hash**: ${tx.hash}
- **Block**: ${receipt.blockNumber}
- **Gas Used**: ${receipt.gasUsed.toString()}

## Status
- **Vote Cast**: ✅ Success
- **Freeze Active**: ${isFrozen ? "✅ Yes" : "❌ No"}

## Next Steps
${isFrozen 
  ? "- Monitor frozen contract\n- Investigate threat\n- Plan unfreeze when safe"
  : "- Coordinate with other guardians\n- Cast additional votes if needed"
}

---
*Generated automatically by emergency-freeze.ts*
`;
    
    fs.writeFileSync(reportPath, report);
    console.log(`\n📄 Emergency report: ${reportPath}`);
    
  } catch (error) {
    console.log(`\n❌ Emergency freeze vote failed: ${error.message}`);
    
    // Log the failure
    emergencyLog.success = false;
    emergencyLog.error = error.message;
    logs[logs.length - 1] = emergencyLog;
    fs.writeFileSync(logPath, JSON.stringify(logs, null, 2));
    
    process.exit(1);
  }
  
  console.log(`\n✅ Emergency freeze vote complete!`);
  console.log(`Guardian ${guardianIdx} has voted to freeze ${targetContract}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error:", error);
    process.exit(1);
  });