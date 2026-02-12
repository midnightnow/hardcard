from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Optional, Union
import uuid
import time
import databutton as db
import json
import re

router = APIRouter(
    prefix="/bitcoin/wallet",
    tags=["Bitcoin Wallet"],
    responses={
        400: {"description": "Bad Request - Invalid input parameters"},
        401: {"description": "Unauthorized - Authentication required"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Resource not found"},
        500: {"description": "Internal Server Error - Unexpected error"},
    }
)


def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


class WalletCreationRequest(BaseModel):
    """Request model for creating a new Bitcoin wallet."""
    user_id: str = Field(..., description="The unique identifier for the user initiating the wallet creation.", example="user_123_abc")
    wallet_name: str = Field(default="My Bitcoin Wallet", description="A user-friendly name for the new wallet. Defaults to 'My Bitcoin Wallet' if not provided.", example="Primary Savings Wallet")
    hardcard_secured: bool = Field(default=True, description="Specifies whether the new wallet should be secured with a Hardcard. Defaults to True.", example=True)

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_789_def",
                "wallet_name": "John Doe's Main Bitcoin Wallet",
                "hardcard_secured": True,
            }
        }


class WalletImportRequest(BaseModel):
    """Request model for importing an existing Bitcoin wallet."""
    user_id: str = Field(..., description="The unique identifier for the user importing the wallet.", example="user_456_ghi")
    wallet_name: str = Field(default="My Imported Wallet", description="A user-friendly name for the imported wallet. Defaults to 'My Imported Wallet'.", example="Legacy Investment Wallet")
    private_key: Optional[str] = Field(default=None, description="The private key of the wallet to import. Provide either this or mnemonic_phrase.", example="KxYz... (full private key string)")
    mnemonic_phrase: Optional[str] = Field(default=None, description="The mnemonic phrase (seed phrase) for recovering and importing the wallet. Provide either this or private_key.", example="apple banana cherry ... (12 or 24 words)")
    hardcard_secured: bool = Field(default=True, description="Specifies whether the imported wallet should be marked as secured with a Hardcard. Defaults to True.", example=False)

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_101_jkl",
                "wallet_name": "Imported Cold Storage Wallet",
                "mnemonic_phrase": "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12",
                "hardcard_secured": False,
            }
        }


class WalletResponse(BaseModel):
    """Response model representing a Bitcoin wallet's summary details."""
    wallet_id: str = Field(..., description="The unique system-generated identifier for the wallet.", example="wallet_abc_123")
    wallet_name: str = Field(..., description="The user-defined name of the wallet.", example="Primary Bitcoin Wallet")
    bitcoin_address: str = Field(..., description="The primary Bitcoin address associated with this wallet. (Mocked in this implementation)", example="bc1q_mock_address_12345")
    balance: float = Field(..., description="The current balance of the wallet in BTC.", example=0.50000000)
    hardcard_secured: bool = Field(..., description="Indicates if the wallet is currently marked as secured by a Hardcard.", example=True)
    created_at: int = Field(..., description="Timestamp (Unix epoch seconds) of when the wallet was created or imported into the system.", example=1678886400)

    class Config:
        schema_extra = {
            "example": {
                "wallet_id": "wallet_def456_xyz",
                "wallet_name": "Family Vacation Fund",
                "bitcoin_address": "bc1q_mock_vacation_fund_67890",
                "balance": 1.23456789,
                "hardcard_secured": True,
                "created_at": 1678886400
            }
        }


class TransactionRequest(BaseModel):
    """Request model for initiating a Bitcoin transaction (sending Bitcoin)."""
    recipient_address: str = Field(..., description="The Bitcoin address of the recipient.", example="bc1p_recipient_address_0000")
    amount: float = Field(..., gt=0, description="The amount of Bitcoin (BTC) to send. Must be greater than zero.", example=0.01)
    hardcard_signature: Optional[str] = Field(default=None, description="A cryptographic signature from the Hardcard, required if the sending wallet is Hardcard-secured.", example="0xabcdef1234567890...")
    two_factor_code: Optional[str] = Field(default=None, description="A two-factor authentication code, if 2FA is enabled for the transaction.", example="123456")

    class Config:
        schema_extra = {
            "example": {
                "recipient_address": "bc1p_another_recipient_1111",
                "amount": 0.005,
                "hardcard_signature": "0x123abc_mock_signature_def456",
                "two_factor_code": "654321"
            }
        }


class TransactionResponse(BaseModel):
    """Response model detailing the result of a transaction operation."""
    transaction_id: str = Field(..., description="The unique system-generated identifier for this transaction.", example="tx_xyz_789")
    wallet_id: str = Field(..., description="The ID of the wallet from which the transaction was made.", example="wallet_abc_123")
    recipient_address: str = Field(..., description="The recipient's Bitcoin address.", example="bc1p_recipient_address_0000")
    amount: float = Field(..., description="The amount of Bitcoin (BTC) sent in this transaction.", example=0.01)
    fee: float = Field(..., description="The transaction fee paid in BTC. (Mocked in this implementation)", example=0.0001)
    status: str = Field(..., description="The current status of the transaction (e.g., 'pending', 'completed', 'failed').", example="pending")
    timestamp: int = Field(..., description="Timestamp (Unix epoch seconds) of when the transaction was initiated.", example=1678886500)

    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "tx_ghi789_abc",
                "wallet_id": "wallet_def456_xyz",
                "recipient_address": "bc1p_another_recipient_1111",
                "amount": 0.005,
                "fee": 0.00005,
                "status": "completed",
                "timestamp": 1678886500
            }
        }


class Transaction(BaseModel):
    """Model representing a single Bitcoin transaction record within the system."""
    transaction_id: str = Field(..., description="Unique identifier for the transaction.", example="tx_123_abc_456")
    wallet_id: str = Field(..., description="Identifier of the wallet associated with this transaction.", example="wallet_abc_123")
    type: str = Field(..., description="Type of transaction: 'send' or 'receive'.", example="send")
    address: str = Field(..., description="The counterparty Bitcoin address. For 'send' type, this is the recipient's address. For 'receive' type, this is the sender's address (mocked).", example="bc1q_counterparty_address_789")
    amount: float = Field(..., description="Amount of BTC transferred in this transaction.", example=0.1)
    fee: float = Field(..., description="Transaction fee in BTC. For 'receive' type, this is typically 0 in this mock system.", example=0.0001)
    status: str = Field(..., description="Status of the transaction (e.g., 'pending', 'completed', 'failed').", example="completed")
    timestamp: int = Field(..., description="Timestamp (Unix epoch seconds) of when the transaction occurred or was recorded.", example=1678886400)

    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "tx_mock_receive_abcdef",
                "wallet_id": "wallet_abc_123",
                "type": "receive",
                "address": "mock_external_sender_address_xyz",
                "amount": 0.25,
                "fee": 0.0,
                "status": "completed",
                "timestamp": 1678887000
            }
        }


class TransactionHistoryResponse(BaseModel):
    """Response model for a list of wallet transactions."""
    transactions: List[Transaction] = Field(..., description="A list of transaction records for the queried wallet.")

    class Config:
        schema_extra = {
            "example": {
                "transactions": [
                    {
                        "transaction_id": "tx_123_abc_456",
                        "wallet_id": "wallet_abc_123",
                        "type": "send",
                        "address": "bc1q_counterparty_address_789",
                        "amount": 0.1,
                        "fee": 0.0001,
                        "status": "completed",
                        "timestamp": 1678886400
                    },
                    {
                        "transaction_id": "tx_mock_receive_abcdef",
                        "wallet_id": "wallet_abc_123",
                        "type": "receive",
                        "address": "mock_external_sender_address_xyz",
                        "amount": 0.25,
                        "fee": 0.0,
                        "status": "completed",
                        "timestamp": 1678887000
                    }
                ]
            }
        }


class BitcoinWalletResponse(BaseModel):
    """Response model for detailed Bitcoin wallet information, including its transaction history."""
    wallet_id: str = Field(..., description="Unique system-generated identifier for the wallet.", example="wallet_abc_123")
    wallet_name: str = Field(..., description="User-defined name of the wallet.", example="Main Savings Bitcoin Wallet")
    bitcoin_address: str = Field(..., description="Primary Bitcoin address of the wallet. (Mocked)", example="bc1q_mock_main_savings_addr")
    balance: float = Field(..., description="Current balance of the wallet in BTC.", example=1.50000000)
    hardcard_secured: bool = Field(..., description="Indicates if the wallet is marked as secured by a Hardcard.", example=True)
    created_at: int = Field(..., description="Timestamp (Unix epoch seconds) of when the wallet was created or imported.", example=1678886400)
    transactions: List[Transaction] = Field(..., description="A list of all transactions associated with this wallet.")

    class Config:
        schema_extra = {
            "example": {
                "wallet_id": "wallet_main_user1_ghi",
                "wallet_name": "User One Primary BTC",
                "bitcoin_address": "bc1q_mock_user1_primary_001",
                "balance": 2.75123456,
                "hardcard_secured": True,
                "created_at": 1678886000,
                "transactions": [
                    {
                        "transaction_id": "tx_send_user1_aaa",
                        "wallet_id": "wallet_main_user1_ghi",
                        "type": "send",
                        "address": "bc1q_recipient_for_user1_bbb",
                        "amount": 0.05,
                        "fee": 0.00008,
                        "status": "completed",
                        "timestamp": 1678886100
                    },
                    {
                        "transaction_id": "tx_receive_user1_ccc",
                        "wallet_id": "wallet_main_user1_ghi",
                        "type": "receive",
                        "address": "mock_external_sender_ddd",
                        "amount": 2.80131456,
                        "fee": 0.0,
                        "status": "completed",
                        "timestamp": 1678885000
                    }
                ]
            }
        }


# --- Helper Functions for Storage ---

def _get_user_wallets_storage_key(user_id: str) -> str:
    return f"bitcoin_wallets_{sanitize_storage_key(user_id)}"

def _get_wallet_transactions_storage_key(user_id: str, wallet_id: str) -> str:
    return f"bitcoin_transactions_{sanitize_storage_key(user_id)}_{sanitize_storage_key(wallet_id)}"

def get_all_user_wallets(user_id: str) -> Dict[str, Dict]:
    """Retrieves all wallets for a given user from storage."""
    wallets_key = _get_user_wallets_storage_key(user_id)
    try:
        return db.storage.json.get(wallets_key, default={})
    except Exception as e:
        print(f"Error retrieving wallets for user {user_id}: {e}")
        return {}

def get_wallet_data(user_id: str, wallet_id: str) -> Optional[Dict]:
    """Retrieves specific wallet data for a user from storage."""
    user_wallets = get_all_user_wallets(user_id)
    return user_wallets.get(sanitize_storage_key(wallet_id))

def save_wallet_data(user_id: str, wallet_id: str, wallet_data_to_save: Dict) -> bool:
    """Saves specific wallet data for a user to storage."""
    wallets_key = _get_user_wallets_storage_key(user_id)
    wallet_id_sanitized = sanitize_storage_key(wallet_id)
    try:
        all_wallets = db.storage.json.get(wallets_key, default={})
        all_wallets[wallet_id_sanitized] = wallet_data_to_save
        db.storage.json.put(wallets_key, all_wallets)
        return True
    except Exception as e:
        print(f"Error saving wallet {wallet_id_sanitized} for user {user_id}: {e}")
        return False

def save_transaction_record(user_id: str, wallet_id: str, transaction_record: Dict) -> bool:
    """Saves a transaction record for a specific wallet of a user."""
    transactions_key = _get_wallet_transactions_storage_key(user_id, wallet_id)
    try:
        transactions = db.storage.json.get(transactions_key, default=[])
        transactions.append(transaction_record)
        db.storage.json.put(transactions_key, transactions)
        return True
    except Exception as e:
        print(f"Error saving transaction for wallet {wallet_id}, user {user_id}: {e}")
        return False

def get_wallet_transactions(user_id: str, wallet_id: str) -> List[Dict]:
    """Retrieves all transaction records for a specific wallet of a user."""
    transactions_key = _get_wallet_transactions_storage_key(user_id, wallet_id)
    try:
        return db.storage.json.get(transactions_key, default=[])
    except Exception as e:
        print(f"Error retrieving transactions for wallet {wallet_id}, user {user_id}: {e}")
        return []

# --- API Endpoints ---

@router.post(
    "/create",
    summary="Create New Bitcoin Wallet",
    description="""Creates a new, empty Bitcoin wallet for the specified user.
This endpoint generates a unique system identifier (wallet_id) and a mock Bitcoin address.
The wallet's initial balance is set to zero. It can be optionally secured with a Hardcard
if `hardcard_secured` is true in the request. Wallet metadata (excluding sensitive details
like raw private keys in a real-world scenario) is persisted to the application's secure storage.

**Note:** This is a simplified mock implementation. A production-grade system would involve
complex cryptographic operations for secure key generation, address derivation, and robust
protection of sensitive materials, likely integrating with hardware security modules or
specialized key management services.""",
    response_model=WalletResponse,
    responses={
        200: {"description": "Wallet created successfully.", "model": WalletResponse},
        500: {"description": "Failed to create or save the wallet due to an internal error."}
    }
)
def create_bitcoin_wallet(request: WalletCreationRequest):
    wallet_id = str(uuid.uuid4())
    bitcoin_address = f"bc1q_mock_{uuid.uuid4().hex[:28]}" # Mock address

    wallet_data = {
        "wallet_id": wallet_id,
        "wallet_name": request.wallet_name,
        "bitcoin_address": bitcoin_address,
        "balance": 0.0,
        "hardcard_secured": request.hardcard_secured,
        "mock_private_key": f"mock_pk_{uuid.uuid4().hex}", # Placeholder for actual key material
        "created_at": int(time.time())
    }

    if not save_wallet_data(request.user_id, wallet_id, wallet_data):
        raise HTTPException(status_code=500, detail="Failed to create and save wallet.")

    return WalletResponse(
        wallet_id=wallet_id,
        wallet_name=request.wallet_name,
        bitcoin_address=bitcoin_address,
        balance=0.0,
        hardcard_secured=request.hardcard_secured,
        created_at=wallet_data["created_at"]
    )


@router.post(
    "/import",
    summary="Import Existing Bitcoin Wallet",
    description="""Imports an existing Bitcoin wallet using a provided private key or mnemonic phrase.
This allows a user to add and manage an externally created wallet within their Hardcard profile.
The system generates a new unique `wallet_id` for this imported wallet and creates a mock Bitcoin
address based on the provided import material (private key or mnemonic). The wallet can be
optionally marked as Hardcard-secured upon import.

**Important Security Note:** In a real application, handling private keys and mnemonic phrases
requires extreme care and robust security measures. This mock implementation does not perform
actual cryptographic operations or secure storage of such sensitive data. Address derivation
and input validation are also simplified. A production system would use specialized cryptographic
libraries and secure enclaves or similar technologies.""",
    response_model=WalletResponse,
    responses={
        200: {"description": "Wallet imported successfully.", "model": WalletResponse},
        400: {"description": "Missing private key or mnemonic phrase for import."},
        500: {"description": "Failed to import or save the wallet due to an internal error."}
    }
)
def import_bitcoin_wallet(request: WalletImportRequest):
    if not request.private_key and not request.mnemonic_phrase:
        raise HTTPException(status_code=400, detail="Either private key or mnemonic phrase must be provided for import.")

    wallet_id = str(uuid.uuid4())
    import_material_excerpt = (request.private_key or request.mnemonic_phrase)[:8].replace(" ", "")
    bitcoin_address = f"bc1q_imp_{import_material_excerpt}{uuid.uuid4().hex[:20]}" # Mock address

    wallet_data = {
        "wallet_id": wallet_id,
        "wallet_name": request.wallet_name,
        "bitcoin_address": bitcoin_address,
        "balance": 0.0, # Imported wallets start with zero balance in this mock system
        "hardcard_secured": request.hardcard_secured,
        "mock_imported_material": request.private_key or request.mnemonic_phrase, # Placeholder
        "created_at": int(time.time())
    }

    if not save_wallet_data(request.user_id, wallet_id, wallet_data):
        raise HTTPException(status_code=500, detail="Failed to import and save wallet.")

    return WalletResponse(
        wallet_id=wallet_id,
        wallet_name=request.wallet_name,
        bitcoin_address=bitcoin_address,
        balance=0.0,
        hardcard_secured=request.hardcard_secured,
        created_at=wallet_data["created_at"]
    )


@router.get(
    "/{user_id}/{wallet_id}",
    summary="Get Specific Wallet Details",
    description="""Retrieves comprehensive information for a specific Bitcoin wallet, identified by `user_id` and `wallet_id`.
The response includes the wallet's user-defined name, its (mock) Bitcoin address, current balance in BTC,
Hardcard security status, creation timestamp (Unix epoch), and a list of all associated transactions
(both sent and received, as recorded by this system).""",
    response_model=BitcoinWalletResponse,
    responses={
        200: {"description": "Wallet details retrieved successfully.", "model": BitcoinWalletResponse},
        404: {"description": "Wallet with the specified ID not found for the given user."}
    }
)
def get_bitcoin_wallet(user_id: str = Path(..., description="The unique identifier of the user who owns the wallet.", example="user_123_abc"),
                       wallet_id: str = Path(..., description="The unique identifier of the wallet to retrieve.", example="wallet_abc_123")):
    wallet_data = get_wallet_data(user_id, wallet_id)
    if not wallet_data:
        raise HTTPException(status_code=404, detail=f"Wallet with ID '{wallet_id}' not found for user '{user_id}'.")

    transaction_records = get_wallet_transactions(user_id, wallet_id)
    transactions = [Transaction(**tx) for tx in transaction_records]

    return BitcoinWalletResponse(
        wallet_id=wallet_data["wallet_id"],
        wallet_name=wallet_data["wallet_name"],
        bitcoin_address=wallet_data["bitcoin_address"],
        balance=wallet_data["balance"],
        hardcard_secured=wallet_data["hardcard_secured"],
        created_at=wallet_data["created_at"],
        transactions=transactions
    )


@router.get(
    "/{user_id}",
    summary="List All Bitcoin Wallets for a User",
    description="""Lists all Bitcoin wallets currently associated with the specified `user_id`.
Returns an array of wallet summaries. Each summary includes the wallet's unique ID (`wallet_id`),
its user-defined name, (mock) Bitcoin address, current balance, Hardcard security status,
and creation timestamp. If the user has no wallets, an empty list is returned.""",
    response_model=List[WalletResponse],
    responses={
        200: {"description": "A list of user's wallets or an empty list if none found.", "model": List[WalletResponse]}
    }
)
def list_bitcoin_wallets(user_id: str = Path(..., description="The unique identifier of the user whose wallets are to be listed.", example="user_456_def")):
    user_wallets = get_all_user_wallets(user_id)
    if not user_wallets:
        return []

    return [
        WalletResponse(
            wallet_id=w_id,
            wallet_name=w_data["wallet_name"],
            bitcoin_address=w_data["bitcoin_address"],
            balance=w_data["balance"],
            hardcard_secured=w_data["hardcard_secured"],
            created_at=w_data["created_at"]
        ) for w_id, w_data in user_wallets.items()
    ]


@router.post(
    "/{user_id}/{wallet_id}/send",
    summary="Send Bitcoin from a Wallet",
    description="""Initiates a Bitcoin transaction from a user's specified wallet to a recipient address.
The request must include the `recipient_address` and the `amount` (in BTC) to send.
If the source wallet (`wallet_id`) is Hardcard-secured, a valid `hardcard_signature`
must be provided in the request body. This endpoint performs mock balance checks and
calculates a mock transaction fee.

**Note:** Transaction broadcasting to the actual Bitcoin network is mocked.
A production system would interact with the Bitcoin blockchain via nodes or APIs,
handle unspent transaction outputs (UTXOs), and manage network fees dynamically.""",
    response_model=TransactionResponse,
    responses={
        200: {"description": "Transaction initiated successfully (mocked).", "model": TransactionResponse},
        400: {"description": "Insufficient balance or invalid request parameters."},
        403: {"description": "Hardcard signature required for this secured wallet but not provided."},
        404: {"description": "Source wallet not found for the user."},
        500: {"description": "Internal error processing the transaction or updating wallet state."}
    }
)
def send_bitcoin(request: TransactionRequest,
                 user_id: str = Path(..., description="User ID of the wallet owner.", example="user_123"),
                 wallet_id: str = Path(..., description="Wallet ID from which to send Bitcoin.", example="wallet_abc")):
    wallet_data = get_wallet_data(user_id, wallet_id)
    if not wallet_data:
        raise HTTPException(status_code=404, detail=f"Wallet with ID '{wallet_id}' not found for user '{user_id}'.")

    if wallet_data["hardcard_secured"] and not request.hardcard_signature:
        raise HTTPException(status_code=403, detail="Hardcard signature is required for transactions from this secured wallet.")

    fee = 0.00005 # Example mock fee
    total_deduction = request.amount + fee

    if wallet_data["balance"] < total_deduction:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Current: {wallet_data['balance']} BTC, Required: {total_deduction} BTC (amount + fee).")

    transaction_id = f"tx_mock_{uuid.uuid4().hex}"
    transaction_record = {
        "transaction_id": transaction_id,
        "wallet_id": wallet_id,
        "type": "send",
        "address": request.recipient_address,
        "amount": request.amount,
        "fee": fee,
        "status": "pending", # Mock status
        "timestamp": int(time.time())
    }

    if not save_transaction_record(user_id, wallet_id, transaction_record):
         raise HTTPException(status_code=500, detail="Failed to save transaction record.")

    wallet_data["balance"] -= total_deduction
    if not save_wallet_data(user_id, wallet_id, wallet_data):
        print(f"CRITICAL: Failed to save updated balance for wallet {wallet_id} after transaction {transaction_id}")
        raise HTTPException(status_code=500, detail="Failed to update wallet balance after transaction.")

    return TransactionResponse(
        transaction_id=transaction_id,
        wallet_id=wallet_id,
        recipient_address=request.recipient_address,
        amount=request.amount,
        fee=fee,
        status="pending",
        timestamp=transaction_record["timestamp"]
    )


@router.get(
    "/{user_id}/{wallet_id}/transactions",
    summary="Get Wallet Transaction History",
    description="""Retrieves the list of all recorded transactions (sent and received) for a specific Bitcoin wallet,
identified by `user_id` and `wallet_id`. The transactions are returned in a list,
with each transaction containing details like ID, type, amount, fee, status, and timestamp.""",
    response_model=TransactionHistoryResponse,
    responses={
        200: {"description": "Transaction history retrieved successfully.", "model": TransactionHistoryResponse},
        404: {"description": "Wallet not found for the specified user and wallet ID."}
    }
)
def get_transaction_history(user_id: str = Path(..., description="User ID of the wallet owner.", example="user_789"),
                            wallet_id: str = Path(..., description="Wallet ID to fetch transaction history for.", example="wallet_def")):
    if not get_wallet_data(user_id, wallet_id): # Check if wallet exists
         raise HTTPException(status_code=404, detail=f"Wallet with ID '{wallet_id}' not found for user '{user_id}'.")

    transaction_records = get_wallet_transactions(user_id, wallet_id)
    transactions = [Transaction(**tx) for tx in transaction_records]
    return TransactionHistoryResponse(transactions=transactions)


@router.post(
    "/{user_id}/{wallet_id}/link-hardcard",
    summary="Link Hardcard to Wallet (Conceptual)",
    description="""Marks an existing wallet as Hardcard-secured.
This is a conceptual operation within this mock system. In a real-world application,
this would involve complex cryptographic pairing procedures with a physical Hardcard device.
Here, it simply updates a 'hardcard_secured' flag and records a linking timestamp
in the wallet's stored data. No actual hardware interaction occurs.""",
    responses={
        200: {"description": "Wallet successfully marked as Hardcard-secured.", "content": {"application/json": {"example": {"status": "success", "message": "Wallet wallet_abc is now marked as hardcard-secured."}}}},
        404: {"description": "Wallet not found for the specified user and wallet ID."},
        500: {"description": "Failed to update wallet data for Hardcard linking."}
    }
)
def link_hardcard_to_wallet(user_id: str = Path(..., description="User ID of the wallet owner.", example="user_123"),
                              wallet_id: str = Path(..., description="Wallet ID to be linked with a Hardcard.", example="wallet_abc")):
    wallet_data = get_wallet_data(user_id, wallet_id)
    if not wallet_data:
        raise HTTPException(status_code=404, detail=f"Wallet with ID '{wallet_id}' not found for user '{user_id}'.")

    wallet_data["hardcard_secured"] = True
    wallet_data["hardcard_linked_at"] = int(time.time()) # Record linking time

    if not save_wallet_data(user_id, wallet_id, wallet_data):
        raise HTTPException(status_code=500, detail="Failed to update wallet for hardcard linking.")

    return {"status": "success", "message": f"Wallet {wallet_id} is now marked as hardcard-secured."}


@router.post(
    "/{user_id}/{wallet_id}/mock/add-funds/{amount}",
    summary="Add Mock Funds to Wallet (Testing Only)",
    description="""Adds a specified amount of mock Bitcoin to a wallet. **This endpoint is for development and testing purposes ONLY.**
It simulates receiving Bitcoin by directly increasing the wallet's balance in the system's storage
and creating a corresponding mock 'receive' transaction record. It does not interact with any
real Bitcoin network or external services. The `amount` must be a positive number.""",
    responses={
        200: {"description": "Mock funds added successfully.", "content": {"application/json": {"example": {"status": "success", "message": "Added 0.5 BTC to wallet wallet_xyz.", "new_balance": 1.5, "transaction_id": "tx_mock_recv_123"}}}},
        400: {"description": "Invalid amount (must be positive)."},
        404: {"description": "Wallet not found for the specified user and wallet ID."},
        500: {"description": "Failed to update wallet balance or save mock transaction."}
    }
)
def add_funds_to_wallet(user_id: str = Path(..., description="User ID of the wallet owner.", example="user_test"),
                        wallet_id: str = Path(..., description="Wallet ID to add funds to.", example="wallet_test"),
                        amount: float = Path(..., gt=0, description="Amount of mock BTC to add.", example=0.5)):
    if amount <= 0: # Redundant due to gt=0 in Path, but good for explicit check
        raise HTTPException(status_code=400, detail="Amount to add must be positive.")

    wallet_data = get_wallet_data(user_id, wallet_id)
    if not wallet_data:
        raise HTTPException(status_code=404, detail=f"Wallet with ID '{wallet_id}' not found for user '{user_id}'.")

    wallet_data["balance"] += amount
    
    receive_tx_id = f"tx_mock_recv_{uuid.uuid4().hex}"
    transaction_record = {
        "transaction_id": receive_tx_id,
        "wallet_id": wallet_id,
        "type": "receive",
        "address": "mock_external_sender_address", # Source of funds
        "amount": amount,
        "fee": 0.0, # No fee for receiving in this mock
        "status": "completed",
        "timestamp": int(time.time())
    }

    save_transaction_success = save_transaction_record(user_id, wallet_id, transaction_record)
    save_wallet_success = save_wallet_data(user_id, wallet_id, wallet_data)

    if not save_transaction_success or not save_wallet_success:
        details = []
        if not save_transaction_success: details.append("Failed to save mock receive transaction.")
        if not save_wallet_success: details.append("Failed to update wallet balance.")
        raise HTTPException(status_code=500, detail=" ".join(details))
        
    return {
        "status": "success",
        "message": f"Added {amount} BTC to wallet {wallet_id}.",
        "new_balance": wallet_data["balance"],
        "transaction_id": receive_tx_id
    }


@router.get(
    "/profile/{user_id}/main-wallet",
    summary="Get Profile's Main Bitcoin Wallet (Illustrative)",
    description="""Illustrative endpoint to retrieve what might be considered a user's 'main' or default Bitcoin wallet.
**This is a placeholder for more complex wallet selection or defaulting logic.**
Currently, it attempts to return the first wallet found associated with the `user_id`.
If no wallets are found, it returns a 404 error. The response includes full wallet details
and its transaction history, similar to the `/bitcoin/wallet/{user_id}/{wallet_id}` endpoint.""",
    response_model=BitcoinWalletResponse,
    deprecated=True, # Marking as potentially deprecated as a more robust solution would be needed
    responses={
        200: {"description": "Main wallet details retrieved successfully.", "model": BitcoinWalletResponse},
        404: {"description": "No wallets found for the user, or the concept of a 'main' wallet is not yet defined."}
    }
)
def get_user_main_bitcoin_wallet(user_id: str = Path(..., description="The unique identifier of the user.", example="user_main_profile")):
    user_wallets = get_all_user_wallets(user_id)
    if not user_wallets:
        raise HTTPException(status_code=404, detail=f"No wallets found for user '{user_id}'.")

    first_wallet_id = next(iter(user_wallets)) # Simplistic: takes the first one
    first_wallet_data = user_wallets[first_wallet_id]
    
    transaction_records = get_wallet_transactions(user_id, first_wallet_id)
    transactions = [Transaction(**tx) for tx in transaction_records]

    return BitcoinWalletResponse(
        wallet_id=first_wallet_data["wallet_id"],
        wallet_name=first_wallet_data["wallet_name"],
        bitcoin_address=first_wallet_data["bitcoin_address"],
        balance=first_wallet_data["balance"],
        hardcard_secured=first_wallet_data["hardcard_secured"],
        created_at=first_wallet_data["created_at"],
        transactions=transactions
    )

