from fastapi import APIRouter, Depends, HTTPException, Query
import databutton as db
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime, timedelta
from app.auth import AuthorizedUser
import json

# Create router
router = APIRouter(prefix="/crm")

# ----- Data Models -----

# Customer Profile
class CustomerTag(BaseModel):
    tag: str

class CustomField(BaseModel):
    key: str
    value: str

class CustomerProfileResponse(BaseModel):
    id: str
    email: str
    display_name: str
    phone_number: Optional[str] = None
    tags: Optional[List[str]] = None
    lifetime_value: Optional[float] = None
    average_order_value: Optional[float] = None
    purchase_frequency: Optional[float] = None
    last_activity: Optional[str] = None
    last_interaction: Optional[str] = None
    risk_level: Optional[str] = None
    acquisition_source: Optional[str] = None
    notes: Optional[List[str]] = None
    segment_ids: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, str]] = None
    created_at: str
    updated_at: str
    order_count: Optional[int] = None
    last_order_date: Optional[str] = None
    has_subscription: Optional[bool] = None
    open_tickets: Optional[int] = None

class CustomerProfileUpdateRequest(BaseModel):
    tags: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, str]] = None
    risk_level: Optional[Literal["low", "medium", "high"]] = None
    acquisition_source: Optional[str] = None

# Segmentation
class SegmentCriteriaRequest(BaseModel):
    purchase_frequency: Optional[Dict[str, Any]] = None
    purchase_value: Optional[Dict[str, Any]] = None
    product_category: Optional[List[str]] = None
    location: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    last_purchase: Optional[Dict[str, Any]] = None
    customer_since: Optional[Dict[str, Any]] = None
    custom_fields: Optional[List[Dict[str, Any]]] = None

class SegmentRequest(BaseModel):
    name: str
    description: str
    criteria: SegmentCriteriaRequest
    active: bool = True

class SegmentResponse(BaseModel):
    id: str
    name: str
    description: str
    criteria: Dict[str, Any]
    created_at: str
    updated_at: str
    created_by: str
    active: bool
    customer_count: Optional[int] = None

# Service Tickets
class TicketCommunicationRequest(BaseModel):
    message: str
    sender_type: Literal["customer", "staff"]
    attachments: Optional[List[str]] = None

class TicketRequest(BaseModel):
    subject: str
    description: str
    category: Literal["order", "product", "shipping", "account", "other"]
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    order_id: Optional[str] = None

class TicketCommunicationResponse(BaseModel):
    id: str
    ticket_id: str
    message: str
    sender_id: str
    sender_type: str
    timestamp: str
    attachments: Optional[List[str]] = None

class TicketResponse(BaseModel):
    id: str
    user_id: str
    subject: str
    description: str
    status: str
    priority: str
    category: str
    order_id: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: str
    updated_at: str
    communications: List[TicketCommunicationResponse]
    resolution: Optional[str] = None
    satisfaction_rating: Optional[int] = None

class TicketUpdateRequest(BaseModel):
    status: Optional[Literal["open", "in_progress", "resolved", "closed"]] = None
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None

# Feedback
class FeedbackRequest(BaseModel):
    order_id: Optional[str] = None
    type: Literal["product", "delivery", "website", "customer_service", "general"]
    rating: int = Field(..., ge=1, le=5)
    comments: str

class FeedbackResponse(BaseModel):
    id: str
    user_id: str
    order_id: Optional[str] = None
    type: str
    rating: int
    comments: str
    created_at: str
    responded_to: bool
    response: Optional[Dict[str, Any]] = None

class FeedbackResponseRequest(BaseModel):
    message: str

# Subscriptions
class SubscriptionPlanRequest(BaseModel):
    name: str
    description: str
    frequency: Literal["weekly", "biweekly", "monthly", "custom"]
    custom_days: Optional[int] = None
    discount_percentage: Optional[float] = None
    active: bool = True

class SubscriptionPlanResponse(BaseModel):
    id: str
    name: str
    description: str
    frequency: str
    custom_days: Optional[int] = None
    discount_percentage: Optional[float] = None
    active: bool
    created_at: str
    updated_at: str

class SubscriptionProduct(BaseModel):
    product_id: str
    quantity: int
    custom_options: Optional[Dict[str, Any]] = None

class SubscriptionRequest(BaseModel):
    plan_id: str
    products: List[SubscriptionProduct]
    shipping_address_id: str
    payment_method_id: str

class SubscriptionPaymentHistory(BaseModel):
    date: str
    amount: float
    status: str
    transaction_id: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    products: List[Dict[str, Any]]
    shipping_address_id: str
    payment_method_id: str
    status: str
    next_delivery_date: str
    last_delivery_date: Optional[str] = None
    created_at: str
    updated_at: str
    payment_history: List[SubscriptionPaymentHistory]
    pause_until: Optional[str] = None
    cancellation_reason: Optional[str] = None

class SubscriptionUpdateRequest(BaseModel):
    status: Optional[Literal["active", "paused", "cancelled"]] = None
    pause_until: Optional[str] = None
    cancellation_reason: Optional[str] = None

# Loyalty
class LoyaltyTierRequest(BaseModel):
    name: str
    description: str
    point_threshold: int
    multiplier: float
    benefits: List[str]
    icon: Optional[str] = None
    color: Optional[str] = None

class LoyaltyTierResponse(BaseModel):
    id: str
    name: str
    description: str
    point_threshold: int
    multiplier: float
    benefits: List[str]
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: str
    updated_at: str

class LoyaltyRewardRequest(BaseModel):
    name: str
    description: str
    point_cost: int
    reward_type: Literal["discount", "free_product", "free_shipping", "gift"]
    discount_value: Optional[float] = None
    discount_type: Optional[Literal["percentage", "fixed"]] = None
    product_id: Optional[str] = None
    active: bool = True
    limited_quantity: Optional[int] = None
    expires_at: Optional[str] = None

class LoyaltyRewardResponse(BaseModel):
    id: str
    name: str
    description: str
    point_cost: int
    reward_type: str
    discount_value: Optional[float] = None
    discount_type: Optional[str] = None
    product_id: Optional[str] = None
    active: bool
    limited_quantity: Optional[int] = None
    remaining: Optional[int] = None
    expires_at: Optional[str] = None
    created_at: str
    updated_at: str

class LoyaltyPointHistoryItem(BaseModel):
    date: str
    amount: int
    type: str
    source: str

class LoyaltyRewardRedemptionItem(BaseModel):
    reward_id: str
    date: str
    points_used: int

class CustomerLoyaltyResponse(BaseModel):
    user_id: str
    points: int
    tier_id: str
    lifetime_points: int
    points_history: List[LoyaltyPointHistoryItem]
    rewards_redeemed: List[LoyaltyRewardRedemptionItem]
    created_at: str
    updated_at: str
    current_tier: Optional[LoyaltyTierResponse] = None

class AddLoyaltyPointsRequest(BaseModel):
    points: int
    source: str

# ----- Helper Functions -----

def get_firestore_data(collection, doc_id, default=None):
    """Helper to get Firestore document data"""
    try:
        data_json = db.storage.text.get(f"firestore_{collection}_{doc_id}")
        return json.loads(data_json)
    except:
        return default

def set_firestore_data(collection, doc_id, data):
    """Helper to store Firestore document data"""
    data_json = json.dumps(data)
    db.storage.text.put(f"firestore_{collection}_{doc_id}", data_json)

def list_firestore_collection(collection):
    """Helper to list all documents in a collection"""
    # Get a list of all documents in the collection
    collection_keys = db.storage.text.list()
    prefix = f"firestore_{collection}_"
    docs = []
    
    for file in collection_keys:
        if file.name.startswith(prefix):
            try:
                doc_data = json.loads(db.storage.text.get(file.name))
                docs.append(doc_data)
            except:
                continue
    
    return docs

# ----- API Endpoints -----

# Customer Profiles

@router.get("/customers/{user_id}")
async def get_customer_profile(user_id: str, user: AuthorizedUser):
    """Get a customer profile with CRM data"""
    # Get basic user profile
    user_profile = get_firestore_data("users", user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get CRM-specific data
    crm_data = get_firestore_data("crm_customer_data", user_id, {})
    
    # Get loyalty data
    loyalty_data = get_firestore_data("customer_loyalty", user_id)
    
    # Count open tickets
    tickets = list_firestore_collection("service_tickets")
    open_tickets = sum(1 for t in tickets if t.get("user_id") == user_id and t.get("status") in ["open", "in_progress"])
    
    # Combine all data
    combined_data = {
        **user_profile,
        **crm_data,
        "open_tickets": open_tickets
    }
    
    if loyalty_data:
        combined_data["has_loyalty"] = True
    
    return CustomerProfileResponse(**combined_data)

@router.put("/customers/{user_id}")
async def update_customer_profile(user_id: str, data: CustomerProfileUpdateRequest, user: AuthorizedUser):
    """Update a customer's CRM data"""
    # Get existing CRM data
    crm_data = get_firestore_data("crm_customer_data", user_id, {})
    
    # Update with new data
    update_data = data.dict(exclude_unset=True)
    timestamp = datetime.now().isoformat()
    
    if not crm_data:
        # Creating new CRM profile
        crm_data = {
            **update_data,
            "created_at": timestamp,
            "updated_at": timestamp
        }
    else:
        # Updating existing profile
        crm_data.update(update_data)
        crm_data["updated_at"] = timestamp
    
    # Save updated data
    set_firestore_data("crm_customer_data", user_id, crm_data)
    
    return {"success": True, "message": "Customer profile updated successfully"}

@router.post("/customers/{user_id}/tags")
async def add_customer_tag(user_id: str, data: CustomerTag, user: AuthorizedUser):
    """Add a tag to a customer profile"""
    # Get existing CRM data
    crm_data = get_firestore_data("crm_customer_data", user_id, {})
    timestamp = datetime.now().isoformat()
    
    # Add tag if it doesn't exist already
    if "tags" not in crm_data:
        crm_data["tags"] = []
    
    if data.tag not in crm_data["tags"]:
        crm_data["tags"].append(data.tag)
    
    if "created_at" not in crm_data:
        crm_data["created_at"] = timestamp
    
    crm_data["updated_at"] = timestamp
    
    # Save updated data
    set_firestore_data("crm_customer_data", user_id, crm_data)
    
    return {"success": True, "message": "Tag added successfully"}

@router.delete("/customers/{user_id}/tags/{tag}")
async def remove_customer_tag(user_id: str, tag: str, user: AuthorizedUser):
    """Remove a tag from a customer profile"""
    # Get existing CRM data
    crm_data = get_firestore_data("crm_customer_data", user_id, {})
    
    # Remove tag if it exists
    if "tags" in crm_data and tag in crm_data["tags"]:
        crm_data["tags"].remove(tag)
        crm_data["updated_at"] = datetime.now().isoformat()
        
        # Save updated data
        set_firestore_data("crm_customer_data", user_id, crm_data)
        
    return {"success": True, "message": "Tag removed successfully"}

@router.post("/customers/{user_id}/custom-fields")
async def set_customer_custom_field(user_id: str, data: CustomField, user: AuthorizedUser):
    """Set a custom field for a customer profile"""
    # Get existing CRM data
    crm_data = get_firestore_data("crm_customer_data", user_id, {})
    timestamp = datetime.now().isoformat()
    
    # Initialize custom_fields if it doesn't exist
    if "custom_fields" not in crm_data:
        crm_data["custom_fields"] = {}
    
    # Add or update custom field
    crm_data["custom_fields"][data.key] = data.value
    
    if "created_at" not in crm_data:
        crm_data["created_at"] = timestamp
    
    crm_data["updated_at"] = timestamp
    
    # Save updated data
    set_firestore_data("crm_customer_data", user_id, crm_data)
    
    return {"success": True, "message": "Custom field updated successfully"}

@router.delete("/customers/{user_id}/custom-fields/{key}")
async def remove_customer_custom_field(user_id: str, key: str, user: AuthorizedUser):
    """Remove a custom field from a customer profile"""
    # Get existing CRM data
    crm_data = get_firestore_data("crm_customer_data", user_id, {})
    
    # Remove custom field if it exists
    if "custom_fields" in crm_data and key in crm_data["custom_fields"]:
        del crm_data["custom_fields"][key]
        crm_data["updated_at"] = datetime.now().isoformat()
        
        # Save updated data
        set_firestore_data("crm_customer_data", user_id, crm_data)
        
    return {"success": True, "message": "Custom field removed successfully"}

# Customer Segmentation

@router.post("/segments")
async def create_segment(data: SegmentRequest, user: AuthorizedUser):
    """Create a new customer segment"""
    timestamp = datetime.now().isoformat()
    segment_id = f"seg_{int(datetime.now().timestamp())}"
    
    # Create segment data
    segment = {
        "id": segment_id,
        "name": data.name,
        "description": data.description,
        "criteria": data.criteria.dict(exclude_unset=True),
        "created_at": timestamp,
        "updated_at": timestamp,
        "created_by": user.sub,
        "active": data.active
    }
    
    # Save segment data
    set_firestore_data("customer_segments", segment_id, segment)
    
    return SegmentResponse(**segment, customer_count=0)

@router.get("/segments")
async def get_segments(
    user: AuthorizedUser,
    active_only: bool = Query(True, description="Only return active segments")
):
    """Get all customer segments"""
    segments = list_firestore_collection("customer_segments")
    
    # Filter by active status if requested
    if active_only:
        segments = [s for s in segments if s.get("active", True)]
    
    # For each segment, count matching customers (stub implementation)
    # In a real implementation, this would evaluate the segment criteria against all customers
    for segment in segments:
        segment["customer_count"] = 0  # Placeholder for actual count
    
    return [SegmentResponse(**s) for s in segments]

@router.get("/segments/{segment_id}")
async def get_segment(segment_id: str, user: AuthorizedUser):
    """Get a customer segment by ID"""
    segment = get_firestore_data("customer_segments", segment_id)
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    # Count matching customers (stub implementation)
    segment["customer_count"] = 0  # Placeholder for actual count
    
    return SegmentResponse(**segment)

@router.put("/segments/{segment_id}")
async def update_segment(segment_id: str, data: SegmentRequest, user: AuthorizedUser):
    """Update a customer segment"""
    segment = get_firestore_data("customer_segments", segment_id)
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    # Update segment data
    update_data = data.dict(exclude_unset=True)
    segment.update(update_data)
    segment["updated_at"] = datetime.now().isoformat()
    
    # Save updated data
    set_firestore_data("customer_segments", segment_id, segment)
    
    return {"success": True, "message": "Segment updated successfully"}

@router.delete("/segments/{segment_id}")
async def delete_segment(segment_id: str, user: AuthorizedUser):
    """Delete a customer segment"""
    segment = get_firestore_data("customer_segments", segment_id)
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    # Delete segment data
    db.storage.text.delete(f"firestore_customer_segments_{segment_id}")
    
    return {"success": True, "message": "Segment deleted successfully"}

# Service Tickets

@router.post("/tickets")
async def create_ticket(data: TicketRequest, user: AuthorizedUser):
    """Create a new service ticket"""
    timestamp = datetime.now().isoformat()
    ticket_id = f"ticket_{int(datetime.now().timestamp())}"
    
    # Create ticket data
    ticket = {
        "id": ticket_id,
        "user_id": user.sub,
        "subject": data.subject,
        "description": data.description,
        "status": "open",
        "priority": data.priority,
        "category": data.category,
        "order_id": data.order_id,
        "assigned_to": None,
        "created_at": timestamp,
        "updated_at": timestamp,
        "communications": [],
        "resolution": None,
        "satisfaction_rating": None
    }
    
    # Save ticket data
    set_firestore_data("service_tickets", ticket_id, ticket)
    
    # Update user's last interaction timestamp
    crm_data = get_firestore_data("crm_customer_data", user.sub, {})
    crm_data["last_interaction"] = timestamp
    
    if "created_at" not in crm_data:
        crm_data["created_at"] = timestamp
    
    crm_data["updated_at"] = timestamp
    set_firestore_data("crm_customer_data", user.sub, crm_data)
    
    return TicketResponse(**ticket)

@router.get("/tickets")
async def get_user_tickets(
    user: AuthorizedUser,
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get all tickets for the authenticated user"""
    tickets = list_firestore_collection("service_tickets")
    
    # Filter by user ID
    user_tickets = [t for t in tickets if t.get("user_id") == user.sub]
    
    # Filter by status if provided
    if status:
        user_tickets = [t for t in user_tickets if t.get("status") == status]
    
    # Sort by created_at (newest first)
    user_tickets.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    
    return [TicketResponse(**t) for t in user_tickets]

@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, user: AuthorizedUser):
    """Get a service ticket by ID"""
    ticket = get_firestore_data("service_tickets", ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if user is authorized to view this ticket
    if ticket["user_id"] != user.sub and not is_admin(user):
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")
    
    return TicketResponse(**ticket)

@router.put("/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, data: TicketUpdateRequest, user: AuthorizedUser):
    """Update a service ticket"""
    ticket = get_firestore_data("service_tickets", ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if user is authorized to update this ticket
    # Regular users can only update their own tickets
    # Admins can update any ticket
    if ticket["user_id"] != user.sub and not is_admin(user):
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")
    
    # Update ticket data
    update_data = data.dict(exclude_unset=True)
    ticket.update(update_data)
    ticket["updated_at"] = datetime.now().isoformat()
    
    # Save updated data
    set_firestore_data("service_tickets", ticket_id, ticket)
    
    return {"success": True, "message": "Ticket updated successfully"}

@router.post("/tickets/{ticket_id}/communications")
async def add_ticket_communication(ticket_id: str, data: TicketCommunicationRequest, user: AuthorizedUser):
    """Add a communication to a service ticket"""
    ticket = get_firestore_data("service_tickets", ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if user is authorized
    if ticket["user_id"] != user.sub and not is_admin(user):
        raise HTTPException(status_code=403, detail="Not authorized to add communication to this ticket")
    
    timestamp = datetime.now().isoformat()
    communication_id = f"comm_{int(datetime.now().timestamp())}"
    
    # Create new communication
    communication = {
        "id": communication_id,
        "ticket_id": ticket_id,
        "message": data.message,
        "sender_id": user.sub,
        "sender_type": data.sender_type,
        "timestamp": timestamp,
        "attachments": data.attachments
    }
    
    # Add to communications array
    if "communications" not in ticket:
        ticket["communications"] = []
    
    ticket["communications"].append(communication)
    ticket["updated_at"] = timestamp
    
    # Save updated ticket
    set_firestore_data("service_tickets", ticket_id, ticket)
    
    # Update user's last interaction timestamp if sender is customer
    if data.sender_type == "customer":
        crm_data = get_firestore_data("crm_customer_data", user.sub, {})
        crm_data["last_interaction"] = timestamp
        
        if "created_at" not in crm_data:
            crm_data["created_at"] = timestamp
        
        crm_data["updated_at"] = timestamp
        set_firestore_data("crm_customer_data", user.sub, crm_data)
    
    return TicketCommunicationResponse(**communication)

# Feedback

@router.post("/feedback")
async def create_feedback(data: FeedbackRequest, user: AuthorizedUser):
    """Create new customer feedback"""
    timestamp = datetime.now().isoformat()
    feedback_id = f"feedback_{int(datetime.now().timestamp())}"
    
    # Create feedback data
    feedback = {
        "id": feedback_id,
        "user_id": user.sub,
        "order_id": data.order_id,
        "type": data.type,
        "rating": data.rating,
        "comments": data.comments,
        "created_at": timestamp,
        "responded_to": False
    }
    
    # Save feedback data
    set_firestore_data("feedback", feedback_id, feedback)
    
    # Update user's last interaction timestamp
    crm_data = get_firestore_data("crm_customer_data", user.sub, {})
    crm_data["last_interaction"] = timestamp
    
    if "created_at" not in crm_data:
        crm_data["created_at"] = timestamp
    
    crm_data["updated_at"] = timestamp
    set_firestore_data("crm_customer_data", user.sub, crm_data)
    
    return FeedbackResponse(**feedback)

@router.get("/feedback")
async def get_user_feedback(user: AuthorizedUser):
    """Get all feedback for the authenticated user"""
    feedback_list = list_firestore_collection("feedback")
    
    # Filter by user ID
    user_feedback = [f for f in feedback_list if f.get("user_id") == user.sub]
    
    # Sort by created_at (newest first)
    user_feedback.sort(key=lambda f: f.get("created_at", ""), reverse=True)
    
    return [FeedbackResponse(**f) for f in user_feedback]

@router.get("/feedback/{feedback_id}")
async def get_feedback(feedback_id: str, user: AuthorizedUser):
    """Get feedback by ID"""
    feedback = get_firestore_data("feedback", feedback_id)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check if user is authorized to view this feedback
    if feedback["user_id"] != user.sub and not is_admin(user):
        raise HTTPException(status_code=403, detail="Not authorized to access this feedback")
    
    return FeedbackResponse(**feedback)

@router.post("/feedback/{feedback_id}/respond")
async def respond_to_feedback(feedback_id: str, data: FeedbackResponseRequest, user: AuthorizedUser):
    """Respond to customer feedback (admin only)"""
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Only administrators can respond to feedback")
    
    feedback = get_firestore_data("feedback", feedback_id)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    timestamp = datetime.now().isoformat()
    
    # Add response
    feedback["responded_to"] = True
    feedback["response"] = {
        "message": data.message,
        "staff_id": user.sub,
        "timestamp": timestamp
    }
    
    # Save updated feedback
    set_firestore_data("feedback", feedback_id, feedback)
    
    return {"success": True, "message": "Response added successfully"}

# Subscription Management

@router.post("/subscription-plans")
async def create_subscription_plan(data: SubscriptionPlanRequest, user: AuthorizedUser):
    """Create a new subscription plan (admin only)"""
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Only administrators can create subscription plans")
    
    timestamp = datetime.now().isoformat()
    plan_id = f"plan_{int(datetime.now().timestamp())}"
    
    # Create plan data
    plan = {
        "id": plan_id,
        "name": data.name,
        "description": data.description,
        "frequency": data.frequency,
        "custom_days": data.custom_days,
        "discount_percentage": data.discount_percentage,
        "active": data.active,
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    # Save plan data
    set_firestore_data("subscription_plans", plan_id, plan)
    
    return SubscriptionPlanResponse(**plan)

@router.get("/subscription-plans")
async def get_subscription_plans(
    user: AuthorizedUser,
    active_only: bool = Query(True, description="Only return active plans")
):
    """Get all subscription plans"""
    plans = list_firestore_collection("subscription_plans")
    
    # Filter by active status if requested
    if active_only:
        plans = [p for p in plans if p.get("active", True)]
    
    return [SubscriptionPlanResponse(**p) for p in plans]

@router.post("/subscriptions")
async def create_subscription(data: SubscriptionRequest, user: AuthorizedUser):
    """Create a new subscription for the authenticated user"""
    # Check if plan exists
    plan = get_firestore_data("subscription_plans", data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    # Check if plan is active
    if not plan.get("active", True):
        raise HTTPException(status_code=400, detail="Subscription plan is not active")
    
    timestamp = datetime.now().isoformat()
    subscription_id = f"sub_{int(datetime.now().timestamp())}"
    
    # Calculate next delivery date based on plan frequency
    next_delivery_date = None
    if plan["frequency"] == "weekly":
        next_delivery_date = (datetime.now() + timedelta(days=7)).isoformat()
    elif plan["frequency"] == "biweekly":
        next_delivery_date = (datetime.now() + timedelta(days=14)).isoformat()
    elif plan["frequency"] == "monthly":
        next_delivery_date = (datetime.now() + timedelta(days=30)).isoformat()
    elif plan["frequency"] == "custom" and plan.get("custom_days"):
        next_delivery_date = (datetime.now() + timedelta(days=plan["custom_days"])).isoformat()
    else:
        next_delivery_date = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Create subscription data
    subscription = {
        "id": subscription_id,
        "user_id": user.sub,
        "plan_id": data.plan_id,
        "products": [p.dict() for p in data.products],
        "shipping_address_id": data.shipping_address_id,
        "payment_method_id": data.payment_method_id,
        "status": "active",
        "next_delivery_date": next_delivery_date,
        "created_at": timestamp,
        "updated_at": timestamp,
        "payment_history": []
    }
    
    # Save subscription data
    set_firestore_data("subscriptions", subscription_id, subscription)
    
    # Update user's CRM data to indicate they have a subscription
    crm_data = get_firestore_data("crm_customer_data", user.sub, {})
    crm_data["has_subscription"] = True
    
    if "created_at" not in crm_data:
        crm_data["created_at"] = timestamp
    
    crm_data["updated_at"] = timestamp
    set_firestore_data("crm_customer_data", user.sub, crm_data)
    
    return SubscriptionResponse(**subscription)

@router.get("/subscriptions")
async def get_user_subscriptions(user: AuthorizedUser):
    """Get all subscriptions for the authenticated user"""
    subscriptions = list_firestore_collection("subscriptions")
    
    # Filter by user ID
    user_subscriptions = [s for s in subscriptions if s.get("user_id") == user.sub]
    
    # Sort by created_at (newest first)
    user_subscriptions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    
    return [SubscriptionResponse(**s) for s in user_subscriptions]

@router.get("/subscriptions/{subscription_id}")
async def get_subscription(subscription_id: str, user: AuthorizedUser):
    """Get a subscription by ID"""
    subscription = get_firestore_data("subscriptions", subscription_id)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check if user is authorized to view this subscription
    if subscription["user_id"] != user.sub and not is_admin(user):
        raise HTTPException(status_code=403, detail="Not authorized to access this subscription")
    
    return SubscriptionResponse(**subscription)

@router.put("/subscriptions/{subscription_id}")
async def update_subscription(subscription_id: str, data: SubscriptionUpdateRequest, user: AuthorizedUser):
    """Update a subscription"""
    subscription = get_firestore_data("subscriptions", subscription_id)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check if user is authorized to update this subscription
    if subscription["user_id"] != user.sub and not is_admin(user):
        raise HTTPException(status_code=403, detail="Not authorized to update this subscription")
    
    # Update subscription data
    update_data = data.dict(exclude_unset=True)
    subscription.update(update_data)
    subscription["updated_at"] = datetime.now().isoformat()
    
    # If cancelling, check if user has any other active subscriptions
    if data.status == "cancelled":
        subscriptions = list_firestore_collection("subscriptions")
        user_active_subscriptions = [
            s for s in subscriptions 
            if s.get("user_id") == subscription["user_id"] 
            and s.get("id") != subscription_id 
            and s.get("status") == "active"
        ]
        
        if not user_active_subscriptions:
            # Update user's CRM data to indicate they no longer have an active subscription
            crm_data = get_firestore_data("crm_customer_data", subscription["user_id"], {})
            crm_data["has_subscription"] = False
            crm_data["updated_at"] = datetime.now().isoformat()
            set_firestore_data("crm_customer_data", subscription["user_id"], crm_data)
    
    # Save updated data
    set_firestore_data("subscriptions", subscription_id, subscription)
    
    return {"success": True, "message": "Subscription updated successfully"}

# Loyalty Program

@router.post("/loyalty/tiers")
async def create_loyalty_tier(data: LoyaltyTierRequest, user: AuthorizedUser):
    """Create a new loyalty tier (admin only)"""
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Only administrators can create loyalty tiers")
    
    timestamp = datetime.now().isoformat()
    tier_id = f"tier_{int(datetime.now().timestamp())}"
    
    # Create tier data
    tier = {
        "id": tier_id,
        "name": data.name,
        "description": data.description,
        "point_threshold": data.point_threshold,
        "multiplier": data.multiplier,
        "benefits": data.benefits,
        "icon": data.icon,
        "color": data.color,
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    # Save tier data
    set_firestore_data("loyalty_tiers", tier_id, tier)
    
    return LoyaltyTierResponse(**tier)

@router.get("/loyalty/tiers")
async def get_loyalty_tiers(user: AuthorizedUser):
    """Get all loyalty tiers"""
    tiers = list_firestore_collection("loyalty_tiers")
    
    # Sort by point threshold (ascending)
    tiers.sort(key=lambda t: t.get("point_threshold", 0))
    
    return [LoyaltyTierResponse(**t) for t in tiers]

@router.post("/loyalty/rewards")
async def create_loyalty_reward(data: LoyaltyRewardRequest, user: AuthorizedUser):
    """Create a new loyalty reward (admin only)"""
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Only administrators can create loyalty rewards")
    
    timestamp = datetime.now().isoformat()
    reward_id = f"reward_{int(datetime.now().timestamp())}"
    
    # Create reward data
    reward = {
        "id": reward_id,
        "name": data.name,
        "description": data.description,
        "point_cost": data.point_cost,
        "reward_type": data.reward_type,
        "discount_value": data.discount_value,
        "discount_type": data.discount_type,
        "product_id": data.product_id,
        "active": data.active,
        "limited_quantity": data.limited_quantity,
        "remaining": data.limited_quantity,  # Initially set remaining to total quantity
        "expires_at": data.expires_at,
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    # Save reward data
    set_firestore_data("loyalty_rewards", reward_id, reward)
    
    return LoyaltyRewardResponse(**reward)

@router.get("/loyalty/rewards")
async def get_loyalty_rewards(
    user: AuthorizedUser,
    active_only: bool = Query(True, description="Only return active rewards")
):
    """Get all loyalty rewards"""
    rewards = list_firestore_collection("loyalty_rewards")
    
    # Filter by active status if requested
    if active_only:
        rewards = [r for r in rewards if r.get("active", True)]
    
    # Sort by point cost (ascending)
    rewards.sort(key=lambda r: r.get("point_cost", 0))
    
    return [LoyaltyRewardResponse(**r) for r in rewards]

@router.get("/loyalty/customer")
async def get_customer_loyalty(user: AuthorizedUser):
    """Get loyalty data for the authenticated user"""
    loyalty = get_firestore_data("customer_loyalty", user.sub)
    
    if not loyalty:
        # Return default empty loyalty data
        return {"message": "No loyalty account found for this user"}
    
    # Get current tier data
    tier = get_firestore_data("loyalty_tiers", loyalty["tier_id"])
    if tier:
        loyalty["current_tier"] = tier
    
    return CustomerLoyaltyResponse(**loyalty)

@router.post("/loyalty/initialize")
async def initialize_customer_loyalty(user: AuthorizedUser):
    """Initialize loyalty account for the authenticated user"""
    # Check if account already exists
    existing_loyalty = get_firestore_data("customer_loyalty", user.sub)
    if existing_loyalty:
        raise HTTPException(status_code=400, detail="Loyalty account already exists for this user")
    
    # Get the lowest tier
    tiers = list_firestore_collection("loyalty_tiers")
    if not tiers:
        raise HTTPException(status_code=404, detail="No loyalty tiers found")
    
    # Sort by point threshold (ascending)
    tiers.sort(key=lambda t: t.get("point_threshold", 0))
    lowest_tier = tiers[0]
    
    timestamp = datetime.now().isoformat()
    
    # Create loyalty data
    loyalty = {
        "user_id": user.sub,
        "points": 0,
        "tier_id": lowest_tier["id"],
        "lifetime_points": 0,
        "points_history": [],
        "rewards_redeemed": [],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    # Save loyalty data
    set_firestore_data("customer_loyalty", user.sub, loyalty)
    
    return CustomerLoyaltyResponse(**loyalty, current_tier=lowest_tier)

@router.post("/loyalty/points")
async def add_loyalty_points(data: AddLoyaltyPointsRequest, user: AuthorizedUser):
    """Add points to the authenticated user's loyalty account"""
    loyalty = get_firestore_data("customer_loyalty", user.sub)
    
    if not loyalty:
        # Initialize loyalty account first
        await initialize_customer_loyalty(user)
        loyalty = get_firestore_data("customer_loyalty", user.sub)
    
    timestamp = datetime.now().isoformat()
    
    # Add points history entry
    if "points_history" not in loyalty:
        loyalty["points_history"] = []
    
    loyalty["points_history"].append({
        "date": timestamp,
        "amount": data.points,
        "type": "earned",
        "source": data.source
    })
    
    # Update points balance and lifetime points
    loyalty["points"] = loyalty.get("points", 0) + data.points
    loyalty["lifetime_points"] = loyalty.get("lifetime_points", 0) + data.points
    loyalty["updated_at"] = timestamp
    
    # Check for tier upgrades
    tiers = list_firestore_collection("loyalty_tiers")
    tiers.sort(key=lambda t: t.get("point_threshold", 0), reverse=True)  # Sort by threshold (descending)
    
    for tier in tiers:
        if loyalty["lifetime_points"] >= tier.get("point_threshold", 0):
            loyalty["tier_id"] = tier["id"]
            break
    
    # Save updated loyalty data
    set_firestore_data("customer_loyalty", user.sub, loyalty)
    
    # Get current tier data for response
    current_tier = get_firestore_data("loyalty_tiers", loyalty["tier_id"])
    
    return CustomerLoyaltyResponse(**loyalty, current_tier=current_tier)

@router.post("/loyalty/redeem/{reward_id}")
async def redeem_loyalty_reward(reward_id: str, user: AuthorizedUser):
    """Redeem a loyalty reward"""
    # Get the reward
    reward = get_firestore_data("loyalty_rewards", reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    # Check if reward is active
    if not reward.get("active", True):
        raise HTTPException(status_code=400, detail="Reward is not active")
    
    # Check if limited quantity is available
    if reward.get("limited_quantity") is not None and reward.get("remaining", 0) <= 0:
        raise HTTPException(status_code=400, detail="Reward is out of stock")
    
    # Get customer loyalty data
    loyalty = get_firestore_data("customer_loyalty", user.sub)
    if not loyalty:
        raise HTTPException(status_code=404, detail="Loyalty account not found")
    
    # Check if customer has enough points
    if loyalty.get("points", 0) < reward.get("point_cost", 0):
        raise HTTPException(status_code=400, detail="Not enough points to redeem this reward")
    
    timestamp = datetime.now().isoformat()
    
    # Update loyalty record
    if "points_history" not in loyalty:
        loyalty["points_history"] = []
    
    loyalty["points_history"].append({
        "date": timestamp,
        "amount": -reward["point_cost"],
        "type": "redeemed",
        "source": f"Reward: {reward['name']}"
    })
    
    if "rewards_redeemed" not in loyalty:
        loyalty["rewards_redeemed"] = []
    
    loyalty["rewards_redeemed"].append({
        "reward_id": reward_id,
        "date": timestamp,
        "points_used": reward["point_cost"]
    })
    
    loyalty["points"] = loyalty.get("points", 0) - reward["point_cost"]
    loyalty["updated_at"] = timestamp
    
    # Update reward quantity if limited
    if reward.get("limited_quantity") is not None and reward.get("remaining") is not None:
        reward["remaining"] = reward["remaining"] - 1
        set_firestore_data("loyalty_rewards", reward_id, reward)
    
    # Save updated loyalty data
    set_firestore_data("customer_loyalty", user.sub, loyalty)
    
    return {
        "success": True,
        "message": f"Successfully redeemed {reward['name']}",
        "points_remaining": loyalty["points"],
        "reward": reward
    }

# Admin helpers

def is_admin(user: AuthorizedUser) -> bool:
    """Check if user is an admin"""
    # This is a placeholder implementation
    # In a real app, you would check against a list of admin users or roles
    admin_users = ["admin_user_id"]  # Replace with actual admin user IDs
    return user.sub in admin_users
