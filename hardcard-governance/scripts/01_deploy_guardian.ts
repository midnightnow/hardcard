import { ethers } from "hardhat";

async function main() {
  console.log("Deploying Guardian Council...");
  
  const [deployer] = await ethers.getSigners();
  const rootOwnerAddress = deployer.address; // In production, use cold HSM address
  
  const GUARDIAN_THRESHOLD = 3;
  const MAX_GUARDIANS = 5;
  
  const GuardianCouncil = await ethers.getContractFactory("GuardianCouncil");
  const guardianCouncil = await GuardianCouncil.deploy(
    GUARDIAN_THRESHOLD,
    MAX_GUARDIANS,
    rootOwnerAddress
  );
  
  await guardianCouncil.waitForDeployment();
  const guardianAddress = await guardianCouncil.getAddress();
  
  console.log("GuardianCouncil deployed to:", guardianAddress);
  console.log("Threshold:", GUARDIAN_THRESHOLD);
  console.log("Max guardians:", MAX_GUARDIANS);
  
  // In production, add initial guardians
  console.log("\n⚠️  Remember to add guardian addresses using addGuardian()");
  
  const deploymentInfo = {
    guardianCouncil: guardianAddress,
    threshold: GUARDIAN_THRESHOLD,
    maxGuardians: MAX_GUARDIANS,
    rootOwner: rootOwnerAddress,
    deployedAt: new Date().toISOString()
  };
  
  console.log("\nDeployment info:", deploymentInfo);
  console.log("\n✅ Guardian Council deployed!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });