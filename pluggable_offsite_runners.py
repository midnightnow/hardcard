#!/usr/bin/env python3
"""
MacAgent Pluggable Off-site Runner Interface
Abstract interface supporting multiple cloud backup providers with unified JSON API
"""

import json
import datetime
import subprocess
import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path

class OffsiteRunner(ABC):
    """Abstract base class for off-site backup runners"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.config = self._load_config()
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backup provider is installed and configured"""
        pass
    
    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """Get backup status in standardized format"""
        pass
    
    @abstractmethod
    def run_backup(self) -> Dict[str, Any]:
        """Execute backup job and return result"""
        pass
    
    def _load_config(self) -> Dict[str, Any]:
        """Load provider-specific configuration"""
        config_path = os.path.expanduser(f"~/.config/macagent/{self.provider_name}.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _get_standardized_status(self, raw_status: Dict[str, Any]) -> Dict[str, Any]:
        """Convert provider-specific status to standardized format"""
        now = datetime.datetime.now(datetime.timezone.utc)
        latest_iso = raw_status.get("latest_backup_iso")
        latest_dt = None
        hours_since = None
        
        if latest_iso:
            try:
                latest_dt = datetime.datetime.fromisoformat(latest_iso.replace("Z", "+00:00"))
                delta = now - latest_dt.astimezone(datetime.timezone.utc)
                hours_since = round(delta.total_seconds() / 3600, 1)
            except Exception:
                pass
        
        return {
            "provider": self.provider_name,
            "repository": raw_status.get("repository"),
            "latest_backup_iso": latest_iso,
            "hours_since_latest": hours_since,
            "backup_id": raw_status.get("backup_id"),
            "hostname": raw_status.get("hostname"),
            "stale": (hours_since is None) or (hours_since > 48) or (not raw_status.get("repository")),
            "generated_at": now.isoformat(),
            "ok": (hours_since is not None) and (hours_since <= 48) and bool(raw_status.get("repository")),
            "error": raw_status.get("error"),
            "size_bytes": raw_status.get("size_bytes"),
            "file_count": raw_status.get("file_count")
        }

class ResticRunner(OffsiteRunner):
    """Restic backup runner implementation"""
    
    def __init__(self):
        super().__init__("restic")
    
    def is_available(self) -> bool:
        """Check if restic is installed"""
        try:
            result = subprocess.run(['which', 'restic'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get restic backup status"""
        if not self.is_available():
            return self._get_standardized_status({
                "error": "restic not installed"
            })
        
        repository = self._get_repository()
        if not repository:
            return self._get_standardized_status({
                "error": "no repository configured"
            })
        
        latest_snapshot = self._get_latest_snapshot(repository)
        if not latest_snapshot:
            return self._get_standardized_status({
                "repository": repository,
                "error": "no snapshots found or authentication failed"
            })
        
        raw_status = {
            "repository": repository,
            "latest_backup_iso": latest_snapshot.get('time'),
            "backup_id": latest_snapshot.get('short_id'),
            "hostname": latest_snapshot.get('hostname'),
            "size_bytes": latest_snapshot.get('size'),
            "file_count": len(latest_snapshot.get('paths', []))
        }
        
        return self._get_standardized_status(raw_status)
    
    def run_backup(self) -> Dict[str, Any]:
        """Execute restic backup"""
        if not self.is_available():
            return {"success": False, "error": "restic not installed"}
        
        repository = self._get_repository()
        if not repository:
            return {"success": False, "error": "no repository configured"}
        
        try:
            # Set up environment
            env = os.environ.copy()
            env['RESTIC_REPOSITORY'] = repository
            
            # Get password
            if 'RESTIC_PASSWORD' not in env:
                password = self._get_password()
                if password:
                    env['RESTIC_PASSWORD'] = password
                else:
                    return {"success": False, "error": "no password available"}
            
            # Run backup
            backup_paths = self.config.get('backup_paths', ['~/Documents', '~/Pictures'])
            expanded_paths = [os.path.expanduser(path) for path in backup_paths]
            
            result = subprocess.run([
                'restic', 'backup'
            ] + expanded_paths, env=env, capture_output=True, text=True, timeout=3600)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "backup timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_repository(self) -> Optional[str]:
        """Get restic repository from various sources"""
        # Environment variable
        repo = os.environ.get('RESTIC_REPOSITORY')
        if repo:
            return repo
        
        # Config file
        repo = self.config.get('repository')
        if repo:
            return repo
        
        # Common config locations
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
    
    def _get_password(self) -> Optional[str]:
        """Get restic password from keychain or config"""
        # Try keychain first
        try:
            result = subprocess.run([
                'security', 'find-generic-password', 
                '-a', 'restic', '-s', 'restic-backup', '-w'
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        # Try config file
        return self.config.get('password')
    
    def _get_latest_snapshot(self, repository: str) -> Optional[Dict[str, Any]]:
        """Get latest restic snapshot"""
        try:
            env = os.environ.copy()
            env['RESTIC_REPOSITORY'] = repository
            
            password = self._get_password()
            if password:
                env['RESTIC_PASSWORD'] = password
            
            result = subprocess.run([
                'restic', 'snapshots', '--json', '--latest', '1'
            ], env=env, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return None
            
            snapshots = json.loads(result.stdout)
            if not snapshots:
                return None
            
            snapshot = snapshots[0]
            return {
                'short_id': snapshot.get('short_id') or snapshot.get('id', '')[:8],
                'time': snapshot.get('time'),
                'hostname': snapshot.get('hostname'),
                'paths': snapshot.get('paths', []),
                'size': snapshot.get('size', 0)
            }
            
        except Exception:
            return None

class BackblazeB2Runner(OffsiteRunner):
    """Backblaze B2 backup runner implementation"""
    
    def __init__(self):
        super().__init__("backblaze")
    
    def is_available(self) -> bool:
        """Check if B2 CLI is installed"""
        try:
            result = subprocess.run(['b2', 'version'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get Backblaze B2 backup status"""
        if not self.is_available():
            return self._get_standardized_status({
                "error": "b2 cli not installed"
            })
        
        bucket_name = self.config.get('bucket_name')
        if not bucket_name:
            return self._get_standardized_status({
                "error": "no bucket configured"
            })
        
        # Check if authenticated
        if not self._is_authenticated():
            return self._get_standardized_status({
                "repository": f"b2://{bucket_name}",
                "error": "not authenticated with B2"
            })
        
        # Get latest backup
        latest_file = self._get_latest_backup_file(bucket_name)
        if not latest_file:
            return self._get_standardized_status({
                "repository": f"b2://{bucket_name}",
                "error": "no backup files found"
            })
        
        raw_status = {
            "repository": f"b2://{bucket_name}",
            "latest_backup_iso": latest_file.get('upload_timestamp'),
            "backup_id": latest_file.get('file_id'),
            "hostname": latest_file.get('file_name', '').split('_')[0] if '_' in latest_file.get('file_name', '') else None,
            "size_bytes": latest_file.get('size', 0)
        }
        
        return self._get_standardized_status(raw_status)
    
    def run_backup(self) -> Dict[str, Any]:
        """Execute B2 backup (mock implementation)"""
        return {"success": False, "error": "B2 backup execution not implemented yet"}
    
    def _is_authenticated(self) -> bool:
        """Check if authenticated with B2"""
        try:
            result = subprocess.run(['b2', 'get-account-info'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_latest_backup_file(self, bucket_name: str) -> Optional[Dict[str, Any]]:
        """Get latest backup file from B2 bucket"""
        try:
            result = subprocess.run([
                'b2', 'ls', '--json', bucket_name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return None
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        file_info = json.loads(line)
                        files.append(file_info)
                    except json.JSONDecodeError:
                        continue
            
            if not files:
                return None
            
            # Sort by upload timestamp and return latest
            files.sort(key=lambda x: x.get('upload_timestamp', ''), reverse=True)
            return files[0]
            
        except Exception:
            return None

class ArqRunner(OffsiteRunner):
    """Arq backup runner implementation"""
    
    def __init__(self):
        super().__init__("arq")
    
    def is_available(self) -> bool:
        """Check if Arq is installed"""
        arq_path = "/Applications/Arq 7.app"
        return os.path.exists(arq_path)
    
    def status(self) -> Dict[str, Any]:
        """Get Arq backup status"""
        if not self.is_available():
            return self._get_standardized_status({
                "error": "Arq not installed"
            })
        
        # Arq stores backup information in SQLite database
        backup_info = self._get_arq_backup_info()
        if not backup_info:
            return self._get_standardized_status({
                "error": "no Arq backups configured or found"
            })
        
        return self._get_standardized_status(backup_info)
    
    def run_backup(self) -> Dict[str, Any]:
        """Execute Arq backup (mock implementation)"""
        return {"success": False, "error": "Arq backup execution not implemented yet"}
    
    def _get_arq_backup_info(self) -> Optional[Dict[str, Any]]:
        """Get Arq backup information (mock implementation)"""
        # This would require parsing Arq's SQLite database
        # For now, return mock data
        return {
            "repository": "arq://configured-destination",
            "error": "Arq status parsing not implemented yet"
        }

class DuplicacyRunner(OffsiteRunner):
    """Duplicacy backup runner implementation"""
    
    def __init__(self):
        super().__init__("duplicacy")
    
    def is_available(self) -> bool:
        """Check if Duplicacy is installed"""
        try:
            result = subprocess.run(['duplicacy', 'version'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get Duplicacy backup status"""
        if not self.is_available():
            return self._get_standardized_status({
                "error": "duplicacy not installed"
            })
        
        # Check for repository initialization
        if not os.path.exists('.duplicacy'):
            return self._get_standardized_status({
                "error": "no duplicacy repository initialized"
            })
        
        # Get latest revision
        latest_revision = self._get_latest_revision()
        if not latest_revision:
            return self._get_standardized_status({
                "repository": "duplicacy://local-repo",
                "error": "no revisions found"
            })
        
        raw_status = {
            "repository": "duplicacy://local-repo",
            "latest_backup_iso": latest_revision.get('timestamp'),
            "backup_id": str(latest_revision.get('revision', '')),
            "hostname": latest_revision.get('computer', ''),
            "size_bytes": latest_revision.get('size', 0),
            "file_count": latest_revision.get('files', 0)
        }
        
        return self._get_standardized_status(raw_status)
    
    def run_backup(self) -> Dict[str, Any]:
        """Execute Duplicacy backup (mock implementation)"""
        return {"success": False, "error": "Duplicacy backup execution not implemented yet"}
    
    def _get_latest_revision(self) -> Optional[Dict[str, Any]]:
        """Get latest Duplicacy revision (mock implementation)"""
        # This would require parsing duplicacy list output
        return None

class OffsiteRunnerFactory:
    """Factory for creating appropriate off-site runners"""
    
    RUNNERS = {
        'restic': ResticRunner,
        'backblaze': BackblazeB2Runner,
        'arq': ArqRunner,
        'duplicacy': DuplicacyRunner
    }
    
    @classmethod
    def get_available_runners(cls) -> List[OffsiteRunner]:
        """Get all available backup runners"""
        runners = []
        for runner_class in cls.RUNNERS.values():
            runner = runner_class()
            if runner.is_available():
                runners.append(runner)
        return runners
    
    @classmethod
    def get_runner(cls, provider: str) -> Optional[OffsiteRunner]:
        """Get specific runner by provider name"""
        runner_class = cls.RUNNERS.get(provider)
        if runner_class:
            runner = runner_class()
            if runner.is_available():
                return runner
        return None
    
    @classmethod
    def auto_detect_provider(cls) -> Optional[OffsiteRunner]:
        """Auto-detect the best available provider"""
        # Priority order: restic, backblaze, arq, duplicacy
        priority_order = ['restic', 'backblaze', 'arq', 'duplicacy']
        
        for provider in priority_order:
            runner = cls.get_runner(provider)
            if runner:
                return runner
        
        return None

# CLI Integration Functions
def cmd_offsite_status_unified():
    """Unified off-site status command supporting multiple providers"""
    # Try to auto-detect provider
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
            "repository": status.get("repository")
        })
    
    # Add unavailable providers
    for provider_name in OffsiteRunnerFactory.RUNNERS.keys():
        if not any(p["provider"] == provider_name for p in providers):
            providers.append({
                "provider": provider_name,
                "available": False,
                "configured": False,
                "last_backup": None,
                "repository": None
            })
    
    result = {
        "providers": providers,
        "primary_provider": runners[0].provider_name if runners else None,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    print(json.dumps(result))

def cmd_offsite_run_unified():
    """Unified off-site backup execution"""
    runner = OffsiteRunnerFactory.auto_detect_provider()
    
    if not runner:
        print("❌ No backup providers available")
        return
    
    print(f"🔄 Starting {runner.provider_name} backup...")
    result = runner.run_backup()
    
    if result.get("success"):
        print(f"✅ {runner.provider_name} backup completed successfully")
    else:
        print(f"❌ {runner.provider_name} backup failed: {result.get('error')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "offsite-status":
            cmd_offsite_status_unified()
        elif cmd == "offsite-providers":
            cmd_offsite_providers()
        elif cmd == "offsite-run":
            cmd_offsite_run_unified()
        else:
            print(f"Unknown command: {cmd}")
    else:
        print("Usage: pluggable_offsite_runners.py [offsite-status|offsite-providers|offsite-run]")