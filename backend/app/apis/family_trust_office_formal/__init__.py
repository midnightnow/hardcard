"""
Family Trust Office Formal API

Provides a mathematically rigorous financial management system for family trusts
with formal algebraic structures, compositional properties, and verification.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from uuid import uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, HTTPException, Query, Body

import databutton as db
import re
import json
import hashlib

router = APIRouter(prefix="/family-trust-office-formal")

# --- Mathematical Formalism Section ---

"""
== FORMAL MATHEMATICAL MODEL: FAMILY TRUST OFFICE ==

DEFINITION 1 (Monetary Value): A monetary value M is defined as a tuple (a, c) where:
- a ∈ ℝ is the amount
- c ∈ C is the currency from the set of valid currencies C

DEFINITION 2 (MonetaryMonoid): The set of monetary values M with the same currency
forms a commutative monoid (M, ⊕, 0_c) where:
- ⊕ is addition defined as (a₁, c) ⊕ (a₂, c) = (a₁ + a₂, c)
- 0_c is the identity element (0, c)
- Associativity: ∀x,y,z ∈ M: (x ⊕ y) ⊕ z = x ⊕ (y ⊕ z)
- Commutativity: ∀x,y ∈ M: x ⊕ y = y ⊕ x
- Identity: ∀x ∈ M: x ⊕ 0_c = x

DEFINITION 3 (Payment): A payment P is defined as a tuple (id, t, m, cat, s) where:
- id is a unique identifier
- t ∈ T is a timestamp
- m ∈ M is a monetary value
- cat ∈ CAT is a category from the set of valid categories
- s ∈ S is a status from the set of valid statuses

DEFINITION 4 (Budget): A budget B is defined as a tuple (id, cat, l) where:
- id is a unique identifier
- cat ∈ CAT is a category
- l ∈ M is the monetary limit

DEFINITION 5 (SavingsGoal): A savings goal G is defined as a tuple (id, n, m_target, m_current, t_target) where:
- id is a unique identifier
- n is a name
- m_target ∈ M is the target monetary value
- m_current ∈ M is the current monetary value
- t_target ∈ T is the target timestamp (optional)

DEFINITION 6 (LifeEvent): A life event E is defined as a tuple (id, t, d, cat, c) where:
- id is a unique identifier
- t ∈ T is a timestamp
- d is a description
- cat ∈ CAT is a category
- c is a boolean indicating completion status

DEFINITION 7 (FamilyTrustState): The state of a family trust F is defined as a tuple (id, M_savings, P, B, G, E) where:
- id is the profile identifier
- M_savings is a set of monetary values representing current savings
- P is a set of payments
- B is a set of budgets
- G is a set of savings goals
- E is a set of life events

DEFINITION 8 (StateTransformation): A state transformation is a function Γ: F × Δ → F
that transforms a trust state F by applying a delta Δ, yielding a new trust state.

DEFINITION 9 (AuditLog): An audit log A is a sequence of tuples (t, e, d, id) where:
- t ∈ T is a timestamp
- e is an event descriptor
- d is a set of details
- id is an optional profile identifier

THEOREM 1 (Budget Constraint): For any category cat ∈ CAT, let P_cat be the set of
all payments with category cat. A budget constraint is satisfied if and only if:
∑_{p ∈ P_cat} p.m.a ≤ B_cat.l.a
where B_cat is the budget for category cat.

THEOREM 2 (Savings Goal Progress): For any savings goal g ∈ G, the progress ratio r is defined as:
r = g.m_current.a / g.m_target.a
A goal is achieved when r ≥ 1.

THEOREM 3 (Temporal Consistency): For any two financial events e₁ and e₂ where
e₁ causally precedes e₂, their timestamps must satisfy: t₁ < t₂.
"""

# --- Models ---

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    BTC = "BTC"
    ETH = "ETH"


class PaymentCategory(str, Enum):
    EDUCATION = "education"
    HEALTH = "health"
    HOUSING = "housing"
    INVESTMENT = "investment"
    LEISURE = "leisure"
    TRANSPORTATION = "transportation"
    FOOD = "food"
    UTILITIES = "utilities"
    OTHER = "other"


class PaymentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELED = "canceled"
    PENDING = "pending"


class EventCategory(str, Enum):
    BIRTHDAY = "birthday"
    GRADUATION = "graduation"
    CAREER = "career"
    LEGAL = "legal"
    MILESTONE = "milestone"
    OTHER = "other"


# --- Core Algebraic Models ---

class MonetaryValue(BaseModel):
    """A monetary value representing the tuple (a, c) in the formal model"""
    amount: float = Field(..., description="The amount value")
    currency: Currency = Field(..., description="The currency code")

    def __add__(self, other: 'MonetaryValue') -> 'MonetaryValue':
        """Implements the ⊕ monoid operation for monetary values"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return MonetaryValue(amount=self.amount + other.amount, currency=self.currency)

    @classmethod
    def zero(cls, currency: Currency) -> 'MonetaryValue':
        """Returns the identity element 0_c for the monoid"""
        return cls(amount=0, currency=currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MonetaryValue):
            return False
        return self.amount == other.amount and self.currency == other.currency


class Payment(BaseModel):
    """A payment in the family trust system"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    amount: MonetaryValue
    category: PaymentCategory
    status: PaymentStatus
    description: Optional[str] = None
    recipient: Optional[str] = None
    profile_id: str


class Budget(BaseModel):
    """A budget constraint for a specific category"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    category: PaymentCategory
    limit: MonetaryValue
    period: str = Field(default="monthly", description="The time period for this budget")
    profile_id: str


class SavingsGoal(BaseModel):
    """A savings goal with target and current amounts"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    target_amount: MonetaryValue
    current_amount: MonetaryValue = Field(default=None)
    target_date: Optional[datetime] = None
    profile_id: str

    @validator("current_amount", pre=True, always=True)
    def set_default_current_amount(cls, v, values):
        if v is None and "target_amount" in values:
            return MonetaryValue(amount=0, currency=values["target_amount"].currency)
        return v

    def progress_ratio(self) -> float:
        """Calculate the progress ratio as defined in Theorem 2"""
        if self.target_amount.amount == 0:
            return 1.0  # Avoid division by zero
        return self.current_amount.amount / self.target_amount.amount

    def is_achieved(self) -> bool:
        """Check if the goal is achieved (r ≥ 1)"""
        return self.progress_ratio() >= 1.0


class LifeEvent(BaseModel):
    """A life event in the family trust timeline"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime
    description: str
    category: EventCategory
    completed: bool = False
    profile_id: str


class AuditLogEntry(BaseModel):
    """An entry in the audit log"""
    timestamp: datetime = Field(default_factory=datetime.now)
    event: str
    details: Dict[str, Any]
    profile_id: Optional[str] = None


class FinancialOverview(BaseModel):
    """A comprehensive overview of the financial state"""
    profile_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    total_savings: Dict[str, float] = Field(default_factory=dict)
    budget_status: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    upcoming_payments: List[Payment] = Field(default_factory=list)
    savings_goals_progress: List[Dict[str, Any]] = Field(default_factory=list)
    recent_events: List[LifeEvent] = Field(default_factory=list)


# --- Request/Response Models ---

class SchedulePaymentRequest(BaseModel):
    profile_id: str
    amount: float
    currency: Currency
    category: PaymentCategory
    description: Optional[str] = None
    recipient: Optional[str] = None
    timestamp: Optional[datetime] = None
    status: PaymentStatus = PaymentStatus.SCHEDULED


class SetBudgetRequest(BaseModel):
    profile_id: str
    category: PaymentCategory
    amount: float
    currency: Currency
    period: str = "monthly"


class SavingsGoalRequest(BaseModel):
    profile_id: str
    name: str
    target_amount: float
    currency: Currency
    target_date: Optional[datetime] = None


class ContributeToGoalRequest(BaseModel):
    profile_id: str
    goal_id: str
    amount: float
    currency: Currency


class ScheduleEventRequest(BaseModel):
    profile_id: str
    description: str
    category: EventCategory
    timestamp: datetime


# --- Helper Functions ---

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


def get_audit_log() -> List[AuditLogEntry]:
    """Retrieve the audit log from storage"""
    try:
        log_data = db.storage.json.get(sanitize_storage_key("family_trust_audit_log"), default=[])
        return [AuditLogEntry(**entry) for entry in log_data]
    except Exception as e:
        print(f"Error retrieving audit log: {e}")
        return []


def save_audit_log(log_entries: List[AuditLogEntry]):
    """Save the audit log to storage"""
    log_data = [entry.dict() for entry in log_entries]
    db.storage.json.put(sanitize_storage_key("family_trust_audit_log"), log_data)


def add_audit_log_entry(event: str, details: Dict[str, Any], profile_id: Optional[str] = None):
    """Add an entry to the audit log"""
    entries = get_audit_log()
    new_entry = AuditLogEntry(
        event=event,
        details=details,
        profile_id=profile_id
    )
    entries.append(new_entry)
    save_audit_log(entries)
    return new_entry


def get_payments(profile_id: str) -> List[Payment]:
    """Get all payments for a profile"""
    try:
        key = sanitize_storage_key(f"payments_{profile_id}")
        data = db.storage.json.get(key, default=[])
        payments = [Payment(**item) for item in data]

        # Sort by timestamp to maintain temporal consistency (Theorem 3)
        payments.sort(key=lambda p: p.timestamp)
        return payments
    except Exception as e:
        print(f"Error getting payments: {e}")
        return []


def save_payments(profile_id: str, payments: List[Payment]):
    """Save payments for a profile"""
    key = sanitize_storage_key(f"payments_{profile_id}")
    data = [payment.dict() for payment in payments]
    db.storage.json.put(key, data)


def get_budgets(profile_id: str) -> List[Budget]:
    """Get all budgets for a profile"""
    try:
        key = sanitize_storage_key(f"budgets_{profile_id}")
        data = db.storage.json.get(key, default=[])
        return [Budget(**item) for item in data]
    except Exception as e:
        print(f"Error getting budgets: {e}")
        return []


def save_budgets(profile_id: str, budgets: List[Budget]):
    """Save budgets for a profile"""
    key = sanitize_storage_key(f"budgets_{profile_id}")
    data = [budget.dict() for budget in budgets]
    db.storage.json.put(key, data)


def get_savings_goals(profile_id: str) -> List[SavingsGoal]:
    """Get all savings goals for a profile"""
    try:
        key = sanitize_storage_key(f"savings_goals_{profile_id}")
        data = db.storage.json.get(key, default=[])
        return [SavingsGoal(**item) for item in data]
    except Exception as e:
        print(f"Error getting savings goals: {e}")
        return []


def save_savings_goals(profile_id: str, goals: List[SavingsGoal]):
    """Save savings goals for a profile"""
    key = sanitize_storage_key(f"savings_goals_{profile_id}")
    data = [goal.dict() for goal in goals]
    db.storage.json.put(key, data)


def get_events(profile_id: str) -> List[LifeEvent]:
    """Get all life events for a profile"""
    try:
        key = sanitize_storage_key(f"events_{profile_id}")
        data = db.storage.json.get(key, default=[])
        events = [LifeEvent(**item) for item in data]
        
        # Sort by timestamp to maintain temporal consistency (Theorem 3)
        events.sort(key=lambda e: e.timestamp)
        return events
    except Exception as e:
        print(f"Error getting events: {e}")
        return []


def save_events(profile_id: str, events: List[LifeEvent]):
    """Save life events for a profile"""
    key = sanitize_storage_key(f"events_{profile_id}")
    data = [event.dict() for event in events]
    db.storage.json.put(key, data)


# --- Formal Verification Functions ---

def verify_budget_constraints(profile_id: str, input_budgets=None, input_payments=None) -> Dict[str, Any]:
    """Verify budget constraints according to Theorem 1"""
    budgets = input_budgets if input_budgets is not None else get_budgets(profile_id)
    payments = input_payments if input_payments is not None else get_payments(profile_id)
    
    # Group payments by category
    category_payments = {}
    for cat in PaymentCategory:
        category_payments[cat] = []
    
    for payment in payments:
        if payment.status == PaymentStatus.COMPLETED:
            category_payments[payment.category].append(payment)
    
    # Check each budget constraint
    results = {
        "satisfied": [],
        "violated": [],
        "no_budget": []
    }
    
    # Calculate spending by category
    category_spending = {}
    for cat, cat_payments in category_payments.items():
        category_spending[cat] = {}
        for payment in cat_payments:
            currency = payment.amount.currency
            if currency not in category_spending[cat]:
                category_spending[cat][currency] = 0
            category_spending[cat][currency] += payment.amount.amount
    
    # Check each budget
    for budget in budgets:
        cat = budget.category
        currency = budget.limit.currency
        limit = budget.limit.amount
        
        if cat in category_spending and currency in category_spending[cat]:
            spent = category_spending[cat][currency]
            if spent <= limit:
                results["satisfied"].append({
                    "category": cat,
                    "currency": currency,
                    "limit": limit,
                    "spent": spent
                })
            else:
                results["violated"].append({
                    "category": cat,
                    "currency": currency,
                    "limit": limit,
                    "spent": spent,
                    "excess": spent - limit
                })
        else:
            results["no_budget"].append({
                "category": cat,
                "currency": currency,
                "limit": limit,
                "spent": 0
            })
    
    return results


def verify_savings_goals_progress(profile_id: str) -> Dict[str, Any]:
    """Verify savings goals progress according to Theorem 2"""
    goals = get_savings_goals(profile_id)
    
    results = {
        "achieved": [],
        "in_progress": [],
        "at_risk": []  # Goals with a target date that might not be achieved on time
    }
    
    now = datetime.now()
    
    for goal in goals:
        progress = goal.progress_ratio()
        status_data = {
            "id": goal.id,
            "name": goal.name,
            "target": goal.target_amount.amount,
            "currency": goal.target_amount.currency,
            "current": goal.current_amount.amount,
            "progress": progress
        }
        
        if goal.is_achieved():
            results["achieved"].append(status_data)
        else:
            # Check if goal is at risk based on target date
            if goal.target_date:
                days_remaining = (goal.target_date - now).days
                if days_remaining > 0:
                    # Calculate required daily contribution
                    remaining_amount = goal.target_amount.amount - goal.current_amount.amount
                    daily_required = remaining_amount / days_remaining if days_remaining > 0 else float('inf')
                    
                    status_data["days_remaining"] = days_remaining
                    status_data["daily_required"] = daily_required
                    
                    # Heuristic: if daily required is > 5% of total, consider at risk
                    if daily_required > 0.05 * goal.target_amount.amount:
                        results["at_risk"].append(status_data)
                    else:
                        results["in_progress"].append(status_data)
                else:
                    # Past target date
                    status_data["days_overdue"] = -days_remaining
                    results["at_risk"].append(status_data)
            else:
                # No target date
                results["in_progress"].append(status_data)
    
    return results


def verify_temporal_consistency(profile_id: str) -> Dict[str, Any]:
    """Verify temporal consistency according to Theorem 3"""
    payments = get_payments(profile_id)
    events = get_events(profile_id)
    
    # Check temporal consistency of payments
    payment_times = [p.timestamp for p in payments]
    payment_consistent = all(payment_times[i] <= payment_times[i+1] for i in range(len(payment_times)-1))
    
    # Check temporal consistency of events
    event_times = [e.timestamp for e in events]
    event_consistent = all(event_times[i] <= event_times[i+1] for i in range(len(event_times)-1))
    
    # Check cross-consistency where relevant (e.g., payments related to life events should happen after events)
    # This is a simplified check - in a real system, you'd need more sophisticated causality tracking
    
    return {
        "payment_consistent": payment_consistent,
        "event_consistent": event_consistent,
        "overall_consistent": payment_consistent and event_consistent
    }


# --- API Endpoints ---

@router.post("/schedule-payment")
async def schedule_formal_payment(request: SchedulePaymentRequest):
    """Schedule a new payment"""
    payment = Payment(
        profile_id=request.profile_id,
        amount=MonetaryValue(amount=request.amount, currency=request.currency),
        category=request.category,
        description=request.description,
        recipient=request.recipient,
        timestamp=request.timestamp or datetime.now(),
        status=request.status
    )
    
    payments = get_payments(request.profile_id)
    payments.append(payment)
    save_payments(request.profile_id, payments)
    
    # Record in audit log
    add_audit_log_entry(
        event="Payment Scheduled",
        details={
            "payment_id": payment.id,
            "amount": request.amount,
            "currency": request.currency,
            "category": request.category
        },
        profile_id=request.profile_id
    )
    
    return {
        "status": "success",
        "message": "Payment scheduled successfully",
        "payment_id": payment.id
    }


@router.get("/payments")
async def get_formal_payments(profile_id: str):
    """Get all payments for a profile"""
    payments = get_payments(profile_id)
    return {
        "status": "success",
        "count": len(payments),
        "payments": [payment.dict() for payment in payments]
    }


@router.delete("/payment/{payment_id}")
async def delete_payment(payment_id: str, profile_id: str):
    """Delete a scheduled payment"""
    payments = get_payments(profile_id)
    original_count = len(payments)
    
    payments = [p for p in payments if p.id != payment_id]
    
    if len(payments) == original_count:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    save_payments(profile_id, payments)
    
    # Record in audit log
    add_audit_log_entry(
        event="Payment Deleted",
        details={"payment_id": payment_id},
        profile_id=profile_id
    )
    
    return {
        "status": "success",
        "message": "Payment deleted successfully"
    }


@router.post("/set-budget")
async def set_formal_budget(request: SetBudgetRequest):
    """Set or update a budget for a category"""
    budgets = get_budgets(request.profile_id)
    
    # Check if budget already exists for this category
    for i, budget in enumerate(budgets):
        if budget.category == request.category and budget.limit.currency == request.currency:
            # Update existing budget
            budgets[i].limit.amount = request.amount
            budgets[i].period = request.period
            budget_id = budget.id
            break
    else:
        # Create new budget
        new_budget = Budget(
            profile_id=request.profile_id,
            category=request.category,
            limit=MonetaryValue(amount=request.amount, currency=request.currency),
            period=request.period
        )
        budgets.append(new_budget)
        budget_id = new_budget.id
    
    save_budgets(request.profile_id, budgets)
    
    # Record in audit log
    add_audit_log_entry(
        event="Budget Set",
        details={
            "budget_id": budget_id,
            "category": request.category,
            "amount": request.amount,
            "currency": request.currency,
            "period": request.period
        },
        profile_id=request.profile_id
    )
    
    return {
        "status": "success",
        "message": "Budget set successfully",
        "budget_id": budget_id
    }


@router.get("/budgets")
async def get_formal_budgets(profile_id: str):
    """Get all budgets for a profile"""
    budgets = get_budgets(profile_id)
    return {
        "status": "success",
        "count": len(budgets),
        "budgets": [budget.dict() for budget in budgets]
    }


@router.delete("/budget/{budget_id}")
async def delete_budget(budget_id: str, profile_id: str):
    """Delete a budget"""
    budgets = get_budgets(profile_id)
    original_count = len(budgets)
    
    budgets = [b for b in budgets if b.id != budget_id]
    
    if len(budgets) == original_count:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    save_budgets(profile_id, budgets)
    
    # Record in audit log
    add_audit_log_entry(
        event="Budget Deleted",
        details={"budget_id": budget_id},
        profile_id=profile_id
    )
    
    return {
        "status": "success",
        "message": "Budget deleted successfully"
    }


@router.post("/set-savings-goal")
async def set_formal_savings_goal(request: SavingsGoalRequest):
    """Create a new savings goal"""
    goal = SavingsGoal(
        profile_id=request.profile_id,
        name=request.name,
        target_amount=MonetaryValue(amount=request.target_amount, currency=request.currency),
        target_date=request.target_date
    )
    
    goals = get_savings_goals(request.profile_id)
    goals.append(goal)
    save_savings_goals(request.profile_id, goals)
    
    # Record in audit log
    add_audit_log_entry(
        event="Savings Goal Created",
        details={
            "goal_id": goal.id,
            "name": request.name,
            "target_amount": request.target_amount,
            "currency": request.currency,
            "target_date": request.target_date.isoformat() if request.target_date else None
        },
        profile_id=request.profile_id
    )
    
    return {
        "status": "success",
        "message": "Savings goal created successfully",
        "goal_id": goal.id
    }


@router.get("/savings-goals")
async def get_formal_savings_goals(profile_id: str):
    """Get all savings goals for a profile"""
    goals = get_savings_goals(profile_id)
    return {
        "status": "success",
        "count": len(goals),
        "goals": [{
            **goal.dict(),
            "progress": goal.progress_ratio(),
            "achieved": goal.is_achieved()
        } for goal in goals]
    }


@router.post("/contribute-to-goal")
async def contribute_to_goal(request: ContributeToGoalRequest):
    """Contribute to a savings goal"""
    goals = get_savings_goals(request.profile_id)
    
    # Find the goal
    for i, goal in enumerate(goals):
        if goal.id == request.goal_id:
            # Verify currency match
            if goal.target_amount.currency != request.currency:
                raise HTTPException(status_code=400, detail=f"Currency mismatch: goal is in {goal.target_amount.currency}, contribution is in {request.currency}")
            
            # Add contribution (implementing the monoid operation)
            contribution = MonetaryValue(amount=request.amount, currency=request.currency)
            goals[i].current_amount = goals[i].current_amount + contribution
            
            # Save updated goals
            save_savings_goals(request.profile_id, goals)
            
            # Record in audit log
            add_audit_log_entry(
                event="Contribution to Savings Goal",
                details={
                    "goal_id": request.goal_id,
                    "amount": request.amount,
                    "currency": request.currency,
                    "new_balance": goals[i].current_amount.amount,
                    "progress": goals[i].progress_ratio(),
                    "achieved": goals[i].is_achieved()
                },
                profile_id=request.profile_id
            )
            
            return {
                "status": "success",
                "message": "Contribution added successfully",
                "new_balance": goals[i].current_amount.amount,
                "progress": goals[i].progress_ratio(),
                "achieved": goals[i].is_achieved()
            }
    
    raise HTTPException(status_code=404, detail="Savings goal not found")


@router.delete("/savings-goal/{goal_id}")
async def delete_savings_goal(goal_id: str, profile_id: str):
    """Delete a savings goal"""
    goals = get_savings_goals(profile_id)
    original_count = len(goals)
    
    goals = [g for g in goals if g.id != goal_id]
    
    if len(goals) == original_count:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    save_savings_goals(profile_id, goals)
    
    # Record in audit log
    add_audit_log_entry(
        event="Savings Goal Deleted",
        details={"goal_id": goal_id},
        profile_id=profile_id
    )
    
    return {
        "status": "success",
        "message": "Savings goal deleted successfully"
    }


@router.post("/schedule-event")
async def schedule_formal_event(request: ScheduleEventRequest):
    """Schedule a new life event"""
    event = LifeEvent(
        profile_id=request.profile_id,
        description=request.description,
        category=request.category,
        timestamp=request.timestamp
    )
    
    events = get_events(request.profile_id)
    events.append(event)
    save_events(request.profile_id, events)
    
    # Record in audit log
    add_audit_log_entry(
        event="Life Event Scheduled",
        details={
            "event_id": event.id,
            "description": request.description,
            "category": request.category,
            "timestamp": request.timestamp.isoformat()
        },
        profile_id=request.profile_id
    )
    
    return {
        "status": "success",
        "message": "Event scheduled successfully",
        "event_id": event.id
    }


@router.get("/events")
async def get_formal_events(profile_id: str):
    """Get all life events for a profile"""
    events = get_events(profile_id)
    return {
        "status": "success",
        "count": len(events),
        "events": [event.dict() for event in events]
    }


@router.delete("/event/{event_id}")
async def delete_event(event_id: str, profile_id: str):
    """Delete a life event"""
    events = get_events(profile_id)
    original_count = len(events)
    
    events = [e for e in events if e.id != event_id]
    
    if len(events) == original_count:
        raise HTTPException(status_code=404, detail="Event not found")
    
    save_events(profile_id, events)
    
    # Record in audit log
    add_audit_log_entry(
        event="Life Event Deleted",
        details={"event_id": event_id},
        profile_id=profile_id
    )
    
    return {
        "status": "success",
        "message": "Event deleted successfully"
    }


@router.get("/financial-overview")
async def get_formal_financial_overview(profile_id: str):
    """Get a comprehensive financial overview for a profile"""
    # Get all data
    payments = get_payments(profile_id)
    goals = get_savings_goals(profile_id)
    events = get_events(profile_id)
    
    # Fetch budgets once and use them for both verification and budget status
    budgets = get_budgets(profile_id)
    budget_verification = verify_budget_constraints(profile_id, input_budgets=budgets, input_payments=payments)
    
    # Verify savings goals progress
    savings_verification = verify_savings_goals_progress(profile_id)
    
    # Verify temporal consistency
    temporal_verification = verify_temporal_consistency(profile_id)
    
    # Calculate total savings
    total_savings = {}
    for goal in goals:
        currency = goal.current_amount.currency
        if currency not in total_savings:
            total_savings[currency] = 0
        total_savings[currency] += goal.current_amount.amount
    
    # Generate budget status
    budget_status = {}
    for result in budget_verification["satisfied"] + budget_verification["violated"]:
        category = result["category"]
        if category not in budget_status:
            budget_status[category] = {}
        
        currency = result["currency"]
        budget_status[category][currency] = {
            "limit": result["limit"],
            "spent": result["spent"],
            "remaining": result["limit"] - result["spent"]
        }
    
    # Get upcoming payments (scheduled but not completed)
    upcoming_payments = [p for p in payments if p.status == PaymentStatus.SCHEDULED]
    upcoming_payments.sort(key=lambda p: p.timestamp)
    
    # Get upcoming events
    now = datetime.now()
    upcoming_events = [e for e in events if e.timestamp > now]
    upcoming_events.sort(key=lambda e: e.timestamp)
    
    # Record in audit log
    add_audit_log_entry(
        event="Financial Overview Generated",
        details={
            "total_savings": total_savings,
            "budget_constraints_satisfied": len(budget_verification["satisfied"]),
            "budget_constraints_violated": len(budget_verification["violated"]),
            "savings_goals_achieved": len(savings_verification["achieved"]),
            "savings_goals_in_progress": len(savings_verification["in_progress"]),
            "savings_goals_at_risk": len(savings_verification["at_risk"]),
            "temporal_consistency": temporal_verification["overall_consistent"]
        },
        profile_id=profile_id
    )
    
    # Prepare response
    return {
        "status": "success",
        "profile_id": profile_id,
        "timestamp": datetime.now().isoformat(),
        "total_savings": total_savings,
        "budget_status": budget_status,
        "upcoming_payments": [p.dict() for p in upcoming_payments[:5]],  # Show next 5
        "goals_progress": {
            "achieved": savings_verification["achieved"],
            "in_progress": savings_verification["in_progress"],
            "at_risk": savings_verification["at_risk"]
        },
        "upcoming_events": [e.dict() for e in upcoming_events[:5]],  # Show next 5
        "verifications": {
            "budget_constraints": budget_verification,
            "savings_goals": savings_verification,
            "temporal_consistency": temporal_verification
        }
    }


@router.get("/audit-logs")
async def get_audit_logs(profile_id: Optional[str] = None, limit: int = Query(100, gt=0, le=1000)):
    """Get audit logs, optionally filtered by profile"""
    logs = get_audit_log()
    
    # Filter by profile if specified
    if profile_id:
        logs = [log for log in logs if log.profile_id == profile_id]
    
    # Sort by timestamp (newest first)
    logs.sort(key=lambda log: log.timestamp, reverse=True)
    
    # Limit results
    logs = logs[:limit]
    
    return {
        "status": "success",
        "count": len(logs),
        "logs": [log.dict() for log in logs]
    }
