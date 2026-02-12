from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import databutton as db
import requests
from datetime import datetime, timedelta
# import json # Removed redundant import, already imported by db.storage implicitly or not needed directly
from app.auth import AuthorizedUser

router = APIRouter()

# Pydantic models for requests and responses
class XeroConnectionRequest(BaseModel):
    redirect_uri: str

class XeroConnectionResponse(BaseModel):
    authorization_url: str

class XeroTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    id_token: Optional[str] = None
    refresh_token: str

class XeroOrganization(BaseModel):
    id: str
    name: str
    tenant_type: str

class XeroOrganizationsResponse(BaseModel):
    organizations: List[XeroOrganization]

class XeroAccount(BaseModel):
    account_id: str
    code: str
    name: str
    type: str
    tax_type: Optional[str] = None
    description: Optional[str] = None
    updated_date_utc: Optional[str] = None

class XeroTransaction(BaseModel):
    transaction_id: str
    type: str
    contact_name: Optional[str] = None
    date: str
    status: str
    line_amount_types: Optional[str] = None
    sub_total: float
    total_tax: float
    total: float
    updated_date_utc: str
    currency_code: str
    reference: Optional[str] = None
    description: Optional[str] = None

class XeroTransactionsResponse(BaseModel):
    transactions: List[XeroTransaction]

class XeroInvoice(BaseModel):
    invoice_id: str
    type: str
    contact_name: str
    date: str
    due_date: str
    status: str
    sub_total: float
    total_tax: float
    total: float
    currency_code: str
    invoice_number: Optional[str] = None
    reference: Optional[str] = None
    line_items: Optional[List[Dict[str, Any]]] = None

class XeroInvoicesResponse(BaseModel):
    invoices: List[XeroInvoice]

class XeroSyncStatusResponse(BaseModel):
    last_sync: Optional[str] = None
    sync_status: str
    item_counts: Dict[str, int]

class XeroFinancialHealthResponse(BaseModel):
    cash_position: float
    accounts_receivable: float
    accounts_payable: float
    revenue_30_days: float
    expenses_30_days: float
    net_position: float

class XeroAnomalyDetectionResponse(BaseModel):
    anomalies: List[Dict[str, Any]]
    analysis_date: str

class XeroTransactionCategorization(BaseModel):
    transaction_id: str
    suggested_category: str
    confidence: float
    alternative_categories: List[Dict[str, float]]

class XeroCategorizeTransactionRequest(BaseModel):
    transaction_id: str
    description: str
    amount: float
    date: str

class XeroCategorizeTransactionsResponse(BaseModel):
    categorizations: List[XeroTransactionCategorization]

# Helper functions
def get_xero_client_config():
    """Get Xero API client configuration from secrets"""
    try:
        client_id = db.secrets.get("XERO_CLIENT_ID")
        client_secret = db.secrets.get("XERO_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise ValueError("Xero API credentials not found")
        return {
            "client_id": client_id,
            "client_secret": client_secret,
        }
    except Exception as e:
        print(f"Error getting Xero client config: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving Xero API configuration") from e

import json # Add for JSONDecodeError if needed, or rely on db.storage specifics

def get_token_data(user_id: str):
    """Get stored token data for a user"""
    storage_key = f"xero_token_{user_id}"
    try:
        return db.storage.json.get(storage_key)
    except FileNotFoundError:
        print(f"Token data not found for user {user_id} at {storage_key}, returning empty dict.")
        return {}
    except Exception as e:
        print(f"Error getting token data for user {user_id} from {storage_key}: {e}. Returning empty dict.")
        # Depending on how critical this is, could re-raise or raise HTTPException
        return {}

def save_token_data(user_id: str, token_data: dict):
    """Save token data for a user"""
    storage_key = f"xero_token_{user_id}"
    try:
        db.storage.json.put(storage_key, token_data)
        print(f"Successfully saved token data for user {user_id} to {storage_key}")
    except Exception as e:
        print(f"Error saving token data for user {user_id} to {storage_key}: {e}")
        # Raising an HTTPException to make the failure immediately apparent
        # to the calling function and ultimately to the client.
        raise HTTPException(status_code=500, detail=f"Failed to save Xero token data: {e}") from e


def refresh_xero_token(user_id: str):
    """Refresh Xero access token if expired"""
    token_data = get_token_data(user_id)
    
    if not token_data or "refresh_token" not in token_data:
        raise HTTPException(status_code=401, detail="No Xero authorization found. Please connect to Xero.")
    
    # Check if token is expired or about to expire (within 5 minutes)
    if ("expires_at" in token_data and 
        datetime.fromtimestamp(token_data["expires_at"]) > datetime.now() + timedelta(minutes=5)):
        return token_data
    
    config = get_xero_client_config()
    
    try:
        response = requests.post(
            "https://identity.xero.com/connect/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": token_data["refresh_token"],
                "client_id": config["client_id"],
                "client_secret": config["client_secret"]
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        response.raise_for_status()
        new_token_data = response.json()
        
        # Update with new tokens and expiry
        token_data.update({
            "access_token": new_token_data["access_token"],
            "refresh_token": new_token_data["refresh_token"],
            "expires_in": new_token_data["expires_in"],
            "expires_at": datetime.now().timestamp() + new_token_data["expires_in"]
        })
        
        save_token_data(user_id, token_data)
        return token_data
        
    except Exception as e:
        print(f"Error refreshing Xero token: {e}")
        raise HTTPException(status_code=401, detail="Failed to refresh Xero authentication") from e


def get_xero_headers(user_id: str):
    """Get authenticated headers for Xero API requests"""
    token_data = refresh_xero_token(user_id)
    return {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def get_tenants(user_id: str):
    """Get Xero organizations (tenants) for the user"""
    try:
        headers = get_xero_headers(user_id)
        response = requests.get(
            "https://api.xero.com/connections",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting Xero tenants: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Xero organizations") from e


def get_selected_tenant_id(user_id: str):
    """Get the selected Xero tenant ID for the user"""
    token_data = get_token_data(user_id)
    
    if "selected_tenant_id" not in token_data:
        # If no tenant is selected, try to get the first available tenant
        tenants = get_tenants(user_id)
        if tenants and len(tenants) > 0:
            token_data["selected_tenant_id"] = tenants[0]["tenantId"]
            save_token_data(user_id, token_data)
        else:
            raise HTTPException(status_code=400, detail="No Xero organization available")
    
    return token_data["selected_tenant_id"]


# API Endpoints
@router.post("/connect")
async def connect_to_xero(request: XeroConnectionRequest, user: AuthorizedUser):
    """Generate an authorization URL for connecting to Xero"""
    config = get_xero_client_config()
    
    scopes = "offline_access openid profile email accounting.transactions accounting.settings"
    auth_url = (
        f"https://login.xero.com/identity/connect/authorize"
        f"?response_type=code"
        f"&client_id={config['client_id']}"
        f"&redirect_uri={request.redirect_uri}"
        f"&scope={scopes}"
        f"&state={user.sub}"
    )
    
    return XeroConnectionResponse(authorization_url=auth_url)


@router.post("/token")
async def exchange_code_for_token(code: str, redirect_uri: str, user: AuthorizedUser):
    """Exchange authorization code for access token"""
    config = get_xero_client_config()
    
    try:
        response = requests.post(
            "https://identity.xero.com/connect/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": config["client_id"],
                "client_secret": config["client_secret"]
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        # Store tokens with expiry time
        save_token_data(user.sub, {
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "expires_in": token_data["expires_in"],
            "expires_at": datetime.now().timestamp() + token_data["expires_in"],
            "id_token": token_data.get("id_token")
        })
        
        # Return token response with cleaned data
        return XeroTokenResponse(
            access_token=token_data["access_token"],
            expires_in=token_data["expires_in"],
            id_token=token_data.get("id_token"),
            refresh_token=token_data["refresh_token"]
        )
        
    except Exception as e:
        print(f"Error exchanging code for token: {e}")
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code") from e


@router.get("/organizations")
async def get_organizations(user: AuthorizedUser):
    """Get list of Xero organizations the user has access to"""
    try:
        tenants = get_tenants(user.sub)
        organizations = []
        
        for tenant in tenants:
            organizations.append(XeroOrganization(
                id=tenant["tenantId"],
                name=tenant["tenantName"],
                tenant_type=tenant["tenantType"]
            ))
        
        return XeroOrganizationsResponse(organizations=organizations)
    except Exception as e:
        print(f"Error getting organizations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Xero organizations") from e


@router.post("/select-organization/{tenant_id}")
async def select_organization(tenant_id: str, user: AuthorizedUser):
    """Select a Xero organization to work with"""
    try:
        # Verify tenant exists
        tenants = get_tenants(user.sub)
        tenant_exists = any(tenant["tenantId"] == tenant_id for tenant in tenants)
        
        if not tenant_exists:
            raise HTTPException(status_code=400, detail="Invalid organization ID")
        
        # Store the selected tenant
        token_data = get_token_data(user.sub)
        token_data["selected_tenant_id"] = tenant_id
        save_token_data(user.sub, token_data)
        
        return {"success": True, "message": "Organization selected successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error selecting organization: {e}")
        raise HTTPException(status_code=500, detail="Failed to select organization") from e


@router.get("/accounts")
async def get_accounts(user: AuthorizedUser):
    """Get chart of accounts from Xero"""
    try:
        headers = get_xero_headers(user.sub)
        tenant_id = get_selected_tenant_id(user.sub)
        
        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Accounts",
            headers={**headers, "Xero-Tenant-Id": tenant_id}
        )
        response.raise_for_status()
        
        data = response.json()
        accounts = []
        
        for account in data.get("Accounts", []):
            accounts.append(XeroAccount(
                account_id=account["AccountID"],
                code=account["Code"],
                name=account["Name"],
                type=account["Type"],
                tax_type=account.get("TaxType"),
                description=account.get("Description"),
                updated_date_utc=account.get("UpdatedDateUTC")
            ))
        
        return {"accounts": accounts}
    except Exception as e:
        print(f"Error getting accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve accounts") from e


@router.get("/transactions")
async def get_transactions(
    user: AuthorizedUser,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 100 # Default to 100, a common Xero API page size
):
    """Get bank transactions from Xero"""
    try:
        headers = get_xero_headers(user.sub)
        tenant_id = get_selected_tenant_id(user.sub)
        
        # Build query parameters
        params = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size # Pass pageSize to Xero API
        
        response = requests.get(
            "https://api.xero.com/api.xro/2.0/BankTransactions",
            headers={**headers, "Xero-Tenant-Id": tenant_id},
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        transactions = []
        
        for tx in data.get("BankTransactions", []):
            transactions.append(XeroTransaction(
                transaction_id=tx["BankTransactionID"],
                type=tx["Type"],
                contact_name=tx.get("Contact", {}).get("Name"),
                date=tx["Date"],
                status=tx["Status"],
                line_amount_types=tx.get("LineAmountTypes"),
                sub_total=float(tx["SubTotal"]),
                total_tax=float(tx["TotalTax"]),
                total=float(tx["Total"]),
                updated_date_utc=tx["UpdatedDateUTC"],
                currency_code=tx["CurrencyCode"],
                reference=tx.get("Reference"),
                description=tx.get("BankAccount", {}).get("Name")
            ))
        
        return XeroTransactionsResponse(transactions=transactions)
    except Exception as e:
        print(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transactions") from e


@router.get("/invoices")
async def get_invoices(
    user: AuthorizedUser,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 100, # Add pageSize parameter, default to 100
    status: Optional[str] = None
):
    """Get invoices from Xero"""
    try:
        headers = get_xero_headers(user.sub)
        tenant_id = get_selected_tenant_id(user.sub)
        
        # Build query parameters
        params = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size # Pass pageSize to Xero API
        if status:
            params["Status"] = status
        
        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Invoices",
            headers={**headers, "Xero-Tenant-Id": tenant_id},
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        invoices = []
        
        for invoice in data.get("Invoices", []):
            invoices.append(XeroInvoice(
                invoice_id=invoice["InvoiceID"],
                type=invoice["Type"],
                contact_name=invoice["Contact"]["Name"],
                date=invoice["Date"],
                due_date=invoice["DueDate"],
                status=invoice["Status"],
                sub_total=float(invoice["SubTotal"]),
                total_tax=float(invoice["TotalTax"]),
                total=float(invoice["Total"]),
                currency_code=invoice["CurrencyCode"],
                invoice_number=invoice.get("InvoiceNumber"),
                reference=invoice.get("Reference"),
                line_items=[{
                    "description": item.get("Description"),
                    "quantity": float(item.get("Quantity", 0)),
                    "unit_amount": float(item.get("UnitAmount", 0)),
                    "line_amount": float(item.get("LineAmount", 0)),
                } for item in invoice.get("LineItems", [])]
            ))
        
        return XeroInvoicesResponse(invoices=invoices)
    except Exception as e:
        print(f"Error getting invoices: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve invoices") from e


@router.get("/sync-status")
async def get_sync_status(user: AuthorizedUser):
    """Get the current synchronization status with Xero"""
    try:
        # Get the storage key for this user's sync info
        storage_key = f"xero_sync_status_{user.sub}"
        sync_data = db.storage.json.get(storage_key, {
            "last_sync": None,
            "sync_status": "not_synced",
            "item_counts": {
                "accounts": 0,
                "transactions": 0,
                "invoices": 0
            }
        })
        
        return XeroSyncStatusResponse(**sync_data)
    except Exception as e:
        print(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sync status") from e


@router.post("/sync")
async def sync_xero_data(user: AuthorizedUser):
    """Synchronize data from Xero to local storage"""
    try:
        # Get the storage keys
        storage_key_sync = f"xero_sync_status_{user.sub}"
        storage_key_accounts = f"xero_accounts_{user.sub}"
        storage_key_transactions = f"xero_transactions_{user.sub}"
        storage_key_invoices = f"xero_invoices_{user.sub}"
        
        # Update sync status to in-progress
        db.storage.json.put(storage_key_sync, {
            "last_sync": datetime.now().isoformat(),
            "sync_status": "in_progress",
            "item_counts": {
                "accounts": 0,
                "transactions": 0,
                "invoices": 0
            }
        })
        
        # Fetch data from Xero
        headers = get_xero_headers(user.sub)
        tenant_id = get_selected_tenant_id(user.sub)
        
        # Sync accounts
        accounts_response = requests.get(
            "https://api.xero.com/api.xro/2.0/Accounts",
            headers={**headers, "Xero-Tenant-Id": tenant_id}
        )
        accounts_response.raise_for_status()
        accounts_data = accounts_response.json()
        accounts = accounts_data.get("Accounts", [])
        db.storage.json.put(storage_key_accounts, accounts)
        
        # Sync transactions (last 90 days)
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        transactions_response = requests.get(
            "https://api.xero.com/api.xro/2.0/BankTransactions",
            headers={**headers, "Xero-Tenant-Id": tenant_id},
            params={"fromDate": from_date}
        )
        transactions_response.raise_for_status()
        transactions_data = transactions_response.json()
        transactions = transactions_data.get("BankTransactions", [])
        db.storage.json.put(storage_key_transactions, transactions)
        
        # Sync invoices (last 90 days)
        invoices_response = requests.get(
            "https://api.xero.com/api.xro/2.0/Invoices",
            headers={**headers, "Xero-Tenant-Id": tenant_id},
            params={"fromDate": from_date}
        )
        invoices_response.raise_for_status()
        invoices_data = invoices_response.json()
        invoices = invoices_data.get("Invoices", [])
        db.storage.json.put(storage_key_invoices, invoices)
        
        # Update sync status to completed
        db.storage.json.put(storage_key_sync, {
            "last_sync": datetime.now().isoformat(),
            "sync_status": "completed",
            "item_counts": {
                "accounts": len(accounts),
                "transactions": len(transactions),
                "invoices": len(invoices)
            }
        })
        
        return {
            "success": True,
            "message": "Synchronization completed successfully",
            "items_synced": {
                "accounts": len(accounts),
                "transactions": len(transactions),
                "invoices": len(invoices)
            }
        }
    except Exception as e:
        # Update sync status to failed
        db.storage.json.put(storage_key_sync, {
            "last_sync": datetime.now().isoformat(),
            "sync_status": "failed",
            "error": str(e),
            "item_counts": {
                "accounts": 0,
                "transactions": 0,
                "invoices": 0
            }
        })
        print(f"Error syncing Xero data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to synchronize Xero data: {e}") from e


@router.get("/financial-health")
async def get_financial_health(user: AuthorizedUser):
    """Get financial health metrics based on Xero data"""
    try:
        # Get stored transaction data
        storage_key_transactions = f"xero_transactions_{user.sub}"
        storage_key_invoices = f"xero_invoices_{user.sub}"
        
        try:
            transactions = db.storage.json.get(storage_key_transactions, [])
            invoices = db.storage.json.get(storage_key_invoices, [])
        except Exception as e:
            print(f"Error retrieving stored data: {e}")
            # If we can't get stored data, try to get it directly from Xero
            await sync_xero_data(user)
            transactions = db.storage.json.get(storage_key_transactions, [])
            invoices = db.storage.json.get(storage_key_invoices, [])
        
        # Calculate financial health metrics
        # Cash position - NOTE: This is a simplistic calculation based on summing RECEIVE transactions.
        # A true cash position would typically come from actual bank account balances,
        # which are not directly fetched by the current /accounts or /transactions endpoints.
        # Xero's BankTransaction Total is signed, so summing all 'Total' might give net cash flow,
        # but not necessarily the balance. For now, retaining the original simplified logic.
        cash_position = sum([float(tx.get("Total", 0)) for tx in transactions 
                             if tx.get("Type") == "RECEIVE"])
        
        # Accounts receivable - sum of outstanding invoices
        accounts_receivable = sum([float(inv.get("Total", 0)) for inv in invoices 
                                  if inv.get("Status") in ["AUTHORISED", "SUBMITTED"]])
        
        # Accounts payable - sum of bills to pay
        accounts_payable = sum([float(inv.get("Total", 0)) for inv in invoices 
                               if inv.get("Type") == "ACCPAY" and inv.get("Status") != "PAID"])
        
        # Recent revenue and expenses (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        revenue_30_days = sum([float(tx.get("Total", 0)) for tx in transactions 
                               if tx.get("Type") == "RECEIVE" and tx.get("Date", "") >= thirty_days_ago])
        
        expenses_30_days = sum([float(tx.get("Total", 0)) for tx in transactions 
                                if tx.get("Type") == "SPEND" and tx.get("Date", "") >= thirty_days_ago])
        
        # Net position
        net_position = cash_position + accounts_receivable - accounts_payable
        
        return XeroFinancialHealthResponse(
            cash_position=cash_position,
            accounts_receivable=accounts_receivable,
            accounts_payable=accounts_payable,
            revenue_30_days=revenue_30_days,
            expenses_30_days=expenses_30_days,
            net_position=net_position
        )
    except Exception as e:
        print(f"Error calculating financial health: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate financial health metrics") from e


@router.get("/anomaly-detection")
async def detect_anomalies(user: AuthorizedUser):
    """Detect anomalies in financial data using AI"""
    try:
        # Get stored transaction data
        storage_key_transactions = f"xero_transactions_{user.sub}"
        
        try:
            transactions = db.storage.json.get(storage_key_transactions, [])
        except Exception:
            # If we can't get stored data, try to get it directly from Xero
            await sync_xero_data(user)
            transactions = db.storage.json.get(storage_key_transactions, [])
        
        if not transactions:
            return XeroAnomalyDetectionResponse(
                anomalies=[], 
                analysis_date=datetime.now().isoformat()
            )
        
        # Simple anomaly detection logic - find outliers in transaction amounts
        # In a real implementation, this would use more sophisticated AI algorithms
        
        # Calculate average and standard deviation of transaction amounts
        amounts = [float(tx.get("Total", 0)) for tx in transactions]
        if not amounts:
            return XeroAnomalyDetectionResponse(
                anomalies=[], 
                analysis_date=datetime.now().isoformat()
            )
            
        avg_amount = sum(amounts) / len(amounts)
        std_dev = (sum([(amt - avg_amount) ** 2 for amt in amounts]) / len(amounts)) ** 0.5
        
        # Identify transactions with amounts more than 2 standard deviations from the mean
        anomalies = []
        for tx in transactions:
            amount = float(tx.get("Total", 0))
            z_score = (amount - avg_amount) / std_dev if std_dev > 0 else 0
            
            if abs(z_score) > 2:
                anomalies.append({
                    "transaction_id": tx.get("BankTransactionID"),
                    "date": tx.get("Date"),
                    "type": tx.get("Type"),
                    "contact": tx.get("Contact", {}).get("Name"),
                    "amount": amount,
                    "z_score": z_score,
                    "reason": "Unusual transaction amount"
                })
        
        # Sort anomalies by absolute z-score (most unusual first)
        anomalies.sort(key=lambda x: abs(x["z_score"]), reverse=True)
        
        return XeroAnomalyDetectionResponse(
            anomalies=anomalies, 
            analysis_date=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect anomalies") from e


@router.post("/categorize-transaction")
async def categorize_transaction(request: XeroCategorizeTransactionRequest, user: AuthorizedUser):
    """Use AI to categorize a transaction"""
    try:
        # In a real implementation, this would use AI to categorize the transaction
        # based on its description, amount, and other factors
        
        # Simple rule-based categorization for demonstration
        description_lower = request.description.lower()
        amount = request.amount
        
        categories = {
            "office_supplies": 0.0,
            "travel": 0.0,
            "meals_entertainment": 0.0,
            "rent": 0.0,
            "utilities": 0.0,
            "professional_services": 0.0,
            "payroll": 0.0,
            "advertising": 0.0,
            "insurance": 0.0,
            "taxes": 0.0,
            "other": 0.0
        }
        
        # Keyword-based matching with confidence scores
        if "office" in description_lower or "supplies" in description_lower or "paper" in description_lower:
            categories["office_supplies"] = 0.8
            categories["other"] = 0.2
        elif "travel" in description_lower or "flight" in description_lower or "hotel" in description_lower:
            categories["travel"] = 0.9
            categories["meals_entertainment"] = 0.1
        elif "meal" in description_lower or "restaurant" in description_lower or "cafe" in description_lower:
            categories["meals_entertainment"] = 0.85
            categories["travel"] = 0.15
        elif "rent" in description_lower or "lease" in description_lower:
            categories["rent"] = 0.95
            categories["other"] = 0.05
        elif "utility" in description_lower or "electric" in description_lower or "water" in description_lower or "gas" in description_lower:
            categories["utilities"] = 0.9
            categories["other"] = 0.1
        elif "lawyer" in description_lower or "accountant" in description_lower or "consult" in description_lower:
            categories["professional_services"] = 0.85
            categories["other"] = 0.15
        elif "salary" in description_lower or "payroll" in description_lower or "wage" in description_lower:
            categories["payroll"] = 0.9
            categories["other"] = 0.1
        elif "ad" in description_lower or "advertising" in description_lower or "marketing" in description_lower:
            categories["advertising"] = 0.8
            categories["professional_services"] = 0.2
        elif "insurance" in description_lower or "coverage" in description_lower:
            categories["insurance"] = 0.9
            categories["other"] = 0.1
        elif "tax" in description_lower or "irs" in description_lower:
            categories["taxes"] = 0.95
            categories["other"] = 0.05
        else:
            categories["other"] = 1.0
        
        # Amount-based heuristics
        if amount > 5000 and categories["rent"] < 0.5:
            categories["rent"] = max(categories["rent"], 0.3)
        elif amount > 2000 and categories["payroll"] < 0.5:
            categories["payroll"] = max(categories["payroll"], 0.3)
        
        # Find top category and alternatives
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        top_category = sorted_categories[0][0]
        confidence = sorted_categories[0][1]
        
        alternatives = [{
            "category": cat_name,
            "confidence": cat_confidence
        } for cat_name, cat_confidence in sorted_categories[1:4] if cat_confidence > 0]
        
        return XeroCategorizeTransactionsResponse(
            categorizations=[
                XeroTransactionCategorization(
                    transaction_id=request.transaction_id,
                    suggested_category=top_category,
                    confidence=confidence,
                    alternative_categories=alternatives
                )
            ]
        )
    except Exception as e:
        print(f"Error categorizing transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to categorize transaction") from e
