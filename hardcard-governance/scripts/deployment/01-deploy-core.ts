import { ethers } from "hardhat";
import { GuardianCouncil, TimelockController, GovernorDAO } from "../../typechain-types";
import * as fs from "fs";
import * as path from "path";
import { verify } from "../utils/verify";

interface DeploymentConfig {
  network: string;
  gasPrice?: number;
  timeout?: number;
  guardianAddresses: string[];
  initialDelay: number;
  votingDelay: number;
  votingPeriod: number;
  quorumPercentage: number;
  proposalThreshold: number;
}

interface DeploymentResult {
  guardianCouncil: string;
  timelockController: string;
  governorDAO: string;
  deploymentBlock: number;
  gasUsed: {
    guardianCouncil: string;
    timelockController: string;
    governorDAO: string;
    total: string;
  };
  transactionHashes: {
    guardianCouncil: string;
    timelockController: string;
    governorDAO: string;
  };
}

async function main() {
  console.log("\n🚀 Hardcard Governance Core Deployment");
  console.log("=" .repeat(50));
  
  const network = await ethers.provider.getNetwork();
  console.log(`Network: ${network.name} (${network.chainId})`);
  console.log(`Deployer: ${(await ethers.getSigners())[0].address}`);
  
  // Load deployment configuration
  const configPath = path.join(__dirname, `../../configs/deployment-${network.name}.json`);
  if (!fs.existsSync(configPath)) {
    throw new Error(`Deployment config not found: ${configPath}`);
  }
  
  const config: DeploymentConfig = JSON.parse(fs.readFileSync(configPath, "utf8"));
  console.log("Configuration loaded successfully");
  
  // Validate configuration
  validateConfig(config);
  
  // Get deployer account and check balance
  const [deployer] = await ethers.getSigners();
  const balance = await deployer.getBalance();
  console.log(`Deployer balance: ${ethers.utils.formatEther(balance)} ETH`);
  
  if (balance.lt(ethers.utils.parseEther("1"))) {
    throw new Error("Insufficient ETH balance for deployment");
  }
  
  // Gas price configuration
  const gasPrice = config.gasPrice 
    ? ethers.utils.parseUnits(config.gasPrice.toString(), "gwei")
    : await ethers.provider.getGasPrice();
  
  console.log(`Gas Price: ${ethers.utils.formatUnits(gasPrice, "gwei")} gwei`);
  
  const deploymentResult: DeploymentResult = {
    guardianCouncil: "",
    timelockController: "",
    governorDAO: "",
    deploymentBlock: 0,
    gasUsed: {
      guardianCouncil: "0",
      timelockController: "0", 
      governorDAO: "0",
      total: "0"
    },
    transactionHashes: {
      guardianCouncil: "",
      timelockController: "",
      governorDAO: ""
    }
  };
  
  let totalGasUsed = ethers.BigNumber.from(0);
  
  try {
    // Step 1: Deploy Guardian Council
    console.log("\n📋 Step 1: Deploying Guardian Council...");
    const GuardianCouncilFactory = await ethers.getContractFactory("GuardianCouncil");
    
    console.log("  Initial guardians:", config.guardianAddresses);
    console.log("  Threshold: 3/5");
    
    const guardianCouncil = await GuardianCouncilFactory.deploy(
      config.guardianAddresses,
      { gasPrice }
    );
    
    await guardianCouncil.deployed();
    const gcReceipt = await guardianCouncil.deployTransaction.wait();
    
    deploymentResult.guardianCouncil = guardianCouncil.address;
    deploymentResult.gasUsed.guardianCouncil = gcReceipt.gasUsed.toString();
    deploymentResult.transactionHashes.guardianCouncil = gcReceipt.transactionHash;
    totalGasUsed = totalGasUsed.add(gcReceipt.gasUsed);
    
    console.log(`  ✅ Guardian Council deployed to: ${guardianCouncil.address}`);
    console.log(`  Gas used: ${gcReceipt.gasUsed.toString()}`);
    
    // Step 2: Deploy Timelock Controller
    console.log("\n⏰ Step 2: Deploying Timelock Controller...");
    const TimelockControllerFactory = await ethers.getContractFactory("TimelockController");
    
    console.log(`  Initial delay: ${config.initialDelay} seconds (${config.initialDelay / 3600}h)`);
    console.log("  Proposers: Will be set to GovernorDAO after deployment");
    console.log("  Executors: Anyone can execute (address(0))");
    console.log(`  Admin: ${deployer.address} (will renounce after setup)`);
    
    const timelockController = await TimelockControllerFactory.deploy(
      config.initialDelay,
      [], // Proposers (will be set later)
      [], // Executors (address(0) allows anyone)
      deployer.address, // Admin (temporary)
      { gasPrice }
    );
    
    await timelockController.deployed();
    const tlcReceipt = await timelockController.deployTransaction.wait();
    
    deploymentResult.timelockController = timelockController.address;
    deploymentResult.gasUsed.timelockController = tlcReceipt.gasUsed.toString();
    deploymentResult.transactionHashes.timelockController = tlcReceipt.transactionHash;
    totalGasUsed = totalGasUsed.add(tlcReceipt.gasUsed);
    
    console.log(`  ✅ Timelock Controller deployed to: ${timelockController.address}`);
    console.log(`  Gas used: ${tlcReceipt.gasUsed.toString()}`);
    
    // Step 3: Deploy Governor DAO
    console.log("\n🏛️  Step 3: Deploying Governor DAO...");
    
    // For this example, we'll use a mock token or create a simple ERC20
    // In production, this would be the actual governance token
    const MockTokenFactory = await ethers.getContractFactory("MockERC20");
    const mockToken = await MockTokenFactory.deploy(
      "Hardcard Governance Token",
      "HGT",
      ethers.utils.parseEther("1000000"), // 1M tokens
      { gasPrice }
    );
    await mockToken.deployed();
    
    console.log(`  Governance token: ${mockToken.address}`);
    console.log(`  Voting delay: ${config.votingDelay} blocks`);
    console.log(`  Voting period: ${config.votingPeriod} blocks`);
    console.log(`  Quorum: ${config.quorumPercentage}%`);
    console.log(`  Proposal threshold: ${config.proposalThreshold} tokens`);
    
    const GovernorDAOFactory = await ethers.getContractFactory("GovernorDAO");
    const governorDAO = await GovernorDAOFactory.deploy(
      mockToken.address,
      timelockController.address,
      config.votingDelay,
      config.votingPeriod,
      config.proposalThreshold,
      config.quorumPercentage,
      { gasPrice }
    );
    
    await governorDAO.deployed();
    const gdReceipt = await governorDAO.deployTransaction.wait();
    
    deploymentResult.governorDAO = governorDAO.address;
    deploymentResult.gasUsed.governorDAO = gdReceipt.gasUsed.toString();
    deploymentResult.transactionHashes.governorDAO = gdReceipt.transactionHash;
    totalGasUsed = totalGasUsed.add(gdReceipt.gasUsed);
    
    console.log(`  ✅ Governor DAO deployed to: ${governorDAO.address}`);
    console.log(`  Gas used: ${gdReceipt.gasUsed.toString()}`);
    
    // Step 4: Configure Timelock Roles
    console.log("\n🔧 Step 4: Configuring Timelock roles...");
    
    const PROPOSER_ROLE = await timelockController.PROPOSER_ROLE();
    const EXECUTOR_ROLE = await timelockController.EXECUTOR_ROLE();
    const CANCELLER_ROLE = await timelockController.CANCELLER_ROLE();
    
    // Grant proposer role to GovernorDAO
    console.log("  Granting PROPOSER_ROLE to GovernorDAO...");
    const grantProposerTx = await timelockController.grantRole(
      PROPOSER_ROLE,
      governorDAO.address,
      { gasPrice }
    );
    await grantProposerTx.wait();
    
    // Grant executor role to everyone (address(0))
    console.log("  Granting EXECUTOR_ROLE to address(0)...");
    const grantExecutorTx = await timelockController.grantRole(
      EXECUTOR_ROLE,
      ethers.constants.AddressZero,
      { gasPrice }
    );
    await grantExecutorTx.wait();
    
    // Grant canceller role to Guardian Council
    console.log("  Granting CANCELLER_ROLE to GuardianCouncil...");
    const grantCancellerTx = await timelockController.grantRole(
      CANCELLER_ROLE,
      guardianCouncil.address,
      { gasPrice }
    );
    await grantCancellerTx.wait();
    
    // Step 5: Configure Guardian Council with Timelock
    console.log("\n🛡️  Step 5: Configuring Guardian Council...");
    
    // Set timelock as the target for guardian emergency actions
    console.log("  Setting timelock as emergency target...");
    const setTimelockTx = await guardianCouncil.setTimelockController(
      timelockController.address,
      { gasPrice }
    );
    await setTimelockTx.wait();
    
    // Final deployment block
    deploymentResult.deploymentBlock = await ethers.provider.getBlockNumber();
    deploymentResult.gasUsed.total = totalGasUsed.toString();
    
    // Step 6: Save deployment artifacts
    console.log("\n💾 Step 6: Saving deployment artifacts...");
    
    const deploymentDir = path.join(__dirname, `../../deployments/${network.name}`);
    fs.mkdirSync(deploymentDir, { recursive: true });
    
    // Save individual contract artifacts
    const contracts = [
      { name: "GuardianCouncil", address: guardianCouncil.address, contract: guardianCouncil },
      { name: "TimelockController", address: timelockController.address, contract: timelockController },
      { name: "GovernorDAO", address: governorDAO.address, contract: governorDAO },
      { name: "MockERC20", address: mockToken.address, contract: mockToken }
    ];
    
    for (const { name, address, contract } of contracts) {
      const artifact = {
        address,
        abi: contract.interface.format("json"),
        bytecode: contract.deployTransaction.data,
        deployer: deployer.address,
        deploymentBlock: deploymentResult.deploymentBlock,
        network: network.name,
        chainId: network.chainId,
        timestamp: new Date().toISOString()
      };
      
      fs.writeFileSync(
        path.join(deploymentDir, `${name}.json`),
        JSON.stringify(artifact, null, 2)
      );
    }
    
    // Save deployment summary
    const summary = {
      network: network.name,
      chainId: network.chainId,
      deployer: deployer.address,
      deploymentBlock: deploymentResult.deploymentBlock,
      timestamp: new Date().toISOString(),
      gasUsed: deploymentResult.gasUsed,
      transactionHashes: deploymentResult.transactionHashes,
      contracts: {
        guardianCouncil: deploymentResult.guardianCouncil,
        timelockController: deploymentResult.timelockController,
        governorDAO: deploymentResult.governorDAO,
        governanceToken: mockToken.address
      },
      configuration: config
    };
    
    fs.writeFileSync(
      path.join(deploymentDir, "deployment-summary.json"),
      JSON.stringify(summary, null, 2)
    );
    
    console.log(`  Artifacts saved to: ${deploymentDir}`);
    
    // Step 7: Verify contracts on Etherscan (if not local network)
    if (network.name !== "hardhat" && network.name !== "localhost") {
      console.log("\n🔍 Step 7: Verifying contracts on Etherscan...");
      
      try {
        await verify(guardianCouncil.address, [config.guardianAddresses]);
        console.log("  ✅ Guardian Council verified");
        
        await verify(timelockController.address, [
          config.initialDelay,
          [],
          [],
          deployer.address
        ]);
        console.log("  ✅ Timelock Controller verified");
        
        await verify(governorDAO.address, [
          mockToken.address,
          timelockController.address,
          config.votingDelay,
          config.votingPeriod,
          config.proposalThreshold,
          config.quorumPercentage
        ]);
        console.log("  ✅ Governor DAO verified");
        
      } catch (error) {
        console.log("  ⚠️  Contract verification failed (will retry later)");
        console.log(`     Error: ${error}`);
      }
    }
    
    // Deployment complete
    console.log("\n🎉 Core Deployment Complete!");
    console.log("=" .repeat(50));
    console.log(`Guardian Council: ${deploymentResult.guardianCouncil}`);
    console.log(`Timelock Controller: ${deploymentResult.timelockController}`);
    console.log(`Governor DAO: ${deploymentResult.governorDAO}`);
    console.log(`Total Gas Used: ${ethers.utils.formatUnits(totalGasUsed, 'gwei')} Gwei`);
    console.log(`Deployment Block: ${deploymentResult.deploymentBlock}`);
    
    console.log("\n📋 Next Steps:");
    console.log("1. Run post-deployment verification");
    console.log("2. Transfer ownership to governance system");
    console.log("3. Renounce deployer privileges");
    console.log("4. Update frontend configuration");
    console.log("5. Notify guardians of deployment");
    
    return deploymentResult;
    
  } catch (error) {
    console.error("\n❌ Deployment failed!");
    console.error(error);
    
    // Save partial deployment state for debugging
    const errorLog = {
      timestamp: new Date().toISOString(),
      network: network.name,
      deployer: deployer.address,
      error: error.message,
      partialState: deploymentResult
    };
    
    const errorDir = path.join(__dirname, "../../deployment-errors");
    fs.mkdirSync(errorDir, { recursive: true });
    fs.writeFileSync(
      path.join(errorDir, `error-${Date.now()}.json`),
      JSON.stringify(errorLog, null, 2)
    );
    
    throw error;
  }
}

function validateConfig(config: DeploymentConfig): void {
  if (!config.guardianAddresses || config.guardianAddresses.length !== 5) {
    throw new Error("Exactly 5 guardian addresses required");
  }
  
  for (const address of config.guardianAddresses) {
    if (!ethers.utils.isAddress(address)) {
      throw new Error(`Invalid guardian address: ${address}`);
    }
  }
  
  if (config.initialDelay < 172800) { // 48 hours
    throw new Error("Initial delay must be at least 48 hours");
  }
  
  if (config.quorumPercentage < 50 || config.quorumPercentage > 100) {
    throw new Error("Quorum percentage must be between 50 and 100");
  }
  
  if (config.votingDelay < 1) {
    throw new Error("Voting delay must be at least 1 block");
  }
  
  if (config.votingPeriod < 50400) { // ~7 days
    throw new Error("Voting period must be at least 7 days");
  }
}

// Execute deployment
if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}

export { main as deployCore, DeploymentConfig, DeploymentResult };