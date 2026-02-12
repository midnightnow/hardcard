# Guardian Key Rotation Runbook

**Version:** 1.0  
**Last Updated:** 2025-06-28  
**Severity:** HIGH  
**Expected Duration:** 15-30 minutes  

## Overview

This runbook details the procedure for rotating a compromised or at-risk Guardian key in the Hardcard governance system. Key rotation is a critical security operation that must be performed carefully to maintain system integrity.

## Pre-Conditions

- [ ] Root Owner HSM key is accessible
- [ ] At least 3/5 acting Guardians are reachable and verified
- [ ] New Guardian candidate has been vetted and verified
- [ ] Hardhat environment is configured and tested
- [ ] Access to contract addresses from deployment

## Trigger Conditions

Execute this runbook when:
- Guardian private key compromise is suspected or confirmed
- Guardian requests key rotation for security reasons
- Periodic rotation schedule is reached (quarterly recommended)
- Guardian is leaving the organization

## Step-by-Step Procedure

### 1. Initial Assessment (5 min)

```bash
# Check current guardian status
npx hardhat run scripts/check_guardian_status.ts --network mainnet

# Verify current guardian count and threshold
echo "Expected: 5 guardians, 3/5 threshold"
```

### 2. Coordinate with Guardians (10 min)

1. **Notify all guardians** via secure channel:
   ```
   Subject: [URGENT] Guardian Key Rotation Required
   
   Guardian [X] key rotation initiated.
   Reason: [compromise/scheduled/resignation]
   
   Please standby for emergency votes if needed.
   ```

2. **Confirm availability** of at least 3 guardians for emergency actions

### 3. Generate New Guardian Key (2 min)

```bash
# Generate new guardian key and shares
cd ops/
python3 gen_shares.py --guardian-count 5 --threshold 3 --output-dir ./rotation_shares

# Extract new guardian address
NEW_GUARDIAN_ADDRESS=$(cat rotation_shares/metadata.json | jq -r '.guardians.guardian_1.public_address')
echo "New Guardian Address: $NEW_GUARDIAN_ADDRESS"
```

### 4. Execute Rotation Transaction (5 min)

```bash
# Set environment variables
export OLD_GUARDIAN_ADDRESS="0x..." # Address to rotate out
export NEW_GUARDIAN_ADDRESS="0x..." # New guardian address
export GUARDIAN_COUNCIL_ADDRESS="0x..." # From deployment
export ROOT_OWNER_PRIVATE_KEY="..." # From HSM

# Run rotation script
npx hardhat run scripts/guardian_rotate.ts --network mainnet
```

**Script Template (`scripts/guardian_rotate.ts`):**
```typescript
import { ethers } from "hardhat";

async function main() {
  const guardianCouncil = await ethers.getContractAt(
    "GuardianCouncil",
    process.env.GUARDIAN_COUNCIL_ADDRESS!
  );
  
  const oldGuardian = process.env.OLD_GUARDIAN_ADDRESS!;
  const newGuardian = process.env.NEW_GUARDIAN_ADDRESS!;
  
  console.log(`Rotating guardian ${oldGuardian} -> ${newGuardian}`);
  
  const tx = await guardianCouncil.rotateGuardian(oldGuardian, newGuardian);
  await tx.wait();
  
  console.log("✅ Guardian rotated successfully");
  console.log("Transaction:", tx.hash);
}

main().catch(console.error);
```

### 5. Verification (3 min)

```bash
# Verify rotation completed
npx hardhat run scripts/check_guardian_status.ts --network mainnet

# Confirm new guardian in list
# Confirm old guardian removed
# Confirm count still equals 5
```

### 6. Distribute New Shares (5 min)

1. **Securely distribute** new SSKR shares to guardians:
   - Each guardian receives ONLY their share file
   - Use encrypted channels (Signal, PGP email)
   - Confirm receipt with each guardian

2. **Update documentation**:
   ```bash
   # Archive old shares
   mv guardian_shares/ guardian_shares_archived_$(date +%Y%m%d)/
   
   # Move new shares into place
   mv rotation_shares/ guardian_shares/
   ```

### 7. Post-Rotation Actions

1. **Test emergency freeze** with new guardian set:
   ```bash
   npx hardhat test test/integration/guardian_freeze_test.ts --network mainnet-fork
   ```

2. **Update access control systems**:
   - Remove old guardian from communication channels
   - Add new guardian to secure channels
   - Update guardian contact list

3. **Audit log entry**:
   ```json
   {
     "event": "guardian_rotation",
     "timestamp": "2025-06-28T10:00:00Z",
     "old_guardian": "0x...",
     "new_guardian": "0x...",
     "reason": "scheduled_rotation",
     "executed_by": "root_owner",
     "tx_hash": "0x..."
   }
   ```

## Rollback Procedure

If rotation fails or needs reversal:

1. **Within 48 hours**: Root owner can execute another rotation back
2. **After 48 hours**: Requires guardian consensus (3/5) to freeze and recover

```bash
# Emergency rollback
export OLD_GUARDIAN_ADDRESS=$NEW_GUARDIAN_ADDRESS
export NEW_GUARDIAN_ADDRESS=$ORIGINAL_GUARDIAN_ADDRESS
npx hardhat run scripts/guardian_rotate.ts --network mainnet
```

## Security Considerations

- **NEVER** share guardian private keys or multiple SSKR shares with one person
- **ALWAYS** verify guardian identity through multiple channels before rotation
- **IMMEDIATELY** revoke compromised guardian access to all systems
- **MAINTAIN** audit trail of all rotation operations

## Monitoring & Alerts

After rotation, monitor for:
- Unexpected guardian transactions
- Failed freeze attempts
- Anomalous voting patterns

```bash
# Set up monitoring
npx hardhat run scripts/monitor_guardian_events.ts --network mainnet
```

## Success Criteria

- [ ] Old guardian successfully removed from GuardianCouncil
- [ ] New guardian successfully added with correct permissions
- [ ] Guardian count remains at 5
- [ ] All guardians have received and confirmed new shares
- [ ] Emergency freeze test passes with new guardian set
- [ ] Audit log updated
- [ ] Monitoring alerts configured

## Emergency Contacts

- **Root Owner**: [SECURE CONTACT]
- **Guardian Coordinator**: [SECURE CONTACT]
- **Security Team**: [SECURE CONTACT]
- **Legal**: [SECURE CONTACT]

---

**Note**: This runbook should be reviewed quarterly and after each rotation event. Store securely and limit access to authorized personnel only.