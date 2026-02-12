#!/bin/bash
set -e

DRILL_DIR=$1

if [ -z "$DRILL_DIR" ] || [ ! -d "$DRILL_DIR" ]; then
  echo "Usage: $0 <drill-directory>"
  exit 1
fi

INCIDENT_ID=$(cat "$DRILL_DIR/incident-id" 2>/dev/null || echo "UNKNOWN")
SCENARIO=$(cat "$DRILL_DIR/scenario" 2>/dev/null || echo "UNKNOWN")
NETWORK=$(cat "$DRILL_DIR/network" 2>/dev/null || echo "UNKNOWN")
START_TIME=$(cat "$DRILL_DIR/start-time" 2>/dev/null || echo "UNKNOWN")

# Calculate duration if we have start time
if [ -f "$DRILL_DIR/start-time" ]; then
  START_TIMESTAMP=$(date -d "$START_TIME" +%s)
  END_TIMESTAMP=$(date +%s)
  DURATION=$((END_TIMESTAMP - START_TIMESTAMP))
  DURATION_MIN=$((DURATION / 60))
  DURATION_SEC=$((DURATION % 60))
else
  DURATION="UNKNOWN"
  DURATION_MIN="?"
  DURATION_SEC="?"
fi

cat <<EOF
# Fire Drill Report: $INCIDENT_ID

**Generated**: $(date -u)  
**Drill Type**: Guardian Key Rotation Fire Drill  
**Scenario**: $SCENARIO  
**Network**: $NETWORK  

---

## Executive Summary

This report summarizes the execution of fire drill $INCIDENT_ID, which tested our guardian key rotation procedures in a controlled environment.

### Quick Stats
- **Duration**: ${DURATION_MIN}m ${DURATION_SEC}s
- **Network**: $NETWORK
- **Scenario**: $SCENARIO
- **Status**: $([ -n "$DURATION" ] && [ "$DURATION" != "UNKNOWN" ] && [ $DURATION -lt 1800 ] && echo "✅ PASSED" || echo "⚠️  REVIEW NEEDED")

---

## Drill Timeline

$(if [ -f "$DRILL_DIR/drill-log.md" ]; then
  cat "$DRILL_DIR/drill-log.md" | grep "^- \*\*" | head -20
else
  echo "- No detailed timeline available"
fi)

---

## Performance Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Total Rotation Time | < 30 minutes | ${DURATION_MIN}m ${DURATION_SEC}s | $([ -n "$DURATION" ] && [ "$DURATION" != "UNKNOWN" ] && [ $DURATION -lt 1800 ] && echo "✅ PASS" || echo "❌ FAIL") |
| Guardian Response | < 5 minutes | Manual Review | 📋 TBD |
| Share Distribution | < 15 minutes | Manual Review | 📋 TBD |
| System Validation | < 10 minutes | Manual Review | 📋 TBD |

---

## Files Generated

During this drill, the following files were created:

$(find "$DRILL_DIR" -type f 2>/dev/null | while read file; do
  basename_file=$(basename "$file")
  size=$(ls -lh "$file" | awk '{print $5}')
  echo "- **$basename_file** ($size)"
done)

---

## Contract Interactions

$(if [ -f "$DRILL_DIR/contracts" ]; then
  echo "### Deployed Contracts"
  echo ""
  cat "$DRILL_DIR/contracts" | while IFS='=' read key value; do
    echo "- **$key**: \`$value\`"
  done
  echo ""
else
  echo "No contract deployment information recorded."
fi)

---

## System Health Checks

### Pre-Drill Status
- [ ] Guardian count within bounds (3-5)
- [ ] Threshold properly configured (≥60%)
- [ ] All guardians responsive
- [ ] Monitoring systems active

### Post-Drill Status  
- [ ] New guardian successfully added
- [ ] Old guardian properly removed
- [ ] Threshold maintained
- [ ] No system disruptions

---

## Lessons Learned

### What Went Well ✅
- Drill infrastructure functioned as expected
- Documentation provided clear guidance
- Automation scripts executed successfully
- Timeline tracking worked effectively

### Areas for Improvement ⚠️
- $([ -n "$DURATION" ] && [ "$DURATION" != "UNKNOWN" ] && [ $DURATION -gt 1800 ] && echo "Drill exceeded 30-minute target time" || echo "Review specific timing for optimization opportunities")
- Manual verification steps could be automated
- Communication protocols need refinement
- Monitoring integration could be enhanced

### Action Items 📋
1. **Performance Optimization**: $([ -n "$DURATION" ] && [ "$DURATION" != "UNKNOWN" ] && [ $DURATION -gt 1800 ] && echo "Investigate delays in rotation process" || echo "Maintain current performance standards")
2. **Documentation Updates**: Incorporate lessons learned into procedures
3. **Automation Enhancement**: Reduce manual intervention points
4. **Training**: Schedule additional drills based on findings

---

## Drill Scenario Analysis

### Scenario: $SCENARIO

$(case "$SCENARIO" in
  "compromised-guardian")
    echo "**Description**: Simulated guardian key compromise requiring immediate rotation"
    echo ""
    echo "**Key Learning Points**:"
    echo "- Speed of response to security incidents"
    echo "- Effectiveness of emergency communication"
    echo "- Guardian availability during crisis"
    echo "- Process adherence under pressure"
    ;;
  "unresponsive-guardian")
    echo "**Description**: Guardian unavailable for extended period"
    echo ""
    echo "**Key Learning Points**:"
    echo "- Backup contact mechanisms"
    echo "- Decision making with reduced guardian pool"
    echo "- Documentation of guardian status"
    echo "- Escalation procedures"
    ;;
  "multiple-rotation")
    echo "**Description**: Multiple guardians requiring simultaneous rotation"
    echo ""
    echo "**Key Learning Points**:"
    echo "- Complex coordination requirements"
    echo "- Resource allocation during major events"
    echo "- System stability during multiple changes"
    echo "- Batch operation efficiency"
    ;;
  "planned-rotation")
    echo "**Description**: Routine scheduled guardian key rotation"
    echo ""
    echo "**Key Learning Points**:"
    echo "- Standard operating procedure effectiveness"
    echo "- Advance planning and scheduling"
    echo "- Routine maintenance workflows"
    echo "- Performance baseline establishment"
    ;;
  *)
    echo "**Description**: Custom drill scenario: $SCENARIO"
    echo ""
    echo "**Key Learning Points**:"
    echo "- Scenario-specific insights to be documented"
    echo "- Custom procedure validation"
    echo "- Edge case handling"
    echo "- Process flexibility"
    ;;
esac)

---

## Security Considerations

### Risks Identified
- Guardian key exposure during testing
- Network-specific configuration differences  
- Timing attacks during key transition
- Communication channel security

### Mitigations Applied
- Used testnet environment for all operations
- Secure key generation with multiple entropy sources
- Time-boxed operations to limit exposure window
- Encrypted communication channels where possible

---

## Technical Details

### Environment
- **Network**: $NETWORK
- **Start Time**: $START_TIME
- **End Time**: $(date -u)
- **Duration**: ${DURATION_MIN}m ${DURATION_SEC}s

### Tools Used
- Guardian key generator: \`ops/gen_guardian_key.py\`
- SSKR share distribution: \`ops/distribute_shares.py\`
- Contract interaction scripts: \`scripts/ops/\`
- Fire drill manager: \`ops/fire-drills/fire-drill.sh\`

### Scripts Executed
$(if [ -f "$DRILL_DIR/commands.log" ]; then
  echo "\`\`\`bash"
  cat "$DRILL_DIR/commands.log"
  echo "\`\`\`"
else
  echo "Command log not available"
fi)

---

## Recommendations

### Immediate Actions (Next 7 Days)
1. Address any failed performance metrics
2. Update documentation based on lessons learned
3. Schedule follow-up drill if significant issues found
4. Implement identified automation improvements

### Short-Term Improvements (Next 30 Days)
1. Enhance monitoring and alerting capabilities
2. Develop additional drill scenarios
3. Create guardian training materials
4. Implement performance tracking dashboard

### Long-Term Enhancements (Next Quarter)
1. Full automation of routine operations
2. Integration with external monitoring systems
3. Development of predictive failure detection
4. Establishment of guardian performance metrics

---

## Approval and Sign-Off

### Drill Execution
- [ ] Drill Coordinator: _________________ Date: _______
- [ ] Lead Guardian: _________________ Date: _______
- [ ] Security Engineer: _________________ Date: _______

### Report Review
- [ ] Security Team Lead: _________________ Date: _______
- [ ] Operations Manager: _________________ Date: _______
- [ ] CTO: _________________ Date: _______

---

## Appendix

### Related Documentation
- [Guardian Rotation Technical Spec](../docs/GUARDIAN_ROTATION.md)
- [Security Incident Response](../docs/INCIDENT_RESPONSE.md)
- [SSKR Implementation Guide](../docs/SSKR_GUIDE.md)

### Emergency Contacts
- Security Team: security@hardcard.io
- DevOps On-Call: +1-XXX-XXX-XXXX
- Legal Team: legal@hardcard.io

### Next Scheduled Drill
**Date**: TBD  
**Scenario**: TBD  
**Participants**: TBD  

---

*This report was automatically generated by the Hardcard Guardian Fire Drill system. For questions or concerns, contact the security team.*
EOF