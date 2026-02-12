const { network } = require("hardhat");

module.exports = async ({ getNamedAccounts, deployments }) => {
  const { deploy, log } = deployments;
  const { deployer } = await getNamedAccounts();

  log("🧬 Deploying HGOV Token for Biological System...");

  const constructorArgs = [
    "Hardcard Governance", // name
    "HGOV",               // symbol
    deployer              // initial owner
  ];

  const hgovToken = await deploy("HGOVToken", {
    from: deployer,
    args: constructorArgs,
    log: true,
    waitConfirmations: network.config.blockConfirmations || 1,
  });

  log(`✅ HGOV Token deployed to: ${hgovToken.address}`);
  log(`🧪 Virtual economy enabled for biological agents`);
  log(`💰 Virtual supply: 10,000,000,000 HGOV tokens`);
  log(`🎯 Bridge threshold: 50,000 virtual HGOV`);

  // Verify contract if not on local network
  if (network.name !== "hardhat" && network.name !== "localhost") {
    log("🔍 Verifying contract on block explorer...");
    await verify(hgovToken.address, constructorArgs);
  }
};

async function verify(contractAddress, args) {
  const { run } = require("hardhat");
  
  try {
    await run("verify:verify", {
      address: contractAddress,
      constructorArguments: args,
    });
    log("✅ Contract verified successfully");
  } catch (e) {
    if (e.message.toLowerCase().includes("already verified")) {
      log("📋 Contract already verified");
    } else {
      log("❌ Verification failed:", e.message);
    }
  }
}

module.exports.tags = ["all", "hgov-token", "biological-system"];
module.exports.dependencies = [];