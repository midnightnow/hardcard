from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import time
import hashlib
import uuid
from app.apis.formal_specification import verify_ledger_integrity

router = APIRouter(prefix="/realtblock")

# RealTBlock trust model implementation
# A pure mathematics–based, consensus-free ledger using high-precision timestamps 
# and cryptographic hash chaining

class BlockEntry(BaseModel):
    """An entry in the RealTBlock ledger"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    previous_hash: Optional[str] = None
    data: Dict[str, Any]
    signature: Optional[str] = None
    hash: Optional[str] = None

class LedgerMetadata(BaseModel):
    """Metadata for the RealTBlock ledger"""
    name: str
    description: str
    created_at: float = Field(default_factory=time.time)
    last_updated: float = Field(default_factory=time.time)
    entry_count: int = 0
    head_hash: Optional[str] = None

class Ledger(BaseModel):
    """A RealTBlock ledger"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: LedgerMetadata
    entries: List[BlockEntry] = []

class CreateLedgerRequest(BaseModel):
    """Request to create a new ledger"""
    name: str
    description: str

class AddEntryRequest(BaseModel):
    """Request to add an entry to a ledger"""
    ledger_id: str
    data: Dict[str, Any]
    signature: Optional[str] = None

class VerifyLedgerRequest(BaseModel):
    """Request to verify a ledger's integrity"""
    ledger_id: str

class VerifyLedgerResponse(BaseModel):
    """Response for ledger verification"""
    valid: bool
    errors: List[str] = []

# In-memory storage for ledgers - would be replaced with db.storage in production
ledgers: Dict[str, Ledger] = {}

def calculate_hash(entry: BlockEntry) -> str:
    """Calculate the hash of an entry"""
    # Create a string representation of the entry data
    data_str = f"{entry.id}-{entry.timestamp}-{entry.previous_hash}-{str(entry.data)}"
    
    # Calculate SHA-256 hash
    return hashlib.sha256(data_str.encode()).hexdigest()

@router.post("/ledgers", response_model=Ledger)
def create_ledger(request: CreateLedgerRequest) -> Ledger:
    """Create a new RealTBlock ledger"""
    metadata = LedgerMetadata(
        name=request.name,
        description=request.description
    )
    
    ledger = Ledger(metadata=metadata)
    ledgers[ledger.id] = ledger
    
    return ledger

@router.get("/ledgers/{ledger_id}", response_model=Ledger)
def get_ledger(ledger_id: str) -> Ledger:
    """Get a ledger by ID"""
    if ledger_id not in ledgers:
        raise HTTPException(status_code=404, detail="Ledger not found")
    
    return ledgers[ledger_id]

@router.get("/ledgers", response_model=List[Ledger])
def get_ledgers() -> List[Ledger]:
    """Get all ledgers"""
    return list(ledgers.values())

@router.post("/entries", response_model=BlockEntry)
def add_entry(request: AddEntryRequest) -> BlockEntry:
    """Add an entry to a ledger"""
    if request.ledger_id not in ledgers:
        raise HTTPException(status_code=404, detail="Ledger not found")
    
    ledger = ledgers[request.ledger_id]
    
    # Create new entry
    entry = BlockEntry(
        data=request.data,
        signature=request.signature
    )
    
    # Set previous hash if there are entries
    if ledger.entries:
        entry.previous_hash = ledger.entries[-1].hash
    
    # Calculate hash
    entry.hash = calculate_hash(entry)
    
    # Add to ledger
    ledger.entries.append(entry)
    
    # Update metadata
    ledger.metadata.entry_count += 1
    ledger.metadata.last_updated = time.time()
    ledger.metadata.head_hash = entry.hash
    
    return entry

@router.post("/verify", response_model=VerifyLedgerResponse)
def verify_realtblock_ledger(request: VerifyLedgerRequest) -> VerifyLedgerResponse:
    """Verify the integrity of a ledger"""
    if request.ledger_id not in ledgers:
        raise HTTPException(status_code=404, detail="Ledger not found")
    
    ledger = ledgers[request.ledger_id]
    errors = []
    
    # Convert ledger entries to format expected by verification function
    ledger_events = [
        {
            "id": entry.id,
            "timestamp": entry.timestamp,
            "previous_hash": entry.previous_hash,
            "data": entry.data,
            "signature": entry.signature,
            "hash": entry.hash
        } for entry in ledger.entries
    ]
    
    # Use the formal verification function
    valid, verification_errors = verify_ledger_integrity(ledger_events)
    errors.extend(verification_errors)
    
    # Additional legacy checks
    for i, entry in enumerate(ledger.entries):
        # Skip the first entry (genesis block)
        if i == 0:
            if entry.previous_hash is not None:
                errors.append("Genesis block should not have previous hash")
    
    return VerifyLedgerResponse(
        valid=len(errors) == 0,
        errors=errors
    )

# Hardcard integration
class HardcardSignRequest(BaseModel):
    """Request to sign data with a Hardcard"""
    hardcard_id: str
    data: Dict[str, Any]

class HardcardSignResponse(BaseModel):
    """Response from signing data with a Hardcard"""
    signature: str
    timestamp: float

@router.post("/hardcard/sign", response_model=HardcardSignResponse)
def sign_with_hardcard(request: HardcardSignRequest) -> HardcardSignResponse:
    """Sign data with a Hardcard (simulated)"""
    # In a real implementation, this would communicate with the Hardcard hardware
    # For now, we'll just simulate a signature
    
    data_str = str(request.data)
    signature = hashlib.sha256(f"{request.hardcard_id}-{data_str}-{time.time()}".encode()).hexdigest()
    
    return HardcardSignResponse(
        signature=signature,
        timestamp=time.time()
    )
