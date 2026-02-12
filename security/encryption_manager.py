"""
Data encryption utilities using strong cryptography
Enhanced version of OSXAgent encryption for HardCard platform
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Tuple, Optional, Dict, Any
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data for HardCard platform
    Compatible with existing HardCard architecture
    """
    
    def __init__(self, key_file: str = None, service_name: str = "hardcard"):
        """
        Initialize EncryptionManager with an optional key file
        
        Args:
            key_file (str, optional): Path to the encryption key file
            service_name (str): Service name for key identification
        """
        self.service_name = service_name
        self.key_file = key_file or os.path.expanduser(f'~/.hardcard/encryption_{service_name}.key')
        self._ensure_key_directory()
        self.fernet = self._initialize_fernet()
        
    def _ensure_key_directory(self):
        """Create the directory for storing the encryption key if it doesn't exist"""
        key_dir = os.path.dirname(self.key_file)
        os.makedirs(key_dir, exist_ok=True)
        
        # Set proper permissions (owner read/write only)
        try:
            os.chmod(key_dir, 0o700)
        except Exception as e:
            logger.warning(f"Could not set directory permissions: {str(e)}")
        
    def _initialize_fernet(self) -> Fernet:
        """
        Initialize Fernet encryption with an existing or new key
        
        Returns:
            Fernet: Initialized Fernet instance
        """
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
            logger.info("Loaded existing encryption key")
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set secure file permissions
            try:
                os.chmod(self.key_file, 0o600)
            except Exception as e:
                logger.warning(f"Could not set file permissions: {str(e)}")
            logger.info("Generated new encryption key")
            
        return Fernet(key)
        
    def encrypt_data(self, data: str) -> Tuple[bytes, bool]:
        """
        Encrypt string data
        
        Args:
            data (str): Data to encrypt
            
        Returns:
            Tuple[bytes, bool]: (Encrypted data, success status)
        """
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            logger.info("Successfully encrypted data")
            return encrypted_data, True
        except Exception as e:
            logger.error(f"Failed to encrypt data: {str(e)}")
            return b"", False
            
    def decrypt_data(self, encrypted_data: bytes) -> Tuple[str, bool]:
        """
        Decrypt encrypted data
        
        Args:
            encrypted_data (bytes): Data to decrypt
            
        Returns:
            Tuple[str, bool]: (Decrypted data, success status)
        """
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            logger.info("Successfully decrypted data")
            return decrypted_data.decode(), True
        except Exception as e:
            logger.error(f"Failed to decrypt data: {str(e)}")
            return "", False
    
    def encrypt_json(self, data: Dict[Any, Any]) -> Tuple[bytes, bool]:
        """
        Encrypt JSON data
        
        Args:
            data (Dict): Dictionary to encrypt
            
        Returns:
            Tuple[bytes, bool]: (Encrypted data, success status)
        """
        try:
            json_str = json.dumps(data)
            return self.encrypt_data(json_str)
        except Exception as e:
            logger.error(f"Failed to encrypt JSON: {str(e)}")
            return b"", False
    
    def decrypt_json(self, encrypted_data: bytes) -> Tuple[Dict[Any, Any], bool]:
        """
        Decrypt JSON data
        
        Args:
            encrypted_data (bytes): Encrypted JSON data
            
        Returns:
            Tuple[Dict, bool]: (Decrypted dictionary, success status)
        """
        try:
            json_str, success = self.decrypt_data(encrypted_data)
            if not success:
                return {}, False
            
            data = json.loads(json_str)
            return data, True
        except Exception as e:
            logger.error(f"Failed to decrypt JSON: {str(e)}")
            return {}, False
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> bool:
        """
        Encrypt a file
        
        Args:
            file_path (str): Path to file to encrypt
            output_path (str, optional): Output path for encrypted file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if output_path is None:
                output_path = file_path + '.encrypted'
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.fernet.encrypt(file_data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Set secure permissions
            try:
                os.chmod(output_path, 0o600)
            except Exception as e:
                logger.warning(f"Could not set file permissions: {str(e)}")
            
            logger.info(f"Successfully encrypted file: {file_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to encrypt file {file_path}: {str(e)}")
            return False
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> bool:
        """
        Decrypt a file
        
        Args:
            encrypted_file_path (str): Path to encrypted file
            output_path (str, optional): Output path for decrypted file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '')
            
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"Successfully decrypted file: {encrypted_file_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to decrypt file {encrypted_file_path}: {str(e)}")
            return False
            
    def rotate_key(self) -> bool:
        """
        Generate a new encryption key
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Backup old key
            backup_path = self.key_file + '.backup'
            if os.path.exists(self.key_file):
                os.rename(self.key_file, backup_path)
            
            # Generate new key
            new_key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(new_key)
            
            # Set secure permissions
            try:
                os.chmod(self.key_file, 0o600)
            except Exception as e:
                logger.warning(f"Could not set file permissions: {str(e)}")
            
            self.fernet = Fernet(new_key)
            logger.info("Successfully rotated encryption key")
            return True
        except Exception as e:
            logger.error(f"Failed to rotate encryption key: {str(e)}")
            # Restore backup if available
            backup_path = self.key_file + '.backup'
            if os.path.exists(backup_path):
                os.rename(backup_path, self.key_file)
            return False
            
    @staticmethod
    def generate_key_from_password(password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Generate an encryption key from a password using PBKDF2
        
        Args:
            password (str): Password to derive key from
            salt (bytes, optional): Salt for key derivation
            
        Returns:
            bytes: Derived key
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def secure_delete_key(self) -> bool:
        """
        Securely delete the encryption key file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.key_file):
                # Overwrite file with random data before deletion
                file_size = os.path.getsize(self.key_file)
                with open(self.key_file, 'wb') as f:
                    f.write(os.urandom(file_size))
                
                os.remove(self.key_file)
                logger.info("Securely deleted encryption key")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to securely delete key: {str(e)}")
            return False
    
    def get_key_info(self) -> Dict[str, Any]:
        """
        Get information about the encryption key
        
        Returns:
            Dict[str, Any]: Key information
        """
        try:
            if os.path.exists(self.key_file):
                stat = os.stat(self.key_file)
                return {
                    'key_file': self.key_file,
                    'key_exists': True,
                    'created_timestamp': stat.st_ctime,
                    'modified_timestamp': stat.st_mtime,
                    'file_size': stat.st_size,
                    'permissions': oct(stat.st_mode)[-3:]
                }
            else:
                return {
                    'key_file': self.key_file,
                    'key_exists': False
                }
        except Exception as e:
            logger.error(f"Failed to get key info: {str(e)}")
            return {'error': str(e)}