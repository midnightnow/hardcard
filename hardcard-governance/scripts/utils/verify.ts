import { run } from "hardhat";

/**
 * Verify contract on Etherscan
 * @param address Contract address
 * @param constructorArguments Constructor arguments
 * @param contractPath Optional contract path for verification
 */
export async function verify(
  address: string, 
  constructorArguments: any[] = [],
  contractPath?: string
): Promise<void> {
  console.log(`Verifying contract at ${address}...`);
  
  try {
    const verifyArgs: any = {
      address,
      constructorArguments,
    };
    
    if (contractPath) {
      verifyArgs.contract = contractPath;
    }
    
    await run("verify:verify", verifyArgs);
    console.log(`✅ Contract verified successfully`);
    
  } catch (error: any) {
    if (error.message.toLowerCase().includes("already verified")) {
      console.log(`ℹ️  Contract already verified`);
    } else {
      console.log(`❌ Verification failed: ${error.message}`);
      throw error;
    }
  }
}

/**
 * Batch verify multiple contracts
 * @param contracts Array of contract verification data
 */
export async function batchVerify(contracts: Array<{
  address: string;
  constructorArguments: any[];
  contractPath?: string;
  name?: string;
}>): Promise<void> {
  console.log(`\n🔍 Batch verifying ${contracts.length} contracts...`);
  
  const results: Array<{ name?: string; address: string; success: boolean; error?: string }> = [];
  
  for (const contract of contracts) {
    try {
      console.log(`\nVerifying ${contract.name || contract.address}...`);
      await verify(contract.address, contract.constructorArguments, contract.contractPath);
      results.push({ 
        name: contract.name, 
        address: contract.address, 
        success: true 
      });
    } catch (error: any) {
      results.push({ 
        name: contract.name, 
        address: contract.address, 
        success: false, 
        error: error.message 
      });
    }
  }
  
  // Summary
  console.log(`\n📊 Verification Summary:`);
  console.log("=" .repeat(60));
  
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);
  
  console.log(`✅ Successful: ${successful.length}/${contracts.length}`);
  if (successful.length > 0) {
    successful.forEach(r => {
      console.log(`   ${r.name || "Contract"}: ${r.address}`);
    });
  }
  
  if (failed.length > 0) {
    console.log(`\n❌ Failed: ${failed.length}/${contracts.length}`);
    failed.forEach(r => {
      console.log(`   ${r.name || "Contract"}: ${r.address}`);
      console.log(`     Error: ${r.error}`);
    });
  }
}