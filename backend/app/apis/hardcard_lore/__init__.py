from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import databutton as db
from typing import List, Dict, Any, Optional
from app.auth import AuthorizedUser
import json

router = APIRouter()

# Define the lore structure
class LoreFragment(BaseModel):
    id: str
    title: str
    content: str
    level_required: int
    category: str
    order: int

class LoreResponse(BaseModel):
    unlocked: List[LoreFragment]
    locked: List[LoreFragment]
    next_unlock: Optional[LoreFragment] = None

# Sample lore data - in production, this would be stored in a database
LORE_FRAGMENTS = [
    {
        "id": "origins-1",
        "title": "Origins of the Hardcard",
        "content": "<p>The Hardcard's origins trace back to the ancient cryptographic guilds of the digital renaissance. Created as a response to the vulnerabilities of traditional security systems, the first prototype was designed by a team of visionary cryptographers working in isolation.</p><p>These early cards utilized revolutionary materials capable of storing encryption keys in ways that were previously thought impossible.</p>",
        "level_required": 0,
        "category": "history",
        "order": 1
    },
    {
        "id": "security-1",
        "title": "Foundation Security Protocols",
        "content": "<p>The base security layer of every Hardcard employs quantum-resistant algorithms that protect against both classical and quantum attacks. Each card contains a unique mathematical fingerprint that cannot be duplicated, even with advanced fabrication techniques.</p><p>This fundamental security layer serves as the foundation upon which all other protective measures are built.</p>",
        "level_required": 0,
        "category": "technical",
        "order": 2
    },
    {
        "id": "guardian-secrets-1",
        "title": "The Guardian Protocol",
        "content": "<p>Upon reaching Guardian status, Hardcard holders gain access to the first level of encrypted knowledge - The Guardian Protocol. This protocol introduces secondary authentication mechanisms that operate on principles beyond typical digital security.</p><p>Guardian-level cards incorporate memory alloy components that physically change their structure based on legitimate authentication attempts, creating a physical record of access history that cannot be altered.</p>",
        "level_required": 1,
        "category": "technical",
        "order": 3
    },
    {
        "id": "sentinel-archives-1",
        "title": "The Sentinel Archives",
        "content": "<p>The Sentinel tier unlocks knowledge of the distributed Archive system - a global network of secure data repositories that automatically mirror and verify each other. This system ensures that even if multiple nodes are compromised, the integrity of the vault remains intact.</p><p>Sentinels learn the techniques for creating secure transmission channels between archives, employing principles of data sharding where no single transmission contains enough information to reconstruct sensitive data.</p>",
        "level_required": 2,
        "category": "technical",
        "order": 4
    },
    {
        "id": "custodian-codex-1",
        "title": "The Custodian Codex",
        "content": "<p>Custodians are entrusted with the knowledge of generational key management - the art of creating cryptographic systems that can be securely transferred across generations. The Codex reveals techniques for creating time-locked encryption that can only be accessed at predetermined future dates.</p><p>Through these methods, assets can be protected not just in space but through time, ensuring that family legacies remain secure across decades without requiring continuous management.</p>",
        "level_required": 3,
        "category": "history",
        "order": 5
    },
    {
        "id": "sovereign-principles-1",
        "title": "The Sovereign Principles",
        "content": "<p>At the Sovereign level, Hardcard holders learn of the hidden mathematical principles that underpin the entire security architecture. These principles draw from obscure branches of number theory and topology to create systems that are provably secure against entire classes of attacks.</p><p>Sovereigns gain the ability to customize their security implementations, adapting their defenses to specific threat models while maintaining compatibility with the broader Hardcard ecosystem.</p>",
        "level_required": 4,
        "category": "technical",
        "order": 6
    },
    {
        "id": "oracle-vision-1",
        "title": "The Oracle Vision",
        "content": "<p>Oracles are granted insight into the predictive security algorithms that anticipate and counter emerging threats before they materialize. These systems employ advanced pattern recognition to identify attack vectors that have not yet been exploited in the wild.</p><p>The Oracle Vision includes knowledge of how the system continually evolves its defenses through distributed intelligence gathering and autonomous adaptation mechanisms that operate at the edge of current AI capabilities.</p>",
        "level_required": 5,
        "category": "technical",
        "order": 7
    },
    {
        "id": "ascendant-wisdom-1",
        "title": "The Ascendant Wisdom",
        "content": "<p>Ascendants receive the closely guarded knowledge of the physical manifestation of digital security - how quantum effects are harnessed at the nanoscale within each Hardcard to create truly random numbers that cannot be predicted by any amount of computational power.</p><p>This wisdom includes understanding of material science breakthroughs that allow Hardcards to store cryptographic keys in the atomic structure of specialized alloys, making them immune to all known forms of electronic surveillance.</p>",
        "level_required": 6,
        "category": "history",
        "order": 8
    },
    {
        "id": "architect-paradigm-1",
        "title": "The Architect Paradigm",
        "content": "<p>Architects learn how to influence the evolution of the entire Hardcard ecosystem, shaping the next generation of security paradigms. This knowledge includes the principles of governance that ensure no single entity can control or compromise the system.</p><p>The Architect Paradigm reveals how cryptographic governance is maintained through mathematical principles rather than institutional authority, creating a truly decentralized security framework that can withstand social and political pressures.</p>",
        "level_required": 7,
        "category": "technical",
        "order": 9
    },
    {
        "id": "chronos-secrets-1",
        "title": "The Chronos Secrets",
        "content": "<p>The Chronos level reveals the temporal security dimensions of the Hardcard system - how encryption keys can be mathematically bound to specific timeframes, creating security systems that operate across decades without degradation or vulnerability to advancing technology.</p><p>These secrets include methods for creating cryptographic time capsules that can only be opened when specific astronomical configurations occur, binding digital security to the physical movements of celestial bodies.</p>",
        "level_required": 8,
        "category": "history",
        "order": 10
    },
    {
        "id": "genesis-codex-1",
        "title": "The Genesis Codex",
        "content": "<p>Those who reach Genesis status receive complete knowledge of the underlying principles that make Hardcards possible - including theoretical frameworks for security systems that transcend current technological limitations.</p><p>The Genesis Codex contains the blueprint for creating entirely new security paradigms, ensuring that as technology evolves, the fundamental security principles of the Hardcard can be re-implemented in whatever new mediums emerge in the future.</p>",
        "level_required": 9,
        "category": "technical",
        "order": 11
    }
]

@router.get("/hardcard-lore")
def get_hardcard_lore(user: AuthorizedUser) -> LoreResponse:
    """Get all lore fragments available to the user based on their level
    
    Returns unlocked and locked lore fragments, as well as the next fragment that will be unlocked
    when the user levels up.
    """
    try:
        # Get user's current level
        user_data = get_user_data(user.sub)
        current_level = user_data.get('level', 0)
        
        # Divide lore into unlocked and locked fragments
        unlocked = []
        locked = []
        next_unlock = None
        
        for fragment in LORE_FRAGMENTS:
            lore_fragment = LoreFragment(**fragment)
            
            if lore_fragment.level_required <= current_level:
                unlocked.append(lore_fragment)
            else:
                locked.append(lore_fragment)
                # Find the next fragment to be unlocked (lowest level required above current level)
                if next_unlock is None or lore_fragment.level_required < next_unlock.level_required:
                    next_unlock = lore_fragment
        
        # Sort by order
        unlocked.sort(key=lambda x: x.order)
        locked.sort(key=lambda x: x.order)
        
        return LoreResponse(
            unlocked=unlocked,
            locked=locked,
            next_unlock=next_unlock
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hardcard-lore/{fragment_id}")
def get_hardcard_lore_fragment(fragment_id: str, user: AuthorizedUser) -> LoreFragment:
    """Get a specific lore fragment if the user has the required level
    
    Returns the requested lore fragment if the user has unlocked it, otherwise returns an error.
    """
    try:
        # Get user's current level
        user_data = get_user_data(user.sub)
        current_level = user_data.get('level', 0)
        
        # Find the requested fragment
        fragment = next((f for f in LORE_FRAGMENTS if f["id"] == fragment_id), None)
        
        if not fragment:
            raise HTTPException(status_code=404, detail=f"Lore fragment '{fragment_id}' not found")
        
        # Check if user has required level
        if fragment["level_required"] > current_level:
            raise HTTPException(
                status_code=403, 
                detail=f"This lore fragment requires level {fragment['level_required']}. Your current level is {current_level}."
            )
        
        return LoreFragment(**fragment)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to get user data from storage
def get_user_data(user_id: str) -> dict:
    """Get user data from Databutton storage"""
    try:
        user_data_key = f"user_profile_{user_id}"
        user_data = db.storage.json.get(user_data_key, default={})
        
        # If no data exists, initialize with defaults
        if not user_data:
            user_data = {
                "level": 0,
                "xp": 0,
                "vault_points": 0,
            }
            db.storage.json.put(user_data_key, user_data)
            
        return user_data
    except Exception as e:
        print(f"Error getting user data: {str(e)}")
        return {"level": 0, "xp": 0, "vault_points": 0}
