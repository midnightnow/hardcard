from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import databutton as db
import requests
import datetime
import uuid
import json

# Import pricing functions from the bitcoin_price API
from app.apis.bitcoin_price import get_current_bitcoin_price

router = APIRouter()

# Define models
class BitcoinPurchaseRequest(BaseModel):
    amount_usd: float
    profile_id: str
    payment_method: str = "stripe"  # "stripe", "bank_transfer", "wise"
    notes: Optional[str] = None

class BitcoinPurchaseResponse(BaseModel):
    transaction_id: str
    profile_id: str
    amount_usd: float
    btc_amount: float
    btc_price: float
    commission_usd: float
    net_amount_usd: float
    timestamp: str
    status: str
    payment_method: str
    payment_details: Optional[Dict] = None

class BitcoinTransactionStatus(BaseModel):
    transaction_id: str
    status: str
    updated_at: str
    details: Optional[Dict] = None

class BitcoinPurchaseHistoryItem(BaseModel):
    transaction_id: str
    profile_id: str
    amount_usd: float
    btc_amount: float
    btc_price: float
    commission_usd: float
    timestamp: str
    status: str
    payment_method: str

class BitcoinWallet(BaseModel):
    profile_id: str
    total_btc: float
    current_value_usd: float
    total_spent_usd: float
    total_commission_usd: float
    roi_percentage: float
    transactions: List[BitcoinPurchaseHistoryItem]

# Helper function to get commission rate based on amount
def get_commission_rate(amount_usd: float) -> float:
    """Calculate commission rate based on purchase amount"""
    if amount_usd < 100:
        return 0.03  # 3% for small purchases
    elif amount_usd < 1000:
        return 0.02  # 2% for medium purchases
    elif amount_usd < 10000:
        return 0.01  # 1% for large purchases
    else:
        return 0.0075  # 0.75% for very large purchases

# Helper function to sanitize storage key
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Endpoint to initiate Bitcoin purchase
@router.post("/purchase")
async def purchase_bitcoin(request: BitcoinPurchaseRequest) -> BitcoinPurchaseResponse:
    """Initiate a Bitcoin purchase for a profile"""
    try:
        # Get current Bitcoin price
        btc_price = get_current_bitcoin_price()
        
        # Calculate commission
        commission_rate = get_commission_rate(request.amount_usd)
        commission_usd = request.amount_usd * commission_rate
        
        # Calculate net amount after commission
        net_amount_usd = request.amount_usd - commission_usd
        
        # Calculate BTC amount (excluding commission)
        btc_amount = net_amount_usd / btc_price
        
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Create transaction record
        transaction = {
            "transaction_id": transaction_id,
            "profile_id": request.profile_id,
            "amount_usd": request.amount_usd,
            "btc_amount": btc_amount,
            "btc_price": btc_price,
            "commission_usd": commission_usd,
            "net_amount_usd": net_amount_usd,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "pending",  # pending, completed, failed
            "payment_method": request.payment_method,
            "notes": request.notes,
            "payment_details": {}
        }
        
        # Store transaction in DB
        transactions_key = sanitize_storage_key(f"bitcoin_transactions_{request.profile_id}")
        try:
            transactions = db.storage.json.get(transactions_key, default=[])
        except:
            transactions = []
            
        transactions.append(transaction)
        db.storage.json.put(transactions_key, transactions)
        
        # In a real implementation, we would integrate with a payment processor here
        # For mock purposes, we'll simulate this being successful
        
        # Return response
        return BitcoinPurchaseResponse(
            transaction_id=transaction_id,
            profile_id=request.profile_id,
            amount_usd=request.amount_usd,
            btc_amount=btc_amount,
            btc_price=btc_price,
            commission_usd=commission_usd,
            net_amount_usd=net_amount_usd,
            timestamp=transaction["timestamp"],
            status="pending",
            payment_method=request.payment_method,
            payment_details={
                "requires_action": True,
                "next_action": "redirect_to_payment",
                "payment_url": f"https://example.com/pay/{transaction_id}"
            }
        )
    except Exception as e:
        print(f"Error processing Bitcoin purchase: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process Bitcoin purchase: {str(e)}")

# Endpoint to check transaction status
@router.get("/transaction/{transaction_id}")
async def get_transaction_status(transaction_id: str) -> BitcoinTransactionStatus:
    """Get the status of a Bitcoin transaction"""
    try:
        # Search for transaction across all profiles
        # In a real implementation, this would be a database query
        all_transaction_keys = db.storage.json.list()
        transaction_found = None
        
        for key in all_transaction_keys:
            if key.name.startswith("bitcoin_transactions_"):
                transactions = db.storage.json.get(key.name, default=[])
                for tx in transactions:
                    if tx.get("transaction_id") == transaction_id:
                        transaction_found = tx
                        break
                if transaction_found:
                    break
        
        if not transaction_found:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        
        # Return transaction status
        return BitcoinTransactionStatus(
            transaction_id=transaction_id,
            status=transaction_found["status"],
            updated_at=transaction_found.get("updated_at", transaction_found["timestamp"]),
            details=transaction_found.get("payment_details", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving transaction status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve transaction status: {str(e)}")

# Endpoint to update transaction status (would be called by webhook in production)
@router.post("/transaction/{transaction_id}/update")
async def update_transaction_status(transaction_id: str, status: str) -> BitcoinTransactionStatus:
    """Update the status of a Bitcoin transaction"""
    try:
        valid_statuses = ["pending", "processing", "completed", "failed", "refunded"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status '{status}'. Must be one of {valid_statuses}")
        
        # Search for transaction across all profiles
        all_transaction_keys = db.storage.json.list()
        transaction_found = None
        profile_id = None
        transactions_key = None
        
        for key in all_transaction_keys:
            if key.name.startswith("bitcoin_transactions_"):
                transactions = db.storage.json.get(key.name, default=[])
                for i, tx in enumerate(transactions):
                    if tx.get("transaction_id") == transaction_id:
                        transaction_found = tx
                        profile_id = tx.get("profile_id")
                        transactions_key = key.name
                        tx_index = i
                        break
                if transaction_found:
                    break
        
        if not transaction_found or not profile_id or not transactions_key:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        
        # Update the transaction status
        transactions = db.storage.json.get(transactions_key, default=[])
        transactions[tx_index]["status"] = status
        transactions[tx_index]["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save updates
        db.storage.json.put(transactions_key, transactions)
        
        # If status is completed, update the wallet
        if status == "completed":
            # Update wallet balance
            wallet_key = sanitize_storage_key(f"bitcoin_wallet_{profile_id}")
            try:
                wallet = db.storage.json.get(wallet_key, default={})
            except:
                wallet = {
                    "profile_id": profile_id,
                    "total_btc": 0,
                    "total_spent_usd": 0,
                    "total_commission_usd": 0
                }
            
            # Update wallet totals
            wallet["total_btc"] = wallet.get("total_btc", 0) + transaction_found["btc_amount"]
            wallet["total_spent_usd"] = wallet.get("total_spent_usd", 0) + transaction_found["amount_usd"]
            wallet["total_commission_usd"] = wallet.get("total_commission_usd", 0) + transaction_found["commission_usd"]
            
            # Save wallet
            db.storage.json.put(wallet_key, wallet)
        
        # Return updated transaction status
        return BitcoinTransactionStatus(
            transaction_id=transaction_id,
            status=status,
            updated_at=transactions[tx_index]["updated_at"],
            details=transaction_found.get("payment_details", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating transaction status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update transaction status: {str(e)}")

# Endpoint to get Bitcoin wallet for a profile
@router.get("/wallet/{profile_id}")
async def get_profile_bitcoin_wallet(profile_id: str) -> BitcoinWallet:
    """Get Bitcoin wallet information for a profile"""
    try:
        # Get current Bitcoin price
        btc_price = get_current_bitcoin_price()
        
        # Get transactions for this profile
        transactions_key = sanitize_storage_key(f"bitcoin_transactions_{profile_id}")
        try:
            transactions = db.storage.json.get(transactions_key, default=[])
        except:
            transactions = []
        
        # Filter completed transactions
        completed_transactions = [tx for tx in transactions if tx.get("status") == "completed"]
        
        # Calculate totals
        total_btc = sum(tx.get("btc_amount", 0) for tx in completed_transactions)
        total_spent_usd = sum(tx.get("amount_usd", 0) for tx in completed_transactions)
        total_commission_usd = sum(tx.get("commission_usd", 0) for tx in completed_transactions)
        
        # Calculate current value and ROI
        current_value_usd = total_btc * btc_price
        roi_percentage = ((current_value_usd - total_spent_usd) / total_spent_usd * 100) if total_spent_usd > 0 else 0
        
        # Format transaction history
        history_items = []
        for tx in transactions:
            history_items.append(BitcoinPurchaseHistoryItem(
                transaction_id=tx.get("transaction_id"),
                profile_id=profile_id,
                amount_usd=tx.get("amount_usd"),
                btc_amount=tx.get("btc_amount", 0),
                btc_price=tx.get("btc_price", 0),
                commission_usd=tx.get("commission_usd", 0),
                timestamp=tx.get("timestamp"),
                status=tx.get("status"),
                payment_method=tx.get("payment_method", "unknown")
            ))
        
        # Return wallet information
        return BitcoinWallet(
            profile_id=profile_id,
            total_btc=total_btc,
            current_value_usd=current_value_usd,
            total_spent_usd=total_spent_usd,
            total_commission_usd=total_commission_usd,
            roi_percentage=roi_percentage,
            transactions=history_items
        )
    except Exception as e:
        print(f"Error retrieving Bitcoin wallet: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Bitcoin wallet: {str(e)}")
