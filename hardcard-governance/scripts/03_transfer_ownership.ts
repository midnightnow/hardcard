import { ethers } from "hardhat";

async function main() {
  console.log("Transferring ownership of core contracts to Timelock...");
  
  const [deployer] = await ethers.getSigners();
  
  // These addresses would come from previous deployments
  const TIMELOCK_ADDRESS = "0x0000000000000000000000000000000000000000"; // Replace
  const CREDENTIAL_REGISTRY_ADDRESS = "0x0000000000000000000000000000000000000000"; // Replace
  const SCHEMA_FACTORY_ADDRESS = "0x0000000000000000000000000000000000000000"; // Replace
  
  // Get contract instances
  const CredentialRegistry = await ethers.getContractFactory("CredentialRegistry");
  const credentialRegistry = CredentialRegistry.attach(CREDENTIAL_REGISTRY_ADDRESS);
  
  const SchemaFactory = await ethers.getContractFactory("SchemaFactory");
  const schemaFactory = SchemaFactory.attach(SCHEMA_FACTORY_ADDRESS);
  
  console.log("\nCurrent owners:");
  console.log("CredentialRegistry owner:", await credentialRegistry.owner());
  console.log("SchemaFactory owner:", await schemaFactory.owner());
  
  // Transfer ownership
  console.log("\nTransferring ownership to Timelock...");
  
  const tx1 = await credentialRegistry.transferOwnership(TIMELOCK_ADDRESS);
  await tx1.wait();
  console.log("✓ CredentialRegistry ownership transferred");
  
  const tx2 = await schemaFactory.transferOwnership(TIMELOCK_ADDRESS);
  await tx2.wait();
  console.log("✓ SchemaFactory ownership transferred");
  
  console.log("\nNew owners:");
  console.log("CredentialRegistry owner:", await credentialRegistry.owner());
  console.log("SchemaFactory owner:", await schemaFactory.owner());
  
  console.log("\n✅ Ownership transfer complete!");
  console.log("\n⚠️  Important: The Timelock now controls all core contracts.");
  console.log("Any changes must go through the governance process with 48h delay.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });