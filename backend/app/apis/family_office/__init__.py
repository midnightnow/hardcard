from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import datetime
import json
import uuid
import databutton as db
from app.auth import AuthorizedUser

router = APIRouter()

# --------------------------
# Data Models
# --------------------------

class PaymentRequest(BaseModel):
    amount: float = Field(..., description="Payment amount")
    category: str = Field(..., description="Payment category (e.g., Utilities, Investment)")
    date: Optional[str] = Field(None, description="Payment date in ISO format (YYYY-MM-DD). Defaults to today if not provided.")
    description: Optional[str] = Field(None, description="Optional payment description")
    profile_id: str = Field(..., description="ID of the family profile this payment belongs to")

class Payment(BaseModel):
    id: str = Field(..., description="Unique payment identifier")
    amount: float = Field(..., description="Payment amount")
    category: str = Field(..., description="Payment category")
    date: str = Field(..., description="Payment date in ISO format (YYYY-MM-DD)")
    description: Optional[str] = Field(None, description="Optional payment description")
    profile_id: str = Field(..., description="ID of the family profile this payment belongs to")
    created_at: str = Field(..., description="Timestamp when this payment was created")

class PaymentResponse(BaseModel):
    payment: Payment
    message: str = Field("Payment scheduled successfully", description="Status message")

class PaymentsResponse(BaseModel):
    payments: List[Payment] = Field([], description="List of payments")
    count: int = Field(0, description="Total number of payments")

class EventRequest(BaseModel):
    description: str = Field(..., description="Event description")
    date: str = Field(..., description="Event date in ISO format (YYYY-MM-DD)")
    profile_id: str = Field(..., description="ID of the family profile this event belongs to")
    type: Optional[str] = Field("general", description="Event type (e.g., meeting, appointment, reminder)")

class Event(BaseModel):
    id: str = Field(..., description="Unique event identifier")
    description: str = Field(..., description="Event description")
    date: str = Field(..., description="Event date in ISO format (YYYY-MM-DD)")
    profile_id: str = Field(..., description="ID of the family profile this event belongs to")
    type: str = Field(..., description="Event type")
    created_at: str = Field(..., description="Timestamp when this event was created")

class EventResponse(BaseModel):
    event: Event
    message: str = Field("Event scheduled successfully", description="Status message")

class EventsResponse(BaseModel):
    events: List[Event] = Field([], description="List of events")
    count: int = Field(0, description="Total number of events")

class BudgetRequest(BaseModel):
    category: str = Field(..., description="Budget category (e.g., Food, Utilities, Entertainment)")
    limit: float = Field(..., description="Monthly budget limit")
    profile_id: str = Field(..., description="ID of the family profile this budget belongs to")

class Budget(BaseModel):
    id: str = Field(..., description="Unique budget identifier")
    category: str = Field(..., description="Budget category")
    limit: float = Field(..., description="Monthly budget limit")
    profile_id: str = Field(..., description="ID of the family profile this budget belongs to")
    created_at: str = Field(..., description="Timestamp when this budget was created")
    updated_at: str = Field(..., description="Timestamp when this budget was last updated")

class BudgetResponse(BaseModel):
    budget: Budget
    message: str = Field("Budget set successfully", description="Status message")

class BudgetsResponse(BaseModel):
    budgets: List[Budget] = Field([], description="List of budgets")
    count: int = Field(0, description="Total number of budgets")

class SavingsGoalRequest(BaseModel):
    name: str = Field(..., description="Goal name (e.g., 'House Down Payment', 'College Fund')")
    target: float = Field(..., description="Target amount to save")
    profile_id: str = Field(..., description="ID of the family profile this savings goal belongs to")
    target_date: Optional[str] = Field(None, description="Target date in ISO format (YYYY-MM-DD)")

class SavingsGoal(BaseModel):
    id: str = Field(..., description="Unique savings goal identifier")
    name: str = Field(..., description="Goal name")
    target: float = Field(..., description="Target amount to save")
    profile_id: str = Field(..., description="ID of the family profile this savings goal belongs to")
    target_date: Optional[str] = Field(None, description="Target date in ISO format (YYYY-MM-DD)")
    current_amount: float = Field(0, description="Current amount saved toward goal")
    created_at: str = Field(..., description="Timestamp when this goal was created")
    updated_at: str = Field(..., description="Timestamp when this goal was last updated")

class SavingsGoalResponse(BaseModel):
    goal: SavingsGoal
    message: str = Field("Savings goal set successfully", description="Status message")

class SavingsGoalsResponse(BaseModel):
    goals: List[SavingsGoal] = Field([], description="List of savings goals")
    count: int = Field(0, description="Total number of goals")

class GoalContributionRequest(BaseModel):
    goal_id: str = Field(..., description="ID of the savings goal")
    amount: float = Field(..., description="Amount to contribute")

class FinancialOverviewResponse(BaseModel):
    profile_id: str = Field(..., description="Family profile ID")
    savings: float = Field(0, description="Current savings amount")
    payments: List[Payment] = Field([], description="Recent payments")
    budgets: List[Budget] = Field([], description="Current budgets")
    goals: List[SavingsGoal] = Field([], description="Current savings goals")
    events: List[Event] = Field([], description="Upcoming events")

class AuditLogEntry(BaseModel):
    id: str = Field(..., description="Unique log entry identifier")
    timestamp: str = Field(..., description="Timestamp of the event")
    event: str = Field(..., description="Event description")
    details: Dict[str, Any] = Field({}, description="Event details")
    profile_id: Optional[str] = Field(None, description="Associated profile ID, if applicable")

class AuditLogResponse(BaseModel):
    logs: List[AuditLogEntry] = Field([], description="Audit log entries")
    count: int = Field(0, description="Total number of log entries")

# --------------------------
# Helper Functions
# --------------------------

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def format_currency(amount: float) -> str:
    """Format currency value as string"""
    return f"${amount:,.2f}"

def get_db_key(profile_id: str, collection: str) -> str:
    """Generate a consistent storage key for a profile's data collection"""
    return sanitize_storage_key(f"family_office_{profile_id}_{collection}")

def get_profile_data(profile_id: str, collection: str) -> List[Dict]:
    """Get data for a specific profile and collection"""
    try:
        key = get_db_key(profile_id, collection)
        data = db.storage.json.get(key, default=[])
        return data
    except Exception as e:
        print(f"Error retrieving {collection} for profile {profile_id}: {str(e)}")
        return []
    
def save_profile_data(profile_id: str, collection: str, data: List[Dict]) -> bool:
    """Save data for a specific profile and collection"""
    try:
        key = get_db_key(profile_id, collection)
        db.storage.json.put(key, data)
        return True
    except Exception as e:
        print(f"Error saving {collection} for profile {profile_id}: {str(e)}")
        return False

def log_event(profile_id: str, event: str, details: Dict[str, Any] = None) -> None:
    """Add an entry to the governance audit log"""
    try:
        logs_key = sanitize_storage_key("family_office_governance_logs")
        logs = db.storage.json.get(logs_key, default=[])
        
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event": event,
            "details": details or {},
            "profile_id": profile_id
        }
        
        logs.append(log_entry)
        db.storage.json.put(logs_key, logs)
    except Exception as e:
        print(f"Error logging governance event: {str(e)}")

# --------------------------
# Payment Management Endpoints
# --------------------------

@router.post("/payments", response_model=PaymentResponse)
def schedule_payment2(payment: PaymentRequest) -> PaymentResponse:
    """Schedule a new payment for a specific family profile."""
    try:
        # Validate date or default to today
        if payment.date:
            date = payment.date
        else:
            date = datetime.date.today().isoformat()
        
        # Create new payment record
        payment_id = str(uuid.uuid4())
        new_payment = {
            "id": payment_id,
            "amount": payment.amount,
            "category": payment.category,
            "date": date,
            "description": payment.description,
            "profile_id": payment.profile_id,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        # Store the payment
        payments = get_profile_data(payment.profile_id, "payments")
        payments.append(new_payment)
        save_profile_data(payment.profile_id, "payments", payments)
        
        # Log the event
        log_event(
            payment.profile_id, 
            "Payment Scheduled", 
            {"payment_id": payment_id, "amount": payment.amount, "category": payment.category}
        )
        
        return PaymentResponse(payment=Payment(**new_payment))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule payment: {str(e)}")

@router.get("/payments/{profile_id}", response_model=PaymentsResponse)
def get_payments(profile_id: str) -> PaymentsResponse:
    """Get all payments for a specific family profile."""
    try:
        payments = get_profile_data(profile_id, "payments")
        return PaymentsResponse(payments=[Payment(**p) for p in payments], count=len(payments))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payments: {str(e)}")

@router.delete("/payments/{payment_id}")
def delete_payment2(payment_id: str, profile_id: str) -> Dict[str, str]:
    """Delete a specific payment."""
    try:
        payments = get_profile_data(profile_id, "payments")
        
        # Find and remove the payment
        for i, payment in enumerate(payments):
            if payment.get("id") == payment_id:
                removed_payment = payments.pop(i)
                save_profile_data(profile_id, "payments", payments)
                
                # Log the event
                log_event(
                    profile_id, 
                    "Payment Deleted", 
                    {"payment_id": payment_id, "amount": removed_payment.get("amount"), "category": removed_payment.get("category")}
                )
                
                return {"message": "Payment deleted successfully"}
        
        # If we get here, payment was not found
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete payment: {str(e)}")

# --------------------------
# Life Coordination Endpoints
# --------------------------

@router.post("/events", response_model=EventResponse)
def schedule_event2(event: EventRequest) -> EventResponse:
    """Schedule a new life event for a specific family profile."""
    try:
        # Create new event record
        event_id = str(uuid.uuid4())
        new_event = {
            "id": event_id,
            "description": event.description,
            "date": event.date,
            "profile_id": event.profile_id,
            "type": event.type,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        # Store the event
        events = get_profile_data(event.profile_id, "events")
        events.append(new_event)
        save_profile_data(event.profile_id, "events", events)
        
        # Log the event
        log_event(
            event.profile_id, 
            "Event Scheduled", 
            {"event_id": event_id, "description": event.description, "date": event.date}
        )
        
        return EventResponse(event=Event(**new_event))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule event: {str(e)}")

@router.get("/events/{profile_id}", response_model=EventsResponse)
def get_events(profile_id: str) -> EventsResponse:
    """Get all events for a specific family profile."""
    try:
        events = get_profile_data(profile_id, "events")
        return EventsResponse(events=[Event(**e) for e in events], count=len(events))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")

@router.delete("/events/{event_id}")
def delete_event2(event_id: str, profile_id: str) -> Dict[str, str]:
    """Delete a specific event."""
    try:
        events = get_profile_data(profile_id, "events")
        
        # Find and remove the event
        for i, event in enumerate(events):
            if event.get("id") == event_id:
                removed_event = events.pop(i)
                save_profile_data(profile_id, "events", events)
                
                # Log the event
                log_event(
                    profile_id, 
                    "Event Deleted", 
                    {"event_id": event_id, "description": removed_event.get("description")}
                )
                
                return {"message": "Event deleted successfully"}
        
        # If we get here, event was not found
        raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

# --------------------------
# Budget Management Endpoints
# --------------------------

@router.post("/budgets", response_model=BudgetResponse)
def set_budget2(budget: BudgetRequest) -> BudgetResponse:
    """Set a budget for a specific category and family profile."""
    try:
        budgets = get_profile_data(budget.profile_id, "budgets")
        
        # Check if budget for this category already exists
        budget_id = None
        for i, b in enumerate(budgets):
            if b.get("category") == budget.category:
                budget_id = b.get("id")
                # Update existing budget
                budgets[i]["limit"] = budget.limit
                budgets[i]["updated_at"] = datetime.datetime.utcnow().isoformat()
                break
        
        # Create new budget if doesn't exist
        if not budget_id:
            budget_id = str(uuid.uuid4())
            new_budget = {
                "id": budget_id,
                "category": budget.category,
                "limit": budget.limit,
                "profile_id": budget.profile_id,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "updated_at": datetime.datetime.utcnow().isoformat()
            }
            budgets.append(new_budget)
        
        # Save budgets
        save_profile_data(budget.profile_id, "budgets", budgets)
        
        # Get the updated/created budget
        updated_budget = next(b for b in budgets if b["id"] == budget_id)
        
        # Log the event
        log_event(
            budget.profile_id, 
            "Budget Set", 
            {"budget_id": budget_id, "category": budget.category, "limit": budget.limit}
        )
        
        return BudgetResponse(budget=Budget(**updated_budget))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set budget: {str(e)}")

@router.get("/budgets/{profile_id}", response_model=BudgetsResponse)
def get_budgets(profile_id: str) -> BudgetsResponse:
    """Get all budgets for a specific family profile."""
    try:
        budgets = get_profile_data(profile_id, "budgets")
        return BudgetsResponse(budgets=[Budget(**b) for b in budgets], count=len(budgets))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve budgets: {str(e)}")

@router.delete("/budgets/{budget_id}")
def delete_budget2(budget_id: str, profile_id: str) -> Dict[str, str]:
    """Delete a specific budget."""
    try:
        budgets = get_profile_data(profile_id, "budgets")
        
        # Find and remove the budget
        for i, budget in enumerate(budgets):
            if budget.get("id") == budget_id:
                removed_budget = budgets.pop(i)
                save_profile_data(profile_id, "budgets", budgets)
                
                # Log the event
                log_event(
                    profile_id, 
                    "Budget Deleted", 
                    {"budget_id": budget_id, "category": removed_budget.get("category")}
                )
                
                return {"message": "Budget deleted successfully"}
        
        # If we get here, budget was not found
        raise HTTPException(status_code=404, detail=f"Budget with ID {budget_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete budget: {str(e)}")

# --------------------------
# Savings Goal Endpoints
# --------------------------

@router.post("/savings-goals", response_model=SavingsGoalResponse)
def set_savings_goal2(goal: SavingsGoalRequest) -> SavingsGoalResponse:
    """Set a savings goal for a specific family profile."""
    try:
        goals = get_profile_data(goal.profile_id, "savings_goals")
        
        # Create new goal
        goal_id = str(uuid.uuid4())
        new_goal = {
            "id": goal_id,
            "name": goal.name,
            "target": goal.target,
            "profile_id": goal.profile_id,
            "target_date": goal.target_date,
            "current_amount": 0,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
        
        goals.append(new_goal)
        save_profile_data(goal.profile_id, "savings_goals", goals)
        
        # Log the event
        log_event(
            goal.profile_id, 
            "Savings Goal Set", 
            {"goal_id": goal_id, "name": goal.name, "target": goal.target}
        )
        
        return SavingsGoalResponse(goal=SavingsGoal(**new_goal))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set savings goal: {str(e)}")

@router.get("/savings-goals/{profile_id}", response_model=SavingsGoalsResponse)
def get_savings_goals(profile_id: str) -> SavingsGoalsResponse:
    """Get all savings goals for a specific family profile."""
    try:
        goals = get_profile_data(profile_id, "savings_goals")
        return SavingsGoalsResponse(goals=[SavingsGoal(**g) for g in goals], count=len(goals))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve savings goals: {str(e)}")

@router.post("/savings-goals/{goal_id}/contribute")
def contribute_to_family_goal(goal_id: str, contribution: GoalContributionRequest) -> Dict[str, Any]:
    """Contribute money to a specific savings goal."""
    try:
        # First, find which profile this goal belongs to
        goals_found = False
        profile_id = None
        
        # Get a list of all family profiles
        from app.apis.family_profiles import list_family_profiles as get_profiles
        profiles_response = get_profiles()
        profiles = profiles_response.get("profiles", [])
        
        # For each profile, check if they have this goal
        for profile in profiles:
            profile_id = profile.get("id")
            goals = get_profile_data(profile_id, "savings_goals")
            
            # Update the goal if found
            for i, goal in enumerate(goals):
                if goal.get("id") == goal_id:
                    goals[i]["current_amount"] = goal.get("current_amount", 0) + contribution.amount
                    goals[i]["updated_at"] = datetime.datetime.utcnow().isoformat()
                    save_profile_data(profile_id, "savings_goals", goals)
                    goals_found = True
                    
                    # Log the event
                    log_event(
                        profile_id, 
                        "Goal Contribution", 
                        {"goal_id": goal_id, "amount": contribution.amount, "goal_name": goal.get("name")}
                    )
                    
                    # Get updated goal
                    updated_goal = goals[i]
                    return {
                        "goal": updated_goal,
                        "message": f"Successfully contributed {format_currency(contribution.amount)} to goal"
                    }
        
        # If we get here, goal was not found
        if not goals_found:
            raise HTTPException(status_code=404, detail=f"Savings goal with ID {goal_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to contribute to goal: {str(e)}")

@router.delete("/savings-goals/{goal_id}")
def delete_family_savings_goal(goal_id: str, profile_id: str) -> Dict[str, str]:
    """Delete a specific savings goal."""
    try:
        goals = get_profile_data(profile_id, "savings_goals")
        
        # Find and remove the goal
        for i, goal in enumerate(goals):
            if goal.get("id") == goal_id:
                removed_goal = goals.pop(i)
                save_profile_data(profile_id, "savings_goals", goals)
                
                # Log the event
                log_event(
                    profile_id, 
                    "Savings Goal Deleted", 
                    {"goal_id": goal_id, "name": removed_goal.get("name")}
                )
                
                return {"message": "Savings goal deleted successfully"}
        
        # If we get here, goal was not found
        raise HTTPException(status_code=404, detail=f"Savings goal with ID {goal_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete savings goal: {str(e)}")

# --------------------------
# Financial Overview Endpoint
# --------------------------

@router.get("/financial-overview/{profile_id}", response_model=FinancialOverviewResponse)
def get_financial_overview2(profile_id: str) -> FinancialOverviewResponse:
    """Get a comprehensive financial overview for a specific family profile."""
    try:
        # Get all related data
        payments = get_profile_data(profile_id, "payments")
        budgets = get_profile_data(profile_id, "budgets")
        goals = get_profile_data(profile_id, "savings_goals")
        events = get_profile_data(profile_id, "events")
        
        # Calculate current savings from goals
        total_savings = sum(goal.get("current_amount", 0) for goal in goals)
        
        # Sort payments by date (most recent first)
        sorted_payments = sorted(
            payments, 
            key=lambda p: p.get("date", "0000-00-00"), 
            reverse=True
        )[:10]  # Get last 10 payments
        
        # Sort events by date (soonest first)
        sorted_events = sorted(
            events,
            key=lambda e: e.get("date", "9999-99-99")
        )[:5]  # Get 5 upcoming events
        
        # Log the view
        log_event(
            profile_id, 
            "Financial Overview Retrieved", 
            {"total_savings": total_savings, "payment_count": len(payments), "goals_count": len(goals)}
        )
        
        return FinancialOverviewResponse(
            profile_id=profile_id,
            savings=total_savings,
            payments=[Payment(**p) for p in sorted_payments],
            budgets=[Budget(**b) for b in budgets],
            goals=[SavingsGoal(**g) for g in goals],
            events=[Event(**e) for e in sorted_events]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve financial overview: {str(e)}")

# --------------------------
# Governance Endpoints
# --------------------------

@router.get("/governance/logs", response_model=AuditLogResponse)
def get_family_audit_logs(profile_id: Optional[str] = None, limit: int = 100) -> AuditLogResponse:
    """Get governance audit logs, optionally filtered by profile_id."""
    try:
        logs_key = sanitize_storage_key("family_office_governance_logs")
        logs = db.storage.json.get(logs_key, default=[])
        
        # Filter by profile_id if provided
        if profile_id:
            filtered_logs = [log for log in logs if log.get("profile_id") == profile_id]
        else:
            filtered_logs = logs
        
        # Sort by timestamp (most recent first) and limit
        sorted_logs = sorted(
            filtered_logs,
            key=lambda log: log.get("timestamp", ""),
            reverse=True
        )[:limit]
        
        return AuditLogResponse(logs=[AuditLogEntry(**log) for log in sorted_logs], count=len(sorted_logs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")

# --------------------------
# Module Integration Endpoint
# --------------------------

@router.post("/run-family-office")
def run_family_office(profile_id: str) -> Dict[str, Any]:
    """Run family office operations for a profile, integrating payments, events, and financial planning."""
    try:
        # Get financial overview
        overview = get_financial_overview2(profile_id)
        
        # Log the operation
        log_event(
            profile_id, 
            "Family Office Operations Run", 
            {"timestamp": datetime.datetime.utcnow().isoformat()}
        )
        
        # Simulate family office benefits
        benefits = [
            "Priority access to estate planning advisors",
            "Exclusive rates on luxury concierge services",
            "Custom investment and tax planning sessions",
            "Personal health and wellness coaching"
        ]
        
        return {
            "message": "Family Office operations completed successfully",
            "overview": overview,
            "benefits": benefits
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run family office operations: {str(e)}")
