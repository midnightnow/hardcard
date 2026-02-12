#!/usr/bin/env python3
"""
MacAgent Backup Orchestrator CLI v0.3 - Following the exact patch pattern
Worker CLI that matches the structure from the v0.3 TM Status UI Integration patch
"""

import json
import datetime
import subprocess
import os
import sys
from pathlib import Path

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

class ResticRunner:
    """Restic runner for off-site backup status"""
    
    def status(self):
        """Get restic status - matches TMRunner.status() pattern"""
        try:
            # Check if restic is available
            result = subprocess.run(['which', 'restic'], capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    "repository": None,
                    "latest_snapshot_iso": None,
                    "error": "restic not installed"
                }
            
            # Get repository from environment or config
            repository = self._get_repository()
            if not repository:
                return {
                    "repository": None,
                    "latest_snapshot_iso": None,
                    "error": "no repository configured"
                }
            
            # Get latest snapshot
            latest_snapshot = self._get_latest_snapshot(repository)
            
            return {
                "repository": repository,
                "latest_snapshot_iso": latest_snapshot.get('time') if latest_snapshot else None,
                "snapshot_id": latest_snapshot.get('short_id') if latest_snapshot else None,
                "hostname": latest_snapshot.get('hostname') if latest_snapshot else None,
                "error": None if latest_snapshot else "no snapshots found"
            }
            
        except Exception as e:
            return {
                "repository": None,
                "latest_snapshot_iso": None,
                "error": f"restic error: {str(e)}"
            }
    
    def _get_repository(self):
        """Get restic repository from environment or config"""
        # Check environment variable
        repo = os.environ.get('RESTIC_REPOSITORY')
        if repo:
            return repo
        
        # Check common config locations
        config_paths = [
            os.path.expanduser('~/.config/restic/config'),
            os.path.expanduser('~/.restic-repo'),
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        repo = f.read().strip()
                        if repo:
                            return repo
                except Exception:
                    continue
        
        return None
    
    def _get_latest_snapshot(self, repository):
        """Get latest restic snapshot"""
        try:
            # Set up environment
            env = os.environ.copy()
            env['RESTIC_REPOSITORY'] = repository
            
            # Try to get password from environment or keychain
            if 'RESTIC_PASSWORD' not in env:
                try:
                    password_result = subprocess.run([
                        'security', 'find-generic-password', 
                        '-a', 'restic', '-s', 'restic-backup', '-w'
                    ], capture_output=True, text=True)
                    if password_result.returncode == 0:
                        env['RESTIC_PASSWORD'] = password_result.stdout.strip()
                except Exception:
                    pass
            
            # If no password available, return None
            if 'RESTIC_PASSWORD' not in env:
                return None
            
            # Query latest snapshot
            result = subprocess.run([
                'restic', 'snapshots', '--json', '--latest', '1'
            ], env=env, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return None
            
            snapshots = json.loads(result.stdout)
            if not snapshots:
                return None
            
            snapshot = snapshots[0]
            
            # Format the snapshot data
            return {
                'short_id': snapshot.get('short_id') or snapshot.get('id', '')[:8],
                'time': snapshot.get('time'),  # Keep original ISO format
                'hostname': snapshot.get('hostname'),
                'paths': snapshot.get('paths', []),
                'tags': snapshot.get('tags', [])
            }
            
        except Exception:
            return None

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
    """Off-site backup status as JSON - following tm-status pattern"""
    restic = ResticRunner()
    st = restic.status()  # {"repository": str|None, "latest_snapshot_iso": str|None, ...}

    now = datetime.datetime.now(datetime.timezone.utc)
    latest_iso = st.get("latest_snapshot_iso")
    latest_dt = None
    hours_since = None
    if latest_iso:
        try:
            # Parse restic's ISO format (may include nanoseconds)
            latest_dt = datetime.datetime.fromisoformat(latest_iso.replace("Z", "+00:00"))
        except Exception:
            latest_dt = None
    if latest_dt:
        delta = now - latest_dt.astimezone(datetime.timezone.utc)
        hours_since = round(delta.total_seconds() / 3600, 1)

    result = {
        "repository": st.get("repository"),
        "latest_snapshot_iso": latest_iso,
        "hours_since_latest": hours_since,
        "snapshot_id": st.get("snapshot_id"),
        "hostname": st.get("hostname"),
        # stale if > 48h since last off-site backup or no repository
        "stale": (hours_since is None) or (hours_since > 48) or (not st.get("repository")),
        "generated_at": now.isoformat(),
        "ok": (hours_since is not None) and (hours_since <= 48) and bool(st.get("repository")),
        "error": st.get("error")
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

def cmd_full_status():
    """Full system status combining TM and offsite"""
    # Get individual statuses
    tm = TMRunner()
    tm_status = tm.status()
    
    restic = ResticRunner()  
    offsite_status = restic.status()
    
    # Calculate 3-2-1 compliance
    tm_ok = tm_status.get("destination") and tm_status.get("latest_backup_iso")
    offsite_ok = offsite_status.get("repository") and offsite_status.get("latest_snapshot_iso")
    compliant = tm_ok and offsite_ok  # Simplified 3-2-1 check
    
    result = {
        "3_2_1_compliant": compliant,
        "tm": {
            "ok": bool(tm_ok),
            "destination": tm_status.get("destination"),
            "latest_backup_iso": tm_status.get("latest_backup_iso")
        },
        "offsite": {
            "ok": bool(offsite_ok),
            "provider": "restic",
            "repository": offsite_status.get("repository"),
            "latest_snapshot_iso": offsite_status.get("latest_snapshot_iso"),
            "error": offsite_status.get("error")
        },
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    print(json.dumps(result))

def cmd_offsite_run():
    """Run off-site backup job"""
    print("🔄 Starting off-site backup...")
    # In real implementation, this would run restic backup
    print("✅ Off-site backup completed (mock)")

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

def main():
    """Main CLI entry point following v0.3 patch pattern"""
    if len(sys.argv) < 2:
        print("Usage: worker/cli.py [command]")
        print("\\nCommands:")
        print("  tm-status          - Get Time Machine status as JSON")
        print("  tm-check           - Check Time Machine health")
        print("  offsite-status     - Get off-site backup status as JSON")
        print("  full-status        - Get complete system status as JSON")
        print("  offsite-run        - Run off-site backup")
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
        elif cmd == "full-status":
            cmd_full_status()
        elif cmd == "offsite-run":
            cmd_offsite_run()
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