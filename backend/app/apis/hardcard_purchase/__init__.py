from fastapi import APIRouter, Request, Depends, HTTPException, Header
from pydantic import BaseModel
import stripe
import json
import databutton as db
from typing import Optional, List
from app.auth import AuthorizedUser
import uuid
import datetime
from app.apis.firebase import (
    get_user_data, 
    update_user_level_xp_points, 
    unlock_lore_fragment,
    get_lore_fragments_for_level,
    log_stripe_event,
    log_stripe_error
)

router = APIRouter()

# Configure Stripe - in production, get these from environment variables
stripe.api_key = db.secrets.get("STRIPE_SECRET_KEY")
ENDPOINT_SECRET = db.secrets.get("STRIPE_WEBHOOK_SECRET")

# Helper function to get Hardcard level data
def get_hardcard_level_data(level):
    """Get title, description, and features for a Hardcard level
    
    Args:
        level (int): The level to get data for
        
    Returns:
        dict: Title, description, and features for the level
    """
    levels = {
        0: {
            "title": "Initiate",
            "description": "The first step on your path to legacy wealth building.",
            "features": [
                "Basic vault access",
                "Investment tracking",
                "Legacy timeline viewer"
            ]
        },
        1: {
            "title": "Guardian",
            "description": "Secure your family's future with enhanced protection features.",
            "features": [
                "Advanced security protocols",
                "Multi-signature protection",
                "Guardian lore access"
            ]
        },
        2: {
            "title": "Sentinel",
            "description": "Watch over your legacy with vigilant monitoring tools.",
            "features": [
                "Real-time performance alerts",
                "Market condition monitoring",
                "Historical analysis tools"
            ]
        },
        3: {
            "title": "Custodian",
            "description": "Manage and grow your legacy assets with precision.",
            "features": [
                "Advanced portfolio analytics",
                "Custom diversification strategies",
                "Generational wealth planning"
            ]
        },
        4: {
            "title": "Sovereign",
            "description": "Take control of your financial destiny across generations.",
            "features": [
                "Cross-border inheritance planning",
                "Jurisdiction optimization",
                "Sovereign principles access"
            ]
        },
        5: {
            "title": "Oracle",
            "description": "See into the financial future with predictive analytics.",
            "features": [
                "AI market trend analysis",
                "Future scenario modeling",
                "Intergenerational opportunity mapping"
            ]
        },
        6: {
            "title": "Ascendant",
            "description": "Rise above conventional wealth management constraints.",
            "features": [
                "Alternative asset integration",
                "Legacy impact evaluation",
                "Wealth consciousness framework"
            ]
        },
        7: {
            "title": "Architect",
            "description": "Design complex wealth structures to last centuries.",
            "features": [
                "Multi-generational trust design",
                "Dynasty optimization tools",
                "Custom legal framework resources"
            ]
        },
        8: {
            "title": "Chronos",
            "description": "Master time itself in your approach to legacy planning.",
            "features": [
                "Millennium planning tools",
                "Temporal wealth strategies",
                "Chronological risk mitigation"
            ]
        },
        9: {
            "title": "Genesis",
            "description": "Create something entirely new - a financial legacy that transcends generations.",
            "features": [
                "Family heritage preservation systems",
                "Legacy cultural impact tools",
                "Genesis codex complete access"
            ]
        }
    }
    
    return levels.get(level, {
        "title": "Unknown",
        "description": "Unknown level",
        "features": ["Basic features"]
    })

# Define XP and Vault Points rewards per level
HARDCARD_REWARDS = {
    0: {"xp": 10, "vault_points": 0},
    1: {"xp": 100, "vault_points": 50},
    2: {"xp": 1000, "vault_points": 100},
    3: {"xp": 10000, "vault_points": 150},
    4: {"xp": 100000, "vault_points": 200},
    5: {"xp": 1000000, "vault_points": 250},
    6: {"xp": 10000000, "vault_points": 300},
    7: {"xp": 100000000, "vault_points": 350},
    8: {"xp": 1000000000, "vault_points": 400},
    9: {"xp": 10000000000, "vault_points": 450},
}

# Hardcard level pricing lookup - will be replaced with actual Stripe product IDs
HARDCARD_PRICE_LOOKUP = {
    0: "price_10power0",  # $1
    1: "price_10power1",  # $10
    2: "price_10power2",  # $100
    3: "price_10power3",  # $1,000
    4: "price_10power4",  # $10,000
    5: "price_10power5",  # $100,000
    6: "price_10power6",  # $1,000,000
    7: "price_10power7",  # $10,000,000
    8: "price_10power8",  # $100,000,000
    9: "price_10power9",  # $1,000,000,000
}

class PurchaseHardcardLevelRequest(BaseModel):
    level: int
    success_url: str
    cancel_url: str

class PurchaseHardcardLevelResponse(BaseModel):
    checkout_url: str
    session_id: str

class UserProfileData(BaseModel):
    level: int
    xp: int
    vault_points: int

@router.post("/purchase-hardcard-level")
def purchase_hardcard_level(request: PurchaseHardcardLevelRequest, user: AuthorizedUser) -> PurchaseHardcardLevelResponse:
    """Create a Stripe checkout session for purchasing a Hardcard level
    
    This endpoint creates a Stripe checkout session for the specified Hardcard level.
    The user will be redirected to the Stripe checkout page to complete the payment.
    """
    if request.level < 0 or request.level > 9:
        raise HTTPException(status_code=400, detail="Level must be between 0 and 9")
    
    try:
        # Get the price ID for the requested level
        price_id = HARDCARD_PRICE_LOOKUP.get(request.level)
        if not price_id:
            raise HTTPException(status_code=400, detail=f"Invalid level: {request.level}")
        
        # Create the checkout session
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f"{request.success_url}?session_id={{}}&level={request.level}",
            cancel_url=request.cancel_url,
            client_reference_id=user.sub,  # Pass the user ID for the webhook
            metadata={
                "user_id": user.sub,
                "level": str(request.level),
            }
        )
        
        return PurchaseHardcardLevelResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    """Handle Stripe webhook events
    
    This webhook handles payment events from Stripe, particularly for successful payments
    which then update the user's level, XP, and vault points in Firestore.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    try:
        # Get the raw request body
        payload = await request.body()
        payload_str = payload.decode("utf-8")
        
        # Verify the webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload=payload_str,
                sig_header=stripe_signature,
                secret=ENDPOINT_SECRET
            )
        except stripe.error.SignatureVerificationError:
            print("Stripe webhook signature verification failed")
            # Log the error but don't return an error to Stripe
            # This allows retries without multiple charges
            return {"status": "success", "message": "Invalid signature, but acknowledged for retry"}
            
        # Record successful authentication but continue processing
        print(f"Received valid Stripe webhook: {event['type']}")
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Check if payment was successful
            if session.payment_status == 'paid':
                # Get user ID and level from metadata
                user_id = session.get('client_reference_id') or session.metadata.get('user_id')
                level = int(session.metadata.get('level', 0))
                
                if not user_id:
                    print("No user ID found in webhook event")
                    return {"status": "error", "message": "No user ID found"}
                
                try:
                    # Get rewards for this level
                    rewards = HARDCARD_REWARDS.get(level, {"xp": 0, "vault_points": 0})
                    xp = rewards["xp"]
                    vault_points = rewards["vault_points"]
                    
                    # Log the Stripe event
                    log_stripe_event(
                        event_id=event['id'],
                        event_type=event['type'],
                        user_id=user_id,
                        data={
                            "level": level,
                            "xp_added": xp,
                            "points_added": vault_points,
                            "session_id": session.id
                        }
                    )
                    
                    # Update the user's profile in Firestore
                    updated_user_data = update_user_level_xp_points(user_id, level, xp, vault_points)
                    
                    # Get lore fragments for this level and unlock them
                    lore_fragments = get_lore_fragments_for_level(level)
                    for fragment_id in lore_fragments:
                        unlock_lore_fragment(user_id, fragment_id)
                    
                    # Send email notification
                    try:
                        # Import here to avoid circular imports
                        from app.apis.email_notifications import send_email_notification_endpoint, EmailNotificationRequest
                        
                        # Get level details
                        level_data = get_hardcard_level_data(level)
                        
                        # Format data for email template
                        current_year = datetime.datetime.now().year
                        template_data = {
                            "level": level,
                            "title": level_data["title"],
                            "description": level_data["description"],
                            "features": level_data["features"],
                            "xp_reward": xp,
                            "points_reward": vault_points,
                            "lore_fragments": bool(lore_fragments),
                            "dashboard_url": "https://midnight.databutton.app/hardcard/Dashboard",
                            "current_year": current_year
                        }
                        
                        # Send the email notification
                        email_request = EmailNotificationRequest(
                            user_id=user_id,
                            # Get email from session if available or leave as None to fetch from user data
                            email=session.customer_details.email if hasattr(session, "customer_details") and hasattr(session.customer_details, "email") else None,
                            subject="",  # Use default subject from template
                            template_name="hardcard_purchase",
                            template_data=template_data
                        )
                        
                        email_response = send_email_notification_endpoint(email_request)
                        print(f"Email notification result: {email_response.message}")
                    except Exception as email_error:
                        print(f"Error sending email notification: {str(email_error)}")
                    
                    print(f"User {user_id} successfully upgraded to level {level}")
                    print(f"Added {xp} XP and {vault_points} Vault Points")
                    if lore_fragments:
                        print(f"Unlocked lore fragments: {', '.join(lore_fragments)}")
                    
                    return {
                        "status": "success", 
                        "message": f"User {user_id} upgraded to level {level}",
                        "xp_added": xp,
                        "points_added": vault_points,
                        "lore_unlocked": lore_fragments
                    }
                except Exception as processing_error:
                    print(f"Error processing successful payment: {str(processing_error)}")
                    # Log error but acknowledge receipt to prevent retries
                    # This prevents double-charging the user
                    
                    # Log the error for debugging
                    log_stripe_error(
                        event_id=event['id'],
                        error_message=str(processing_error),
                        payload={
                            "user_id": user_id,
                            "level": level,
                            "session_id": session.id
                        }
                    )
                    
                    return {
                        "status": "error_but_acknowledged", 
                        "message": f"Error processing payment: {str(processing_error)}"
                    }
        
        # For other event types, just acknowledge receipt
        return {"status": "success", "message": f"Unhandled event type: {event['type']}"}
    
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        # Still return a 200 response to acknowledge receipt
        
        # Try to log the error for debugging
        try:
            log_stripe_error(
                event_id="unknown",
                error_message=str(e),
                payload={
                    "raw_payload": payload_str if isinstance(payload_str, str) else "Invalid payload",
                    "signature": stripe_signature or "None"
                }
            )
        except Exception as log_error:
            print(f"Error logging stripe error: {str(log_error)}")
        
        return {"status": "error", "message": str(e)}

@router.get("/api/me")
def get_user_profile(user: AuthorizedUser) -> UserProfileData:
    """Get user profile data including level, XP, and vault points
    
    This endpoint returns the user's current level, XP, and vault points.
    Used by the frontend after purchase success to show updated stats.
    """
    try:
        # Get user data from Firestore
        user_data = get_user_data(user.sub)
        
        # Calculate next level XP thresholds
        current_level = user_data.get('level', 0)
        next_level_xp = 10 ** (current_level + 1)  # 10^(level+1)
        
        return UserProfileData(
            level=current_level,
            xp=user_data.get('xp', 0),
            vault_points=user_data.get('vault_points', 0)
        )
    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper function for lore fragments
# Use the function from firebase module instead
# This is here for reference only
def get_lore_fragments_for_level_legacy(level: int) -> List[str]:
    """Get lore fragments unlocked at a specific level
    
    Args:
        level (int): The level to get lore fragments for
        
    Returns:
        List[str]: List of lore fragment IDs unlocked at this level
    """
    # This mapping defines which fragments are unlocked at each level
    level_to_fragments = {
        0: ["origins-1", "security-1"],
        1: ["guardian-secrets-1"],
        2: ["sentinel-archives-1"],
        3: ["custodian-codex-1"],
        4: ["sovereign-principles-1"],
        5: ["oracle-vision-1"],
        6: ["ascendant-wisdom-1"],
        7: ["architect-paradigm-1"],
        8: ["chronos-secrets-1"],
        9: ["genesis-codex-1"],
    }
    
    return level_to_fragments.get(level, [])
