# 🚨 Guardian Key Rotation Fire Drill Runbook

**Version**: 1.0  
**Last Updated**: 2025-06-28  
**Classification**: OPERATIONAL - TRAINING  
**Purpose**: Practice guardian key rotation in a controlled environment

---

## 🎯 Fire Drill Objectives

1. **Test key rotation procedures** without affecting production
2. **Train team members** on emergency response procedures
3. **Identify gaps** in documentation or tooling
4. **Measure response times** for each step
5. **Build muscle memory** for real emergencies

---

## 📋 Pre-Drill Checklist

### Environment Setup
- [ ] Testnet contracts deployed
- [ ] Test guardian accounts created (5 guardians)
- [ ] Test SSKR shares generated and distributed
- [ ] Fire drill coordinator assigned
- [ ] All participants available (minimum 3/5 guardians)
- [ ] Communication channels tested
- [ ] Monitoring dashboards ready
- [ ] Timer/stopwatch ready

### Participant Roles
- **Drill Coordinator**: Manages the exercise
- **Incident Commander**: Leads the rotation
- **Guardian Operators**: Execute key operations
- **Observer**: Documents issues and timing
- **Root Owner Operator**: Executes contract changes

---

## 🔄 Fire Drill Scenarios

### Scenario 1: Planned Rotation (Routine Maintenance)
**Trigger**: Scheduled quarterly key rotation  
**Severity**: Low  
**Target Time**: 2 hours  

### Scenario 2: Compromised Guardian (Security Incident)
**Trigger**: Guardian reports potential key compromise  
**Severity**: High  
**Target Time**: 30 minutes  

### Scenario 3: Unresponsive Guardian (Operational Issue)
**Trigger**: Guardian unreachable for 24 hours  
**Severity**: Medium  
**Target Time**: 1 hour  

### Scenario 4: Multiple Guardian Rotation (Major Incident)
**Trigger**: 2+ guardians need immediate rotation  
**Severity**: Critical  
**Target Time**: 45 minutes  

---

## 📝 Drill Execution Steps

### Phase 1: Initiation (T+0 to T+5 minutes)
```bash
# Coordinator starts the drill
./fire-drill.sh start --scenario compromised-guardian --testnet

# Expected output:
# 🚨 FIRE DRILL INITIATED
# Scenario: Compromised Guardian
# Network: Sepolia Testnet
# Start Time: 2025-06-28 10:00:00 UTC
# Incident ID: DRILL-2025-06-28-001
```

1. **Coordinator Actions**:
   - [ ] Announce drill start in #security-drills channel
   - [ ] Start timer
   - [ ] Assign incident ID
   - [ ] Notify all participants

2. **Incident Commander Actions**:
   - [ ] Acknowledge incident
   - [ ] Review scenario parameters
   - [ ] Confirm guardian availability
   - [ ] Open incident log

### Phase 2: Assessment (T+5 to T+15 minutes)

3. **Guardian Status Check**:
   ```bash
   # Check current guardian configuration
   npx hardhat run scripts/ops/check-guardians.ts --network sepolia
   
   # Verify compromised guardian
   echo "Guardian 3 (0x789...) marked as COMPROMISED"
   ```

4. **Document Current State**:
   - [ ] Current guardian addresses
   - [ ] Current threshold (3/5)
   - [ ] Recent guardian actions
   - [ ] Contract freeze status

### Phase 3: Preparation (T+15 to T+25 minutes)

5. **Generate New Guardian Keys**:
   ```bash
   # Generate new guardian keypair
   cd ops/
   python3 gen_guardian_key.py --guardian-id guardian_3_new --testnet
   
   # Split into SSKR shares
   python3 gen_shares.py \
     --secret-file guardian_3_new_key.json \
     --threshold 3 \
     --shares 5 \
     --guardian-id guardian_3_new
   ```

6. **Prepare Rotation Transaction**:
   ```javascript
   // scripts/ops/prepare-rotation.ts
   const oldGuardian = "0x789..."; // Compromised
   const newGuardian = "0xABC..."; // New guardian
   
   const tx = await guardianCouncil.rotateGuardian(
     oldGuardian,
     newGuardian
   );
   
   console.log("Rotation TX prepared:", tx.hash);
   ```

### Phase 4: Execution (T+25 to T+35 minutes)

7. **Execute Guardian Rotation**:
   ```bash
   # Root owner executes rotation
   npx hardhat run scripts/ops/rotate-guardian.ts \
     --old 0x789... \
     --new 0xABC... \
     --network sepolia
   ```

8. **Verify Rotation**:
   ```bash
   # Confirm new guardian set
   npx hardhat run scripts/ops/verify-guardians.ts --network sepolia
   
   # Expected output:
   # ✅ Guardian rotation successful
   # Old: 0x789... (REMOVED)
   # New: 0xABC... (ACTIVE)
   # Threshold: 3/5 (unchanged)
   ```

### Phase 5: Distribution (T+35 to T+50 minutes)

9. **Distribute New Shares**:
   ```bash
   # Use distribution script
   python3 distribute_shares.py \
     --shares-dir ./guardian_3_new_shares \
     --guardian-config ./fire_drill_guardians.yaml \
     --dry-run # Remove for actual distribution
   ```

10. **Confirm Receipt**:
    - [ ] Guardian 1 confirms share received
    - [ ] Guardian 2 confirms share received  
    - [ ] Guardian 3 (new) confirms share received
    - [ ] Guardian 4 confirms share received
    - [ ] Guardian 5 confirms share received

### Phase 6: Validation (T+50 to T+60 minutes)

11. **Test New Configuration**:
    ```bash
    # Attempt test freeze with new guardian set
    npx hardhat run scripts/ops/test-freeze.ts \
      --guardians 1,2,3_new \
      --target 0xTEST... \
      --network sepolia
    ```

12. **Verify System Health**:
    - [ ] All guardians can sign
    - [ ] Threshold voting works
    - [ ] Old guardian cannot act
    - [ ] Events properly emitted

### Phase 7: Conclusion (T+60 minutes)

13. **End Drill**:
    ```bash
    ./fire-drill.sh complete --incident-id DRILL-2025-06-28-001
    
    # Generates report
    ```

14. **Document Results**:
    - Total time: _______ minutes
    - Issues encountered: _______
    - Process improvements: _______

---

## 📊 Drill Metrics

### Target Performance Indicators
| Metric | Target | Actual | Pass/Fail |
|--------|--------|--------|-----------|
| Total rotation time | < 30 min | _____ | _____ |
| Guardian response time | < 5 min | _____ | _____ |
| Share distribution | < 15 min | _____ | _____ |
| Validation complete | < 10 min | _____ | _____ |
| No security incidents | 0 | _____ | _____ |

### Communication Effectiveness
- [ ] All participants received initial alert
- [ ] Updates posted every 5 minutes
- [ ] Clear command structure maintained
- [ ] No confusion about roles

### Technical Performance
- [ ] All scripts executed successfully
- [ ] No transaction failures
- [ ] Monitoring detected all changes
- [ ] Logs captured correctly

---

## 🔍 Common Issues and Solutions

### Issue 1: Guardian Unavailable
**Problem**: Not enough guardians respond (< 3/5)  
**Solution**: 
```bash
# Use backup guardian contacts
./notify-backup-guardians.sh --priority urgent

# If still insufficient, escalate to root owner
./escalate-to-root.sh --reason guardian-availability
```

### Issue 2: Transaction Fails
**Problem**: Rotation transaction reverts  
**Solution**:
```bash
# Check gas settings
export GAS_MULTIPLIER=1.5

# Retry with higher gas
npx hardhat run scripts/ops/rotate-guardian.ts \
  --gas-price 50 \
  --gas-limit 500000
```

### Issue 3: Share Distribution Delays
**Problem**: Email/messaging delays  
**Solution**:
```bash
# Use alternate distribution method
python3 distribute_shares.py \
  --method encrypted-file \
  --urgent
```

---

## 🎓 Lessons Learned Template

After each drill, complete this template:

### Drill Information
- Date: _______
- Scenario: _______
- Participants: _______
- Duration: _______

### What Went Well
1. _______
2. _______
3. _______

### What Could Be Improved
1. _______
2. _______
3. _______

### Action Items
| Item | Owner | Due Date |
|------|-------|----------|
| _____ | _____ | _____ |
| _____ | _____ | _____ |

### Process Updates Needed
- [ ] Documentation updates
- [ ] Script improvements
- [ ] Communication enhancements
- [ ] Tool additions

---

## 🚀 Drill Automation Scripts

### Initialize Drill Environment
```bash
#!/bin/bash
# fire-drill.sh

set -e

COMMAND=$1
SCENARIO=${2:-"compromised-guardian"}
NETWORK=${3:-"sepolia"}

case $COMMAND in
  start)
    echo "🚨 FIRE DRILL INITIATED"
    echo "Scenario: $SCENARIO"
    echo "Network: $NETWORK"
    echo "Start Time: $(date -u)"
    echo "Incident ID: DRILL-$(date +%Y-%m-%d-%H%M)"
    
    # Deploy test contracts if needed
    if [ ! -f ".fire-drill-contracts" ]; then
      npx hardhat run scripts/deploy.ts --network $NETWORK
      echo "GUARDIAN_COUNCIL=$(cat deployments/$NETWORK/GuardianCouncil.json | jq -r .address)" > .fire-drill-contracts
    fi
    
    # Start monitoring
    ./start-monitoring.sh --drill-mode &
    
    # Notify participants
    ./notify-participants.sh --channel security-drills --message "Fire drill started: $SCENARIO"
    ;;
    
  complete)
    INCIDENT_ID=$2
    END_TIME=$(date -u)
    
    echo "✅ FIRE DRILL COMPLETE"
    echo "End Time: $END_TIME"
    
    # Generate report
    ./generate-drill-report.sh $INCIDENT_ID > "reports/drill-$INCIDENT_ID.md"
    
    # Stop monitoring
    pkill -f "start-monitoring.sh --drill-mode"
    
    # Cleanup
    rm -f .fire-drill-contracts
    ;;
    
  *)
    echo "Usage: $0 {start|complete} [scenario] [network]"
    exit 1
    ;;
esac
```

### Quick Guardian Check
```typescript
// scripts/ops/check-guardians.ts
import { ethers } from "hardhat";

async function main() {
  const guardianCouncil = await ethers.getContractAt(
    "GuardianCouncil",
    process.env.GUARDIAN_COUNCIL_ADDRESS!
  );
  
  const guardianCount = await guardianCouncil.getGuardianCount();
  const threshold = await guardianCouncil.getThreshold();
  
  console.log(`\n🛡️  Guardian Status`);
  console.log(`${"=".repeat(50)}`);
  console.log(`Total Guardians: ${guardianCount}`);
  console.log(`Threshold: ${threshold}`);
  console.log(`\nActive Guardians:`);
  
  for (let i = 0; i < guardianCount; i++) {
    const guardian = await guardianCouncil.getGuardian(i);
    const lastAction = await guardianCouncil.getLastAction(guardian);
    console.log(`  ${i + 1}. ${guardian}`);
    console.log(`     Last action: ${new Date(lastAction * 1000).toISOString()}`);
  }
}

main().catch(console.error);
```

---

## 📚 Additional Resources

### Emergency Contacts
- Security Team: security@hardcard.io
- DevOps On-Call: +1-XXX-XXX-XXXX
- Legal Team: legal@hardcard.io

### Documentation
- [Guardian Rotation Technical Spec](../docs/GUARDIAN_ROTATION.md)
- [Security Incident Response](../docs/INCIDENT_RESPONSE.md)
- [SSKR Implementation Guide](../docs/SSKR_GUIDE.md)

### Tools
- Guardian Key Generator: `ops/gen_guardian_key.py`
- Share Distribution: `ops/distribute_shares.py`
- Rotation Scripts: `scripts/ops/rotate-guardian.ts`
- Monitoring Dashboard: `https://monitoring.hardcard.io/guardians`

---

**Remember**: Fire drills are learning opportunities. The goal is continuous improvement, not perfection. Document everything, learn from mistakes, and iterate on the process.