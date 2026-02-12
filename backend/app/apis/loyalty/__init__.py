from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
import databutton as db
import firebase_admin
from firebase_admin import firestore
from datetime import datetime
import re
from app.auth import AuthorizedUser

router = APIRouter()

# Initialize Firestore DB
db_firestore = firestore.client()

# Collection constants
COLLECTIONS = {
    "LOYALTY": "loyalty",
    "REWARDS": "loyalty_rewards",
    "TIERS": "loyalty_tiers",
    "ORDERS": "orders"
}

# Define tier levels and point thresholds
DEFAULT_TIERS = [
    {
        "id": "bronze",
        "name": "Bronze",
        "min_points": 0,
        "max_points": 499,
        "point_multiplier": 1.0,
        "benefits": [
            "Base reward points",
            "Access to standard rewards"
        ]
    },
    {
        "id": "silver",
        "name": "Silver",
        "min_points": 500,
        "max_points": 1499,
        "point_multiplier": 1.25,
        "benefits": [
            "25% bonus reward points",
            "Free shipping on orders over $50",
            "Early access to new products"
        ]
    },
    {
        "id": "gold",
        "name": "Gold",
        "min_points": 1500,
        "max_points": 999999,
        "point_multiplier": 1.5,
        "benefits": [
            "50% bonus reward points",
            "Free shipping on all orders",
            "VIP customer support",
            "Exclusive gold member events",
            "Access to limited edition products"
        ]
    }
]

# Default rewards
DEFAULT_REWARDS = [
    {
        "id": "discount_10",
        "name": "10% Discount",
        "description": "Get 10% off your next order",
        "points_required": 100,
        "reward_type": "discount",
        "value": 10,
        "expires_days": 60,
        "tiers": ["bronze", "silver", "gold"]
    },
    {
        "id": "discount_15",
        "name": "15% Discount",
        "description": "Get 15% off your next order",
        "points_required": 200,
        "reward_type": "discount",
        "value": 15,
        "expires_days": 60,
        "tiers": ["bronze", "silver", "gold"]
    },
    {
        "id": "discount_20",
        "name": "20% Discount",
        "description": "Get 20% off your next order",
        "points_required": 300,
        "reward_type": "discount",
        "value": 20,
        "expires_days": 60,
        "tiers": ["silver", "gold"]
    },
    {
        "id": "free_shipping",
        "name": "Free Shipping",
        "description": "Free shipping on your next order",
        "points_required": 150,
        "reward_type": "free_shipping",
        "value": 0,
        "expires_days": 60,
        "tiers": ["bronze", "silver", "gold"]
    },
    {
        "id": "free_product",
        "name": "Free CBD Sample Pack",
        "description": "Get a free CBD sample pack with your next order",
        "points_required": 400,
        "reward_type": "free_product",
        "value": 0,
        "product_id": "sample-pack",
        "expires_days": 60,
        "tiers": ["silver", "gold"]
    },
    {
        "id": "exclusive_access",
        "name": "Early Access Pass",
        "description": "Get early access to new product launches for 30 days",
        "points_required": 750,
        "reward_type": "exclusive_access",
        "value": 0,
        "expires_days": 30,
        "tiers": ["gold"]
    }
]


class LoyaltyPointTransaction(BaseModel):
    """Record of a loyalty point transaction"""
    type: str = Field(..., description="Type of transaction (earn, redeem, expire, adjust)")
    points: int = Field(..., description="Number of points (positive for earn, negative for redeem/expire)")
    source: str = Field(..., description="Source of the transaction (order, reward, admin, system)")
    source_id: Optional[str] = Field(None, description="ID of the source (order ID, reward ID, etc.)")
    description: str = Field(..., description="Description of the transaction")
    timestamp: str = Field(..., description="ISO datetime of the transaction")


class CustomerLoyalty(BaseModel):
    """Customer loyalty program data"""
    customer_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    current_points: int = 0
    lifetime_points: int = 0
    tier_id: str = "bronze"
    tier_name: str = "Bronze"
    joined_date: str  # ISO datetime
    last_activity: str  # ISO datetime
    transactions: List[LoyaltyPointTransaction] = []
    active_rewards: List[Dict[str, Any]] = []


class LoyaltyTier(BaseModel):
    """Loyalty tier definition"""
    id: str
    name: str
    min_points: int
    max_points: int
    point_multiplier: float = 1.0
    benefits: List[str] = []


class LoyaltyReward(BaseModel):
    """Loyalty reward definition"""
    id: str
    name: str
    description: str
    points_required: int
    reward_type: str  # discount, free_shipping, free_product, exclusive_access
    value: int = 0  # Value depends on reward_type (e.g., discount percentage)
    product_id: Optional[str] = None  # For free_product rewards
    expires_days: int = 60  # Days until the reward expires after redemption
    tiers: List[str] = ["bronze", "silver", "gold"]  # Which tiers can access this reward
    active: bool = True


class RedeemRewardRequest(BaseModel):
    """Request to redeem a reward"""
    reward_id: str


class AddPointsRequest(BaseModel):
    """Request to add points to a customer's account"""
    points: int
    source: str = "admin"
    source_id: Optional[str] = None
    description: str = "Manual adjustment"


class LoyaltyResponse(BaseModel):
    """Response for loyalty operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/tiers", response_model=LoyaltyResponse)
def get_all_loyalty_tiers():
    """Get all loyalty tiers"""
    try:
        # Check if tiers exist in Firestore
        tiers_ref = db_firestore.collection(COLLECTIONS["TIERS"])
        tiers = list(tiers_ref.get())

        # If tiers don't exist, initialize with defaults
        if not tiers:
            initialize_tiers()
            tiers = list(tiers_ref.get())

        # Convert to list of dictionaries
        tier_data = [doc.to_dict() for doc in tiers]
        tier_data.sort(key=lambda x: x["min_points"])

        return LoyaltyResponse(
            success=True,
            message=f"Retrieved {len(tier_data)} loyalty tiers",
            data={"tiers": tier_data}
        )
    except Exception as e:
        print(f"Error retrieving loyalty tiers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve loyalty tiers: {str(e)}"
        )


@router.post("/tiers", response_model=LoyaltyResponse)
def create_new_loyalty_tier(tier: LoyaltyTier):
    """Create a new loyalty tier"""
    try:
        # Check if tier with this ID already exists
        tier_ref = db_firestore.collection(COLLECTIONS["TIERS"]).document(tier.id)
        if tier_ref.get().exists:
            raise HTTPException(
                status_code=400,
                detail=f"Tier with ID {tier.id} already exists"
            )

        # Create the tier
        tier_data = tier.dict()
        tier_ref.set(tier_data)

        return LoyaltyResponse(
            success=True,
            message=f"Loyalty tier {tier.name} created successfully",
            data={"tier": tier_data}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating loyalty tier: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create loyalty tier: {str(e)}"
        )


@router.get("/rewards", response_model=LoyaltyResponse)
def get_loyalty_rewards2():
    """Get all loyalty rewards"""
    try:
        # Check if rewards exist in Firestore
        rewards_ref = db_firestore.collection(COLLECTIONS["REWARDS"])
        rewards = list(rewards_ref.get())

        # If rewards don't exist, initialize with defaults
        if not rewards:
            initialize_rewards()
            rewards = list(rewards_ref.get())

        # Convert to list of dictionaries
        reward_data = [doc.to_dict() for doc in rewards]

        return LoyaltyResponse(
            success=True,
            message=f"Retrieved {len(reward_data)} loyalty rewards",
            data={"rewards": reward_data}
        )
    except Exception as e:
        print(f"Error retrieving loyalty rewards: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve loyalty rewards: {str(e)}"
        )


@router.post("/rewards", response_model=LoyaltyResponse)
def create_loyalty_reward2(reward: LoyaltyReward):
    """Create a new loyalty reward"""
    try:
        # Validate reward ID (avoid duplicates)
        reward_ref = db_firestore.collection(COLLECTIONS["REWARDS"]).document(reward.id)
        if reward_ref.get().exists:
            raise HTTPException(
                status_code=400,
                detail=f"Reward with ID {reward.id} already exists"
            )

        # Create the reward
        reward_data = reward.dict()
        reward_ref.set(reward_data)

        return LoyaltyResponse(
            success=True,
            message=f"Loyalty reward {reward.name} created successfully",
            data={"reward": reward_data}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating loyalty reward: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create loyalty reward: {str(e)}"
        )


@router.get("/customer/{customer_id}", response_model=LoyaltyResponse)
def get_customer_loyalty2(customer_id: str):
    """Get a customer's loyalty program data"""
    try:
        # Check if customer exists in loyalty program
        loyalty_ref = db_firestore.collection(COLLECTIONS["LOYALTY"]).document(customer_id)
        loyalty_doc = loyalty_ref.get()

        if not loyalty_doc.exists:
            return LoyaltyResponse(
                success=False,
                message=f"Customer {customer_id} is not enrolled in the loyalty program",
                data={"is_enrolled": False}
            )

        # Get customer loyalty data
        loyalty_data = loyalty_doc.to_dict()

        # Get customer's current tier
        tier_ref = db_firestore.collection(COLLECTIONS["TIERS"]).document(loyalty_data["tier_id"])
        tier_doc = tier_ref.get()
        tier_data = tier_doc.to_dict() if tier_doc.exists else None

        # Add tier details to response
        loyalty_data["tier_details"] = tier_data

        # Get available rewards based on tier and points
        rewards = get_available_rewards_for_customer(loyalty_data)
        loyalty_data["available_rewards"] = rewards

        return LoyaltyResponse(
            success=True,
            message=f"Retrieved loyalty data for customer {customer_id}",
            data={"loyalty": loyalty_data, "is_enrolled": True}
        )
    except Exception as e:
        print(f"Error retrieving customer loyalty data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve customer loyalty data: {str(e)}"
        )


@router.post("/customer/{customer_id}/initialize", response_model=LoyaltyResponse)
def initialize_customer_loyalty2(customer_id: str, user: AuthorizedUser):
    """Initialize a customer in the loyalty program"""
    try:
        # Check if customer already exists in loyalty program
        loyalty_ref = db_firestore.collection(COLLECTIONS["LOYALTY"]).document(customer_id)
        if loyalty_ref.get().exists:
            return LoyaltyResponse(
                success=False,
                message=f"Customer {customer_id} is already enrolled in the loyalty program",
                data={"is_enrolled": True}
            )

        # Get user data from Firestore
        user_ref = db_firestore.collection("users").document(customer_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {customer_id} not found"
            )

        user_data = user_doc.to_dict()
        now = datetime.utcnow().isoformat()

        # Create initial loyalty profile with bronze tier
        loyalty_data = {
            "customer_id": customer_id,
            "display_name": user_data.get("display_name", "Customer"),
            "email": user_data.get("email", ""),
            "current_points": 0,
            "lifetime_points": 0,
            "tier_id": "bronze",
            "tier_name": "Bronze",
            "joined_date": now,
            "last_activity": now,
            "transactions": [
                {
                    "type": "system",
                    "points": 0,
                    "source": "enrollment",
                    "source_id": None,
                    "description": "Loyalty program enrollment",
                    "timestamp": now
                }
            ],
            "active_rewards": []
        }

        # Save to Firestore
        loyalty_ref.set(loyalty_data)

        # Send welcome email
        try:
            send_loyalty_email(
                customer_id=customer_id,
                email=user_data.get("email", ""),
                template_type="loyalty_welcome",
                data={
                    "customer_name": user_data.get("display_name", "Customer"),
                    "tier_name": "Bronze"
                }
            )
        except Exception as email_error:
            print(f"Error sending welcome email: {str(email_error)}")
            # Continue processing - email failure shouldn't block enrollment

        return LoyaltyResponse(
            success=True,
            message=f"Customer {customer_id} enrolled in loyalty program",
            data={"loyalty": loyalty_data}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error initializing customer loyalty: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize customer loyalty: {str(e)}"
        )


@router.post("/customer/{customer_id}/points", response_model=LoyaltyResponse)
def add_loyalty_points2(customer_id: str, request: AddPointsRequest):
    """Add points to a customer's loyalty account"""
    try:
        # Check if customer exists in loyalty program
        loyalty_ref = db_firestore.collection(COLLECTIONS["LOYALTY"]).document(customer_id)
        loyalty_doc = loyalty_ref.get()

        if not loyalty_doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} is not enrolled in the loyalty program"
            )

        loyalty_data = loyalty_doc.to_dict()
        now = datetime.utcnow().isoformat()

        # Add transaction
        transaction = {
            "type": "earn",
            "points": request.points,
            "source": request.source,
            "source_id": request.source_id,
            "description": request.description,
            "timestamp": now
        }

        # Update points
        current_points = loyalty_data["current_points"] + request.points
        lifetime_points = loyalty_data["lifetime_points"] + max(0, request.points)  # Only positive values affect lifetime points

        # Update loyalty data
        updates = {
            "current_points": current_points,
            "lifetime_points": lifetime_points,
            "last_activity": now,
            "transactions": firestore.ArrayUnion([transaction])
        }

        # Check if tier needs to be upgraded
        current_tier_id = loyalty_data["tier_id"]
        new_tier = get_tier_for_points(lifetime_points)

        if new_tier and new_tier["id"] != current_tier_id:
            updates["tier_id"] = new_tier["id"]
            updates["tier_name"] = new_tier["name"]

            # Add tier change transaction
            tier_transaction = {
                "type": "system",
                "points": 0,
                "source": "tier_change",
                "source_id": new_tier["id"],
                "description": f"Upgraded to {new_tier['name']} tier",
                "timestamp": now
            }
            updates["transactions"] = firestore.ArrayUnion([transaction, tier_transaction])

            # Send tier upgrade email
            try:
                send_loyalty_email(
                    customer_id=customer_id,
                    email=loyalty_data.get("email", ""),
                    template_type="tier_upgrade",
                    data={
                        "customer_name": loyalty_data.get("display_name", "Customer"),
                        "new_tier": new_tier["name"],
                        "benefits": new_tier["benefits"]
                    }
                )
            except Exception as email_error:
                print(f"Error sending tier upgrade email: {str(email_error)}")
                # Continue processing - email failure shouldn't block points addition

        # Apply updates
        loyalty_ref.update(updates)

        # Get updated loyalty data
        updated_loyalty = loyalty_ref.get().to_dict()

        # Send points earned email for all point earnings
        if request.points > 0:
            try:
                send_loyalty_email(
                    customer_id=customer_id,
                    email=loyalty_data.get("email", ""),
                    template_type="points_earned",
                    data={
                        "customer_name": loyalty_data.get("display_name", "Customer"),
                        "points_earned": request.points,
                        "current_points": current_points,
                        "tier_name": updated_loyalty["tier_name"]
                    }
                )
            except Exception as email_error:
                print(f"Error sending points earned email: {str(email_error)}")
                # Continue processing - email failure shouldn't block points addition

        return LoyaltyResponse(
            success=True,
            message=f"Added {request.points} points to customer {customer_id}",
            data={
                "loyalty": updated_loyalty,
                "tier_changed": new_tier is not None and new_tier["id"] != current_tier_id
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding loyalty points: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add loyalty points: {str(e)}"
        )


@router.post("/customer/{customer_id}/redeem", response_model=LoyaltyResponse)
def redeem_loyalty_reward2(customer_id: str, request: RedeemRewardRequest):
    """Redeem a loyalty reward"""
    try:
        # Check if customer exists in loyalty program
        loyalty_ref = db_firestore.collection(COLLECTIONS["LOYALTY"]).document(customer_id)
        loyalty_doc = loyalty_ref.get()

        if not loyalty_doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} is not enrolled in the loyalty program"
            )

        # Get reward details
        reward_ref = db_firestore.collection(COLLECTIONS["REWARDS"]).document(request.reward_id)
        reward_doc = reward_ref.get()

        if not reward_doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Reward with ID {request.reward_id} not found"
            )

        loyalty_data = loyalty_doc.to_dict()
        reward_data = reward_doc.to_dict()

        # Check if customer has enough points
        if loyalty_data["current_points"] < reward_data["points_required"]:
            raise HTTPException(
                status_code=400,
                detail=f"Customer does not have enough points to redeem this reward. Required: {reward_data['points_required']}, Available: {loyalty_data['current_points']}"
            )

        # Check if customer's tier can access this reward
        if loyalty_data["tier_id"] not in reward_data["tiers"]:
            raise HTTPException(
                status_code=400,
                detail=f"This reward is not available for {loyalty_data['tier_name']} tier members"
            )

        now = datetime.utcnow()
        expiry_date = now.replace(hour=23, minute=59, second=59)
        expiry_date = expiry_date.replace(day=expiry_date.day + reward_data["expires_days"])

        # Create active reward
        active_reward = {
            "id": f"{request.reward_id}-{now.strftime('%Y%m%d%H%M%S')}",
            "reward_id": request.reward_id,
            "name": reward_data["name"],
            "description": reward_data["description"],
            "reward_type": reward_data["reward_type"],
            "value": reward_data["value"],
            "product_id": reward_data.get("product_id"),
            "redeemed_date": now.isoformat(),
            "expires_date": expiry_date.isoformat(),
            "is_used": False
        }

        # Create transaction for redeeming points
        transaction = {
            "type": "redeem",
            "points": -reward_data["points_required"],  # Negative because points are being spent
            "source": "reward",
            "source_id": request.reward_id,
            "description": f"Redeemed {reward_data['name']}",
            "timestamp": now.isoformat()
        }

        # Update loyalty data
        updates = {
            "current_points": loyalty_data["current_points"] - reward_data["points_required"],
            "last_activity": now.isoformat(),
            "transactions": firestore.ArrayUnion([transaction]),
            "active_rewards": firestore.ArrayUnion([active_reward])
        }

        # Apply updates
        loyalty_ref.update(updates)

        # Send reward redemption email
        try:
            send_loyalty_email(
                customer_id=customer_id,
                email=loyalty_data.get("email", ""),
                template_type="reward_redeemed",
                data={
                    "customer_name": loyalty_data.get("display_name", "Customer"),
                    "reward_name": reward_data["name"],
                    "reward_description": reward_data["description"],
                    "points_used": reward_data["points_required"],
                    "remaining_points": loyalty_data["current_points"] - reward_data["points_required"],
                    "expiry_date": expiry_date.strftime("%B %d, %Y")
                }
            )
        except Exception as email_error:
            print(f"Error sending reward redemption email: {str(email_error)}")
            # Continue processing - email failure shouldn't block redemption

        return LoyaltyResponse(
            success=True,
            message=f"Successfully redeemed {reward_data['name']}",
            data={
                "reward": active_reward,
                "points_remaining": updates["current_points"]
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error redeeming loyalty reward: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to redeem loyalty reward: {str(e)}"
        )


# Helper Functions
def initialize_tiers():
    """Initialize default tier levels"""
    batch = db_firestore.batch()

    for tier in DEFAULT_TIERS:
        tier_ref = db_firestore.collection(COLLECTIONS["TIERS"]).document(tier["id"])
        batch.set(tier_ref, tier)

    batch.commit()
    print("Initialized default tier levels")


def initialize_rewards():
    """Initialize default rewards"""
    batch = db_firestore.batch()

    for reward in DEFAULT_REWARDS:
        reward_ref = db_firestore.collection(COLLECTIONS["REWARDS"]).document(reward["id"])
        batch.set(reward_ref, reward)

    batch.commit()
    print("Initialized default rewards")


def get_tier_for_points(points: int):
    """Get the appropriate tier for a given point total"""
    tiers_ref = db_firestore.collection(COLLECTIONS["TIERS"])
    tiers = [doc.to_dict() for doc in tiers_ref.get()]

    # If tiers don't exist, initialize with defaults
    if not tiers:
        initialize_tiers()
        tiers = [doc.to_dict() for doc in tiers_ref.get()]

    # Sort tiers by min_points
    tiers.sort(key=lambda x: x["min_points"])

    # Find the highest tier the customer qualifies for
    for i in range(len(tiers) - 1, -1, -1):
        if points >= tiers[i]["min_points"]:
            return tiers[i]

    # Default to the lowest tier
    return tiers[0] if tiers else None


def get_available_rewards_for_customer(loyalty_data: dict):
    """Get available rewards for a customer based on their tier and points"""
    rewards_ref = db_firestore.collection(COLLECTIONS["REWARDS"])
    rewards = [doc.to_dict() for doc in rewards_ref.get()]

    # If rewards don't exist, initialize with defaults
    if not rewards:
        initialize_rewards()
        rewards = [doc.to_dict() for doc in rewards_ref.get()]

    available_rewards = [
        reward for reward in rewards
        if reward["active"] and
           loyalty_data["tier_id"] in reward["tiers"] and
           loyalty_data["current_points"] >= reward["points_required"]
    ]

    return available_rewards


def send_loyalty_email(customer_id: str, email: str, template_type: str, data: dict):
    """Send a loyalty program related email"""
    if not email:
        print(f"No email address available for customer {customer_id}")
        return

    from app.apis.notifications import send_email
    from pydantic import BaseModel

    # Define email templates
    templates = {
        "loyalty_welcome": {
            "subject": "Welcome to Hempex Rewards! 🌱",
            "html": f"""
            <h2>Welcome to Hempex Rewards, {data.get('customer_name', 'Valued Customer')}!</h2>
            <p>Thank you for joining our loyalty program. As a {data.get('tier_name', 'member')}, you'll enjoy:</p>
            <ul>
                <li>Earn 1 point for every $1 spent</li>
                <li>Redeem points for discounts, free products, and exclusive benefits</li>
                <li>Progress through tiers for enhanced rewards and benefits</li>
            </ul>
            <p>Visit your <a href="https://midnight.databutton.app/loyalty-program">Loyalty Dashboard</a> to track your points and available rewards.</p>
            <p>Thank you for choosing Hempex for your wellness journey!</p>
            """,
            "text": f"""
            Welcome to Hempex Rewards, {data.get('customer_name', 'Valued Customer')}!
            
            Thank you for joining our loyalty program. As a {data.get('tier_name', 'member')}, you'll enjoy:
            - Earn 1 point for every $1 spent
            - Redeem points for discounts, free products, and exclusive benefits
            - Progress through tiers for enhanced rewards and benefits
            
            Visit your Loyalty Dashboard to track your points and available rewards.
            
            Thank you for choosing Hempex for your wellness journey!
            """
        },
        "points_earned": {
            "subject": "You've Earned Hempex Rewards Points! 🌟",
            "html": f"""
            <h2>You've earned {data.get('points_earned', 0)} points!</h2>
            <p>Hello {data.get('customer_name', 'Valued Customer')},</p>
            <p>Great news! We've added <strong>{data.get('points_earned', 0)} points</strong> to your Hempex Rewards account.</p>
            <p>Your current balance is now <strong>{data.get('current_points', 0)} points</strong> as a <strong>{data.get('tier_name', 'member')}</strong>.</p>
            <p>Visit your <a href="https://midnight.databutton.app/loyalty-program">Loyalty Dashboard</a> to see what rewards you can redeem.</p>
            <p>Thank you for your continued support!</p>
            """,
            "text": f"""
            You've earned {data.get('points_earned', 0)} points!
            
            Hello {data.get('customer_name', 'Valued Customer')},
            
            Great news! We've added {data.get('points_earned', 0)} points to your Hempex Rewards account.
            
            Your current balance is now {data.get('current_points', 0)} points as a {data.get('tier_name', 'member')}.
            
            Visit your Loyalty Dashboard to see what rewards you can redeem.
            
            Thank you for your continued support!
            """
        },
        "tier_upgrade": {
            "subject": f"Congratulations on Your {data.get('new_tier', 'New')} Tier Upgrade! ✨",
            "html": f"""
            <h2>Congratulations on reaching {data.get('new_tier', 'a new tier')}!</h2>
            <p>Hello {data.get('customer_name', 'Valued Customer')},</p>
            <p>We're thrilled to inform you that you've been upgraded to our <strong>{data.get('new_tier', 'new')}</strong> tier!</p>
            <p>As a {data.get('new_tier', 'valued member')}, you now enjoy these enhanced benefits:</p>
            <ul>
                {' '.join([f'<li>{benefit}</li>' for benefit in data.get('benefits', [])])}
            </ul>
            <p>Visit your <a href="https://midnight.databutton.app/loyalty-program">Loyalty Dashboard</a> to see your new rewards and benefits.</p>
            <p>Thank you for your continued loyalty to Hempex!</p>
            """,
            "text": f"""
            Congratulations on reaching {data.get('new_tier', 'a new tier')}!
            
            Hello {data.get('customer_name', 'Valued Customer')},
            
            We're thrilled to inform you that you've been upgraded to our {data.get('new_tier', 'new')} tier!
            
            As a {data.get('new_tier', 'valued member')}, you now enjoy these enhanced benefits:
            {chr(10).join([f'- {benefit}' for benefit in data.get('benefits', [])])}
            
            Visit your Loyalty Dashboard to see your new rewards and benefits.
            
            Thank you for your continued loyalty to Hempex!
            """
        },
        "reward_redeemed": {
            "subject": "Your Hempex Reward Has Been Redeemed! 🎁",
            "html": f"""
            <h2>You've successfully redeemed a reward!</h2>
            <p>Hello {data.get('customer_name', 'Valued Customer')},</p>
            <p>You've successfully redeemed <strong>{data.get('reward_name', 'a reward')}</strong>.</p>
            <p>{data.get('reward_description', '')}</p>
            <p>You used <strong>{data.get('points_used', 0)} points</strong> and have <strong>{data.get('remaining_points', 0)} points</strong> remaining.</p>
            <p>Your reward will be valid until <strong>{data.get('expiry_date', 'expiration')}</strong>.</p>
            <p>Visit your <a href="https://midnight.databutton.app/loyalty-program">Loyalty Dashboard</a> to view your active rewards.</p>
            <p>Thank you for being a loyal Hempex customer!</p>
            """,
            "text": f"""
            You've successfully redeemed a reward!
            
            Hello {data.get('customer_name', 'Valued Customer')},
            
            You've successfully redeemed {data.get('reward_name', 'a reward')}.
            
            {data.get('reward_description', '')}
            
            You used {data.get('points_used', 0)} points and have {data.get('remaining_points', 0)} points remaining.
            
            Your reward will be valid until {data.get('expiry_date', 'expiration')}.
            
            Visit your Loyalty Dashboard to view your active rewards.
            
            Thank you for being a loyal Hempex customer!
            """
        }
    }

    template = templates.get(template_type)
    if not template:
        print(f"Email template {template_type} not found")
        return

    class EmailNotification(BaseModel):
        customer_email: str
        subject: str
        content_html: str
        content_text: str
        template_id: Optional[str] = None

    email_notification = EmailNotification(
        customer_email=email,
        subject=template["subject"],
        content_html=template["html"],
        content_text=template["text"]
    )

    try:
        response = send_email(email_notification)
        return response
    except Exception as e:
        print(f"Error sending loyalty email: {str(e)}")
        raise e
