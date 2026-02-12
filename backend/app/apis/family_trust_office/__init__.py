"""
Family Trust Office API

Provides endpoints for managing family trust finances, budgeting, and lifecycle coordination.
Implements a sovereign family office that manages payments, budgets, and life coordination
with robust governance, audit trails, and extensibility.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4
from pydantic import BaseModel, Field, validator, ValidationError
from fastapi import APIRouter, HTTPException, Query

import databutton as db

router = APIRouter(prefix="/family-trust-office")

# --- Models ---

class PaymentRecord(BaseModel):
    """Record of a payment made or scheduled"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    date: str
    amount: float
    category: str
    description: Optional[str] = None
    status: str = "scheduled"  # scheduled, completed, failed
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @validator('date')
    def date_format(cls, v):
        """Ensure date is in ISO format"""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('Date must be in ISO format')

class BudgetCategory(BaseModel):
    """Budget category with spending limit"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    limit: float
    description: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class LifeEvent(BaseModel):
    """Life event or appointment"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    date: str
    description: str
    category: str
    completed: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class SavingsGoal(BaseModel):
    """Long-term savings goal"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    target: float
    current_amount: float = 0
    target_date: Optional[str] = None
    description: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class AuditLogEntry(BaseModel):
    """Record of an action for governance and audit"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event: str
    details: Dict[str, Any] = {}
    profile_id: Optional[str] = None

class FamilyTrustSummary(BaseModel):
    """Summary of trust finances and activities"""
    profile_id: str
    total_savings: float
    payments: List[PaymentRecord]
    budgets: List[BudgetCategory]
    savings_goals: List[SavingsGoal]
    upcoming_events: List[LifeEvent]

# --- Request and Response Models ---

class SchedulePaymentRequest(BaseModel):
    """Request to schedule a payment"""
    profile_id: str
    amount: float
    category: str
    description: Optional[str] = None
    date: str

class SchedulePaymentResponse(BaseModel):
    """Response after scheduling a payment"""
    payment: PaymentRecord
    message: str = "Payment scheduled successfully"

class SetBudgetRequest(BaseModel):
    """Request to set a budget category"""
    profile_id: str
    name: str
    limit: float
    description: Optional[str] = None

class SetBudgetResponse(BaseModel):
    """Response after setting a budget"""
    budget: BudgetCategory
    message: str = "Budget set successfully"

class ScheduleEventRequest(BaseModel):
    """Request to schedule a life event"""
    profile_id: str
    date: str
    description: str
    category: str

class ScheduleEventResponse(BaseModel):
    """Response after scheduling an event"""
    event: LifeEvent
    message: str = "Event scheduled successfully"

class SetSavingsGoalRequest(BaseModel):
    """Request to set a savings goal"""
    profile_id: str
    name: str
    target: float
    target_date: Optional[str] = None
    description: Optional[str] = None

class SetSavingsGoalResponse(BaseModel):
    """Response after setting a savings goal"""
    goal: SavingsGoal
    message: str = "Savings goal set successfully"

class AddIncomeRequest(BaseModel):
    """Request to add income to savings"""
    profile_id: str
    amount: float
    description: Optional[str] = None

class AddIncomeResponse(BaseModel):
    """Response after adding income"""
    new_savings: float
    message: str = "Income added successfully"

class GetFinancialOverviewResponse(BaseModel):
    """Complete financial overview for a profile"""
    profile_id: str
    savings: float
    payments: List[PaymentRecord]
    budgets: List[BudgetCategory]
    savings_goals: List[SavingsGoal]
    upcoming_events: List[LifeEvent]

class ConciergeRecommendationResponse(BaseModel):
    """Response with personalized recommendations"""
    recommendations: List[str]
    financial_insights: List[str]
    suggested_actions: List[str]

# --- Helper Functions ---

def _get_storage_key(profile_id: str, collection: str) -> str:
    """Generate a sanitized storage key for a profile and collection"""
    # Sanitize to ensure only alphanumeric, dots, underscores and dashes
    sanitized_profile_id = ''.join(c for c in profile_id if c.isalnum() or c in '._-')
    return f"family_trust_office.{sanitized_profile_id}.{collection}"

def _log_event(profile_id: str, event: str, details: Dict[str, Any] = None, is_error: bool = False) -> None:
    """Log an event to the audit trail. If is_error is True, it indicates an error event."""
    event_name = f"ERROR: {event}" if is_error else event
    log_entry = AuditLogEntry(
        event=event_name,
        details=details or {},
        profile_id=profile_id
    )
    
    # Get existing log entries
    storage_key = _get_storage_key(profile_id, "audit_log")
    audit_log_list = [] # Initialize as empty list
    try:
        raw_audit_log = db.storage.json.get(storage_key, default=[])
        # Ensure raw_audit_log is a list before trying to append
        if isinstance(raw_audit_log, list):
            audit_log_list = raw_audit_log
        else:
            print(f"Warning: audit_log for profile {profile_id} from {storage_key} was not a list, re-initializing.")
    except FileNotFoundError:
        pass # audit_log_list remains []
    except ValidationError as ve:
        print(f"Pydantic ValidationError getting audit_log for profile {profile_id} from {storage_key}: {ve}. Will attempt to save new log to a fresh list.")
    except Exception as e:
        print(f"Unexpected error getting audit_log for profile {profile_id} from {storage_key}: {e}. Will attempt to save new log to a fresh list.")
    
    # Add new entry and save
    audit_log_list.append(log_entry.dict()) # Append to the list of dicts
    try:
        db.storage.json.put(storage_key, audit_log_list)
    except Exception as e:
        print(f"Error saving audit_log for profile {profile_id} to {storage_key}: {e}")

def _get_savings(profile_id: str) -> float:
    """Get current savings for a profile"""
    storage_key = _get_storage_key(profile_id, "savings")
    try:
        return db.storage.json.get(storage_key, default=0.0)
    except FileNotFoundError:
        # This is an expected case, e.g., new profile with no savings yet
        return 0.0
    except Exception as e:
        print(f"Error getting savings for profile {profile_id} from {storage_key}: {e}")
        # For other errors, we might want to raise them or handle differently
        # For now, maintaining original behavior of returning 0.0 but logging the error
        return 0.0

def _update_savings(profile_id: str, amount: float) -> tuple[float | None, bool]:
    """Update savings for a profile. Returns (new_amount, success_flag)."""
    current = _get_savings(profile_id)
    new_amount = max(current + amount, 0)  # Prevent negative savings
    storage_key = _get_storage_key(profile_id, "savings")
    try:
        db.storage.json.put(storage_key, new_amount)
        return new_amount, True
    except Exception as e:
        print(f"Error saving savings for profile {profile_id} to {storage_key}: {e}")
        return None, False

def _get_payments(profile_id: str) -> List[PaymentRecord]:
    """Get payments for a profile"""
    storage_key = _get_storage_key(profile_id, "payments")
    try:
        payments_data = db.storage.json.get(storage_key, default=[])
        if not payments_data: # Handle case where default=[] is returned by .get()
            return []
        return [PaymentRecord(**payment) for payment in payments_data]
    except FileNotFoundError:
        # Expected case: no payments file yet for this profile
        return []
    except ValidationError as ve:
        print(f"Pydantic ValidationError getting payments for profile {profile_id} from {storage_key}: {ve}")
        # Data corruption or model mismatch, return empty list to prevent crash
        return []
    except Exception as e:
        print(f"Unexpected error getting payments for profile {profile_id} from {storage_key}: {e}")
        # Fallback for other errors, log and return empty
        return []

def _get_budgets(profile_id: str) -> List[BudgetCategory]:
    """Get budgets for a profile"""
    storage_key = _get_storage_key(profile_id, "budgets")
    try:
        budgets_data = db.storage.json.get(storage_key, default=[])
        if not budgets_data:
            return []
        return [BudgetCategory(**budget) for budget in budgets_data]
    except FileNotFoundError:
        return []
    except ValidationError as ve:
        print(f"Pydantic ValidationError getting budgets for profile {profile_id} from {storage_key}: {ve}")
        return []
    except Exception as e:
        print(f"Unexpected error getting budgets for profile {profile_id} from {storage_key}: {e}")
        return []

def _get_events(profile_id: str) -> List[LifeEvent]:
    """Get life events for a profile"""
    storage_key = _get_storage_key(profile_id, "events")
    try:
        events_data = db.storage.json.get(storage_key, default=[])
        if not events_data:
            return []
        return [LifeEvent(**event) for event in events_data]
    except FileNotFoundError:
        return []
    except ValidationError as ve:
        print(f"Pydantic ValidationError getting events for profile {profile_id} from {storage_key}: {ve}")
        return []
    except Exception as e:
        print(f"Unexpected error getting events for profile {profile_id} from {storage_key}: {e}")
        return []

def _get_savings_goals(profile_id: str) -> List[SavingsGoal]:
    """Get savings goals for a profile"""
    storage_key = _get_storage_key(profile_id, "savings_goals")
    try:
        goals_data = db.storage.json.get(storage_key, default=[])
        if not goals_data:
            return []
        return [SavingsGoal(**goal) for goal in goals_data]
    except FileNotFoundError:
        return []
    except ValidationError as ve:
        print(f"Pydantic ValidationError getting savings_goals for profile {profile_id} from {storage_key}: {ve}")
        return []
    except Exception as e:
        print(f"Unexpected error getting savings_goals for profile {profile_id} from {storage_key}: {e}")
        return []

def _save_payments(profile_id: str, payments: List[PaymentRecord]) -> bool:
    """Save payments for a profile. Returns True on success, False on failure."""
    storage_key = _get_storage_key(profile_id, "payments")
    payments_data = [payment.dict() for payment in payments]
    try:
        db.storage.json.put(storage_key, payments_data)
        return True
    except Exception as e:
        print(f"Error saving payments for profile {profile_id} to {storage_key}: {e}")
        return False

def _save_budgets(profile_id: str, budgets: List[BudgetCategory]) -> bool:
    """Save budgets for a profile. Returns True on success, False on failure."""
    storage_key = _get_storage_key(profile_id, "budgets")
    budgets_data = [budget.dict() for budget in budgets]
    try:
        db.storage.json.put(storage_key, budgets_data)
        return True
    except Exception as e:
        print(f"Error saving budgets for profile {profile_id} to {storage_key}: {e}")
        return False

def _save_events(profile_id: str, events: List[LifeEvent]) -> bool:
    """Save life events for a profile. Returns True on success, False on failure."""
    storage_key = _get_storage_key(profile_id, "events")
    events_data = [event.dict() for event in events]
    try:
        db.storage.json.put(storage_key, events_data)
        return True
    except Exception as e:
        print(f"Error saving events for profile {profile_id} to {storage_key}: {e}")
        return False

def _save_savings_goals(profile_id: str, goals: List[SavingsGoal]) -> bool:
    """Save savings goals for a profile. Returns True on success, False on failure."""
    storage_key = _get_storage_key(profile_id, "savings_goals")
    goals_data = [goal.dict() for goal in goals]
    try:
        db.storage.json.put(storage_key, goals_data)
        return True
    except Exception as e:
        print(f"Error saving savings_goals for profile {profile_id} to {storage_key}: {e}")
        return False

# --- API Endpoints ---

@router.post("/schedule-payment", response_model=SchedulePaymentResponse)
def schedule_payment(request: SchedulePaymentRequest) -> SchedulePaymentResponse:
    """
    Schedule a payment for a specified date.
    Payments can be for investments, expenses, or savings allocations.
    """
    payment = PaymentRecord(
        date=request.date,
        amount=request.amount,
        category=request.category,
        description=request.description,
    )
    
    # Get existing payments
    payments = _get_payments(request.profile_id)
    
    # Add new payment and save
    payments.append(payment)
    if not _save_payments(request.profile_id, payments):
        _log_event(
            request.profile_id,
            "Payment Scheduling Failed",
            {"payment_id": payment.id, "error": "Failed to save payments data"}
        )
        raise HTTPException(status_code=500, detail="Failed to save payment data.")
    
    # Log the event
    _log_event(
        request.profile_id, 
        "Payment Scheduled", 
        {"payment_id": payment.id, "amount": payment.amount, "category": payment.category}
    )
    
    return SchedulePaymentResponse(payment=payment)

@router.post("/set-budget", response_model=SetBudgetResponse)
def set_budget(request: SetBudgetRequest) -> SetBudgetResponse:
    """
    Set a budget category with a spending limit.
    Helps maintain financial discipline across spending categories.
    """
    budget = BudgetCategory(
        name=request.name,
        limit=request.limit,
        description=request.description,
    )
    
    # Get existing budgets
    budgets = _get_budgets(request.profile_id)
    
    # Check if this category already exists, update if it does
    existing_index = next((i for i, b in enumerate(budgets) if b.name == request.name), None)
    if existing_index is not None:
        budgets[existing_index] = budget
    else:
        budgets.append(budget)
    
    # Save updated budgets
    if not _save_budgets(request.profile_id, budgets):
        _log_event(
            request.profile_id,
            "Budget Set Failed",
            {"budget_id": budget.id, "name": budget.name, "error": "Failed to save budgets data"}
        )
        raise HTTPException(status_code=500, detail="Failed to save budget data.")

    # Log the event
    _log_event(
        request.profile_id, 
        "Budget Set", 
        {"budget_id": budget.id, "name": budget.name, "limit": budget.limit}
    )
    
    return SetBudgetResponse(budget=budget)

@router.post("/schedule-event", response_model=ScheduleEventResponse)
def schedule_event(request: ScheduleEventRequest) -> ScheduleEventResponse:
    """
    Schedule a life event or appointment.
    Helps coordinate important events like meetings, appointments, or financial reviews.
    """
    event = LifeEvent(
        date=request.date,
        description=request.description,
        category=request.category,
    )
    
    # Get existing events
    events = _get_events(request.profile_id)
    
    # Add new event and save
    events.append(event)
    if not _save_events(request.profile_id, events):
        _log_event(
            request.profile_id,
            "Event Scheduling Failed",
            {"event_id": event.id, "description": event.description, "error": "Failed to save events data"}
        )
        raise HTTPException(status_code=500, detail="Failed to save event data.")
    
    # Log the event
    _log_event(
        request.profile_id, 
        "Event Scheduled", 
        {"event_id": event.id, "description": event.description, "date": event.date}
    )
    
    return ScheduleEventResponse(event=event)

@router.post("/set-savings-goal", response_model=SetSavingsGoalResponse)
def set_savings_goal(request: SetSavingsGoalRequest) -> SetSavingsGoalResponse:
    """
    Set a long-term savings goal.
    Establishes targets for various financial goals like education or house down payment.
    """
    goal = SavingsGoal(
        name=request.name,
        target=request.target,
        target_date=request.target_date,
        description=request.description,
    )
    
    # Get existing goals
    goals = _get_savings_goals(request.profile_id)
    
    # Check if this goal already exists, update if it does
    existing_index = next((i for i, g in enumerate(goals) if g.name == request.name), None)
    if existing_index is not None:
        # Preserve current amount if updating
        goal.current_amount = goals[existing_index].current_amount
        goals[existing_index] = goal
    else:
        goals.append(goal)
    
    # Save updated goals
    if not _save_savings_goals(request.profile_id, goals):
        _log_event(
            request.profile_id,
            "Savings Goal Set Failed",
            {"goal_id": goal.id, "name": goal.name, "error": "Failed to save savings goals data"}
        )
        raise HTTPException(status_code=500, detail="Failed to save savings goal data.")
    
    # Log the event
    _log_event(
        request.profile_id, 
        "Savings Goal Set", 
        {"goal_id": goal.id, "name": goal.name, "target": goal.target}
    )
    
    return SetSavingsGoalResponse(goal=goal)

@router.post("/add-income", response_model=AddIncomeResponse)
def add_income(request: AddIncomeRequest) -> AddIncomeResponse:
    """
    Add income to the trust savings.
    Records new income and updates total savings amount.
    """
    # Update savings
    new_savings, success = _update_savings(request.profile_id, request.amount)
    if not success:
        _log_event(
            request.profile_id,
            "Income Add Failed",
            {"amount": request.amount, "description": request.description, "error": "Failed to save savings data"},
            is_error=True
        )
        raise HTTPException(status_code=500, detail="Failed to update savings.")
    
    # Log the event
    _log_event(
        request.profile_id, 
        "Income Added", 
        {"amount": request.amount, "new_savings": new_savings, "description": request.description}
    )
    
    return AddIncomeResponse(new_savings=new_savings)

@router.get("/financial-overview", response_model=GetFinancialOverviewResponse)
def get_financial_overview(profile_id: str = Query(..., description="Profile ID to get overview for")) -> GetFinancialOverviewResponse:
    """
    Get a complete financial overview for a profile.
    Returns current savings, payments, budgets, goals and upcoming events.
    """
    # Get all financial data
    savings = _get_savings(profile_id)
    payments = _get_payments(profile_id)
    budgets = _get_budgets(profile_id)
    savings_goals = _get_savings_goals(profile_id)
    events = _get_events(profile_id)
    
    # Filter to upcoming events only
    now = datetime.now().isoformat()
    upcoming_events = [e for e in events if e.date >= now]
    
    # Log the retrieval
    _log_event(profile_id, "Financial Overview Retrieved")
    
    return GetFinancialOverviewResponse(
        profile_id=profile_id,
        savings=savings,
        payments=payments,
        budgets=budgets,
        savings_goals=savings_goals,
        upcoming_events=upcoming_events
    )

@router.get("/concierge-recommendations", response_model=ConciergeRecommendationResponse)
def get_concierge_recommendations(profile_id: str = Query(..., description="Profile ID to get recommendations for")) -> ConciergeRecommendationResponse:
    """
    Get personalized recommendations based on financial data.
    Provides AI-driven insights and suggestions for optimizing finances.
    """
    # Get financial data
    # Note: savings variable is used indirectly in future analysis
    current_savings = _get_savings(profile_id)
    payments = _get_payments(profile_id)
    budgets = _get_budgets(profile_id)
    goals = _get_savings_goals(profile_id)
    
    # Simple recommendation logic (in a real app, this would be more sophisticated)
    recommendations = []
    financial_insights = []
    suggested_actions = []
    
    # Check budget vs spending
    for budget in budgets:
        spent = sum(p.amount for p in payments if p.category == budget.name)
        if spent > budget.limit:
            recommendations.append(f"Your spending in {budget.name} is above budget by {spent - budget.limit:.2f}")
            suggested_actions.append(f"Reduce {budget.name} spending for the rest of the month")
    
    # Check savings progress
    for goal in goals:
        if goal.current_amount < goal.target * 0.5:
            financial_insights.append(f"You're less than halfway to your {goal.name} goal")
            suggested_actions.append(f"Consider allocating more to your {goal.name} savings")
    
    # Default recommendations if none generated
    if not recommendations:
        recommendations.append("Your finances appear to be in good order")
    
    if not financial_insights:
        financial_insights.append("Continue maintaining your current savings rate")
    
    if not suggested_actions:
        suggested_actions.append("Review your investment portfolio for potential optimization")
    
    # Log the recommendation event
    _log_event(profile_id, "Recommendations Generated")
    
    return ConciergeRecommendationResponse(
        recommendations=recommendations,
        financial_insights=financial_insights,
        suggested_actions=suggested_actions
    )

@router.get("/audit-log")
def get_audit_log(profile_id: str = Query(..., description="Profile ID to get audit log for")) -> List[AuditLogEntry]:
    """
    Get the audit log for a profile.
    Provides transparency and governance over all financial activities.
    """
    storage_key = _get_storage_key(profile_id, "audit_log")
    try:
        audit_log_data = db.storage.json.get(storage_key, default=[])
        return [AuditLogEntry(**entry) for entry in audit_log_data]
    except Exception:
        return []
