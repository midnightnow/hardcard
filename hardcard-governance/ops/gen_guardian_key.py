#!/usr/bin/env python3
"""
Guardian Key Generator
Generates cryptographically secure keys for guardians with proper entropy
"""

import argparse
import json
import os
import secrets
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import subprocess

try:
    from eth_account import Account
    from eth_keys import keys
    ETH_AVAILABLE = True
except ImportError:
    ETH_AVAILABLE = False
    print("⚠️  eth-account not available. Install with: pip install eth-account eth-keys")

class GuardianKeyGenerator:
    def __init__(self, testnet: bool = False):
        """Initialize guardian key generator"""
        self.testnet = testnet
        self.entropy_sources = []
        
    def generate_entropy(self) -> bytes:
        """Generate high-quality entropy from multiple sources"""
        print("🎲 Gathering entropy...")
        
        # Primary entropy from system CSPRNG
        primary_entropy = secrets.token_bytes(32)
        self.entropy_sources.append("system_csprng")
        
        # Additional entropy from system state
        try:
            # System uptime and process info
            uptime = subprocess.check_output(['uptime'], text=True)
            system_entropy = hashlib.sha256(uptime.encode()).digest()[:16]
            
            # Mix with primary
            combined = hashlib.sha256(primary_entropy + system_entropy).digest()
            self.entropy_sources.append("system_state")
            
        except:
            combined = primary_entropy
        
        # User interaction entropy (for additional randomness)
        print("🔑 For additional entropy, please type 20+ random characters:")
        user_input = input("Random chars: ").encode()
        
        if len(user_input) >= 20:
            user_hash = hashlib.sha256(user_input).digest()[:16]
            combined = hashlib.sha256(combined + user_hash).digest()
            self.entropy_sources.append("user_interaction")
        
        print(f"✅ Entropy gathered from: {', '.join(self.entropy_sources)}")
        return combined
    
    def generate_guardian_key(self, guardian_id: str) -> Dict[str, Any]:
        """Generate a new guardian key pair"""
        print(f"\n🔐 Generating key for guardian: {guardian_id}")
        
        if not ETH_AVAILABLE:
            print("❌ Ethereum libraries not available")
            return self._generate_generic_key(guardian_id)
        
        # Generate high-quality entropy
        entropy = self.generate_entropy()
        
        # Create Ethereum account from entropy
        account = Account.from_key(entropy)
        
        # Extract key components
        private_key_hex = account.key.hex()
        public_key_hex = account._key_obj.public_key.to_hex()
        address = account.address
        
        # Generate additional metadata
        key_data = {
            "guardian_id": guardian_id,
            "created": datetime.utcnow().isoformat(),
            "network": "testnet" if self.testnet else "mainnet",
            "key_type": "secp256k1",
            "address": address,
            "public_key": public_key_hex,
            "private_key": private_key_hex,
            "entropy_sources": self.entropy_sources,
            "verification": {
                "address_checksum": Web3.toChecksumAddress(address) if 'Web3' in globals() else address,
                "key_hash": hashlib.sha256(private_key_hex.encode()).hexdigest(),
                "public_key_hash": hashlib.sha256(public_key_hex.encode()).hexdigest()
            }
        }
        
        print(f"✅ Key generated successfully")
        print(f"   Address: {address}")
        print(f"   Network: {'Testnet' if self.testnet else 'Mainnet'}")
        
        return key_data
    
    def _generate_generic_key(self, guardian_id: str) -> Dict[str, Any]:
        """Generate a generic key when Ethereum libraries are not available"""
        entropy = self.generate_entropy()
        
        # Use entropy as private key (simplified)
        private_key_hex = entropy.hex()
        
        key_data = {
            "guardian_id": guardian_id,
            "created": datetime.utcnow().isoformat(),
            "network": "testnet" if self.testnet else "mainnet",
            "key_type": "generic",
            "private_key": private_key_hex,
            "entropy_sources": self.entropy_sources,
            "warning": "Generated without Ethereum libraries - verify before use"
        }
        
        return key_data
    
    def save_key(self, key_data: Dict[str, Any], output_dir: str = "./guardian_keys") -> str:
        """Save guardian key to secure file"""
        os.makedirs(output_dir, exist_ok=True)
        
        guardian_id = key_data["guardian_id"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{guardian_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Create secure copy without private key for sharing
        public_data = key_data.copy()
        if "private_key" in public_data:
            del public_data["private_key"]
        
        # Save full key data
        with open(filepath, 'w') as f:
            json.dump(key_data, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(filepath, 0o600)
        
        # Save public data
        public_filepath = filepath.replace('.json', '_public.json')
        with open(public_filepath, 'w') as f:
            json.dump(public_data, f, indent=2)
        
        print(f"💾 Private key saved: {filepath}")
        print(f"💾 Public data saved: {public_filepath}")
        print(f"🔒 File permissions set to 600 (owner read/write only)")
        
        return filepath
    
    def verify_key(self, key_file: str) -> bool:
        """Verify guardian key integrity"""
        print(f"\n🔍 Verifying key: {key_file}")
        
        try:
            with open(key_file, 'r') as f:
                key_data = json.load(f)
            
            # Basic structure checks
            required_fields = ["guardian_id", "created", "network"]
            for field in required_fields:
                if field not in key_data:
                    print(f"❌ Missing field: {field}")
                    return False
            
            # Verify checksums if available
            if "verification" in key_data:
                verification = key_data["verification"]
                
                if "private_key" in key_data:
                    actual_hash = hashlib.sha256(key_data["private_key"].encode()).hexdigest()
                    if verification.get("key_hash") != actual_hash:
                        print("❌ Private key hash mismatch")
                        return False
                
                if "public_key" in key_data:
                    actual_hash = hashlib.sha256(key_data["public_key"].encode()).hexdigest()
                    if verification.get("public_key_hash") != actual_hash:
                        print("❌ Public key hash mismatch")
                        return False
            
            # Verify Ethereum account if possible
            if ETH_AVAILABLE and "private_key" in key_data and "address" in key_data:
                try:
                    account = Account.from_key(key_data["private_key"])
                    if account.address.lower() != key_data["address"].lower():
                        print("❌ Address derivation mismatch")
                        return False
                except Exception as e:
                    print(f"❌ Account verification failed: {e}")
                    return False
            
            print("✅ Key verification passed")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def rotate_key(self, old_key_file: str, guardian_id: str) -> str:
        """Rotate an existing guardian key"""
        print(f"\n🔄 Rotating key for guardian: {guardian_id}")
        
        # Load old key for audit trail
        try:
            with open(old_key_file, 'r') as f:
                old_key_data = json.load(f)
            print(f"📜 Loaded old key from: {old_key_file}")
        except Exception as e:
            print(f"⚠️  Could not load old key: {e}")
            old_key_data = None
        
        # Generate new key
        new_key_data = self.generate_guardian_key(guardian_id)
        
        # Add rotation metadata
        new_key_data["rotation"] = {
            "is_rotation": True,
            "rotated_from": old_key_data.get("address") if old_key_data else "unknown",
            "rotation_reason": "key_rotation",
            "old_key_file": old_key_file
        }
        
        # Save new key
        new_key_file = self.save_key(new_key_data)
        
        # Archive old key
        if old_key_data:
            archive_dir = os.path.join(os.path.dirname(old_key_file), "archived")
            os.makedirs(archive_dir, exist_ok=True)
            
            archive_path = os.path.join(
                archive_dir, 
                f"archived_{os.path.basename(old_key_file)}"
            )
            
            old_key_data["archived"] = {
                "archived_at": datetime.utcnow().isoformat(),
                "rotated_to": new_key_data.get("address"),
                "reason": "key_rotation"
            }
            
            with open(archive_path, 'w') as f:
                json.dump(old_key_data, f, indent=2)
            
            print(f"📁 Old key archived: {archive_path}")
        
        return new_key_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate secure guardian keys for Hardcard Governance"
    )
    parser.add_argument(
        "--guardian-id",
        type=str,
        required=True,
        help="Guardian identifier (e.g., guardian_1, alice)"
    )
    parser.add_argument(
        "--testnet",
        action="store_true",
        help="Generate key for testnet use"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./guardian_keys",
        help="Output directory for key files"
    )
    parser.add_argument(
        "--rotate",
        type=str,
        help="Path to old key file to rotate"
    )
    parser.add_argument(
        "--verify",
        type=str,
        help="Path to key file to verify"
    )
    
    args = parser.parse_args()
    
    generator = GuardianKeyGenerator(testnet=args.testnet)
    
    if args.verify:
        # Verify existing key
        success = generator.verify_key(args.verify)
        exit(0 if success else 1)
    
    elif args.rotate:
        # Rotate existing key
        new_key_file = generator.rotate_key(args.rotate, args.guardian_id)
        print(f"\n✅ Key rotation complete!")
        print(f"   New key: {new_key_file}")
        
    else:
        # Generate new key
        key_data = generator.generate_guardian_key(args.guardian_id)
        key_file = generator.save_key(key_data, args.output_dir)
        
        # Verify the generated key
        if generator.verify_key(key_file):
            print(f"\n✅ Guardian key generation complete!")
            print(f"   Guardian: {args.guardian_id}")
            print(f"   Key file: {key_file}")
            
            if "address" in key_data:
                print(f"   Address: {key_data['address']}")
            
            print(f"\n🔒 SECURITY REMINDERS:")
            print(f"   • Store private key securely offline")
            print(f"   • Backup in multiple secure locations")
            print(f"   • Never share private key")
            print(f"   • Use hardware security module if possible")
        else:
            print("❌ Key generation verification failed!")
            exit(1)


if __name__ == "__main__":
    main()