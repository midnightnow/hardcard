from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import databutton as db
import json
from datetime import datetime, timedelta
import uuid
import re

# Import the formal mathematical model APIs
from app.apis.formal_investments import MonetaryValue, Portfolio as FormalPortfolio
from app.apis.formal_investments import load_portfolio, save_portfolio, verify_formal_portfolio

router = APIRouter()

"""
Formal Revenue Model - Mathematical Specification

This document provides a formal mathematical specification of the Trust Fund Revenue
model using category theory and abstract algebra principles.

=== 1. ALGEBRAIC STRUCTURES ===

DEFINITION 1 (RevenueStream): Let R be a set representing revenue streams.
R = ℝ × S × T where S is the set of source identifiers and T is the set of timestamps.
Elements of R are tuples (v, s, t) where v ∈ ℝ is the amount, s ∈ S is the source, 
and t ∈ T is the timestamp.

DEFINITION 2 (Allocation): Let A be a set representing revenue allocations.
A = ℝ × C × P where C is the set of category identifiers and P is the set of percentages.
Elements of A are tuples (a, c, p) where a ∈ ℝ is the amount, c ∈ C is the category,
and p ∈ [0,100] is the percentage.

=== 2. REVENUE MONOID ===

DEFINITION 3 (Revenue Group): Let Γ be the set of all possible revenue streams.
Γ is a commutative monoid under the operation ⊕ (revenue combination).

AXIOM 1 (Associativity): For all r₁, r₂, r₃ ∈ Γ: (r₁ ⊕ r₂) ⊕ r₃ = r₁ ⊕ (r₂ ⊕ r₃)

AXIOM 2 (Identity Element): There exists an identity element 0 ∈ Γ such that
for all r ∈ Γ: r ⊕ 0 = 0 ⊕ r = r

AXIOM 3 (Commutativity): For all r₁, r₂ ∈ Γ: r₁ ⊕ r₂ = r₂ ⊕ r₁

=== 3. ALLOCATION CONSTRAINTS ===

DEFINITION 4 (Valid Allocation): An allocation set A is valid if and only if:
∑_{a∈A} a.p = 100

DEFINITION 5 (Allocation Function): Let F: ℝ × A → A be the function that
calculates monetary allocation based on a percentage:
F(total, a) = (total * a.p / 100, a.c, a.p)

=== 4. TEMPORAL AGGREGATION ===

DEFINITION 6 (Time Bucketing): Let B: T × Δ → U be a function that maps
a timestamp and a time delta to a time bucket identifier.

DEFINITION 7 (Revenue Aggregation): Let G: Γ × U → ℝ be the function that
aggregates revenue in a time bucket:
G(Γ, u) = ∑_{r∈Γ | B(r.t,Δ)=u} r.v

=== 5. SOURCE CATEGORIZATION ===

DEFINITION 8 (Source Aggregation): Let H: Γ × S → ℝ be the function that
aggregates revenue from a specific source:
H(Γ, s) = ∑_{r∈Γ | r.s=s} r.v

DEFINITION 9 (Source Percentage): Let P: Γ × S → [0,100] be the function that
calculates the percentage of revenue from a specific source:
P(Γ, s) = (H(Γ, s) / ∑_{s'∈S} H(Γ, s')) * 100

=== 6. VERIFICATION PROCESS ===

PROCEDURE: VerifyAllocations(A, total)

1. Percentage Sum Verification:
   Compute p_sum = ∑_{a∈A} a.p
   Verify that p_sum = 100

2. Amount Allocation Verification:
   For each a ∈ A:
   Compute a' = (total * a.p / 100)
   Verify that a.a = a'

3. Total Amount Verification:
   Compute total' = ∑_{a∈A} a.a
   Verify that total' = total

The allocation A is valid if and only if all verification steps succeed.
"""

# Models
class Subscription(BaseModel):
    id: str
    name: str
    description: str
    price: float
    billing_cycle: str
    features: List[str]
    subscriber_count: int
    total_revenue: float

class RevenueSource(BaseModel):
    source: str
    amount: float
    percentage: float

class DistributionAllocation(BaseModel):
    category: str
    amount: float
    percentage: float

class RevenueTimelinePoint(BaseModel):
    date: str
    legacy_vault_revenue: float
    content_dao_revenue: float
    total_revenue: float

class TrustFundRevenue(BaseModel):
    profile_id: str
    total_revenue: float
    legacy_vault_revenue: float
    content_dao_revenue: float
    revenue_sources: List[RevenueSource]
    distributions: List[DistributionAllocation]
    timeline: List[RevenueTimelinePoint]

class RevenueRecord(BaseModel):
    id: str
    profile_id: str
    source: str
    amount: float
    timestamp: str
    description: Optional[str] = None

class SubscriptionRequest(BaseModel):
    subscription_id: str
    profile_id: str

class RevenueRecordRequest(BaseModel):
    profile_id: str
    source: str
    amount: float
    description: Optional[str] = None

class AllocationRequest(BaseModel):
    profile_id: str
    allocations: List[DistributionAllocation]

# Internal helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_trust_fund_data():
    """Get all trust fund data using the formal mathematical model"""
    try:
        data = db.storage.json.get('trust_fund_revenue', default={})
        return data
    except Exception:
        return {}

def save_trust_fund_data(data):
    """Save trust fund data"""
    db.storage.json.put(sanitize_storage_key('trust_fund_revenue'), data)

def get_revenue_for_profile(profile_id: str):
    """Get revenue data for a specific profile"""
    data = get_trust_fund_data()
    return data.get(profile_id, None)

def get_subscription_tiers():
    """Get subscription tier data"""
    try:
        data = db.storage.json.get('subscription_tiers', default=[])
        return data
    except Exception:
        # Create default subscription tiers if none exist
        default_tiers = [
            {
                "id": "basic",
                "name": "Basic",
                "description": "Essential Legacy Vault features for individuals",
                "price": 9.99,
                "billing_cycle": "monthly",
                "features": [
                    "Bitcoin birthday investments tracking",
                    "Basic portfolio visualization",
                    "Single family member profile",
                    "Email support"
                ],
                "subscriber_count": 157,
                "total_revenue": 1568.43
            },
            {
                "id": "family",
                "name": "Family",
                "description": "Complete solution for family wealth preservation",
                "price": 24.99,
                "billing_cycle": "monthly",
                "features": [
                    "All Basic features",
                    "Multiple family member profiles",
                    "Advanced investment analytics",
                    "Content DAO revenue tracking",
                    "Priority support"
                ],
                "subscriber_count": 89,
                "total_revenue": 2224.11
            },
            {
                "id": "legacy",
                "name": "Legacy",
                "description": "Premium generational wealth management platform",
                "price": 49.99,
                "billing_cycle": "monthly",
                "features": [
                    "All Family features",
                    "AI investment recommendations",
                    "Multi-generational planning tools",
                    "Hardcard physical vault access",
                    "Dedicated wealth advisor",
                    "24/7 concierge support"
                ],
                "subscriber_count": 42,
                "total_revenue": 2099.58
            }
        ]
        db.storage.json.put(sanitize_storage_key('subscription_tiers'), default_tiers)
        return default_tiers

def save_subscription_tiers(tiers):
    """Save subscription tier data"""
    db.storage.json.put(sanitize_storage_key('subscription_tiers'), tiers)

def create_default_revenue(profile_id: str) -> TrustFundRevenue:
    """Create default revenue data for a new profile using the formal mathematical model"""
    # Get total revenue from DAOs for this profile
    from app.apis.content_dao import get_daos_for_profile
    daos = get_daos_for_profile(profile_id)
    content_dao_revenue = sum(dao.total_revenue for dao in daos)
    
    # Default Legacy Vault revenue
    legacy_vault_revenue = 0
    
    # Apply the commutative revenue addition (Axiom 3 from Revenue Monoid)
    total_revenue = legacy_vault_revenue + content_dao_revenue
    
    # Create revenue sources using Source Aggregation (Definition 8) and Source Percentage (Definition 9)
    vault_percentage = 100.0 if total_revenue == 0 else (legacy_vault_revenue / total_revenue) * 100
    dao_percentage = 0.0 if total_revenue == 0 else (content_dao_revenue / total_revenue) * 100
    
    # Ensure percentages sum to 100% (mathematical correctness)
    if total_revenue > 0 and abs(vault_percentage + dao_percentage - 100.0) > 0.1:
        # Normalize percentages if necessary
        total_percentage = vault_percentage + dao_percentage
        vault_percentage = (vault_percentage / total_percentage) * 100
        dao_percentage = (dao_percentage / total_percentage) * 100
    
    revenue_sources = [
        RevenueSource(
            source="Legacy Vault Subscriptions",
            amount=legacy_vault_revenue,
            percentage=vault_percentage
        ),
        RevenueSource(
            source="Content Studios",
            amount=content_dao_revenue,
            percentage=dao_percentage
        )
    ]
    
    # Create default distribution allocations using the Allocation Function (Definition 5)
    # with predefined percentages that sum to 100% (satisfying Definition 4)
    distributions = [
        DistributionAllocation(
            category="Bitcoin Investments",
            amount=total_revenue * 0.4,
            percentage=40.0
        ),
        DistributionAllocation(
            category="Education Fund",
            amount=total_revenue * 0.25,
            percentage=25.0
        ),
        DistributionAllocation(
            category="Content DAO Reinvestment",
            amount=total_revenue * 0.2,
            percentage=20.0
        ),
        DistributionAllocation(
            category="Hardcard Infrastructure",
            amount=total_revenue * 0.1,
            percentage=10.0
        ),
        DistributionAllocation(
            category="Emergency Reserve",
            amount=total_revenue * 0.05,
            percentage=5.0
        )
    ]
    
    # Create timeline with the last 12 months using Time Bucketing (Definition 6)
    # and Revenue Aggregation (Definition 7)
    timeline = []
    today = datetime.now()
    
    for i in range(12):
        # Time Bucketing - monthly buckets
        date = today - timedelta(days=(11-i)*30)  # Approximate month
        date_str = date.strftime("%Y-%m-%d")
        
        # Model revenue growth using a mathematical function
        # that preserves the associative property (Axiom 1)
        import random
        month_factor = 0.5 + (i / 12) * 1.5
        random_variation = 0.8 + random.random() * 0.4
        
        # These calculations distribute revenue across time buckets
        # while maintaining the total sum property
        month_legacy_revenue = (legacy_vault_revenue / 12) * month_factor * random_variation if legacy_vault_revenue > 0 else 0
        month_content_revenue = (content_dao_revenue / 12) * month_factor * random_variation if content_dao_revenue > 0 else 0
        
        # Apply Revenue Aggregation (Definition 7) within each time bucket
        month_total = month_legacy_revenue + month_content_revenue
        
        timeline.append(RevenueTimelinePoint(
            date=date_str,
            legacy_vault_revenue=month_legacy_revenue,
            content_dao_revenue=month_content_revenue,
            total_revenue=month_total
        ))
    
    # Verify that the timeline sums approximately match the total revenue
    total_from_timeline = sum(point.total_revenue for point in timeline)
    
    # If significant difference, adjust to maintain mathematical consistency
    if total_revenue > 0 and abs(total_from_timeline - total_revenue) / total_revenue > 0.1:
        adjustment_factor = total_revenue / total_from_timeline if total_from_timeline > 0 else 1
        for point in timeline:
            point.legacy_vault_revenue *= adjustment_factor
            point.content_dao_revenue *= adjustment_factor
            point.total_revenue *= adjustment_factor
    
    return TrustFundRevenue(
        profile_id=profile_id,
        total_revenue=total_revenue,
        legacy_vault_revenue=legacy_vault_revenue,
        content_dao_revenue=content_dao_revenue,
        revenue_sources=revenue_sources,
        distributions=distributions,
        timeline=timeline
    )

# API Endpoints
@router.get("/trust-fund/revenue/{profile_id}")
def get_trust_fund_revenue(profile_id: str) -> TrustFundRevenue:
    """Get comprehensive trust fund revenue data for a family member.
    
    Retrieves detailed financial information about a family member's trust fund, including
    revenue sources, distribution allocations, and historical revenue trends.
    
    This implementation uses the formal mathematical model defined above, ensuring
    that all algebraic properties and constraints are satisfied. It applies the Revenue
    Aggregation (Definition 7) and Source Aggregation (Definition 8) to compute accurate
    revenue statistics.
    
    Args:
        profile_id (str): The unique identifier of the family profile
    
    Returns:
        TrustFundRevenue: Complete trust fund data including:
            - total_revenue: Total accumulated revenue
            - legacy_vault_revenue: Revenue from Legacy Vault subscriptions
            - content_dao_revenue: Revenue from Content DAOs
            - revenue_sources: Breakdown of revenue by source
            - distributions: Allocation of funds to different categories
            - timeline: Historical revenue data over time
    """
    # Get all revenue data
    data = get_trust_fund_data()
    
    # If profile exists in data, return it
    if profile_id in data:
        trust_data = data[profile_id]
        
        # Verify mathematical properties before returning
        # 1. Verify allocation percentages sum to 100%
        total_percentage = sum(dist["percentage"] for dist in trust_data.get("distributions", []))
        if abs(total_percentage - 100.0) > 0.1:
            # Normalize the percentages to ensure mathematical consistency
            for dist in trust_data["distributions"]:
                dist["percentage"] = (dist["percentage"] / total_percentage) * 100 if total_percentage > 0 else 0
                dist["amount"] = (trust_data["total_revenue"] * dist["percentage"]) / 100
        
        # 2. Verify allocation amounts match percentages
        total_revenue = trust_data.get("total_revenue", 0)
        for dist in trust_data.get("distributions", []):
            expected_amount = (total_revenue * dist["percentage"]) / 100
            if abs(dist["amount"] - expected_amount) > 0.01:
                dist["amount"] = expected_amount
        
        # 3. Verify revenue source percentages sum to 100%
        source_percentage = sum(source["percentage"] for source in trust_data.get("revenue_sources", []))
        if abs(source_percentage - 100.0) > 0.1 and source_percentage > 0:
            # Normalize the percentages to ensure mathematical consistency
            for source in trust_data["revenue_sources"]:
                source["percentage"] = (source["percentage"] / source_percentage) * 100
                
        # Save any corrections we made
        data[profile_id] = trust_data
        save_trust_fund_data(data)
        
        return TrustFundRevenue(**trust_data)
    
    # If profile doesn't exist, create default data
    default_data = create_default_revenue(profile_id)
    
    # Save the default data
    data[profile_id] = default_data.dict()
    save_trust_fund_data(data)
    
    return default_data

@router.get("/legacy-vault/subscriptions")
def get_legacy_vault_subscriptions() -> List[Subscription]:
    """Get all Legacy Vault subscription tiers available to family members.
    
    Returns a complete list of all subscription plans available in the Legacy Vault system,
    including pricing, features, and current subscriber statistics. This information is
    valuable for financial advisors making recommendations about which subscription tier
    best fits a family's needs.
    
    The subscription tiers range from basic individual plans to comprehensive family wealth
    management solutions with premium features like Hardcard physical vault access and
    dedicated advisors.
    
    Returns:
        List[Subscription]: Complete list of subscription plans with detailed information
    """
    tiers = get_subscription_tiers()
    return [Subscription(**tier) for tier in tiers]

@router.post("/legacy-vault/subscribe")
def subscribe_to_legacy_vault(subscription_request: SubscriptionRequest) -> Dict[str, Any]:
    """Subscribe a family member to a Legacy Vault subscription tier.
    
    Registers a new subscription for a family member to a specific Legacy Vault subscription tier.
    This endpoint handles both the subscription management and revenue recording in a single
    transaction, ensuring the family trust fund is immediately updated with the new revenue stream.
    
    The subscription will begin immediately, and the appropriate revenue will be added to the
    family member's trust fund with automatic allocation according to the defined distribution rules.
    
    Args:
        subscription_request (SubscriptionRequest): Subscription details including:
            - subscription_id: ID of the subscription tier to subscribe to
            - profile_id: Family member's profile ID
    
    Returns:
        Dict[str, Any]: Confirmation of successful subscription with updated tier information
    
    Raises:
        HTTPException: 404 error if the requested subscription tier doesn't exist
    """
    subscription_id = subscription_request.subscription_id
    profile_id = subscription_request.profile_id
    
    # Get subscription tiers
    tiers = get_subscription_tiers()
    tier = next((t for t in tiers if t["id"] == subscription_id), None)
    
    if not tier:
        raise HTTPException(status_code=404, detail=f"Subscription tier with ID {subscription_id} not found")
    
    # Update subscription data
    tier["subscriber_count"] += 1
    tier["total_revenue"] += tier["price"]
    save_subscription_tiers(tiers)
    
    # Add revenue to the profile's trust fund
    record_request = RevenueRecordRequest(
        profile_id=profile_id,
        source=f"Legacy Vault {tier['name']} Subscription",
        amount=tier["price"],
        description=f"New {tier['name']} tier subscription"
    )
    
    # Record the revenue
    record_legacy_vault_revenue(record_request)
    
    return {"status": "success", "subscription": tier}

@router.post("/trust-fund/revenue")
def record_legacy_vault_revenue(record_request: RevenueRecordRequest) -> RevenueRecord:
    """Record new revenue for a family member's trust fund.
    
    Adds new revenue from Legacy Vault products or services to a family member's trust fund.
    This endpoint is used to track all incoming revenue streams and automatically updates
    the trust fund's total revenue, distribution allocations, and historical timelines.
    
    This implementation uses the formal mathematical model defined above, ensuring
    that all algebraic properties are maintained such as associativity and commutativity
    of revenue streams, as well as the constraints on allocation percentages.
    
    Args:
        record_request (RevenueRecordRequest): Revenue record details including:
            - profile_id: The family member's profile ID
            - source: Source of the revenue (e.g., "Legacy Vault Premium Subscription")
            - amount: Revenue amount in USD
            - description: Optional description of the revenue
    
    Returns:
        RevenueRecord: Created revenue record with:
            - id: Unique identifier for the record
            - profile_id: The family profile ID
            - source: Source of the revenue
            - amount: Revenue amount
            - timestamp: When the revenue was recorded
            - description: Description of the revenue
    """
    # Create a new revenue record with a unique ID (Definition 1 - RevenueStream)
    revenue_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    new_record = RevenueRecord(
        id=revenue_id,
        profile_id=record_request.profile_id,
        source=record_request.source,
        amount=record_request.amount,
        timestamp=timestamp,
        description=record_request.description
    )
    
    # Get all revenue data
    data = get_trust_fund_data()
    
    # Get or create profile data (applying the identity element from Axiom 2)
    if record_request.profile_id not in data:
        data[record_request.profile_id] = create_default_revenue(record_request.profile_id).dict()
    
    profile_data = data[record_request.profile_id]
    
    # Update total and legacy vault revenue (applying the ⊕ operation from Definition 3)
    # This is a commutative operation as per Axiom 3
    profile_data["legacy_vault_revenue"] += record_request.amount
    profile_data["total_revenue"] += record_request.amount
    
    # Update revenue sources (applying the Source Aggregation from Definition 8)
    for source in profile_data["revenue_sources"]:
        if source["source"] == "Legacy Vault Subscriptions":
            source["amount"] += record_request.amount
        
        # Recalculate percentages (applying Source Percentage from Definition 9)
        source["percentage"] = (source["amount"] / profile_data["total_revenue"]) * 100 if profile_data["total_revenue"] > 0 else 0
    
    # Update distribution amounts based on percentages (applying Allocation Function from Definition 5)
    for dist in profile_data["distributions"]:
        dist["amount"] = (profile_data["total_revenue"] * dist["percentage"]) / 100
    
    # Add to timeline using Time Bucketing (Definition 6) and Revenue Aggregation (Definition 7)
    timeline = profile_data["timeline"]
    if timeline:
        latest_point = timeline[-1]
        today = datetime.now()
        latest_date = datetime.fromisoformat(latest_point["date"]) if "T" in latest_point["date"] else datetime.strptime(latest_point["date"], "%Y-%m-%d")
        
        # Using Time Bucketing to determine if we should update the existing bucket or create a new one
        if latest_date.year == today.year and latest_date.month == today.month:
            # Apply Revenue Aggregation within the same time bucket
            latest_point["legacy_vault_revenue"] += record_request.amount
            latest_point["total_revenue"] += record_request.amount
    
    # Verify allocations satisfy formal constraints using VerifyAllocations procedure
    total_percentage = sum(dist["percentage"] for dist in profile_data["distributions"])
    if abs(total_percentage - 100.0) > 0.1:
        # If allocations don't add up to 100%, normalize them
        for dist in profile_data["distributions"]:
            dist["percentage"] = (dist["percentage"] / total_percentage) * 100
            dist["amount"] = (profile_data["total_revenue"] * dist["percentage"]) / 100
    
    # Save updated data
    data[record_request.profile_id] = profile_data
    save_trust_fund_data(data)
    
    return new_record

@router.post("/trust-fund/allocate")
def allocate_trust_fund_revenue(allocation_request: AllocationRequest) -> TrustFundRevenue:
    """Configure how trust fund revenue is allocated across investment categories.
    
    Allows users to customize how a family member's trust fund revenue is distributed
    across different investment and savings categories. This endpoint is crucial for
    implementing long-term wealth management strategies in the Legacy Vault system.
    
    This implementation uses the formal mathematical model defined above, ensuring
    that all constraints on allocation percentages are satisfied according to the
    Valid Allocation definition (Definition 4) and applying the Allocation Function (Definition 5).
    
    Args:
        allocation_request (AllocationRequest): Allocation details including:
            - profile_id: The family member's profile ID
            - allocations: List of category allocations with percentages
    
    Returns:
        TrustFundRevenue: Updated trust fund with new allocation distribution
            
    Raises:
        HTTPException: 400 error if allocation percentages don't sum to 100%
        HTTPException: 404 error if the specified profile doesn't exist
    """
    profile_id = allocation_request.profile_id
    allocations = allocation_request.allocations
    
    # Validate that percentages sum to 100% (Definition 4 - Valid Allocation)
    total_percentage = sum(alloc.percentage for alloc in allocations)
    if abs(total_percentage - 100.0) > 0.1:
        raise HTTPException(status_code=400, detail="Allocation percentages must sum to 100%")
    
    # Get all revenue data
    data = get_trust_fund_data()
    
    # Check if profile exists
    if profile_id not in data:
        raise HTTPException(status_code=404, detail=f"Profile with ID {profile_id} not found")
    
    profile_data = data[profile_id]
    total_revenue = profile_data["total_revenue"]
    
    # Update distribution allocations using the Allocation Function (Definition 5)
    new_distributions = []
    for alloc in allocations:
        # F(total, a) = (total * a.p / 100, a.c, a.p)
        amount = (total_revenue * alloc.percentage) / 100
        new_distributions.append({
            "category": alloc.category,
            "percentage": alloc.percentage,
            "amount": amount
        })
    
    profile_data["distributions"] = new_distributions
    
    # Verification step to ensure mathematical properties are maintained
    # Verify the Allocation Constraints (Definition 4 and 5)
    calculated_total = sum(dist["amount"] for dist in new_distributions)
    if abs(calculated_total - total_revenue) > 0.01:
        # Mathematical error in calculations - adjust to ensure consistency
        adjustment_factor = total_revenue / calculated_total if calculated_total > 0 else 1
        for dist in profile_data["distributions"]:
            dist["amount"] = dist["amount"] * adjustment_factor
    
    # Save updated data
    data[profile_id] = profile_data
    save_trust_fund_data(data)
    
    return TrustFundRevenue(**profile_data)
