import { ethers } from "hardhat";
import { GuardianCouncil } from "../../typechain-types";
import * as fs from "fs";
import * as path from "path";

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const oldGuardianIndex = args.findIndex(arg => arg === "--old");
  const newGuardianIndex = args.findIndex(arg => arg === "--new");
  
  if (oldGuardianIndex === -1 || newGuardianIndex === -1) {
    console.error("Usage: npx hardhat run scripts/ops/rotate-guardian.ts --old <address> --new <address> --network <network>");
    process.exit(1);
  }
  
  const oldGuardian = args[oldGuardianIndex + 1];
  const newGuardian = args[newGuardianIndex + 1];
  
  console.log("\n🔄 Guardian Rotation");
  console.log("=" .repeat(50));
  console.log(`Old Guardian: ${oldGuardian}`);
  console.log(`New Guardian: ${newGuardian}`);
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
  
  // Verify old guardian exists
  const isOldGuardian = await guardianCouncil.hasRole(
    await guardianCouncil.GUARDIAN_ROLE(),
    oldGuardian
  );
  
  if (!isOldGuardian) {
    console.error(`❌ ${oldGuardian} is not a current guardian`);
    process.exit(1);
  }
  
  // Verify new guardian is valid
  if (newGuardian === ethers.constants.AddressZero) {
    console.error("❌ New guardian cannot be zero address");
    process.exit(1);
  }
  
  const isNewGuardian = await guardianCouncil.hasRole(
    await guardianCouncil.GUARDIAN_ROLE(),
    newGuardian
  );
  
  if (isNewGuardian) {
    console.error(`❌ ${newGuardian} is already a guardian`);
    process.exit(1);
  }
  
  // Get current state
  const guardianCount = await guardianCouncil.getGuardianCount();
  const threshold = await guardianCouncil.getThreshold();
  
  console.log(`\nCurrent State:`);
  console.log(`  Guardians: ${guardianCount}`);
  console.log(`  Threshold: ${threshold}`);
  
  // Estimate gas
  const estimatedGas = await guardianCouncil.estimateGas.rotateGuardian(
    oldGuardian,
    newGuardian
  );
  console.log(`  Estimated Gas: ${estimatedGas.toString()}`);
  
  // Confirm rotation
  console.log("\n⚠️  This will rotate the guardian on-chain");
  console.log("Press ENTER to continue or CTRL+C to cancel...");
  await new Promise(resolve => process.stdin.once("data", resolve));
  
  // Execute rotation
  console.log("\n🚀 Executing rotation...");
  const tx = await guardianCouncil.rotateGuardian(oldGuardian, newGuardian);
  console.log(`Transaction: ${tx.hash}`);
  
  // Wait for confirmation
  const receipt = await tx.wait();
  console.log(`✅ Rotation confirmed in block ${receipt.blockNumber}`);
  
  // Verify new state
  const newGuardianCount = await guardianCouncil.getGuardianCount();
  const isRotated = await guardianCouncil.hasRole(
    await guardianCouncil.GUARDIAN_ROLE(),
    newGuardian
  );
  const oldRemoved = !(await guardianCouncil.hasRole(
    await guardianCouncil.GUARDIAN_ROLE(),
    oldGuardian
  ));
  
  console.log("\n📊 Post-Rotation State:");
  console.log(`  Guardians: ${newGuardianCount} (unchanged)`);
  console.log(`  New Guardian Active: ${isRotated ? "✅" : "❌"}`);
  console.log(`  Old Guardian Removed: ${oldRemoved ? "✅" : "❌"}`);
  
  // Log rotation event
  const event = receipt.events?.find(e => e.event === "GuardianRotated");
  if (event) {
    console.log("\n📝 Event Details:");
    console.log(`  Old Guardian: ${event.args?.oldGuardian}`);
    console.log(`  New Guardian: ${event.args?.newGuardian}`);
    console.log(`  Executor: ${event.args?.executor}`);
  }
  
  // Save rotation record
  const rotationRecord = {
    timestamp: new Date().toISOString(),
    network: ethers.provider.network.name,
    transaction: tx.hash,
    block: receipt.blockNumber,
    oldGuardian,
    newGuardian,
    gasUsed: receipt.gasUsed.toString()
  };
  
  const recordPath = path.join(__dirname, "../../logs/guardian-rotations.json");
  const records = fs.existsSync(recordPath) 
    ? JSON.parse(fs.readFileSync(recordPath, "utf8"))
    : [];
  
  records.push(rotationRecord);
  fs.mkdirSync(path.dirname(recordPath), { recursive: true });
  fs.writeFileSync(recordPath, JSON.stringify(records, null, 2));
  
  console.log("\n✅ Rotation complete and logged!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error:", error);
    process.exit(1);
  });