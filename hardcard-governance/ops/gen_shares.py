#!/usr/bin/env python3
"""
SSKR (Shamir Secret Key Recovery) Share Generation for Guardian Keys
Implements BIP-39 compatible SSKR share generation for secure key distribution
"""

import argparse
import json
import os
import secrets
import sys
from typing import List, Tuple, Dict
from datetime import datetime
import hashlib
import base64

# Shamir's Secret Sharing implementation
class SSS:
    def __init__(self):
        self.prime = 2**256 - 2**224 + 2**192 + 2**96 - 1  # secp256k1 field prime
    
    def _eval_at(self, poly: List[int], x: int) -> int:
        """Evaluate polynomial at x"""
        result = 0
        power = 1
        for coeff in poly:
            result = (result + coeff * power) % self.prime
            power = (power * x) % self.prime
        return result
    
    def _mod_inverse(self, a: int) -> int:
        """Modular inverse using Fermat's little theorem"""
        return pow(a, self.prime - 2, self.prime)
    
    def split(self, secret: int, threshold: int, shares: int) -> List[Tuple[int, int]]:
        """Split secret into shares using Shamir's Secret Sharing"""
        if threshold > shares:
            raise ValueError("Threshold cannot be greater than number of shares")
        if threshold < 2:
            raise ValueError("Threshold must be at least 2")
        
        # Create random polynomial with secret as constant term
        poly = [secret] + [secrets.randbelow(self.prime) for _ in range(threshold - 1)]
        
        # Generate shares
        points = []
        for i in range(1, shares + 1):
            x = i
            y = self._eval_at(poly, x)
            points.append((x, y))
        
        return points
    
    def recover(self, shares: List[Tuple[int, int]]) -> int:
        """Recover secret from shares using Lagrange interpolation"""
        if len(shares) < 2:
            raise ValueError("Need at least 2 shares to recover secret")
        
        secret = 0
        for i, (xi, yi) in enumerate(shares):
            numerator = 1
            denominator = 1
            
            for j, (xj, _) in enumerate(shares):
                if i != j:
                    numerator = (numerator * (-xj)) % self.prime
                    denominator = (denominator * (xi - xj)) % self.prime
            
            lagrange = (numerator * self._mod_inverse(denominator)) % self.prime
            secret = (secret + yi * lagrange) % self.prime
        
        return secret


class GuardianShareGenerator:
    def __init__(self):
        self.sss = SSS()
    
    def generate_guardian_key(self) -> bytes:
        """Generate a new guardian private key"""
        return secrets.token_bytes(32)
    
    def generate_shares(self, 
                       guardian_count: int, 
                       threshold: int, 
                       guardian_keys: Dict[str, bytes] = None) -> Dict:
        """
        Generate SSKR shares for guardian keys
        
        Args:
            guardian_count: Total number of guardians
            threshold: Minimum guardians needed to recover
            guardian_keys: Optional pre-existing guardian keys
        
        Returns:
            Dictionary containing shares and metadata
        """
        if guardian_keys is None:
            # Generate new guardian keys
            guardian_keys = {}
            for i in range(guardian_count):
                guardian_keys[f"guardian_{i+1}"] = self.generate_guardian_key()
        
        result = {
            "metadata": {
                "version": "1.0",
                "created": datetime.utcnow().isoformat(),
                "guardian_count": guardian_count,
                "threshold": threshold,
                "scheme": "SSKR-256"
            },
            "guardians": {},
            "shares": {},
            "verification": {}
        }
        
        # For each guardian, create shares of their key
        for guardian_id, key in guardian_keys.items():
            # Convert key to integer
            key_int = int.from_bytes(key, 'big')
            
            # Generate shares
            shares = self.sss.split(key_int, threshold, guardian_count)
            
            # Store guardian info
            result["guardians"][guardian_id] = {
                "public_address": self._derive_address(key),
                "key_fingerprint": hashlib.sha256(key).hexdigest()[:8]
            }
            
            # Distribute shares
            for i, (x, y) in enumerate(shares):
                share_holder = f"guardian_{i+1}"
                if share_holder not in result["shares"]:
                    result["shares"][share_holder] = {}
                
                # Encode share
                share_data = {
                    "x": x,
                    "y": base64.b64encode(y.to_bytes(32, 'big')).decode(),
                    "for_guardian": guardian_id,
                    "holder": share_holder
                }
                
                result["shares"][share_holder][guardian_id] = share_data
        
        # Generate verification hashes
        for holder, shares in result["shares"].items():
            share_concat = json.dumps(shares, sort_keys=True)
            result["verification"][holder] = hashlib.sha256(
                share_concat.encode()
            ).hexdigest()
        
        return result
    
    def _derive_address(self, private_key: bytes) -> str:
        """Derive Ethereum address from private key"""
        # Simplified - in production use proper secp256k1 library
        # This is a placeholder that generates a deterministic address
        return "0x" + hashlib.sha256(private_key).hexdigest()[:40]
    
    def save_shares(self, shares_data: Dict, output_dir: str):
        """Save shares to individual files for distribution"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save metadata
        with open(os.path.join(output_dir, "metadata.json"), "w") as f:
            json.dump({
                "metadata": shares_data["metadata"],
                "guardians": shares_data["guardians"],
                "verification": shares_data["verification"]
            }, f, indent=2)
        
        # Save individual guardian shares
        for guardian, shares in shares_data["shares"].items():
            guardian_file = os.path.join(output_dir, f"{guardian}_shares.json")
            with open(guardian_file, "w") as f:
                json.dump({
                    "guardian": guardian,
                    "shares": shares,
                    "metadata": shares_data["metadata"],
                    "verification_hash": shares_data["verification"][guardian]
                }, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(guardian_file, 0o600)
        
        print(f"✅ Shares generated and saved to {output_dir}/")
        print(f"📁 Files created:")
        print(f"   - metadata.json (public)")
        for guardian in shares_data["shares"]:
            print(f"   - {guardian}_shares.json (CONFIDENTIAL)")
    
    def verify_shares(self, shares_data: Dict) -> bool:
        """Verify that shares can reconstruct the original keys"""
        threshold = shares_data["metadata"]["threshold"]
        
        for guardian_id in shares_data["guardians"]:
            # Collect threshold shares for this guardian
            test_shares = []
            for i, (holder, holder_shares) in enumerate(shares_data["shares"].items()):
                if i >= threshold:
                    break
                
                share = holder_shares[guardian_id]
                x = share["x"]
                y = int.from_bytes(base64.b64decode(share["y"]), 'big')
                test_shares.append((x, y))
            
            # Try to recover
            try:
                recovered = self.sss.recover(test_shares)
                recovered_bytes = recovered.to_bytes(32, 'big')
                fingerprint = hashlib.sha256(recovered_bytes).hexdigest()[:8]
                
                if fingerprint != shares_data["guardians"][guardian_id]["key_fingerprint"]:
                    print(f"❌ Verification failed for {guardian_id}")
                    return False
            except Exception as e:
                print(f"❌ Recovery failed for {guardian_id}: {e}")
                return False
        
        print("✅ All shares verified successfully")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate SSKR shares for Hardcard Guardian Council"
    )
    parser.add_argument(
        "--guardian-count", 
        type=int, 
        default=5,
        help="Total number of guardians (default: 5)"
    )
    parser.add_argument(
        "--threshold", 
        type=int, 
        default=3,
        help="Minimum guardians needed to recover (default: 3)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./guardian_shares",
        help="Output directory for share files"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing shares"
    )
    
    args = parser.parse_args()
    
    generator = GuardianShareGenerator()
    
    if args.verify_only:
        # Load and verify existing shares
        try:
            with open(os.path.join(args.output_dir, "metadata.json"), "r") as f:
                metadata = json.load(f)
            
            # Reconstruct shares data
            shares_data = {
                "metadata": metadata["metadata"],
                "guardians": metadata["guardians"],
                "verification": metadata["verification"],
                "shares": {}
            }
            
            # Load each guardian's shares
            for i in range(1, metadata["metadata"]["guardian_count"] + 1):
                guardian_id = f"guardian_{i}"
                with open(os.path.join(args.output_dir, f"{guardian_id}_shares.json"), "r") as f:
                    guardian_data = json.load(f)
                    shares_data["shares"][guardian_id] = guardian_data["shares"]
            
            generator.verify_shares(shares_data)
        except Exception as e:
            print(f"❌ Error loading shares: {e}")
            sys.exit(1)
    else:
        # Generate new shares
        print(f"🔐 Generating {args.guardian_count} guardian keys with {args.threshold}/{args.guardian_count} threshold...")
        
        shares_data = generator.generate_shares(args.guardian_count, args.threshold)
        
        # Verify before saving
        if generator.verify_shares(shares_data):
            generator.save_shares(shares_data, args.output_dir)
            print(f"\n⚠️  IMPORTANT: Distribute share files securely to each guardian")
            print(f"⚠️  Each guardian should receive ONLY their own share file")
            print(f"⚠️  Store the root private keys in cold storage immediately")
        else:
            print("❌ Share verification failed, aborting")
            sys.exit(1)


if __name__ == "__main__":
    main()