const { network } = require("hardhat");

module.exports = async ({ getNamedAccounts, deployments }) => {
  const { deploy, log } = deployments;
  const { deployer } = await getNamedAccounts();

  log("💳 Deploying HCC Stablecoin for Virtual Economy...");

  const constructorArgs = [
    "Hardcard Cash",      // name
    "HCC",               // symbol
    deployer             // initial owner
  ];

  const hccToken = await deploy("HardcardCash", {
    from: deployer,
    args: constructorArgs,
    log: true,
    waitConfirmations: network.config.blockConfirmations || 1,
  });

  log(`✅ HCC Token deployed to: ${hccToken.address}`);
  log(`🏭 Virtual stablecoin for biological ecosystem`);
  log(`💰 Virtual supply: 1,000,000,000 HCC tokens`);
  log(`🔒 Zero-cost operation enabled`);

  // Verify contract if not on local network
  if (network.name !== "hardhat" && network.name !== "localhost") {
    log("🔍 Verifying contract on block explorer...");
    await verify(hccToken.address, constructorArgs);
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

module.exports.tags = ["all", "hcc-token", "biological-system"];
module.exports.dependencies = [];