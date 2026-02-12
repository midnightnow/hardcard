from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List

from app.libs.mock_contract_service import get_mock_contract_service, MockContractService as SmartContractService

router = APIRouter(prefix="/api/escrow", tags=["Escrow"])

# --- Pydantic Models ---

class CreateEscrowRequest(BaseModel):
    jobId: int
    provider: str  # Ethereum address
    milestoneAmounts: List[int]

class TransactionResponse(BaseModel):
    status: str
    transaction_hash: str | None = None
    error: str | None = None
    
# --- Endpoints ---

@router.post("/create", response_model=TransactionResponse)
def create_escrow(
    escrow_request: CreateEscrowRequest,
    contract_service: SmartContractService = Depends(get_mock_contract_service)
):
    """
    Creates an on-chain escrow for a new job.
    This endpoint constructs and signs a transaction to call the `createEscrow`
    function on the NexusAIEscrow smart contract.
    """
    contract = contract_service.get_contract()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Smart contract service is not available. Check configuration.",
        )

    w3 = contract_service.w3
    operator = contract_service.operator_account

    try:
        tx_data = contract.functions.createEscrow(
            escrow_request.jobId,
            w3.to_checksum_address(escrow_request.provider),
            escrow_request.milestoneAmounts
        ).build_transaction({
            'from': operator.address,
            'nonce': w3.eth.get_transaction_count(operator.address),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=operator.key)
        tx_hash_hex = signed_tx.hash.hex()
        # In a real scenario, you would send it:
        # w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Placeholder Mode: Signed createEscrow transaction with hash: {tx_hash_hex}")
        return TransactionResponse(status="success_signed_placeholder", transaction_hash=tx_hash_hex)

    except Exception as e:
        print(f"Error creating escrow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )

# --- Additional Models & Endpoints ---

class MilestoneRequest(BaseModel):
    escrowId: int
    milestoneIndex: int

class ResolveDisputeRequest(BaseModel):
    escrowId: int
    providerAmount: int
    clientAmount: int

@router.post("/release-milestone", response_model=TransactionResponse)
def release_milestone(
    request: MilestoneRequest,
    contract_service: SmartContractService = Depends(get_mock_contract_service)
):
    """Releases a single milestone payment from the escrow."""
    contract = contract_service.get_contract()
    if not contract:
        raise HTTPException(status_code=503, detail="Smart contract service not available")
    
    w3 = contract_service.w3
    operator = contract_service.operator_account

    try:
        tx_data = contract.functions.releaseMilestone(
            request.escrowId,
            request.milestoneIndex
        ).build_transaction({
            'from': operator.address,
            'nonce': w3.eth.get_transaction_count(operator.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=operator.key)
        tx_hash_hex = signed_tx.hash.hex()
        print(f"Placeholder Mode: Signed releaseMilestone transaction with hash: {tx_hash_hex}")
        return TransactionResponse(status="success_signed_placeholder", transaction_hash=tx_hash_hex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initiate-dispute", response_model=TransactionResponse)
def initiate_dispute(
    request: MilestoneRequest, # Re-using for escrowId
    contract_service: SmartContractService = Depends(get_mock_contract_service)
):
    """Initiates a dispute for an escrow."""
    contract = contract_service.get_contract()
    if not contract:
        raise HTTPException(status_code=503, detail="Smart contract service not available")

    w3 = contract_service.w3
    operator = contract_service.operator_account

    try:
        tx_data = contract.functions.initiateDispute(request.escrowId).build_transaction({
            'from': operator.address,
            'nonce': w3.eth.get_transaction_count(operator.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=operator.key)
        tx_hash_hex = signed_tx.hash.hex()
        print(f"Placeholder Mode: Signed initiateDispute transaction with hash: {tx_hash_hex}")
        return TransactionResponse(status="success_signed_placeholder", transaction_hash=tx_hash_hex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resolve-dispute", response_model=TransactionResponse)
def resolve_dispute(
    request: ResolveDisputeRequest,
    contract_service: SmartContractService = Depends(get_mock_contract_service)
):
    """Resolves a dispute by allocating funds between client and provider."""
    contract = contract_service.get_contract()
    if not contract:
        raise HTTPException(status_code=503, detail="Smart contract service not available")

    w3 = contract_service.w3
    operator = contract_service.operator_account

    try:
        tx_data = contract.functions.resolveDispute(
            request.escrowId,
            request.providerAmount,
            request.clientAmount
        ).build_transaction({
            'from': operator.address,
            'nonce': w3.eth.get_transaction_count(operator.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=operator.key)
        tx_hash_hex = signed_tx.hash.hex()
        print(f"Placeholder Mode: Signed resolveDispute transaction with hash: {tx_hash_hex}")
        return TransactionResponse(status="success_signed_placeholder", transaction_hash=tx_hash_hex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/details/{escrow_id}")
def get_escrow_details(
    escrow_id: int,
    contract_service: SmartContractService = Depends(get_mock_contract_service)
):
    """Fetches high-level details for a specific escrow."""
    contract = contract_service.get_contract()
    if not contract:
        raise HTTPException(status_code=503, detail="Smart contract service not available")
    try:
        details = contract.functions.getEscrowDetails(escrow_id).call()
        # Details are returned as a tuple, convert to a dict for JSON response
        return {
            "jobId": details[0],
            "client": details[1],
            "provider": details[2],
            "balance": details[3],
            "milestoneCount": details[4],
            "state": details[5] # Enum: 0=Active, 1=Complete, 2=Disputed, 3=Cancelled
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/milestone/{escrow_id}/{milestone_index}")
def get_milestone_details(
    escrow_id: int,
    milestone_index: int,
    contract_service: SmartContractService = Depends(get_mock_contract_service)
):
    """Fetches details for a specific milestone within an escrow."""
    contract = contract_service.get_contract()
    if not contract:
        raise HTTPException(status_code=503, detail="Smart contract service not available")
    try:
        details = contract.functions.getMilestoneDetails(escrow_id, milestone_index).call()
        return {
            "amount": details[0],
            "released": details[1]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job-id/{job_id}")
def get_escrow_id_for_job(
    job_id: int,
    contract_service: SmartContractService = Depends(get_mock_contract_service)
):
    """Fetches the escrow ID associated with a given job ID."""
    contract = contract_service.get_contract()
    if not contract:
        raise HTTPException(status_code=503, detail="Smart contract service not available")
    try:
        escrow_id = contract.functions.getEscrowIdForJob(job_id).call()
        if escrow_id == 0:
            raise HTTPException(status_code=404, detail="No escrow found for this job ID")
        return {"escrowId": escrow_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

