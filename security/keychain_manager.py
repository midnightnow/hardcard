"""
Secure API key management using macOS Keychain
Enhanced version of OSXAgent keychain integration for HardCard
"""
import keyring
import logging
import threading
from typing import Optional, Dict, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class KeychainManager:
    """
    Manages secure storage of credentials using macOS Keychain Services
    Compatible with HardCard platform requirements
    """
    
    def __init__(self, service_name: str = "hardcard"):
        """
        Initialize KeychainManager with a service name and thread safety
        
        Args:
            service_name (str): Name of the service for keychain entries
        """
        self.service_name = service_name
        
        # Thread safety implementation
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._metadata_lock = threading.Lock()  # Separate lock for metadata operations
        
    def store_api_key(self, key_name: str, api_key: str) -> bool:
        """
        Securely store an API key in the macOS Keychain with thread safety
        
        Args:
            key_name (str): Identifier for the API key (e.g., 'openai_api', 'twilio_sid')
            api_key (str): The API key to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        with self._lock:
            try:
                keyring.set_password(self.service_name, key_name, api_key)
                logger.info(f"Successfully stored API key: {key_name}")
                
                # Store metadata for tracking
                self._store_key_metadata(key_name)
                return True
            except Exception as e:
                logger.error(f"Failed to store API key {key_name}: {str(e)}")
                return False
            
    def get_api_key(self, key_name: str) -> Optional[str]:
        """
        Retrieve an API key from the macOS Keychain with thread safety
        
        Args:
            key_name (str): Identifier for the API key
            
        Returns:
            Optional[str]: The API key if found, None otherwise
        """
        with self._lock:
            try:
                api_key = keyring.get_password(self.service_name, key_name)
                if api_key:
                    logger.info(f"Successfully retrieved API key: {key_name}")
                    self._update_access_time(key_name)
                    return api_key
                logger.warning(f"API key not found: {key_name}")
                return None
            except Exception as e:
                logger.error(f"Failed to retrieve API key {key_name}: {str(e)}")
                return None
            
    def delete_api_key(self, key_name: str) -> bool:
        """
        Delete an API key from the macOS Keychain with thread safety
        
        Args:
            key_name (str): Identifier for the API key
            
        Returns:
            bool: True if successful, False otherwise
        """
        with self._lock:
            try:
                keyring.delete_password(self.service_name, key_name)
                logger.info(f"Successfully deleted API key: {key_name}")
                
                # Clean up metadata
                self._remove_key_metadata(key_name)
                return True
            except Exception as e:
                logger.error(f"Failed to delete API key {key_name}: {str(e)}")
                return False
            
    def update_api_key(self, key_name: str, new_api_key: str) -> bool:
        """
        Update an existing API key in the macOS Keychain with thread safety
        
        Args:
            key_name (str): Identifier for the API key
            new_api_key (str): The new API key value
            
        Returns:
            bool: True if successful, False otherwise
        """
        with self._lock:
            try:
                # Delete existing key if present
                try:
                    keyring.delete_password(self.service_name, key_name)
                except:
                    pass
                    
                # Store new key
                keyring.set_password(self.service_name, key_name, new_api_key)
                logger.info(f"Successfully updated API key: {key_name}")
                
                # Update metadata
                self._store_key_metadata(key_name, is_update=True)
                return True
            except Exception as e:
                logger.error(f"Failed to update API key {key_name}: {str(e)}")
                return False
    
    def list_stored_keys(self) -> List[str]:
        """
        List all API keys stored for this service with thread safety
        
        Returns:
            List[str]: List of key names
        """
        with self._lock:
            try:
                metadata = self._get_metadata()
                return list(metadata.get('keys', {}).keys())
            except Exception as e:
                logger.error(f"Failed to list stored keys: {str(e)}")
                return []
    
    def get_key_info(self, key_name: str) -> Optional[Dict]:
        """
        Get information about a stored key with thread safety
        
        Args:
            key_name (str): Identifier for the API key
            
        Returns:
            Optional[Dict]: Key metadata or None
        """
        with self._lock:
            try:
                metadata = self._get_metadata()
                return metadata.get('keys', {}).get(key_name)
            except Exception as e:
                logger.error(f"Failed to get key info for {key_name}: {str(e)}")
                return None
    
    def _store_key_metadata(self, key_name: str, is_update: bool = False):
        """Store metadata about the key for tracking purposes with thread safety"""
        with self._metadata_lock:
            try:
                metadata = self._get_metadata()
                if 'keys' not in metadata:
                    metadata['keys'] = {}
                
                metadata['keys'][key_name] = {
                    'created_at': datetime.now().isoformat() if not is_update else 
                                  metadata.get('keys', {}).get(key_name, {}).get('created_at'),
                    'updated_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'access_count': metadata.get('keys', {}).get(key_name, {}).get('access_count', 0) + 1
                }
                
                self._save_metadata(metadata)
            except Exception as e:
                logger.error(f"Failed to store metadata for {key_name}: {str(e)}")
    
    def _update_access_time(self, key_name: str):
        """Update the last access time for a key with thread safety"""
        with self._metadata_lock:
            try:
                metadata = self._get_metadata()
                if 'keys' in metadata and key_name in metadata['keys']:
                    metadata['keys'][key_name]['last_accessed'] = datetime.now().isoformat()
                    metadata['keys'][key_name]['access_count'] = metadata['keys'][key_name].get('access_count', 0) + 1
                    self._save_metadata(metadata)
            except Exception as e:
                logger.error(f"Failed to update access time for {key_name}: {str(e)}")
    
    def _remove_key_metadata(self, key_name: str):
        """Remove metadata for a deleted key with thread safety"""
        with self._metadata_lock:
            try:
                metadata = self._get_metadata()
                if 'keys' in metadata and key_name in metadata['keys']:
                    del metadata['keys'][key_name]
                    self._save_metadata(metadata)
            except Exception as e:
                logger.error(f"Failed to remove metadata for {key_name}: {str(e)}")
    
    def _get_metadata(self) -> Dict:
        """Retrieve metadata from keychain"""
        try:
            metadata_str = keyring.get_password(self.service_name, '_metadata')
            if metadata_str:
                return json.loads(metadata_str)
            return {}
        except Exception:
            return {}
    
    def _save_metadata(self, metadata: Dict):
        """Save metadata to keychain"""
        try:
            metadata_str = json.dumps(metadata)
            keyring.set_password(self.service_name, '_metadata', metadata_str)
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")

    # HardCard-specific convenience methods
    def store_firebase_config(self, config: Dict[str, str]) -> bool:
        """Store Firebase configuration securely"""
        success = True
        for key, value in config.items():
            if not self.store_api_key(f"firebase_{key}", value):
                success = False
        return success
    
    def get_firebase_config(self) -> Dict[str, str]:
        """Retrieve Firebase configuration"""
        config = {}
        firebase_keys = [
            'apiKey', 'authDomain', 'projectId', 'storageBucket', 
            'messagingSenderId', 'appId', 'measurementId'
        ]
        
        for key in firebase_keys:
            value = self.get_api_key(f"firebase_{key}")
            if value:
                config[key] = value
        
        return config
    
    def store_twilio_config(self, config: Dict[str, str]) -> bool:
        """Store Twilio configuration securely"""
        success = True
        for key, value in config.items():
            if not self.store_api_key(f"twilio_{key}", value):
                success = False
        return success
    
    def get_twilio_config(self) -> Dict[str, str]:
        """Retrieve Twilio configuration"""
        config = {}
        twilio_keys = [
            'account_sid', 'api_key_sid', 'api_key_secret', 
            'auth_token', 'phone_number'
        ]
        
        for key in twilio_keys:
            value = self.get_api_key(f"twilio_{key}")
            if value:
                config[key] = value
        
        return config