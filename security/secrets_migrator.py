"""
Secrets Migration Tool for HardCard Platform
Migrates existing plaintext secrets to secure keychain storage
"""
import os
import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import configparser
from dataclasses import dataclass

from .keychain_manager import KeychainManager
from .encryption_manager import EncryptionManager

logger = logging.getLogger(__name__)

@dataclass
class SecretLocation:
    """Information about where a secret was found"""
    file_path: str
    line_number: int
    key_name: str
    value: str
    context: str
    secret_type: str

class SecretsMigrator:
    """
    Migrates secrets from plaintext storage to secure keychain
    """
    
    def __init__(self, base_path: str = "/Users/studio/hardcard"):
        """
        Initialize the secrets migrator
        
        Args:
            base_path (str): Base path to scan for secrets
        """
        self.base_path = Path(base_path)
        self.keychain = KeychainManager("hardcard")
        self.encryption = EncryptionManager()
        
        # Patterns for detecting secrets
        self.secret_patterns = {
            'api_key': [
                r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_]+)["\']?',
                r'API[_-]?KEY["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_]+)["\']?',
            ],
            'firebase_key': [
                r'apiKey["\']?\s*[:=]\s*["\']?(AIza[A-Za-z0-9\-_]+)["\']?',
            ],
            'twilio': [
                r'TWILIO_ACCOUNT_SID["\']?\s*[:=]\s*["\']?(AC[A-Za-z0-9]+)["\']?',
                r'TWILIO_API_KEY_SID["\']?\s*[:=]\s*["\']?(SK[A-Za-z0-9]+)["\']?',
                r'TWILIO_API_KEY_SECRET["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)["\']?',
                r'TWILIO_AUTH_TOKEN["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)["\']?',
                r'TWILIO_PHONE_NUMBER["\']?\s*[:=]\s*["\']?(\+[0-9]+)["\']?',
            ],
            'jwt_secret': [
                r'JWT_SECRET["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_+=\/]+)["\']?',
                r'SECRET_KEY["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_+=\/]+)["\']?',
            ],
            'database_url': [
                r'DATABASE_URL["\']?\s*[:=]\s*["\']?(postgresql[^"\']+)["\']?',
                r'REDIS_URL["\']?\s*[:=]\s*["\']?(redis[^"\']+)["\']?',
            ],
            'token': [
                r'token["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_\.]+)["\']?',
                r'TOKEN["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_\.]+)["\']?',
            ]
        }
        
        # File patterns to scan
        self.file_patterns = [
            '**/.env',
            '**/.env.*',
            '**/config.py',
            '**/settings.py',
            '**/firebase.ts',
            '**/firebaseConfig.ts',
            '**/*.json',
            '**/*.yaml',
            '**/*.yml'
        ]
        
        # Files to exclude from scanning
        self.exclude_patterns = [
            '**/node_modules/**',
            '**/.git/**',
            '**/venv/**',
            '**/env/**',
            '**/__pycache__/**',
            '**/*.pyc',
            '**/.env.example',
            '**/.env.template'
        ]
    
    def scan_for_secrets(self) -> List[SecretLocation]:
        """
        Scan the codebase for secrets
        
        Returns:
            List[SecretLocation]: List of found secrets
        """
        logger.info(f"Scanning for secrets in: {self.base_path}")
        secrets = []
        
        for pattern in self.file_patterns:
            for file_path in self.base_path.glob(pattern):
                if self._should_exclude_file(file_path):
                    continue
                
                try:
                    secrets.extend(self._scan_file(file_path))
                except Exception as e:
                    logger.error(f"Error scanning file {file_path}: {str(e)}")
        
        logger.info(f"Found {len(secrets)} secrets")
        return secrets
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning"""
        for exclude_pattern in self.exclude_patterns:
            if file_path.match(exclude_pattern):
                return True
        return False
    
    def _scan_file(self, file_path: Path) -> List[SecretLocation]:
        """Scan a single file for secrets"""
        secrets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line_secrets = self._scan_line(str(file_path), line_num, line)
                secrets.extend(line_secrets)
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
        
        return secrets
    
    def _scan_line(self, file_path: str, line_num: int, line: str) -> List[SecretLocation]:
        """Scan a single line for secrets"""
        secrets = []
        
        for secret_type, patterns in self.secret_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    secret_value = match.group(1)
                    
                    # Skip obvious placeholders
                    if self._is_placeholder(secret_value):
                        continue
                    
                    # Extract key name from context
                    key_name = self._extract_key_name(line, secret_type)
                    
                    secret = SecretLocation(
                        file_path=file_path,
                        line_number=line_num,
                        key_name=key_name,
                        value=secret_value,
                        context=line.strip(),
                        secret_type=secret_type
                    )
                    secrets.append(secret)
        
        return secrets
    
    def _is_placeholder(self, value: str) -> bool:
        """Check if value is a placeholder"""
        placeholders = [
            'your_api_key', 'your_secret', 'placeholder', 'example',
            'xxx', 'yyy', 'zzz', 'abc123', 'secret_here',
            'change_me', 'replace_me', 'your_key_here'
        ]
        return value.lower() in placeholders or len(value) < 8
    
    def _extract_key_name(self, line: str, secret_type: str) -> str:
        """Extract a meaningful key name from the line context"""
        # Try to extract the variable name
        key_patterns = [
            r'([A-Z_]+)["\']?\s*[:=]',  # Environment variable style
            r'([a-zA-Z_]+)["\']?\s*[:=]',  # Regular variable style
        ]
        
        for pattern in key_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1).lower()
        
        # Fallback to secret type
        return secret_type
    
    def migrate_secrets(self, secrets: List[SecretLocation], dry_run: bool = True) -> Dict[str, any]:
        """
        Migrate secrets to keychain
        
        Args:
            secrets (List[SecretLocation]): Secrets to migrate
            dry_run (bool): If True, don't actually store secrets
            
        Returns:
            Dict: Migration results
        """
        results = {
            'migrated': [],
            'failed': [],
            'skipped': [],
            'total': len(secrets)
        }
        
        logger.info(f"Migrating {len(secrets)} secrets (dry_run={dry_run})")
        
        for secret in secrets:
            try:
                # Generate a unique key name
                key_name = self._generate_key_name(secret)
                
                # Check if already exists
                if self.keychain.get_api_key(key_name):
                    logger.info(f"Secret already exists in keychain: {key_name}")
                    results['skipped'].append({
                        'key_name': key_name,
                        'reason': 'already_exists',
                        'location': f"{secret.file_path}:{secret.line_number}"
                    })
                    continue
                
                if not dry_run:
                    # Store in keychain
                    success = self.keychain.store_api_key(key_name, secret.value)
                    if success:
                        results['migrated'].append({
                            'key_name': key_name,
                            'secret_type': secret.secret_type,
                            'location': f"{secret.file_path}:{secret.line_number}"
                        })
                        logger.info(f"Migrated secret: {key_name}")
                    else:
                        results['failed'].append({
                            'key_name': key_name,
                            'reason': 'keychain_store_failed',
                            'location': f"{secret.file_path}:{secret.line_number}"
                        })
                else:
                    # Dry run - just log what would be done
                    results['migrated'].append({
                        'key_name': key_name,
                        'secret_type': secret.secret_type,
                        'location': f"{secret.file_path}:{secret.line_number}",
                        'dry_run': True
                    })
                    logger.info(f"Would migrate secret: {key_name}")
                    
            except Exception as e:
                logger.error(f"Error migrating secret from {secret.file_path}:{secret.line_number}: {str(e)}")
                results['failed'].append({
                    'key_name': getattr(secret, 'key_name', 'unknown'),
                    'reason': str(e),
                    'location': f"{secret.file_path}:{secret.line_number}"
                })
        
        return results
    
    def _generate_key_name(self, secret: SecretLocation) -> str:
        """Generate a unique key name for the secret"""
        # Clean up the key name
        key_name = secret.key_name.lower()
        key_name = re.sub(r'[^a-z0-9_]', '_', key_name)
        
        # Add secret type prefix for clarity
        if not key_name.startswith(secret.secret_type):
            key_name = f"{secret.secret_type}_{key_name}"
        
        return key_name
    
    def generate_migration_script(self, secrets: List[SecretLocation], output_path: str = None) -> str:
        """
        Generate a script to update code to use keychain
        
        Args:
            secrets (List[SecretLocation]): Secrets to migrate
            output_path (str, optional): Path to save the script
            
        Returns:
            str: Generated script content
        """
        script_content = """#!/usr/bin/env python3
\"\"\"
HardCard Secrets Migration Script
Automatically generated script to update code to use keychain
\"\"\"

from hardcard.security import KeychainManager

# Initialize keychain manager
keychain = KeychainManager("hardcard")

# Example usage for migrated secrets:
"""
        
        for secret in secrets:
            key_name = self._generate_key_name(secret)
            script_content += f"""
# {secret.secret_type.upper()} - {secret.file_path}:{secret.line_number}
# Replace: {secret.context}
# With: {key_name} = keychain.get_api_key("{key_name}")
{key_name} = keychain.get_api_key("{key_name}")
"""
        
        script_content += """
# HardCard-specific convenience methods:
firebase_config = keychain.get_firebase_config()
twilio_config = keychain.get_twilio_config()
"""
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(script_content)
            logger.info(f"Migration script saved to: {output_path}")
        
        return script_content
    
    def backup_env_files(self, backup_dir: str = None) -> str:
        """
        Create encrypted backups of .env files before migration
        
        Args:
            backup_dir (str, optional): Directory to store backups
            
        Returns:
            str: Path to backup directory
        """
        if backup_dir is None:
            backup_dir = str(self.base_path / "secrets_backup")
        
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        logger.info(f"Creating encrypted backups in: {backup_path}")
        
        for env_file in self.base_path.glob("**/.env*"):
            if self._should_exclude_file(env_file):
                continue
            
            try:
                # Create relative path for backup
                rel_path = env_file.relative_to(self.base_path)
                backup_file = backup_path / f"{str(rel_path).replace('/', '_')}.encrypted"
                
                # Encrypt and backup
                success = self.encryption.encrypt_file(str(env_file), str(backup_file))
                if success:
                    logger.info(f"Backed up: {env_file} -> {backup_file}")
                else:
                    logger.error(f"Failed to backup: {env_file}")
                    
            except Exception as e:
                logger.error(f"Error backing up {env_file}: {str(e)}")
        
        return str(backup_path)
    
    def run_full_migration(self, dry_run: bool = True) -> Dict[str, any]:
        """
        Run the complete migration process
        
        Args:
            dry_run (bool): If True, don't actually migrate secrets
            
        Returns:
            Dict: Complete migration results
        """
        logger.info("Starting full secrets migration")
        
        # Step 1: Backup existing files
        if not dry_run:
            backup_dir = self.backup_env_files()
        else:
            backup_dir = "dry_run_no_backup"
        
        # Step 2: Scan for secrets
        secrets = self.scan_for_secrets()
        
        # Step 3: Migrate secrets
        migration_results = self.migrate_secrets(secrets, dry_run)
        
        # Step 4: Generate migration script
        script_path = str(self.base_path / "secrets_migration_script.py")
        if not dry_run:
            self.generate_migration_script(secrets, script_path)
        else:
            script_content = self.generate_migration_script(secrets)
        
        return {
            'backup_directory': backup_dir,
            'secrets_found': len(secrets),
            'migration_results': migration_results,
            'script_path': script_path if not dry_run else None,
            'script_content': script_content if dry_run else None
        }