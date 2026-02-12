# Session API - Bitcoin Electrum session manager
# Singleton pattern for Electrum session management

import threading
import time
from typing import Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

# Required router for all API files in Databutton
router = APIRouter()

# Global variables for the singleton pattern
_electrum_session = None
_electrum_lock = threading.Lock()
_last_activity = 0
_SESSION_TIMEOUT = 300  # 5 minutes timeout

# Define API models
class SessionStatusResponse(BaseModel):
    """Response model for session status"""
    active: bool
    last_activity: float
    timeout_seconds: int

@router.get("/session-status")
def get_session_status() -> SessionStatusResponse:
    """Get the current status of the Electrum session"""
    with _electrum_lock:
        is_active = _electrum_session is not None
        return SessionStatusResponse(
            active=is_active,
            last_activity=_last_activity,
            timeout_seconds=_SESSION_TIMEOUT
        )

def get_electrum():
    """
    Get a singleton Electrum session.
    This function centralizes Electrum connection management to avoid
    creating multiple connections across different modules.
    
    Returns:
        The Electrum session object
    """
    global _electrum_session, _last_activity
    
    with _electrum_lock:
        current_time = time.time()
        
        # Check if session exists and is still valid
        if _electrum_session is not None:
            # Reset timeout if session exists
            _last_activity = current_time
            return _electrum_session
        
        # Create a new session
        try:
            # In a real implementation, this would import and initialize the actual Electrum client
            # from electrum.simple_config import SimpleConfig
            # from electrum.network import Network
            # from electrum.interface import Interface
            # config = SimpleConfig()
            # network = Network(config)
            # _electrum_session = network
            
            # For now, we'll create a mock Electrum session
            _electrum_session = ElectrumSessionMock()
            
            print("Created new Electrum session")
            _last_activity = current_time
            return _electrum_session
            
        except Exception as e:
            print(f"Error creating Electrum session: {e}")
            raise

class ElectrumSessionMock:
    """
    A mock Electrum session for development and testing
    without requiring the actual Electrum client library.
    
    In production, this would be replaced with actual Electrum client implementation.
    """
    
    def __init__(self):
        self.connected = True
        self.height = 800000  # Mock blockchain height
        self.fees = {"fast": 5, "medium": 2, "slow": 1}  # Mock fee estimates (sat/byte)
        
    def is_connected(self) -> bool:
        return self.connected
    
    def get_local_height(self) -> int:
        return self.height
    
    def get_fee_estimates(self) -> Dict[str, float]:
        return self.fees
    
    def get_address_history(self, address: str) -> list:
        # Return a mock transaction history
        return [
            {
                "tx_hash": "1a2b3c4d5e6f",
                "height": 790000,
                "value": 50000  # 0.0005 BTC in satoshis
            }
        ]
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        # Return a mock transaction
        return {
            "txid": tx_hash,
            "time": int(time.time()) - 3600,  # 1 hour ago
            "inputs": [
                {"prevout_hash": "abcdef", "value": 100000}
            ],
            "outputs": [
                {"value": 50000, "address": "bc1q..."}
            ]
        }
    
    def broadcast_transaction(self, raw_tx: str) -> str:
        # Mock broadcast - would actually submit to Bitcoin network
        return "1a2b3c4d5e6f7890"  # Mock transaction ID
    
    def close(self):
        self.connected = False
        print("Electrum session closed")

def cleanup_idle_sessions():
    """
    Cleanup idle Electrum sessions to free resources.
    This function should be called periodically by a background task.
    """
    global _electrum_session, _last_activity
    
    with _electrum_lock:
        current_time = time.time()
        
        if _electrum_session is not None and (current_time - _last_activity) > _SESSION_TIMEOUT:
            try:
                # Close the session
                _electrum_session.close()
                _electrum_session = None
                print(f"Closed idle Electrum session after {_SESSION_TIMEOUT} seconds")
            except Exception as e:
                print(f"Error closing Electrum session: {e}")
