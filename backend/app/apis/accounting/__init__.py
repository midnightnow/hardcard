from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
import databutton as db
from enum import Enum
import re
import json
from datetime import datetime, date
from app.auth import AuthorizedUser

router = APIRouter(prefix="/accounting")

# Define models
class AccountingProvider(str, Enum):
    XERO = "xero"
    QUICKBOOKS = "quickbooks"
    
class AccountingConfig(BaseModel):
    provider: AccountingProvider
    client_id: str
    client_secret: str
    redirect_uri: str
    is_connected: bool = False
    last_sync: Optional[datetime] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

class AccountStatus(BaseModel):
    is_connected: bool
    provider: Optional[AccountingProvider] = None
    last_sync: Optional[datetime] = None
    
class AccountingAccount(BaseModel):
    id: str
    name: str
    code: str
    type: str
    tax_type: Optional[str] = None
    is_active: bool = True

class TaxRate(BaseModel):
    id: str
    name: str
    rate: float
    is_compound: bool = False
    is_active: bool = True

class ExpenseCategory(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    account_id: str
    tax_rate_id: Optional[str] = None
    is_active: bool = True

class FinancialTransaction(BaseModel):
    id: str
    date: date
    description: str
    amount: float
    type: Literal["sale", "purchase", "adjustment"]
    category_id: Optional[str] = None
    account_id: str
    reference: Optional[str] = None
    tax_amount: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    synced: bool = False

class FinancialPeriod(BaseModel):
    start_date: date
    end_date: date
    description: Optional[str] = None

class FinancialMetric(BaseModel):
    name: str
    value: float
    previous_value: Optional[float] = None
    change_percentage: Optional[float] = None
    trend: Optional[Literal["up", "down", "stable"]] = None

class ProfitLossReport(BaseModel):
    period: FinancialPeriod
    revenue: List[Dict[str, Any]]
    expenses: List[Dict[str, Any]]
    gross_profit: float
    net_profit: float
    margin: float
    metrics: List[FinancialMetric]

class BalanceSheetReport(BaseModel):
    as_of_date: date
    assets: List[Dict[str, Any]]
    liabilities: List[Dict[str, Any]]
    equity: List[Dict[str, Any]]
    total_assets: float
    total_liabilities: float
    total_equity: float

class CashFlowReport(BaseModel):
    period: FinancialPeriod
    operating_activities: List[Dict[str, Any]]
    investing_activities: List[Dict[str, Any]]
    financing_activities: List[Dict[str, Any]]
    net_cash_flow: float
    starting_balance: float
    ending_balance: float

class ProductCategoryMarginReport(BaseModel):
    category: str
    revenue: float
    cost_of_goods: float
    gross_profit: float
    margin_percentage: float
    sales_count: int
    average_order_value: float

class MarginAnalysisReport(BaseModel):
    period: FinancialPeriod
    overall_margin: float
    categories: List[ProductCategoryMarginReport]
    
class TaxReportItem(BaseModel):
    tax_rate: str
    total_sales: float
    tax_collected: float
    total_purchases: float
    tax_paid: float
    net_tax: float

class TaxReport(BaseModel):
    period: FinancialPeriod
    tax_items: List[TaxReportItem]
    total_tax_collected: float
    total_tax_paid: float
    net_tax_liability: float

class SyncRequest(BaseModel):
    force_full_sync: bool = False

class SyncResult(BaseModel):
    success: bool
    transactions_synced: int
    accounts_updated: int
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)

class ConfigUpdateRequest(BaseModel):
    provider: Optional[AccountingProvider] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_accounting_config() -> Optional[AccountingConfig]:
    """Get the current accounting configuration from storage"""
    try:
        config_data = db.storage.json.get("accounting_config")
        return AccountingConfig(**config_data)
    except:
        return None

def save_accounting_config(config: AccountingConfig):
    """Save the accounting configuration to storage"""
    db.storage.json.put("accounting_config", config.dict())
    
def get_transactions(filters: Dict[str, Any] = None) -> List[FinancialTransaction]:
    """Get transactions from storage with optional filtering"""
    try:
        all_transactions = db.storage.json.get("accounting_transactions", default=[])
        
        if not filters:
            return [FinancialTransaction(**t) for t in all_transactions]
            
        filtered_transactions = []
        for t in all_transactions:
            match = True
            for key, value in filters.items():
                if key not in t or t[key] != value:
                    match = False
                    break
            if match:
                filtered_transactions.append(FinancialTransaction(**t))
                
        return filtered_transactions
    except:
        return []

def save_transaction(transaction: FinancialTransaction):
    """Save a transaction to storage"""
    transactions = get_transactions()
    
    # Update existing or add new
    found = False
    for i, t in enumerate(transactions):
        if t.id == transaction.id:
            transactions[i] = transaction
            found = True
            break
            
    if not found:
        transactions.append(transaction)
    
    # Save back to storage
    db.storage.json.put("accounting_transactions", [t.dict() for t in transactions])
    return transaction

# Implement mock data for testing
def generate_mock_accounts() -> List[AccountingAccount]:
    """Generate mock accounting accounts for testing"""
    return [
        AccountingAccount(id="acc-1", name="Sales Revenue", code="4000", type="revenue"),
        AccountingAccount(id="acc-2", name="Cost of Goods Sold", code="5000", type="expense"),
        AccountingAccount(id="acc-3", name="Office Expenses", code="6000", type="expense"),
        AccountingAccount(id="acc-4", name="Marketing Expenses", code="6100", type="expense"),
        AccountingAccount(id="acc-5", name="Bank Account", code="1000", type="asset"),
        AccountingAccount(id="acc-6", name="Accounts Receivable", code="1100", type="asset"),
        AccountingAccount(id="acc-7", name="Inventory", code="1200", type="asset"),
        AccountingAccount(id="acc-8", name="Accounts Payable", code="2000", type="liability"),
        AccountingAccount(id="acc-9", name="Sales Tax Payable", code="2100", type="liability"),
    ]

def generate_mock_tax_rates() -> List[TaxRate]:
    """Generate mock tax rates for testing"""
    return [
        TaxRate(id="tax-1", name="GST (10%)", rate=0.10),
        TaxRate(id="tax-2", name="No Tax", rate=0.0),
    ]

def generate_mock_categories() -> List[ExpenseCategory]:
    """Generate mock expense categories for testing"""
    return [
        ExpenseCategory(id="cat-1", name="CBD Products", account_id="acc-2", tax_rate_id="tax-1"),
        ExpenseCategory(id="cat-2", name="Hemp Flower", account_id="acc-2", tax_rate_id="tax-1"),
        ExpenseCategory(id="cat-3", name="Office Supplies", account_id="acc-3", tax_rate_id="tax-1"),
        ExpenseCategory(id="cat-4", name="Online Advertising", account_id="acc-4", tax_rate_id="tax-1"),
        ExpenseCategory(id="cat-5", name="Packaging", account_id="acc-2", tax_rate_id="tax-1"),
    ]

def generate_mock_pl_report(period: FinancialPeriod) -> ProfitLossReport:
    """Generate a mock profit & loss report for testing"""
    revenue_items = [
        {"account": "CBD Product Sales", "amount": 42500.00},
        {"account": "Hemp Flower Sales", "amount": 28750.00},
        {"account": "Accessories", "amount": 7850.00},
    ]
    
    expense_items = [
        {"account": "Cost of Goods Sold", "amount": 31200.00},
        {"account": "Shipping Expenses", "amount": 4850.00},
        {"account": "Marketing", "amount": 7500.00},
        {"account": "Website & Tech", "amount": 2200.00},
        {"account": "Office Expenses", "amount": 1800.00},
    ]
    
    total_revenue = sum(item["amount"] for item in revenue_items)
    total_expenses = sum(item["amount"] for item in expense_items)
    gross_profit = total_revenue
    net_profit = total_revenue - total_expenses
    margin = net_profit / total_revenue if total_revenue > 0 else 0
    
    metrics = [
        FinancialMetric(
            name="Total Revenue", 
            value=total_revenue,
            previous_value=73500.0,
            change_percentage=7.55,
            trend="up"
        ),
        FinancialMetric(
            name="Gross Profit", 
            value=gross_profit,
            previous_value=73500.0,
            change_percentage=7.55,
            trend="up"
        ),
        FinancialMetric(
            name="Net Profit", 
            value=net_profit,
            previous_value=25250.0,
            change_percentage=4.75,
            trend="up"
        ),
        FinancialMetric(
            name="Profit Margin", 
            value=margin * 100,
            previous_value=34.35,
            change_percentage=-1.44,
            trend="down"
        ),
    ]
    
    return ProfitLossReport(
        period=period,
        revenue=revenue_items,
        expenses=expense_items,
        gross_profit=gross_profit,
        net_profit=net_profit,
        margin=margin,
        metrics=metrics
    )

def generate_mock_balance_sheet(as_of_date: date) -> BalanceSheetReport:
    """Generate a mock balance sheet for testing"""
    asset_items = [
        {"account": "Bank Accounts", "amount": 84250.00},
        {"account": "Accounts Receivable", "amount": 12500.00},
        {"account": "Inventory", "amount": 65750.00},
        {"account": "Prepaid Expenses", "amount": 3500.00},
    ]
    
    liability_items = [
        {"account": "Accounts Payable", "amount": 23750.00},
        {"account": "Sales Tax Payable", "amount": 7850.00},
        {"account": "Credit Card", "amount": 4200.00},
    ]
    
    equity_items = [
        {"account": "Owner's Capital", "amount": 100000.00},
        {"account": "Retained Earnings", "amount": 30200.00},
    ]
    
    total_assets = sum(item["amount"] for item in asset_items)
    total_liabilities = sum(item["amount"] for item in liability_items)
    total_equity = sum(item["amount"] for item in equity_items)
    
    return BalanceSheetReport(
        as_of_date=as_of_date,
        assets=asset_items,
        liabilities=liability_items,
        equity=equity_items,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        total_equity=total_equity
    )

def generate_mock_cash_flow(period: FinancialPeriod) -> CashFlowReport:
    """Generate a mock cash flow report for testing"""
    operating_items = [
        {"activity": "Sales Receipts", "amount": 76500.00},
        {"activity": "Supplier Payments", "amount": -42750.00},
        {"activity": "Operating Expenses", "amount": -13850.00},
        {"activity": "Tax Payments", "amount": -7550.00},
    ]
    
    investing_items = [
        {"activity": "Equipment Purchase", "amount": -5000.00},
    ]
    
    financing_items = [
        {"activity": "Owner's Draw", "amount": -10000.00},
    ]
    
    operating_cash = sum(item["amount"] for item in operating_items)
    investing_cash = sum(item["amount"] for item in investing_items)
    financing_cash = sum(item["amount"] for item in financing_items)
    net_cash_flow = operating_cash + investing_cash + financing_cash
    
    starting_balance = 87900.00
    ending_balance = starting_balance + net_cash_flow
    
    return CashFlowReport(
        period=period,
        operating_activities=operating_items,
        investing_activities=investing_items,
        financing_activities=financing_items,
        net_cash_flow=net_cash_flow,
        starting_balance=starting_balance,
        ending_balance=ending_balance
    )

def generate_mock_margin_analysis(period: FinancialPeriod) -> MarginAnalysisReport:
    """Generate a mock margin analysis report for testing"""
    categories = [
        ProductCategoryMarginReport(
            category="CBD Oils",
            revenue=32500.00,
            cost_of_goods=16250.00,
            gross_profit=16250.00,
            margin_percentage=50.0,
            sales_count=325,
            average_order_value=100.00
        ),
        ProductCategoryMarginReport(
            category="CBD Topicals",
            revenue=10000.00,
            cost_of_goods=3750.00,
            gross_profit=6250.00,
            margin_percentage=62.5,
            sales_count=125,
            average_order_value=80.00
        ),
        ProductCategoryMarginReport(
            category="Hemp Flower",
            revenue=28750.00,
            cost_of_goods=9675.00,
            gross_profit=19075.00,
            margin_percentage=66.35,
            sales_count=575,
            average_order_value=50.00
        ),
        ProductCategoryMarginReport(
            category="Accessories",
            revenue=7850.00,
            cost_of_goods=3532.50,
            gross_profit=4317.50,
            margin_percentage=55.0,
            sales_count=157,
            average_order_value=50.00
        ),
    ]
    
    total_revenue = sum(cat.revenue for cat in categories)
    total_profit = sum(cat.gross_profit for cat in categories)
    overall_margin = total_profit / total_revenue if total_revenue > 0 else 0
    
    return MarginAnalysisReport(
        period=period,
        overall_margin=overall_margin,
        categories=categories
    )

def generate_mock_tax_report(period: FinancialPeriod) -> TaxReport:
    """Generate a mock tax report for testing"""
    tax_items = [
        TaxReportItem(
            tax_rate="GST (10%)",
            total_sales=79100.00,
            tax_collected=7910.00,
            total_purchases=47550.00,
            tax_paid=4755.00,
            net_tax=3155.00
        ),
    ]
    
    total_collected = sum(item.tax_collected for item in tax_items)
    total_paid = sum(item.tax_paid for item in tax_items)
    net_liability = total_collected - total_paid
    
    return TaxReport(
        period=period,
        tax_items=tax_items,
        total_tax_collected=total_collected,
        total_tax_paid=total_paid,
        net_tax_liability=net_liability
    )

# Endpoints
@router.get("/health")
def check_health2():
    """Check if the accounting API is working"""
    return {"status": "ok", "message": "Accounting API is operational"}

@router.get("/status", response_model=AccountStatus)
def get_status():
    """Get the current status of the accounting integration"""
    config = get_accounting_config()
    if not config:
        return AccountStatus(is_connected=False)
    
    return AccountStatus(
        is_connected=config.is_connected,
        provider=config.provider,
        last_sync=config.last_sync
    )

@router.post("/config", response_model=AccountingConfig)
def update_config2(config_update: ConfigUpdateRequest):
    """Update the accounting integration configuration"""
    current_config = get_accounting_config()
    
    if not current_config:
        # Creating new config requires all fields
        if not all([config_update.provider, config_update.client_id, config_update.client_secret, config_update.redirect_uri]):
            raise HTTPException(status_code=400, detail="Missing required fields for initial configuration")
            
        new_config = AccountingConfig(
            provider=config_update.provider,
            client_id=config_update.client_id,
            client_secret=config_update.client_secret,
            redirect_uri=config_update.redirect_uri,
            settings=config_update.settings or {}
        )
        save_accounting_config(new_config)
        return new_config
    
    # Update only provided fields
    updated = False
    if config_update.provider is not None:
        current_config.provider = config_update.provider
        updated = True
        
    if config_update.client_id is not None:
        current_config.client_id = config_update.client_id
        updated = True
        
    if config_update.client_secret is not None:
        current_config.client_secret = config_update.client_secret
        updated = True
        
    if config_update.redirect_uri is not None:
        current_config.redirect_uri = config_update.redirect_uri
        updated = True
        
    if config_update.settings is not None:
        current_config.settings = config_update.settings
        updated = True
        
    if updated:
        # When config changes, we should reset connection status
        current_config.is_connected = False
        save_accounting_config(current_config)
        
    return current_config

@router.get("/config", response_model=AccountingConfig)
def get_config2():
    """Get the current accounting configuration"""
    config = get_accounting_config()
    if not config:
        raise HTTPException(status_code=404, detail="Accounting not configured")
    return config

@router.post("/connect")
def connect_accounting():
    """Connect to the accounting provider API"""
    config = get_accounting_config()
    if not config:
        raise HTTPException(status_code=404, detail="Accounting not configured")
    
    # In a real implementation, this would authenticate with the provider
    # and store credentials for later use.
    # For demo purposes, we'll just mark it as connected.
    config.is_connected = True
    save_accounting_config(config)
    
    return {"status": "success", "message": "Connected to accounting provider"}

@router.post("/sync", response_model=SyncResult)
def sync_accounting(request: SyncRequest = Body(...)):
    """Sync transactions with the accounting provider"""
    config = get_accounting_config()
    if not config:
        raise HTTPException(status_code=404, detail="Accounting not configured")
        
    if not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    # In a real implementation, this would:
    # 1. Get new transactions from the e-commerce system
    # 2. Format them for the accounting system
    # 3. Push them to the accounting API
    # 4. Mark them as synced
    # 5. Update the last_sync timestamp
    
    # For demo purposes, we'll simulate a successful sync
    config.last_sync = datetime.now()
    save_accounting_config(config)
    
    return SyncResult(
        success=True,
        transactions_synced=27,
        accounts_updated=5,
        warnings=["Some tax rates needed adjustment to match accounting system"]
    )

@router.get("/accounts", response_model=List[AccountingAccount])
def get_accounts():
    """Get the chart of accounts from the accounting system"""
    config = get_accounting_config()
    if not config or not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    # For demo purposes, return mock accounts
    return generate_mock_accounts()

@router.get("/tax-rates", response_model=List[TaxRate])
def get_tax_rates():
    """Get the tax rates from the accounting system"""
    config = get_accounting_config()
    if not config or not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    # For demo purposes, return mock tax rates
    return generate_mock_tax_rates()

@router.get("/categories", response_model=List[ExpenseCategory])
def get_categories():
    """Get expense categories"""
    config = get_accounting_config()
    if not config or not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    # For demo purposes, return mock categories
    return generate_mock_categories()

@router.get("/transactions", response_model=List[FinancialTransaction])
def list_transactions(
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    synced: Optional[bool] = Query(None, description="Filter by sync status")
):
    """Get financial transactions with optional filtering"""
    config = get_accounting_config()
    if not config:
        raise HTTPException(status_code=404, detail="Accounting not configured")
    
    # Build filters
    filters = {}
    if transaction_type:
        filters["type"] = transaction_type
    if category_id:
        filters["category_id"] = category_id
    if synced is not None:
        filters["synced"] = synced
    
    return get_transactions(filters)

@router.post("/transactions", response_model=FinancialTransaction)
def create_transaction(transaction: FinancialTransaction):
    """Create a new financial transaction"""
    config = get_accounting_config()
    if not config:
        raise HTTPException(status_code=404, detail="Accounting not configured")
    
    # Save the transaction
    return save_transaction(transaction)

@router.get("/reports/profit-loss", response_model=ProfitLossReport)
def get_profit_loss_report(
    start_date: date = Query(..., description="Start date for the report period"),
    end_date: date = Query(..., description="End date for the report period")
):
    """Get a profit and loss report for a specified period"""
    config = get_accounting_config()
    if not config or not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    period = FinancialPeriod(start_date=start_date, end_date=end_date)
    return generate_mock_pl_report(period)

@router.get("/reports/balance-sheet", response_model=BalanceSheetReport)
def get_balance_sheet(as_of_date: date = Query(..., description="Date for the balance sheet")):
    """Get a balance sheet as of a specified date"""
    config = get_accounting_config()
    if not config or not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    return generate_mock_balance_sheet(as_of_date)

@router.get("/reports/cash-flow", response_model=CashFlowReport)
def get_cash_flow_report(
    start_date: date = Query(..., description="Start date for the report period"),
    end_date: date = Query(..., description="End date for the report period")
):
    """Get a cash flow report for a specified period"""
    config = get_accounting_config()
    if not config or not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    period = FinancialPeriod(start_date=start_date, end_date=end_date)
    return generate_mock_cash_flow(period)

@router.get("/reports/margin-analysis", response_model=MarginAnalysisReport)
def get_margin_analysis(
    start_date: date = Query(..., description="Start date for the report period"),
    end_date: date = Query(..., description="End date for the report period")
):
    """Get margin analysis by product category"""
    config = get_accounting_config()
    if not config or not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    period = FinancialPeriod(start_date=start_date, end_date=end_date)
    return generate_mock_margin_analysis(period)

@router.get("/reports/tax", response_model=TaxReport)
def get_tax_report(
    start_date: date = Query(..., description="Start date for the report period"),
    end_date: date = Query(..., description="End date for the report period")
):
    """Get a tax report for a specified period"""
    config = get_accounting_config()
    if not config or not config.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to accounting provider")
    
    period = FinancialPeriod(start_date=start_date, end_date=end_date)
    return generate_mock_tax_report(period)
