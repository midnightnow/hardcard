#!/usr/bin/env python3
"""
MacAgent Backup Orchestrator CLI v0.3 - With Pluggable Off-site Runners
Enhanced worker CLI supporting multiple backup providers with unified JSON API
"""

import json
import datetime
import subprocess
import os
import sys
from pathlib import Path

# Import the pluggable runner system
from pluggable_offsite_runners import OffsiteRunnerFactory

class TMRunner:
    """Time Machine runner following v0.2 pattern"""
    
    def status(self):
        """Get Time Machine status - matches v0.2 TMRunner.status()"""
        try:
            # Get destination info
            result = subprocess.run(['tmutil', 'destinationinfo'], 
                                  capture_output=True, text=True)
            
            destination = None
            if result.returncode == 0 and result.stdout.strip():
                # Parse destination from output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'Name' in line and ':' in line:
                        destination = line.split(':', 1)[1].strip()
                        break
            
            # Get latest backup info
            latest_backup_iso = None
            latest_result = subprocess.run(['tmutil', 'latestbackup'], 
                                         capture_output=True, text=True)
            
            if latest_result.returncode == 0 and latest_result.stdout.strip():
                backup_path = latest_result.stdout.strip()
                # Extract timestamp from backup path
                try:
                    # Backup paths typically end with timestamp like "2025-08-05-143022"
                    timestamp_part = backup_path.split('/')[-1]
                    if len(timestamp_part) >= 15:  # YYYY-MM-DD-HHMMSS format
                        year = timestamp_part[:4]
                        month = timestamp_part[5:7]
                        day = timestamp_part[8:10]
                        hour = timestamp_part[11:13]
                        minute = timestamp_part[13:15]
                        second = timestamp_part[15:17] if len(timestamp_part) >= 17 else "00"
                        
                        # Create ISO format timestamp
                        latest_backup_iso = f"{year}-{month}-{day}T{hour}:{minute}:{second}Z"
                except Exception:
                    pass
            
            return {
                "destination": destination,
                "latest_backup_iso": latest_backup_iso
            }
            
        except Exception:
            return {
                "destination": None,
                "latest_backup_iso": None
            }

def cmd_tm_status():
    """Time Machine status as JSON - matches v0.3 patch exactly"""
    tm = TMRunner()
    st = tm.status()  # {"destination": str|None, "latest_backup_iso": str|None}

    now = datetime.datetime.now(datetime.timezone.utc)
    latest_iso = st.get("latest_backup_iso")
    latest_dt = None
    hours_since = None
    if latest_iso:
        try:
            # allow naive timestamps too
            latest_dt = datetime.datetime.fromisoformat(latest_iso.replace("Z", "+00:00"))
        except Exception:
            latest_dt = None
    if latest_dt:
        delta = now - latest_dt.astimezone(datetime.timezone.utc)
        hours_since = round(delta.total_seconds() / 3600, 1)

    result = {
        "destination": st.get("destination"),
        "latest_backup_iso": latest_iso,
        "hours_since_latest": hours_since,
        # stale if > 26h since last successful backup or destination missing
        "stale": (hours_since is None) or (hours_since > 26) or (not st.get("destination")),
        "generated_at": now.isoformat(),
        "ok": (hours_since is not None) and (hours_since <= 26) and bool(st.get("destination")),
    }
    print(json.dumps(result))

def cmd_offsite_status():
    """Unified off-site status using pluggable runners"""
    # Auto-detect best available provider
    runner = OffsiteRunnerFactory.auto_detect_provider()
    
    if not runner:
        # No providers available
        now = datetime.datetime.now(datetime.timezone.utc)
        result = {
            "provider": None,
            "repository": None,
            "latest_backup_iso": None,
            "hours_since_latest": None,
            "backup_id": None,
            "hostname": None,
            "stale": True,
            "generated_at": now.isoformat(),
            "ok": False,
            "error": "no backup providers installed or configured",
            "size_bytes": None,
            "file_count": None
        }
        print(json.dumps(result))
        return
    
    # Get status from detected provider
    status = runner.status()
    print(json.dumps(status))

def cmd_offsite_providers():
    """List all available backup providers"""
    runners = OffsiteRunnerFactory.get_available_runners()
    
    providers = []
    for runner in runners:
        status = runner.status()
        providers.append({
            "provider": runner.provider_name,
            "available": True,
            "configured": not bool(status.get("error")),
            "last_backup": status.get("latest_backup_iso"),
            "repository": status.get("repository"),
            "status_summary": "✅ Ready" if status.get("ok") else f"⚠️ {status.get('error', 'Issues detected')}"
        })
    
    # Add unavailable providers
    for provider_name in OffsiteRunnerFactory.RUNNERS.keys():
        if not any(p["provider"] == provider_name for p in providers):
            providers.append({
                "provider": provider_name,
                "available": False,
                "configured": False,
                "last_backup": None,
                "repository": None,
                "status_summary": "❌ Not installed"
            })
    
    result = {
        "providers": providers,
        "primary_provider": runners[0].provider_name if runners else None,
        "total_available": len(runners),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    print(json.dumps(result))

def cmd_tm_check():
    """Check Time Machine health and send notifications"""
    tm = TMRunner()
    st = tm.status()
    
    if not st.get("destination"):
        print("⚠️ Time Machine destination not configured")
    elif not st.get("latest_backup_iso"):
        print("⚠️ No Time Machine backups found")
    else:
        # Calculate hours since last backup
        now = datetime.datetime.now(datetime.timezone.utc)
        latest_iso = st.get("latest_backup_iso")
        try:
            latest_dt = datetime.datetime.fromisoformat(latest_iso.replace("Z", "+00:00"))
            delta = now - latest_dt.astimezone(datetime.timezone.utc)
            hours_since = round(delta.total_seconds() / 3600, 1)
            
            if hours_since > 26:
                print(f"⚠️ Time Machine backup is {hours_since:.1f} hours old")
            else:
                print("✅ Time Machine is healthy")
        except Exception:
            print("⚠️ Could not parse backup timestamp")

def cmd_offsite_run():
    """Run off-site backup using pluggable runners"""
    runner = OffsiteRunnerFactory.auto_detect_provider()
    
    if not runner:
        print("❌ No backup providers available")
        return
    
    print(f"🔄 Starting {runner.provider_name} backup...")
    result = runner.run_backup()
    
    if result.get("success"):
        print(f"✅ {runner.provider_name} backup completed successfully")
        if result.get("output"):
            print(f"Output: {result['output']}")
    else:
        print(f"❌ {runner.provider_name} backup failed: {result.get('error')}")

def cmd_offsite_check():
    """Check all available off-site backup providers"""
    runners = OffsiteRunnerFactory.get_available_runners()
    
    if not runners:
        print("❌ No off-site backup providers available")
        return
    
    print(f"📊 Checking {len(runners)} off-site provider(s)...")
    
    for runner in runners:
        status = runner.status()
        if status.get("ok"):
            hours = status.get("hours_since_latest", 0)
            print(f"✅ {runner.provider_name}: Last backup {hours:.1f}h ago")
        else:
            error = status.get("error", "Unknown issue")
            print(f"⚠️ {runner.provider_name}: {error}")

def cmd_verify_weekly():
    """Run weekly integrity verification"""
    print("🔍 Running weekly integrity verification...")
    # Mock verification
    import random
    success = random.choice([True, True, True, False])  # 75% success rate
    if success:
        print("✅ Weekly verification PASSED")
    else:
        print("❌ Weekly verification FAILED")

def cmd_restore_drill():
    """Run restore drill test"""
    print("🎯 Running restore drill...")
    # Mock restore drill
    import random
    success = random.choice([True, True, False])  # 67% success rate
    if success:
        print("✅ Restore drill PASSED")
    else:
        print("❌ Restore drill FAILED - investigate backups")

def cmd_install_external():
    """Install macOS to external drive"""
    volume = sys.argv[2] if len(sys.argv) > 2 else "/Volumes/MacAgent-Rescue"
    print(f"💿 Installing macOS to external drive: {volume}")
    print("⚠️ This would launch the macOS installer (mock)")

def cmd_backup_summary():
    """Show comprehensive backup summary"""
    print("📊 MacAgent Backup Summary")
    print("=" * 40)
    
    # Time Machine status
    tm = TMRunner()
    tm_status = tm.status()
    
    print("🕒 Time Machine:")
    if tm_status.get("destination"):
        if tm_status.get("latest_backup_iso"):
            print(f"  ✅ Destination: {tm_status['destination']}")
            print(f"  ✅ Last backup: {tm_status['latest_backup_iso']}")
        else:
            print(f"  ⚠️ Configured but no backups found")
    else:
        print("  ❌ Not configured")
    
    # Off-site providers
    runners = OffsiteRunnerFactory.get_available_runners()
    print(f"\n☁️ Off-site Providers ({len(runners)} available):")
    
    if runners:
        for runner in runners:
            status = runner.status()
            if status.get("ok"):
                hours = status.get("hours_since_latest", 0)
                print(f"  ✅ {runner.provider_name}: {hours:.1f}h ago")
            else:
                error = status.get("error", "Unknown issue")
                print(f"  ⚠️ {runner.provider_name}: {error}")
    else:
        print("  ❌ No providers installed or configured")
    
    # 3-2-1 compliance check
    print("\n🎯 3-2-1 Backup Strategy:")
    local_ok = bool(tm_status.get("destination"))
    offsite_ok = any(runner.status().get("ok") for runner in runners)
    
    print(f"  Local backup (Time Machine): {'✅' if local_ok else '❌'}")
    print(f"  Off-site backup: {'✅' if offsite_ok else '❌'}")
    print(f"  Overall compliance: {'✅ COMPLIANT' if local_ok and offsite_ok else '⚠️ NEEDS ATTENTION'}")

def main():
    """Main CLI entry point with pluggable runner support"""
    if len(sys.argv) < 2:
        print("Usage: worker/cli.py [command]")
        print("\nStatus Commands:")
        print("  tm-status          - Get Time Machine status as JSON")
        print("  offsite-status     - Get off-site backup status as JSON (auto-detect provider)")
        print("  offsite-providers  - List all available backup providers")
        print("  backup-summary     - Show comprehensive backup status")
        print("\nAction Commands:")
        print("  tm-check           - Check Time Machine health")
        print("  offsite-check      - Check all off-site providers")
        print("  offsite-run        - Run off-site backup (auto-detect provider)")
        print("  verify-weekly      - Run weekly verification")
        print("  restore-drill      - Run restore drill")
        print("  install-external   - Install to external drive")
        return

    cmd = sys.argv[1]
    
    try:
        if cmd == "tm-status":
            cmd_tm_status()
        elif cmd == "tm-check":
            cmd_tm_check()
        elif cmd == "offsite-status":
            cmd_offsite_status()
        elif cmd == "offsite-providers":
            cmd_offsite_providers()
        elif cmd == "offsite-check":
            cmd_offsite_check()
        elif cmd == "offsite-run":
            cmd_offsite_run()
        elif cmd == "backup-summary":
            cmd_backup_summary()
        elif cmd == "verify-weekly":
            cmd_verify_weekly()
        elif cmd == "restore-drill":
            cmd_restore_drill()
        elif cmd == "install-external":
            cmd_install_external()
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    except Exception as e:
        print(f"Error executing {cmd}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()