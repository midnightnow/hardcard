# 📖 Hardcard Governance Operational Playbooks

**Version**: 1.0  
**Last Updated**: 2025-06-28  
**Purpose**: Standard operating procedures for common governance scenarios  
**Audience**: Operations team, guardians, security engineers

---

## 📚 Table of Contents

1. [Guardian Management](#guardian-management)
2. [Proposal Lifecycle](#proposal-lifecycle)
3. [Emergency Procedures](#emergency-procedures)
4. [System Maintenance](#system-maintenance)
5. [Security Incidents](#security-incidents)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Key Rotation](#key-rotation)
8. [Troubleshooting](#troubleshooting)

---

## 🛡️ Guardian Management

### Adding a New Guardian

**When to Use**: Expanding guardian council or replacing inactive guardian  
**Prerequisites**: Root owner access, new guardian identity verified  
**SLA**: Complete within 2 hours  

#### Process
1. **Preparation**
   ```bash
   # Verify current guardian state
   npx hardhat run scripts/ops/check-guardians.ts --network mainnet
   
   # Ensure we won't exceed max guardians (5)
   # Verify new guardian address is valid
   ```

2. **Generate Guardian Keys**
   ```bash
   cd ops/
   python3 gen_guardian_key.py \
     --guardian-id guardian_new \
     --output-dir ./new_guardian_keys
   
   # Verify key generation
   python3 gen_guardian_key.py --verify ./new_guardian_keys/guardian_new_*.json
   ```

3. **Execute Addition**
   ```bash
   npx hardhat run scripts/governance/add-guardian.ts \
     --guardian 0xNEW_GUARDIAN_ADDRESS \
     --network mainnet
   ```

4. **Distribute Shares**
   ```bash
   # Generate SSKR shares
   python3 gen_shares.py \
     --secret-file ./new_guardian_keys/guardian_new_*.json \
     --threshold 3 \
     --shares 5 \
     --guardian-id guardian_new
   
   # Distribute shares
   python3 distribute_shares.py \
     --shares-dir ./guardian_new_shares \
     --guardian-config ./guardian_config.yaml
   ```

5. **Verification**
   ```bash
   # Confirm addition
   npx hardhat run scripts/ops/check-guardians.ts --network mainnet
   
   # Test new guardian can vote
   npx hardhat run scripts/ops/test-guardian-vote.ts \
     --guardian 0xNEW_GUARDIAN_ADDRESS \
     --network sepolia  # Test on testnet first
   ```

#### Rollback Procedure
```bash
# If addition fails or guardian proves problematic
npx hardhat run scripts/governance/remove-guardian.ts \
  --guardian 0xNEW_GUARDIAN_ADDRESS \
  --reason "failed_verification" \
  --network mainnet
```

---

### Removing a Guardian

**When to Use**: Guardian compromise, extended unavailability, or voluntary exit  
**Prerequisites**: Root owner access, valid reason documented  
**SLA**: Emergency (< 1 hour), Planned (< 4 hours)  

#### Process
1. **Assessment**
   ```bash
   # Check current guardian status
   npx hardhat run scripts/ops/check-guardians.ts --network mainnet
   
   # Verify removal won't drop below minimum (3)
   # Document reason for removal
   ```

2. **Emergency Freeze (if compromised)**
   ```bash
   # If guardian is compromised, freeze first
   npx hardhat run scripts/ops/emergency-freeze-guardian.ts \
     --guardian 0xCOMPROMISED_GUARDIAN \
     --network mainnet
   ```

3. **Execute Removal**
   ```bash
   npx hardhat run scripts/governance/remove-guardian.ts \
     --guardian 0xGUARDIAN_TO_REMOVE \
     --reason "voluntary_exit" \
     --network mainnet
   ```

4. **Key Revocation**
   ```bash
   # Archive guardian keys
   ./archive-guardian-keys.sh 0xGUARDIAN_TO_REMOVE
   
   # Update share distribution
   python3 redistribute_shares.py \
     --removed-guardian 0xGUARDIAN_TO_REMOVE
   ```

5. **Communication**
   ```bash
   # Notify remaining guardians
   ./notify-guardians.sh \
     --message "Guardian removed: 0xGUARDIAN_TO_REMOVE" \
     --priority high
   ```

---

## 🗳️ Proposal Lifecycle

### Creating a Proposal

**When to Use**: Implementing governance changes  
**Prerequisites**: Proposer has sufficient tokens, proposal tested  
**SLA**: Submit within 24 hours of approval  

#### Process
1. **Proposal Preparation**
   ```bash
   # Create proposal document
   cp templates/proposal-template.md proposals/PROP-001-description.md
   
   # Review proposal format
   ./validate-proposal.sh proposals/PROP-001-description.md
   ```

2. **Technical Implementation**
   ```bash
   # Create execution script
   npx hardhat run scripts/proposals/prepare-proposal.ts \
     --title "Proposal Title" \
     --description "Description" \
     --targets "[\"0xTarget1\", \"0xTarget2\"]" \
     --values "[0, 0]" \
     --calldatas "[\"0xCalldata1\", \"0xCalldata2\"]"
   ```

3. **Submit Proposal**
   ```bash
   npx hardhat run scripts/proposals/submit-proposal.ts \
     --proposal-file ./prepared-proposal.json \
     --network mainnet
   ```

4. **Monitor Proposal**
   ```bash
   # Track voting progress
   npx hardhat run scripts/ops/monitor-proposal.ts \
     --proposal-id PROPOSAL_ID \
     --network mainnet
   ```

---

### Voting on Proposals

**When to Use**: Active proposal requires community decision  
**Prerequisites**: Voting power, proposal review completed  
**SLA**: Vote within 48 hours of proposal start  

#### Process
1. **Proposal Analysis**
   ```bash
   # Get proposal details
   npx hardhat run scripts/ops/get-proposal.ts \
     --proposal-id PROPOSAL_ID \
     --network mainnet
   
   # Review technical implementation
   ./analyze-proposal-impact.sh PROPOSAL_ID
   ```

2. **Cast Vote**
   ```bash
   # Vote: 0=Against, 1=For, 2=Abstain
   npx hardhat run scripts/governance/cast-vote.ts \
     --proposal-id PROPOSAL_ID \
     --support 1 \
     --reason "Supporting due to..." \
     --network mainnet
   ```

3. **Verify Vote**
   ```bash
   # Confirm vote was recorded
   npx hardhat run scripts/ops/verify-vote.ts \
     --proposal-id PROPOSAL_ID \
     --voter 0xVOTER_ADDRESS \
     --network mainnet
   ```

---

## 🚨 Emergency Procedures

### Emergency Freeze Activation

**When to Use**: Critical security threat detected  
**Prerequisites**: 3/5 guardian consensus  
**SLA**: Execute within 15 minutes  

#### Process
1. **Threat Assessment**
   ```bash
   # Document threat
   echo "EMERGENCY: $(date): Threat description" >> logs/emergency.log
   
   # Identify affected contracts
   ./identify-threat-scope.sh
   ```

2. **Guardian Coordination**
   ```bash
   # Alert all guardians
   ./emergency-alert-guardians.sh \
     --threat "Description of threat" \
     --target-contracts "0xContract1,0xContract2"
   
   # Set up emergency communication channel
   ./setup-emergency-comms.sh
   ```

3. **Execute Freeze**
   ```bash
   # Guardian 1
   npx hardhat run scripts/ops/emergency-freeze.ts \
     --target 0xTARGET_CONTRACT \
     --guardian-index 0 \
     --network mainnet
   
   # Guardian 2
   npx hardhat run scripts/ops/emergency-freeze.ts \
     --target 0xTARGET_CONTRACT \
     --guardian-index 1 \
     --network mainnet
   
   # Guardian 3 (triggers freeze when threshold reached)
   npx hardhat run scripts/ops/emergency-freeze.ts \
     --target 0xTARGET_CONTRACT \
     --guardian-index 2 \
     --network mainnet
   ```

4. **Post-Freeze Actions**
   ```bash
   # Verify freeze is active
   npx hardhat run scripts/ops/verify-freeze.ts \
     --target 0xTARGET_CONTRACT \
     --network mainnet
   
   # Notify stakeholders
   ./notify-freeze-activation.sh 0xTARGET_CONTRACT
   
   # Begin incident response
   ./start-incident-response.sh
   ```

---

### Emergency Unfreeze

**When to Use**: Threat resolved, normal operations can resume  
**Prerequisites**: Threat mitigation confirmed, 3/5 guardian consensus  
**SLA**: Execute within 1 hour of resolution  

#### Process
1. **Resolution Verification**
   ```bash
   # Confirm threat is resolved
   ./verify-threat-resolution.sh
   
   # Review system state
   npx hardhat run scripts/ops/system-health-check.ts --network mainnet
   ```

2. **Guardian Consensus**
   ```bash
   # Coordinate unfreeze vote
   ./coordinate-unfreeze-vote.sh 0xFROZEN_CONTRACT
   ```

3. **Execute Unfreeze**
   ```bash
   # Three guardians vote to unfreeze
   npx hardhat run scripts/ops/emergency-unfreeze.ts \
     --target 0xFROZEN_CONTRACT \
     --guardian-index 0 \
     --network mainnet
   
   npx hardhat run scripts/ops/emergency-unfreeze.ts \
     --target 0xFROZEN_CONTRACT \
     --guardian-index 1 \
     --network mainnet
   
   npx hardhat run scripts/ops/emergency-unfreeze.ts \
     --target 0xFROZEN_CONTRACT \
     --guardian-index 2 \
     --network mainnet
   ```

4. **Post-Unfreeze**
   ```bash
   # Verify normal operations
   ./test-normal-operations.sh 0xFROZEN_CONTRACT
   
   # Update incident log
   echo "RESOLVED: $(date): Contract unfrozen" >> logs/emergency.log
   
   # Notify stakeholders
   ./notify-unfreeze.sh 0xFROZEN_CONTRACT
   ```

---

### Root Owner Veto

**When to Use**: Catastrophic governance proposal or system compromise  
**Prerequisites**: Root owner access, extreme circumstances  
**SLA**: Execute within 30 minutes  

#### Process
1. **Veto Authorization**
   ```bash
   # Document veto reason
   echo "ROOT VETO: $(date): Reason" >> logs/root-actions.log
   
   # Verify veto authority
   ./verify-root-authority.sh
   ```

2. **Execute Veto**
   ```bash
   # Connect hardware security module
   ./connect-root-hsm.sh
   
   # Execute veto
   npx hardhat run scripts/governance/root-veto.ts \
     --operation-id OPERATION_ID \
     --reason "Catastrophic risk prevention" \
     --network mainnet
   ```

3. **Post-Veto**
   ```bash
   # Verify veto success
   npx hardhat run scripts/ops/verify-veto.ts \
     --operation-id OPERATION_ID \
     --network mainnet
   
   # Emergency communication
   ./emergency-broadcast.sh "Root veto executed: OPERATION_ID"
   
   # Begin governance review
   ./initiate-governance-review.sh
   ```

---

## 🔧 System Maintenance

### Timelock Delay Update

**When to Use**: Security posture change required  
**Prerequisites**: Governance approval, root owner access  
**SLA**: Complete within planned maintenance window  

#### Process
1. **Preparation**
   ```bash
   # Verify current delay
   npx hardhat run scripts/ops/check-timelock.ts --network mainnet
   
   # Calculate new delay (minimum 48 hours)
   NEW_DELAY=172800  # 48 hours in seconds
   ```

2. **Update Delay**
   ```bash
   npx hardhat run scripts/governance/update-timelock-delay.ts \
     --new-delay $NEW_DELAY \
     --network mainnet
   ```

3. **Verification**
   ```bash
   # Confirm delay update
   npx hardhat run scripts/ops/check-timelock.ts --network mainnet
   
   # Test delay enforcement
   ./test-timelock-delay.sh
   ```

---

### Contract Upgrade

**When to Use**: Bug fixes or feature additions approved by governance  
**Prerequisites**: Governance approval, tested implementation  
**SLA**: Complete within scheduled maintenance window  

#### Process
1. **Pre-Upgrade**
   ```bash
   # Backup current state
   ./backup-contract-state.sh
   
   # Verify upgrade safety
   ./verify-upgrade-safety.sh NEW_IMPLEMENTATION_ADDRESS
   ```

2. **Execute Upgrade**
   ```bash
   # Submit upgrade proposal
   npx hardhat run scripts/proposals/submit-upgrade.ts \
     --target PROXY_ADDRESS \
     --implementation NEW_IMPLEMENTATION_ADDRESS \
     --network mainnet
   ```

3. **Post-Upgrade**
   ```bash
   # Verify upgrade success
   ./verify-upgrade-success.sh PROXY_ADDRESS
   
   # Run integration tests
   npm run test:integration
   
   # Monitor system health
   ./monitor-post-upgrade.sh
   ```

---

## 🔒 Security Incidents

### Suspected Guardian Compromise

**When to Use**: Guardian key may be compromised  
**Prerequisites**: Evidence of compromise  
**SLA**: Immediate response (< 15 minutes)  

#### Process
1. **Immediate Response**
   ```bash
   # Emergency freeze if needed
   ./emergency-freeze-all.sh "Suspected guardian compromise"
   
   # Isolate suspected guardian
   ./isolate-guardian.sh 0xSUSPECTED_GUARDIAN
   ```

2. **Investigation**
   ```bash
   # Analyze recent transactions
   ./analyze-guardian-activity.sh 0xSUSPECTED_GUARDIAN
   
   # Check for unauthorized actions
   ./check-unauthorized-actions.sh 0xSUSPECTED_GUARDIAN
   ```

3. **Containment**
   ```bash
   # Rotate guardian if compromise confirmed
   npx hardhat run scripts/governance/emergency-rotate-guardian.ts \
     --compromised 0xSUSPECTED_GUARDIAN \
     --replacement 0xNEW_GUARDIAN \
     --network mainnet
   ```

---

### Smart Contract Vulnerability

**When to Use**: Critical vulnerability discovered in contracts  
**Prerequisites**: Vulnerability assessment completed  
**SLA**: Mitigation within 1 hour  

#### Process
1. **Assessment**
   ```bash
   # Evaluate vulnerability impact
   ./assess-vulnerability.sh VULNERABILITY_REPORT.md
   
   # Determine affected contracts
   ./identify-affected-contracts.sh
   ```

2. **Mitigation**
   ```bash
   # Emergency pause if available
   ./emergency-pause-contracts.sh
   
   # Implement hotfix if possible
   ./deploy-hotfix.sh VULNERABILITY_FIX
   ```

3. **Recovery**
   ```bash
   # Deploy permanent fix
   ./deploy-permanent-fix.sh
   
   # Resume operations
   ./resume-operations.sh
   ```

---

## 📊 Monitoring & Alerting

### Alert Response

**When to Use**: Critical alert received  
**Prerequisites**: Alert classification system  
**SLA**: Acknowledge within 5 minutes, respond within 15 minutes  

#### Process
1. **Alert Triage**
   ```bash
   # Check alert details
   ./check-alert-details.sh ALERT_ID
   
   # Assess severity
   ./assess-alert-severity.sh ALERT_ID
   ```

2. **Response**
   ```bash
   # Execute appropriate playbook
   case $ALERT_TYPE in
     "guardian_inactive")
       ./playbooks/guardian-inactive-response.sh
       ;;
     "emergency_freeze")
       ./playbooks/emergency-freeze-response.sh
       ;;
     "system_down")
       ./playbooks/system-down-response.sh
       ;;
   esac
   ```

3. **Resolution**
   ```bash
   # Mark alert resolved
   ./resolve-alert.sh ALERT_ID "Resolution description"
   
   # Update runbook if needed
   ./update-runbook.sh ALERT_TYPE
   ```

---

### System Health Check

**When to Use**: Regular maintenance or after incidents  
**Prerequisites**: Monitoring access  
**SLA**: Complete within 30 minutes  

#### Process
```bash
# Comprehensive system check
./comprehensive-health-check.sh

# Guardian status
npx hardhat run scripts/ops/check-guardians.ts --network mainnet

# Timelock status
npx hardhat run scripts/ops/check-timelock.ts --network mainnet

# Proposal status
npx hardhat run scripts/ops/check-proposals.ts --network mainnet

# Network connectivity
./check-network-connectivity.sh

# Generate health report
./generate-health-report.sh
```

---

## 🔑 Key Rotation

### Scheduled Guardian Key Rotation

**When to Use**: Quarterly security maintenance  
**Prerequisites**: All guardians available, new keys generated  
**SLA**: Complete within 4 hours  

#### Process
1. **Preparation**
   ```bash
   # Schedule rotation window
   ./schedule-rotation-window.sh "2025-07-01 02:00 UTC"
   
   # Pre-generate new keys
   for i in {1..5}; do
     python3 gen_guardian_key.py --guardian-id guardian_$i --output-dir ./rotation_keys/
   done
   ```

2. **Execution**
   ```bash
   # Run fire drill to practice
   ./fire-drills/fire-drill.sh start planned-rotation sepolia
   
   # Execute actual rotation
   ./execute-key-rotation.sh --rotation-plan rotation_plan.json
   ```

3. **Verification**
   ```bash
   # Test new keys
   ./test-all-guardian-keys.sh
   
   # Verify system functionality
   ./comprehensive-functionality-test.sh
   ```

---

## 🔧 Troubleshooting

### Common Issues

#### Transaction Failing
```bash
# Check gas settings
npx hardhat run scripts/debug/check-gas-price.ts --network mainnet

# Verify contract state
npx hardhat run scripts/debug/verify-contract-state.ts --network mainnet

# Check account balance
npx hardhat run scripts/debug/check-balances.ts --network mainnet
```

#### Guardian Vote Not Counting
```bash
# Verify guardian status
npx hardhat run scripts/ops/check-guardian-status.ts \
  --guardian 0xGUARDIAN_ADDRESS \
  --network mainnet

# Check vote timing
npx hardhat run scripts/debug/check-vote-timing.ts \
  --proposal-id PROPOSAL_ID \
  --network mainnet

# Verify vote transaction
npx hardhat run scripts/debug/verify-vote-tx.ts \
  --tx-hash 0xTRANSACTION_HASH \
  --network mainnet
```

#### Timelock Not Executing
```bash
# Check execution prerequisites
npx hardhat run scripts/debug/check-execution-prereqs.ts \
  --operation-id OPERATION_ID \
  --network mainnet

# Verify delay period
npx hardhat run scripts/debug/check-delay-period.ts \
  --operation-id OPERATION_ID \
  --network mainnet

# Check operation status
npx hardhat run scripts/debug/check-operation-status.ts \
  --operation-id OPERATION_ID \
  --network mainnet
```

---

## 📞 Emergency Contacts

### Primary Response Team
- **Security Lead**: security-lead@hardcard.io / +1-XXX-XXX-XXXX
- **DevOps Lead**: devops-lead@hardcard.io / +1-XXX-XXX-XXXX
- **CTO**: cto@hardcard.io / +1-XXX-XXX-XXXX

### Guardian Contacts
- **Guardian 1**: guardian1@hardcard.io / +1-XXX-XXX-XXXX
- **Guardian 2**: guardian2@hardcard.io / +1-XXX-XXX-XXXX
- **Guardian 3**: guardian3@hardcard.io / +1-XXX-XXX-XXXX
- **Guardian 4**: guardian4@hardcard.io / +1-XXX-XXX-XXXX
- **Guardian 5**: guardian5@hardcard.io / +1-XXX-XXX-XXXX

### External Partners
- **Security Auditor**: auditor@securityfirm.com
- **Legal Counsel**: legal@lawfirm.com
- **Insurance Provider**: claims@insuranceco.com

---

## 📚 Quick Reference

### Command Shortcuts
```bash
# Add to your ~/.bashrc or ~/.zshrc
alias hc-guardians="npx hardhat run scripts/ops/check-guardians.ts --network mainnet"
alias hc-proposals="npx hardhat run scripts/ops/check-proposals.ts --network mainnet"
alias hc-timelock="npx hardhat run scripts/ops/check-timelock.ts --network mainnet"
alias hc-health="./comprehensive-health-check.sh"
alias hc-freeze="npx hardhat run scripts/ops/emergency-freeze.ts"
alias hc-unfreeze="npx hardhat run scripts/ops/emergency-unfreeze.ts"
```

### Status Codes
- **0**: Success
- **1**: General error
- **2**: Configuration error
- **3**: Network error
- **4**: Authorization error
- **5**: Validation error

### Log Locations
- **System Logs**: `/var/log/hardcard/`
- **Guardian Logs**: `./logs/guardian-*.log`
- **Emergency Logs**: `./logs/emergency.log`
- **Audit Logs**: `./logs/audit-*.log`

---

**Note**: These playbooks should be regularly reviewed and updated based on operational experience. All procedures should be tested in non-production environments before deployment to mainnet.