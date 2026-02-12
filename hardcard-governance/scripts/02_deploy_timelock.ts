import { ethers } from "hardhat";

async function main() {
  console.log("Deploying Timelock Controller...");
  
  const [deployer] = await ethers.getSigners();
  const rootOwnerAddress = deployer.address; // In production, use cold HSM address
  
  // These would come from previous deployments
  const VOTES_TOKEN_ADDRESS = "0x0000000000000000000000000000000000000000"; // Replace
  const GUARDIAN_COUNCIL_ADDRESS = "0x0000000000000000000000000000000000000000"; // Replace
  
  const MIN_DELAY = 48 * 60 * 60; // 48 hours in seconds
  
  // Deploy Timelock
  const TimelockController = await ethers.getContractFactory("HardcardTimelockController");
  const timelock = await TimelockController.deploy(
    MIN_DELAY,
    [], // proposers - will be set to GovernorDAO
    [], // executors - anyone can execute
    ethers.ZeroAddress, // admin - will renounce after setup
    rootOwnerAddress
  );
  
  await timelock.waitForDeployment();
  const timelockAddress = await timelock.getAddress();
  
  console.log("TimelockController deployed to:", timelockAddress);
  console.log("Min delay:", MIN_DELAY, "seconds (48 hours)");
  
  // Deploy GovernorDAO
  const GovernorDAO = await ethers.getContractFactory("GovernorDAO");
  const governor = await GovernorDAO.deploy(
    VOTES_TOKEN_ADDRESS,
    timelockAddress,
    1, // voting delay: 1 block
    50400, // voting period: ~7 days (assuming 12s blocks)
    0 // proposal threshold
  );
  
  await governor.waitForDeployment();
  const governorAddress = await governor.getAddress();
  
  console.log("GovernorDAO deployed to:", governorAddress);
  
  // Setup roles
  const PROPOSER_ROLE = await timelock.PROPOSER_ROLE();
  const EXECUTOR_ROLE = await timelock.EXECUTOR_ROLE();
  const CANCELLER_ROLE = await timelock.CANCELLER_ROLE();
  
  console.log("\nSetting up Timelock roles...");
  
  // Grant proposer role to governor
  await timelock.grantRole(PROPOSER_ROLE, governorAddress);
  console.log("✓ Granted PROPOSER_ROLE to GovernorDAO");
  
  // Grant executor role to address(0) = anyone can execute
  await timelock.grantRole(EXECUTOR_ROLE, ethers.ZeroAddress);
  console.log("✓ Granted EXECUTOR_ROLE to everyone");
  
  // Grant canceller role to guardian council
  await timelock.grantRole(CANCELLER_ROLE, GUARDIAN_COUNCIL_ADDRESS);
  console.log("✓ Granted CANCELLER_ROLE to GuardianCouncil");
  
  const deploymentInfo = {
    timelock: timelockAddress,
    governor: governorAddress,
    minDelay: MIN_DELAY,
    rootOwner: rootOwnerAddress,
    deployedAt: new Date().toISOString()
  };
  
  console.log("\nDeployment info:", deploymentInfo);
  console.log("\n✅ Timelock and Governor deployed!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });