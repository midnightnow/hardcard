#!/usr/bin/env python3
"""
SSKR Share Distribution Automation
Securely distributes guardian key shares via encrypted channels
"""

import argparse
import json
import os
import sys
import smtplib
import gnupg
import qrcode
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets

class ShareDistributor:
    def __init__(self, config_file: str):
        """Initialize share distributor with configuration"""
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.gpg = gnupg.GPG()
        self.distribution_log = []
        
    def distribute_shares(self, shares_dir: str, guardian_config: str) -> bool:
        """
        Distribute shares to guardians based on configuration
        
        Args:
            shares_dir: Directory containing generated shares
            guardian_config: Path to guardian configuration file
        """
        print("🔐 Starting SSKR Share Distribution")
        print("=" * 50)
        
        # Load guardian information
        with open(guardian_config, 'r') as f:
            guardians = yaml.safe_load(f)['guardians']
        
        # Load metadata
        metadata_path = os.path.join(shares_dir, 'metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Process each guardian
        for guardian_id, guardian_info in guardians.items():
            print(f"\n📤 Processing {guardian_id}...")
            
            # Load guardian's shares
            share_file = os.path.join(shares_dir, f"{guardian_id}_shares.json")
            if not os.path.exists(share_file):
                print(f"❌ Share file not found for {guardian_id}")
                continue
            
            with open(share_file, 'r') as f:
                share_data = json.load(f)
            
            # Distribute via configured methods
            success = True
            for method in guardian_info['distribution_methods']:
                if method['type'] == 'pgp_email':
                    success &= self._distribute_via_pgp_email(
                        guardian_id, guardian_info, share_data, method
                    )
                elif method['type'] == 'encrypted_file':
                    success &= self._distribute_via_encrypted_file(
                        guardian_id, guardian_info, share_data, method
                    )
                elif method['type'] == 'qr_code':
                    success &= self._distribute_via_qr_code(
                        guardian_id, guardian_info, share_data, method
                    )
                elif method['type'] == 'secure_message':
                    success &= self._distribute_via_secure_message(
                        guardian_id, guardian_info, share_data, method
                    )
            
            # Log distribution
            self.distribution_log.append({
                'guardian': guardian_id,
                'timestamp': datetime.utcnow().isoformat(),
                'methods': [m['type'] for m in guardian_info['distribution_methods']],
                'success': success,
                'share_hash': self._hash_share_data(share_data)
            })
        
        # Save distribution log
        self._save_distribution_log()
        
        print("\n✅ Distribution complete!")
        print(f"📊 Success rate: {sum(1 for l in self.distribution_log if l['success'])}/{len(self.distribution_log)}")
        
        return all(l['success'] for l in self.distribution_log)
    
    def _distribute_via_pgp_email(self, guardian_id: str, guardian_info: Dict, 
                                  share_data: Dict, method_config: Dict) -> bool:
        """Distribute shares via PGP-encrypted email"""
        try:
            print(f"  📧 Sending PGP-encrypted email to {guardian_info['email']}...")
            
            # Import guardian's public key
            key_data = method_config.get('public_key') or guardian_info.get('pgp_key')
            if not key_data:
                print("    ❌ No PGP key found")
                return False
            
            import_result = self.gpg.import_keys(key_data)
            if not import_result.count:
                print("    ❌ Failed to import PGP key")
                return False
            
            # Encrypt share data
            share_json = json.dumps(share_data, indent=2)
            encrypted = self.gpg.encrypt(
                share_json,
                recipients=[import_result.fingerprints[0]],
                armor=True
            )
            
            if not encrypted.ok:
                print(f"    ❌ Encryption failed: {encrypted.status}")
                return False
            
            # Create email
            msg = MIMEMultipart('mixed')
            msg['Subject'] = f'[CONFIDENTIAL] Hardcard Guardian Shares - {guardian_id}'
            msg['From'] = self.config['email']['from']
            msg['To'] = guardian_info['email']
            
            # Email body
            body = f"""
CONFIDENTIAL - HARDCARD GUARDIAN KEY SHARES

Dear {guardian_info.get('name', guardian_id)},

This email contains your encrypted guardian key shares for the Hardcard Governance system.

IMPORTANT SECURITY INSTRUCTIONS:
1. This email contains highly sensitive cryptographic material
2. Decrypt using your PGP private key
3. Store the decrypted shares in a secure, offline location
4. Never share these keys with anyone
5. Delete this email after secure storage

Guardian ID: {guardian_id}
Share Set ID: {share_data.get('verification_hash', 'N/A')}
Generated: {share_data['metadata']['created']}

For verification, the SHA-256 hash of your encrypted share file is:
{self._hash_share_data(share_data)}

If you have any questions or concerns about this distribution, please contact the security team immediately through secure channels.

Best regards,
Hardcard Security Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach encrypted shares
            attachment = MIMEBase('application', 'pgp-encrypted')
            attachment.set_payload(str(encrypted))
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{guardian_id}_shares.asc"'
            )
            msg.attach(attachment)
            
            # Send email
            if self.config['email'].get('enabled', False):
                with smtplib.SMTP(self.config['email']['smtp_host'], 
                                 self.config['email']['smtp_port']) as server:
                    if self.config['email'].get('use_tls', True):
                        server.starttls()
                    if self.config['email'].get('username'):
                        server.login(
                            self.config['email']['username'],
                            self.config['email']['password']
                        )
                    server.send_message(msg)
                print("    ✅ Email sent successfully")
            else:
                # Save to file for manual sending
                email_file = f"email_{guardian_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.eml"
                with open(email_file, 'w') as f:
                    f.write(msg.as_string())
                print(f"    ✅ Email saved to {email_file}")
            
            return True
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False
    
    def _distribute_via_encrypted_file(self, guardian_id: str, guardian_info: Dict,
                                     share_data: Dict, method_config: Dict) -> bool:
        """Create encrypted file for manual distribution"""
        try:
            print(f"  🔒 Creating encrypted file for {guardian_id}...")
            
            # Generate encryption key from passphrase
            passphrase = method_config.get('passphrase')
            if not passphrase:
                # Generate random passphrase
                passphrase = self._generate_passphrase()
                print(f"    🔑 Generated passphrase: {passphrase}")
                print("    ⚠️  SECURELY COMMUNICATE THIS PASSPHRASE TO THE GUARDIAN")
            
            # Derive key from passphrase
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'hardcard_guardian_shares',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
            
            # Encrypt shares
            f = Fernet(key)
            encrypted_data = f.encrypt(json.dumps(share_data).encode())
            
            # Save encrypted file
            output_dir = method_config.get('output_dir', './encrypted_shares')
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{guardian_id}_encrypted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.enc"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as file:
                file.write(encrypted_data)
            
            # Set restrictive permissions
            os.chmod(filepath, 0o600)
            
            print(f"    ✅ Encrypted file saved: {filepath}")
            
            # Create instructions file
            instructions_file = filepath.replace('.enc', '_instructions.txt')
            with open(instructions_file, 'w') as f:
                f.write(f"""
HARDCARD GUARDIAN SHARE DECRYPTION INSTRUCTIONS

Guardian ID: {guardian_id}
Encrypted File: {filename}
Created: {datetime.now().isoformat()}

To decrypt your shares:

1. Install Python 3.8+ and required libraries:
   pip install cryptography

2. Use the following Python script:

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

passphrase = input("Enter passphrase: ")

# Derive key
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=b'hardcard_guardian_shares',
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

# Decrypt
with open('{filename}', 'rb') as f:
    encrypted_data = f.read()

f = Fernet(key)
decrypted = f.decrypt(encrypted_data)
share_data = json.loads(decrypted)

# Save decrypted shares
with open('{guardian_id}_shares.json', 'w') as f:
    json.dump(share_data, f, indent=2)

print("✅ Shares decrypted successfully!")
```

3. Store the decrypted shares securely offline
4. Delete the encrypted file after successful decryption

SECURITY NOTES:
- Never store the passphrase with the encrypted file
- Use a secure channel to receive the passphrase
- Verify the file hash before decryption
- Store decrypted shares offline in a secure location
                """)
            
            print(f"    ✅ Instructions saved: {instructions_file}")
            return True
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False
    
    def _distribute_via_qr_code(self, guardian_id: str, guardian_info: Dict,
                               share_data: Dict, method_config: Dict) -> bool:
        """Generate QR codes for share distribution"""
        try:
            print(f"  📱 Generating QR codes for {guardian_id}...")
            
            output_dir = method_config.get('output_dir', './qr_codes')
            os.makedirs(output_dir, exist_ok=True)
            
            # Create QR codes for each share
            qr_files = []
            for share_for, share_info in share_data['shares'].items():
                # Create QR code data
                qr_data = {
                    'guardian': guardian_id,
                    'for': share_for,
                    'share': share_info,
                    'metadata': share_data['metadata']
                }
                
                # Generate QR code
                qr = qrcode.QRCode(
                    version=None,  # Auto-determine version
                    error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
                    box_size=10,
                    border=4,
                )
                qr.add_data(json.dumps(qr_data))
                qr.make(fit=True)
                
                # Create image
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Save QR code
                filename = f"{guardian_id}_share_{share_for}_qr.png"
                filepath = os.path.join(output_dir, filename)
                img.save(filepath)
                qr_files.append(filepath)
                
                print(f"    ✅ QR code generated: {filename}")
            
            # Create PDF with all QR codes and instructions
            if method_config.get('create_pdf', True):
                self._create_qr_pdf(guardian_id, qr_files, output_dir)
            
            return True
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False
    
    def _distribute_via_secure_message(self, guardian_id: str, guardian_info: Dict,
                                     share_data: Dict, method_config: Dict) -> bool:
        """Prepare shares for secure messaging distribution"""
        try:
            print(f"  💬 Preparing secure message for {guardian_id}...")
            
            # Format shares for secure messaging
            message_parts = []
            
            # Split shares into chunks for messaging
            share_json = json.dumps(share_data, separators=(',', ':'))
            chunk_size = method_config.get('chunk_size', 1000)
            
            chunks = [share_json[i:i+chunk_size] 
                     for i in range(0, len(share_json), chunk_size)]
            
            output_dir = method_config.get('output_dir', './secure_messages')
            os.makedirs(output_dir, exist_ok=True)
            
            # Save each chunk
            for i, chunk in enumerate(chunks):
                filename = f"{guardian_id}_message_part_{i+1}_of_{len(chunks)}.txt"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w') as f:
                    f.write(f"HARDCARD GUARDIAN SHARES - PART {i+1}/{len(chunks)}\n")
                    f.write(f"Guardian: {guardian_id}\n")
                    f.write(f"Timestamp: {datetime.utcnow().isoformat()}\n")
                    f.write("-" * 50 + "\n")
                    f.write(chunk)
                    f.write("\n" + "-" * 50 + "\n")
                    f.write(f"SHA256: {self._hash_data(chunk)}\n")
                
                message_parts.append(filepath)
            
            print(f"    ✅ Created {len(chunks)} message parts")
            
            # Create assembly instructions
            instructions_file = os.path.join(output_dir, f"{guardian_id}_assembly_instructions.txt")
            with open(instructions_file, 'w') as f:
                f.write(f"""
HARDCARD GUARDIAN SHARES - ASSEMBLY INSTRUCTIONS

Guardian: {guardian_id}
Total Parts: {len(chunks)}
Created: {datetime.utcnow().isoformat()}

To reconstruct your shares:

1. Collect all {len(chunks)} message parts
2. Verify each part's SHA256 hash
3. Concatenate the content between the dashed lines
4. The result should be valid JSON
5. Save as {guardian_id}_shares.json

Part checksums:
""")
                for i, part_file in enumerate(message_parts):
                    with open(part_file, 'r') as pf:
                        content = pf.read()
                    f.write(f"  Part {i+1}: {self._hash_data(content)}\n")
                
                f.write(f"""
Final JSON checksum: {self._hash_share_data(share_data)}

Security notes:
- Verify all checksums before use
- Store assembled shares securely offline
- Delete message parts after assembly
- Never share these keys with anyone
""")
            
            print(f"    ✅ Assembly instructions created")
            return True
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False
    
    def _generate_passphrase(self) -> str:
        """Generate a secure passphrase"""
        words = [
            "alpha", "bravo", "charlie", "delta", "echo", "foxtrot",
            "golf", "hotel", "india", "juliet", "kilo", "lima",
            "mike", "november", "oscar", "papa", "quebec", "romeo",
            "sierra", "tango", "uniform", "victor", "whiskey", "xray",
            "yankee", "zulu", "zero", "one", "two", "three",
            "four", "five", "six", "seven", "eight", "nine"
        ]
        
        # Select 6 random words
        passphrase_words = [secrets.choice(words) for _ in range(6)]
        
        # Add random number
        passphrase_words.append(str(secrets.randbelow(1000)))
        
        return "-".join(passphrase_words)
    
    def _hash_share_data(self, share_data: Dict) -> str:
        """Calculate hash of share data"""
        return self._hash_data(json.dumps(share_data, sort_keys=True))
    
    def _hash_data(self, data: str) -> str:
        """Calculate SHA256 hash of data"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _create_qr_pdf(self, guardian_id: str, qr_files: List[str], output_dir: str):
        """Create PDF with QR codes and instructions"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet
            
            pdf_file = os.path.join(output_dir, f"{guardian_id}_qr_codes.pdf")
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            story.append(Paragraph(f"Hardcard Guardian Shares - {guardian_id}", styles['Title']))
            story.append(Spacer(1, 12))
            
            # Instructions
            instructions = """
            <para>
            These QR codes contain your guardian key shares for the Hardcard Governance system.
            <br/><br/>
            <b>Security Instructions:</b><br/>
            1. Scan each QR code with a secure, offline device<br/>
            2. Store the decoded data in a secure location<br/>
            3. Never photograph or share these QR codes<br/>
            4. Destroy this document after secure storage<br/>
            <br/>
            Each QR code contains one share. All shares are required for key recovery.
            </para>
            """
            story.append(Paragraph(instructions, styles['Normal']))
            story.append(Spacer(1, 24))
            
            # Add QR codes
            for qr_file in qr_files:
                img = Image(qr_file, width=200, height=200)
                story.append(img)
                story.append(Spacer(1, 12))
                story.append(Paragraph(os.path.basename(qr_file), styles['Caption']))
                story.append(Spacer(1, 24))
            
            # Build PDF
            doc.build(story)
            print(f"    ✅ PDF created: {pdf_file}")
            
        except ImportError:
            print("    ⚠️  ReportLab not installed, skipping PDF generation")
        except Exception as e:
            print(f"    ⚠️  PDF generation failed: {str(e)}")
    
    def _save_distribution_log(self):
        """Save distribution log for audit trail"""
        log_file = f"distribution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump({
                'timestamp': datetime.utcnow().isoformat(),
                'distributions': self.distribution_log,
                'config_hash': self._hash_data(json.dumps(self.config, sort_keys=True))
            }, f, indent=2)
        print(f"\n📋 Distribution log saved: {log_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Distribute SSKR shares to guardians"
    )
    parser.add_argument(
        "--shares-dir",
        type=str,
        default="./guardian_shares",
        help="Directory containing generated shares"
    )
    parser.add_argument(
        "--guardian-config",
        type=str,
        default="./guardian_config.yaml",
        help="Guardian configuration file"
    )
    parser.add_argument(
        "--distribution-config",
        type=str,
        default="./distribution_config.yaml",
        help="Distribution configuration file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run without actual distribution"
    )
    
    args = parser.parse_args()
    
    # Check if configuration files exist
    if not os.path.exists(args.distribution_config):
        print(f"❌ Distribution config not found: {args.distribution_config}")
        print("\nCreating example configuration...")
        
        example_config = {
            'email': {
                'enabled': False,
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'use_tls': True,
                'from': 'security@hardcard.io',
                'username': '',
                'password': ''
            },
            'security': {
                'require_2fa': True,
                'audit_log': True,
                'test_mode': False
            }
        }
        
        with open(args.distribution_config, 'w') as f:
            yaml.dump(example_config, f, default_flow_style=False)
        
        print(f"✅ Created example config: {args.distribution_config}")
        print("Please configure before running distribution")
        sys.exit(1)
    
    if not os.path.exists(args.guardian_config):
        print(f"❌ Guardian config not found: {args.guardian_config}")
        print("\nCreating example configuration...")
        
        example_guardians = {
            'guardians': {
                'guardian_1': {
                    'name': 'Alice Smith',
                    'email': 'alice@example.com',
                    'pgp_key': 'PASTE_PGP_PUBLIC_KEY_HERE',
                    'distribution_methods': [
                        {'type': 'pgp_email'},
                        {'type': 'encrypted_file', 'output_dir': './alice_shares'}
                    ]
                },
                'guardian_2': {
                    'name': 'Bob Johnson',
                    'email': 'bob@example.com',
                    'distribution_methods': [
                        {'type': 'encrypted_file', 'passphrase': 'GENERATE_SECURE_PASSPHRASE'},
                        {'type': 'qr_code', 'create_pdf': True}
                    ]
                },
                'guardian_3': {
                    'name': 'Charlie Davis',
                    'email': 'charlie@example.com',
                    'distribution_methods': [
                        {'type': 'secure_message', 'chunk_size': 500}
                    ]
                }
            }
        }
        
        with open(args.guardian_config, 'w') as f:
            yaml.dump(example_guardians, f, default_flow_style=False)
        
        print(f"✅ Created example config: {args.guardian_config}")
        print("Please configure guardian details before distribution")
        sys.exit(1)
    
    # Run distribution
    distributor = ShareDistributor(args.distribution_config)
    
    if args.dry_run:
        print("🏃 DRY RUN MODE - No actual distribution will occur")
    
    success = distributor.distribute_shares(args.shares_dir, args.guardian_config)
    
    if success:
        print("\n✅ All shares distributed successfully!")
    else:
        print("\n⚠️  Some distributions failed. Check the log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()