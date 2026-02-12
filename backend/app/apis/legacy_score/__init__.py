from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import databutton as db
import json
import re
from datetime import datetime
from app.apis.vault_config import get_vault_config, VaultConfig

router = APIRouter()

# Define response models
class LegacyScoreBreakdown(BaseModel):
    content: int = Field(..., description="Score component for content contributions (stories, photos, documents)")
    financial: int = Field(..., description="Score component for financial stewardship")
    family: int = Field(..., description="Score component for family connections and engagement")

class LegacyScoreResponse(BaseModel):
    score: int = Field(..., description="Total legacy score (0-1000)")
    tier: str = Field(..., description="Achievement tier based on the score")
    breakdown: LegacyScoreBreakdown = Field(..., description="Score breakdown by category")
    last_updated: str = Field(..., description="Timestamp when the score was last calculated")

# Function to calculate tier based on score
def calculate_tier(score: int) -> str:
    """Calculate the tier based on the score"""
    if score >= 900:
        return "Legendary"
    elif score >= 750:
        return "Visionary"
    elif score >= 600:
        return "Flourishing"
    elif score >= 450:
        return "Growing"
    elif score >= 300:
        return "Developing"
    elif score >= 150:
        return "Budding"
    else:
        return "Emerging"

# Helper function to calculate legacy score
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


def calculate_content_score(vault_id: str) -> int:
    """Calculate the content component of the legacy score"""
    try:
        # Check family stories count and quality
        stories_key = sanitize_storage_key(f"family_stories_{vault_id}")
        stories = db.storage.json.get(stories_key, default=[])
        
        # Base score: 5 points per story, up to 100 points
        story_count_score = min(len(stories) * 5, 100)
        
        # Media richness: 3 points per media item, up to 100 points
        media_count = sum(len(story.get("media", [])) for story in stories)
        media_score = min(media_count * 3, 100)
        
        # Content length: Up to 100 points based on average content length
        if stories:
            avg_content_length = sum(len(story.get("content", "")) for story in stories) / len(stories)
            content_length_score = min(int(avg_content_length / 10), 100)
        else:
            content_length_score = 0
        
        # Bonus for story diversity (different authors, tags)
        authors = set(story.get("author", "") for story in stories)
        author_diversity_score = min(len(authors) * 10, 50)
        
        all_tags = []
        for story in stories:
            all_tags.extend(story.get("tags", []))
        unique_tags = set(all_tags)
        tag_diversity_score = min(len(unique_tags) * 5, 50)
        
        # Calculate base family stories score
        family_stories_score = story_count_score + media_score + content_length_score + author_diversity_score + tag_diversity_score
        
        return family_stories_score
    except Exception as e:
        print(f"Error calculating family stories score: {e}")
        return 0


def calculate_gifting_score(vault_id: str) -> float:
    """Calculate a score based on legacy point gifting activity"""
    try:
        # Get all point gifts
        try:
            legacy_points_gifts = db.storage.json.get("legacy_points_gifts", default=[])
        except Exception:
            return 0
            
        if not legacy_points_gifts:
            return 0
            
        # Get all profiles for this vault
        try:
            from app.apis.family_profiles import get_all_profiles
            profiles = get_all_profiles()
            vault_profile_ids = [p.id for p in profiles if p.vault_id == vault_id]
        except Exception:
            return 0
            
        if not vault_profile_ids:
            return 0
            
        # Count gifts sent/received by profiles in this vault
        points_received = 0
        gifts_sent = 0
        
        for gift in legacy_points_gifts:
            # Count points received by profiles in this vault
            if gift.get("recipient_id") in vault_profile_ids:
                points_received += gift.get("points", 0)
                
            # Count gifts sent by profiles in this vault    
            if gift.get("sender_id") in vault_profile_ids:
                gifts_sent += 1
        
        # Calculate score based on points received and gifts sent
        # This incentivizes both receiving recognition and recognizing others
        gifting_score = min(25, points_received / 10) + min(15, gifts_sent * 3)
        
        # Normalize to 0-25 range (25% of content score)
        return min(25, gifting_score)
    except Exception as e:
        print(f"Error calculating gifting score: {e}")
        return 0


def calculate_legacy_score(vault_config: VaultConfig) -> LegacyScoreResponse:
    """Calculate legacy score based on vault content, financial stewardship, and family connections"""
    
    # Content score (stories, photos, documents) - 40% of total
    content_score = 0
    vault_id = vault_config.id
    
    # Family stories contribution
    family_stories_score = calculate_content_score(vault_id)
    content_score += family_stories_score
    
    # Legacy point gifting contribution
    legacy_points_score = calculate_gifting_score(vault_id)
    content_score += legacy_points_score
    
    # Check for content DAOs
    content_score += 50  # Base score for having content
    
    # Check for enlightenment trail progress
    if hasattr(vault_config, 'enlightenment_trail') and vault_config.enlightenment_trail:
        milestones = getattr(vault_config.enlightenment_trail, 'milestones', [])
        content_score += min(len(milestones) * 15, 75)  # Up to 75 points for milestones
    
    # Check for music IP
    if hasattr(vault_config, 'music_ip') and vault_config.music_ip:
        content_score += min(len(vault_config.music_ip) * 10, 50)  # Up to 50 points for music IP
    
    # Financial score - 30% of total
    # TODO: Replace with actual financial metrics from investment portfolios
    financial_score = 200  # Placeholder score
    
    # Family connections score - 30% of total
    # TODO: Replace with actual family connection metrics
    family_score = 190  # Placeholder score
    
    # Normalize scores to correct proportions (40%, 30%, 30%)
    normalized_content_score = min(int(content_score * 0.8), 400)  # 40% of 1000 = 400
    normalized_financial_score = min(int(financial_score * 1.5), 300)  # 30% of 1000 = 300
    normalized_family_score = min(int(family_score * 1.5), 300)  # 30% of 1000 = 300
    
    # Calculate total score (normalized to 0-1000)
    total_score = min(normalized_content_score + normalized_financial_score + normalized_family_score, 1000)
    
    # Determine tier
    tier = calculate_tier(total_score)
    
    return LegacyScoreResponse(
        score=total_score,
        tier=tier,
        breakdown=LegacyScoreBreakdown(
            content=normalized_content_score,
            financial=normalized_financial_score,
            family=normalized_family_score
        ),
        last_updated=datetime.now().isoformat()
    )

@router.get("/calculate/{vault_id}", response_model=LegacyScoreResponse)
def get_legacy_score(vault_id: str) -> LegacyScoreResponse:
    """Calculate and return the legacy score for a specific vault
    
    This endpoint analyzes the vault's content contributions, financial stewardship,
    and family connections to generate a comprehensive legacy score and tier ranking.
    The score breakdown helps identify areas of strength and opportunities for growth.
    """
    try:
        # Check for cached score
        score_key = sanitize_storage_key(f"legacy_score_{vault_id}")
        try:
            cached_score = db.storage.json.get(score_key)
            # Return cached score if it exists and is recent
            return LegacyScoreResponse(**cached_score)
        except Exception as cache_error:
            print(f"No cached score found or error: {cache_error}")
        
        # Get vault configuration
        vault_config = get_vault_config(vault_id)
        
        # Calculate legacy score
        score_response = calculate_legacy_score(vault_config)
        
        # Cache the score
        db.storage.json.put(score_key, score_response.dict())
        
        return score_response
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error calculating legacy score: {str(e)}")


def recalculate_legacy_score(vault_id: str) -> LegacyScoreResponse:
    """Force recalculation of the legacy score for a vault"""
    try:
        # Get vault configuration
        vault_config = get_vault_config(vault_id)
        
        # Calculate legacy score
        score_response = calculate_legacy_score(vault_config)
        
        # Cache the score
        score_key = sanitize_storage_key(f"legacy_score_{vault_id}")
        db.storage.json.put(score_key, score_response.dict())
        
        return score_response
    except Exception as e:
        print(f"Error recalculating legacy score: {e}")
        raise HTTPException(status_code=500, detail=f"Error recalculating legacy score: {str(e)}")
