# Break-Glass Emergency Response Runbook

**Version:** 1.0  
**Last Updated:** 2025-06-28  
**Severity:** CRITICAL  
**Expected Duration:** 5-15 minutes  

## Overview

This runbook details emergency "break-glass" procedures for the Hardcard governance system. These procedures should ONLY be used in critical situations where normal governance processes cannot be followed due to active attacks, critical vulnerabilities, or system compromise.

## Emergency Response Levels

### Level 1: Guardian Freeze (3-5 min)
- **Threshold**: 3/5 Guardians
- **Impact**: Freezes contracts for 7 days
- **Use Case**: Suspicious activity, potential exploit

### Level 2: Root Veto (2-3 min)
- **Threshold**: Root Owner only
- **Impact**: Cancels pending timelock operations
- **Use Case**: Malicious governance proposal detected

### Level 3: Emergency Shutdown (5-10 min)
- **Threshold**: Root Owner + 3/5 Guardians
- **Impact**: Full system pause
- **Use Case**: Active exploit, critical vulnerability

## Pre-Flight Checklist

- [ ] Incident commander identified
- [ ] Communication channels secured
- [ ] Root Owner HSM accessible (Level 2/3)
- [ ] Guardian availability confirmed (Level 1/3)
- [ ] Legal team notified
- [ ] Public communication drafted

## Level 1: Guardian Emergency Freeze

### Trigger Conditions
- Suspicious transactions detected
- Anomalous contract behavior
- Potential exploit activity
- Failed security monitoring alerts

### Procedure

#### 1. Assess Threat (1 min)
```bash
# Check recent contract activity
npx hardhat run scripts_redteam/check_anomalies.ts --network mainnet

# Review transaction logs
cast logs --from-block -1000 --address $CONTRACT_ADDRESS
```

#### 2. Coordinate Guardian Response (2 min)
```
EMERGENCY ALERT - GUARDIAN ACTION REQUIRED

Threat Level: HIGH
Action Required: Emergency Freeze
Target: [CONTRACT_ADDRESS]
Reason: [Brief description]

Respond with "CONFIRMED" to participate in freeze
```

#### 3. Execute Freeze (1 min)
```bash
# Each guardian runs:
export GUARDIAN_PRIVATE_KEY="..." # From secure storage
export TARGET_CONTRACT="0x..." # Contract to freeze

npx hardhat run scripts/guardian_freeze.ts --network mainnet
```

**Guardian Freeze Script (`scripts/guardian_freeze.ts`):**
```typescript
import { ethers } from "hardhat";

async function main() {
  const [guardian] = await ethers.getSigners();
  const guardianCouncil = await ethers.getContractAt(
    "GuardianCouncil",
    process.env.GUARDIAN_COUNCIL_ADDRESS!
  );
  
  const target = process.env.TARGET_CONTRACT!;
  
  console.log(`Guardian ${guardian.address} voting to freeze ${target}`);
  
  const tx = await guardianCouncil.freeze(target);
  await tx.wait();
  
  console.log("✅ Freeze vote submitted");
  console.log("Transaction:", tx.hash);
}
```

#### 4. Verify Freeze (1 min)
```bash
# Check freeze status
cast call $GUARDIAN_COUNCIL "isFrozen(address)(bool)" $TARGET_CONTRACT

# Monitor for 3/5 threshold
npx hardhat run scripts/monitor_freeze_votes.ts --network mainnet
```

## Level 2: Root Owner Veto

### Trigger Conditions
- Malicious governance proposal in timelock
- Compromised governor voting
- Time-sensitive threat (<48h to execution)

### Procedure

#### 1. Identify Malicious Operation (1 min)
```bash
# List pending timelock operations
cast call $TIMELOCK_ADDRESS "getOperationState(bytes32)(uint8)" $OPERATION_ID

# Decode operation data
cast call $TIMELOCK_ADDRESS "getOperation(bytes32)" $OPERATION_ID
```

#### 2. Execute Emergency Veto (1 min)
```bash
# Root owner executes veto
export ROOT_OWNER_KEY="..." # From HSM
export OPERATION_ID="0x..." # Malicious operation ID

npx hardhat run scripts/root_veto.ts --network mainnet
```

**Root Veto Script (`scripts/root_veto.ts`):**
```typescript
import { ethers } from "hardhat";

async function main() {
  const timelock = await ethers.getContractAt(
    "HardcardTimelockController",
    process.env.TIMELOCK_ADDRESS!
  );
  
  const operationId = process.env.OPERATION_ID!;
  
  console.log(`🚨 EMERGENCY VETO: ${operationId}`);
  
  const tx = await timelock.emergencyVeto(operationId);
  await tx.wait();
  
  console.log("✅ Operation vetoed");
  console.log("Transaction:", tx.hash);
}
```

#### 3. Post-Veto Actions (1 min)
```bash
# Verify operation cancelled
cast call $TIMELOCK_ADDRESS "isOperationPending(bytes32)(bool)" $OPERATION_ID

# Notify guardians and community
echo "Emergency veto executed. See tx: $TX_HASH"
```

## Level 3: Emergency System Shutdown

### Trigger Conditions
- Active exploit draining funds
- Critical vulnerability with no immediate fix
- Complete governance compromise

### Procedure

#### 1. Root Owner Initiates (2 min)
```bash
# Pause all pausable contracts
export CONTRACTS_TO_PAUSE=("$CREDENTIAL_REGISTRY" "$SCHEMA_FACTORY")

for contract in "${CONTRACTS_TO_PAUSE[@]}"; do
  cast send $contract "pause()" --private-key $ROOT_OWNER_KEY
done
```

#### 2. Guardian Consensus Freeze (3 min)
```bash
# Freeze all critical contracts
# Requires 3/5 guardians to execute simultaneously

export CRITICAL_CONTRACTS=("$TIMELOCK" "$GOVERNOR" "$TREASURY")

# Each guardian executes
for contract in "${CRITICAL_CONTRACTS[@]}"; do
  npx hardhat run scripts/guardian_freeze.ts --network mainnet
done
```

#### 3. Emergency Migration Prep (5 min)
```bash
# Snapshot current state
npx hardhat run scripts/emergency_snapshot.ts --network mainnet

# Prepare migration contracts
cd contracts/emergency/
npx hardhat compile

# Deploy new safe contracts
npx hardhat run scripts/deploy_emergency_safe.ts --network mainnet
```

## Communication Templates

### Public Announcement (Level 1)
```
🔒 Hardcard Security Notice

The Guardian Council has initiated a precautionary freeze on [affected contracts].
This is a standard security measure lasting 7 days.
User funds are safe. Operations will resume after security review.

Details: [link to postmortem]
```

### Critical Alert (Level 2/3)
```
🚨 URGENT: Hardcard Emergency Response Active

Level: [2/3]
Status: [Veto Executed/System Paused]
Impact: [Describe impact]
Action Required: [User actions if any]

Full details: [security blog post]
Updates: [Twitter/Discord]
```

## Recovery Procedures

### After Level 1 Freeze (7 days)
1. Complete security audit
2. Deploy fixes if needed
3. Guardian vote to unfreeze (3/5)
4. Resume normal operations

### After Level 2 Veto
1. Investigate compromised proposal
2. Identify and ban malicious actors
3. Submit clean proposal if legitimate
4. Enhanced monitoring period

### After Level 3 Shutdown
1. Full post-mortem analysis
2. Contract upgrades/migration
3. Phased system restart
4. Compensation process if needed

## Monitoring Commands

```bash
# Real-time event monitoring
cast events --address $GUARDIAN_COUNCIL "ContractFrozen(address,uint256)"

# Check system health
npx hardhat run scripts/system_health_check.ts --network mainnet

# Export audit logs
npx hardhat run scripts/export_audit_logs.ts --network mainnet --output ./incident_logs/
```

## Key Contacts

### Internal
- **Incident Commander**: [SECURE CONTACT]
- **Root Owner**: [HSM CUSTODIAN]
- **Guardian Coordinator**: [SECURE CONTACT]
- **Legal Team**: [SECURE CONTACT]
- **Comms Lead**: [SECURE CONTACT]

### External
- **Security Auditor**: [CONTACT]
- **Crisis PR**: [CONTACT]
- **Exchange Partners**: [CONTACT LIST]

## Post-Incident Checklist

- [ ] Incident report drafted
- [ ] Root cause analysis complete
- [ ] Fixes deployed and tested
- [ ] User communications sent
- [ ] Regulatory notifications (if required)
- [ ] Runbook updated with lessons learned
- [ ] Security drill scheduled

## Appendix: Quick Reference

### Contract Addresses
```bash
GUARDIAN_COUNCIL="0x..."
TIMELOCK_ADDRESS="0x..."
GOVERNOR_ADDRESS="0x..."
CREDENTIAL_REGISTRY="0x..."
SCHEMA_FACTORY="0x..."
```

### Critical Commands
```bash
# Freeze
cast send $GUARDIAN_COUNCIL "freeze(address)" $TARGET --private-key $GUARDIAN_KEY

# Veto
cast send $TIMELOCK "emergencyVeto(bytes32)" $OPERATION_ID --private-key $ROOT_KEY

# Pause
cast send $CONTRACT "pause()" --private-key $OWNER_KEY

# Check Status
cast call $GUARDIAN_COUNCIL "isFrozen(address)(bool)" $TARGET
```

---

**WARNING**: This runbook contains sensitive security procedures. Access should be restricted to authorized personnel only. Regular drills should be conducted quarterly.