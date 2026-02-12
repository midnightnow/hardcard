#!/bin/bash
# 🛡️ MacAgent 3-2-1 Compliance Verification Script

cd /Users/studio/hardcard

echo "🔍 MacAgent 3-2-1 Compliance Verification"
echo "=========================================="
echo ""

# Set environment variables for this session
export RESTIC_REPOSITORY="$HOME/backup-restic-local"
export RESTIC_PASSWORD="hardcard-secure-backup-2025"

echo "Step 1: Test Time Machine Status"
echo "--------------------------------"
python3 worker_cli_v03_patch.py tm-status | jq '.'
echo ""

echo "Step 2: Test Restic Offsite Status" 
echo "-----------------------------------"
python3 worker_cli_v03_patch.py offsite-status | jq '.'
echo ""

echo "Step 3: Test Overall 3-2-1 Compliance"
echo "-------------------------------------"
python3 worker_cli_v03_patch.py full-status | jq '.'
echo ""

echo "Step 4: Beautiful Status Display"
echo "--------------------------------"
if [ -f "./backup-status" ]; then
    ./backup-status
else
    echo "⚠️  backup-status script not found"
fi
echo ""

echo "Step 5: Test New Provider Architecture"
echo "-------------------------------------"
if [ -f "test_new_providers.py" ]; then
    python3 test_new_providers.py
else
    echo "⚠️  test_new_providers.py not found"
fi
echo ""

echo "🎯 SUCCESS CRITERIA:"
echo "✅ tm-status shows 'ok': true and valid destination"
echo "✅ offsite-status shows 'ok': true and recent snapshot"
echo "✅ full-status shows '3_2_1_compliant': true"
echo "✅ backup-status shows green checkmarks"
echo "✅ Provider architecture tests pass"
echo ""
echo "If all checks pass, you have achieved true 3-2-1 compliance! 🛡️"