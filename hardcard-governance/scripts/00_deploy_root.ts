import { ethers } from "hardhat";

async function main() {
  console.log("Deploying Root Owner setup...");
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  
  // In production, this would be a cold HSM address
  const rootOwnerAddress = deployer.address;
  console.log("Root Owner address:", rootOwnerAddress);
  
  // Deploy a simple Votes token for governance (in production, use existing token)
  const VotesToken = await ethers.getContractFactory("contracts/mocks/VotesToken.sol:VotesToken");
  const votesToken = await VotesToken.deploy("Hardcard Governance Token", "HGT");
  await votesToken.waitForDeployment();
  
  console.log("Votes token deployed to:", await votesToken.getAddress());
  
  // Store deployment info
  const deploymentInfo = {
    rootOwner: rootOwnerAddress,
    votesToken: await votesToken.getAddress(),
    deployedAt: new Date().toISOString(),
    network: (await ethers.provider.getNetwork()).name
  };
  
  console.log("\nDeployment info:", deploymentInfo);
  console.log("\n✅ Root setup complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });