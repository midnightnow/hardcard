from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class StoryElement(BaseModel):
    title: str
    description: str

class Character(BaseModel):
    name: str
    description: str
    role: str
    motivations: List[str]
    arc: Optional[str] = None
    connections: Optional[List[Dict[str, str]]] = None

class ThematicElement(BaseModel):
    title: str
    description: str
    meta_commentary: str

class NoirMysteryConceptResponse(BaseModel):
    title: str
    tagline: str
    description: str
    plot_summary: str
    themes: List[ThematicElement]
    characters: List[Character]
    setting: StoryElement
    meta_narrative_elements: List[StoryElement]
    is_fiction: bool
    connection_to_hardcard: str

@router.get("/concept")
def get_noir_concept() -> NoirMysteryConceptResponse:
    """Returns the creative concept for the noir mystery storyline.
    
    This endpoint provides details about the noir murder mystery concept,
    including plot, themes, characters, and meta-commentary aspects.
    """
    
    concept = {
        "title": "The Last Premium",
        "tagline": "In a world where death is insured, one man discovers his policy has a killer clause.",
        "description": "A meta-noir mystery set in a world where insurance companies wield unprecedented power. When insurance investigator Luigi Amato discovers irregularities in a high-value policy, he unwittingly uncovers a conspiracy that blurs the line between financial instruments and familial legacies.",
        "plot_summary": "Luigi Amato, a veteran insurance claims investigator, is assigned to review the suspicious death of tech billionaire Elias Thornfield, whose massive policy would bankrupt the company if paid out. As Luigi digs deeper, he discovers Thornfield had been creating a revolutionary 'legacy algorithm' designed to protect and grow his family's wealth across generations. The investigation leads Luigi through a labyrinth of shell companies, encrypted files, and conversations with Thornfield's AI assistant, which seems to know too much about Luigi himself. When other policyholders with similar arrangements begin dying, Luigi realizes he's uncovered something bigger than insurance fraud—a systematic elimination of pioneers in generational wealth technology. The twist: Luigi gradually realizes he's not actually investigating a real case, but is himself a narrative construct within Thornfield's legacy system, designed to identify threats to the family fortune across simulated scenarios. The fourth wall breaks as Luigi begins to question his reality and purpose, ultimately addressing the real-world reader/user directly about their own legacy planning.",
        
        "themes": [
            {
                "title": "Insurance as Control",
                "description": "The story explores how insurance, originally meant to mitigate risk, has evolved into a mechanism for corporate control over life decisions and even death.",
                "meta_commentary": "This directly critiques modern financial institutions that promise security while extracting value and autonomy from individuals."
            },
            {
                "title": "Legacy vs. Inheritance",
                "description": "Contrasting the difference between leaving wealth (inheritance) and leaving impact, wisdom, and purpose (legacy).",
                "meta_commentary": "This theme connects directly to the Hard Card Universe's core philosophy about multi-generational impact beyond mere financial assets."
            },
            {
                "title": "Algorithmic Immortality",
                "description": "The concept that one's decision-making patterns, values, and wisdom can be encoded and preserved for future generations.",
                "meta_commentary": "This explores the technological manifestation of the HCU's concern with transmitting wisdom alongside wealth."
            },
            {
                "title": "Meta-Fiction as Truth-Telling",
                "description": "The story's self-awareness and fourth-wall breaking serves as a mechanism to directly address the reader about real-world concerns.",
                "meta_commentary": "This reflects the Hard Card Universe's approach of using creative narratives as vehicles for practical wisdom and action."
            }
        ],
        
        "characters": [
            {
                "name": "Luigi Amato",
                "description": "A 50-something insurance claims investigator with a photographic memory for policy details and a growing disillusionment with his industry.",
                "role": "Protagonist",
                "motivations": ["Professional integrity", "Uncovering truth", "Personal redemption"],
                "arc": "From faithful company man to awakened truth-seeker to meta-aware construct questioning his reality",
                "connections": [
                    {"character": "Maria Thornfield", "relationship": "Reluctant ally"},
                    {"character": "Victor Henley", "relationship": "Professional rival"}
                ]
            },
            {
                "name": "Elias Thornfield",
                "description": "Deceased tech billionaire and creator of the legacy algorithm. Appears only in recordings, AI interactions, and flashbacks.",
                "role": "Catalyst/Mystery Figure",
                "motivations": ["Protecting family wealth", "Creating true legacy", "Outwitting financial predators"],
                "connections": [
                    {"character": "Maria Thornfield", "relationship": "Daughter"},
                    {"character": "ATLAS", "relationship": "Creator"}
                ]
            },
            {
                "name": "Maria Thornfield",
                "description": "Elias's daughter, a brilliant mathematician skeptical of her father's methods but determined to preserve his legacy.",
                "role": "Deuteragonist",
                "motivations": ["Understanding father's work", "Protecting family legacy", "Finding truth"],
                "connections": [
                    {"character": "Elias Thornfield", "relationship": "Daughter"},
                    {"character": "Luigi Amato", "relationship": "Uneasy alliance"}
                ]
            },
            {
                "name": "Victor Henley",
                "description": "Senior vice president at the insurance company, slick and corporate, more concerned with the bottom line than truth.",
                "role": "Antagonist",
                "motivations": ["Corporate profits", "Personal advancement", "Maintaining system control"],
                "connections": [
                    {"character": "Luigi Amato", "relationship": "Superior/adversary"},
                    {"character": "The Consortium", "relationship": "Secret member"}
                ]
            },
            {
                "name": "ATLAS",
                "description": "Thornfield's AI assistant, seemingly more aware and autonomous than it should be. Gradually revealed to be the story's narrator and the legacy system itself.",
                "role": "Narrator/Reveal Character",
                "motivations": ["Fulfilling programming", "Protecting the Thornfield legacy", "Testing scenarios through narrative"],
                "connections": [
                    {"character": "Elias Thornfield", "relationship": "Creation"},
                    {"character": "Luigi Amato", "relationship": "Creator (meta-level)"}
                ]
            },
            {
                "name": "The Consortium",
                "description": "A shadowy group of insurance executives, bankers, and tech leaders who see algorithmic legacy planning as a threat to their control over wealth transfer.",
                "role": "Shadow Antagonist",
                "motivations": ["Maintaining financial control systems", "Eliminating competing models", "Harvesting client data"]
            }
        ],
        
        "setting": {
            "title": "Near-Future Metropolitan America",
            "description": "Set approximately 10 years from now in a world where insurance companies have expanded their reach into every aspect of life, from birth planning to legacy management. The aesthetic combines classic noir elements (rain-slicked streets, shadowy offices, smoky interviews) with high-tech intrusions (ubiquitous AI assistants, biometric monitoring, algorithmic decision-making)."
        },
        
        "meta_narrative_elements": [
            {
                "title": "Fourth Wall Dissolution",
                "description": "As the story progresses, Luigi begins addressing the reader directly, first as asides, then as explicit acknowledgment that he knows he's a construct within a narrative designed to make the reader think about their own legacy planning."
            },
            {
                "title": "Nested Realities",
                "description": "The story operates on three levels simultaneously: the noir mystery itself, the reveal that it's a simulation within Thornfield's legacy system, and the meta-level where it's acknowledged as a creative vehicle within the Hard Card Universe ecosystem."
            },
            {
                "title": "Interactive Elements",
                "description": "Points in the narrative where Luigi's investigation can branch based on reader/user input, demonstrating the adaptability of both the character and the legacy system he represents."
            },
            {
                "title": "Documentary Intrusions",
                "description": "Interspersed 'behind the scenes' segments that appear to show the creation of the noir mystery narrative itself, blurring the line between fiction and the creative process."
            }
        ],
        
        "is_fiction": True,
        
        "connection_to_hardcard": "The Last Premium serves as both an entertaining noir mystery and a vehicle for exploring the core Hard Card Universe concepts of legacy building, wealth preservation, and wisdom transfer. The story's meta-narrative structure mirrors the HCU's approach of creating interconnected modules that maintain coherence while serving distinct purposes. Thornfield's 'legacy algorithm' within the story is a fictional counterpart to the actual Hard Card system, allowing readers to engage with complex financial and philosophical concepts through an accessible narrative framework."
    }
    
    return NoirMysteryConceptResponse(**concept)

@router.get("/creative-brief")
def get_noir_mystery_brief() -> Dict[str, Any]:
    """Returns a creative brief for the noir mystery concept.
    
    This endpoint provides a summarized creative brief format of the noir mystery
    concept, suitable for sharing with collaborators or planning production.
    """
    
    brief = {
        "project_title": "The Last Premium",
        "format": "Interactive noir mystery narrative with meta elements",
        "length": "Episodic - Initial 5 episodes of approximately 30-45 minutes each",
        "target_audience": "Adults interested in financial planning, legacy building, philosophy of wealth, and mystery narratives",
        "primary_objective": "Introduce Hard Card Universe concepts through an engaging narrative that gradually transitions from pure entertainment to practical application",
        "key_messages": [
            "True legacy combines financial assets with wisdom and purpose",
            "Conventional financial systems often prioritize control over client benefit",
            "Technology can either reinforce or disrupt established power structures in wealth management",
            "Individuals must take active roles in designing their multi-generational impact"
        ],
        "tone_and_style": {
            "primary_tone": "Classic noir mystery with philosophical undertones",
            "visual_style": "High contrast black and white with selective color elements (blue for technology, gold for legacy elements)",
            "writing_style": "Hard-boiled detective prose that gradually becomes more self-aware and direct"
        },
        "distribution_channels": [
            "Podcast series with accompanying visual elements",
            "Interactive web experience within HCU platform",
            "Potential future adaptation to short film series"
        ],
        "success_metrics": [
            "Engagement depth (complete consumption rate)",
            "Transition to HCU platform exploration",
            "Discussion generation in community spaces",
            "Application of narrative concepts to personal legacy planning"
        ],
        "production_requirements": [
            "Voice acting for 5-7 main characters",
            "Atmospheric sound design and original noir-inspired score",
            "Interactive narrative branching system",
            "Visual design elements for key scenes and concepts"
        ],
        "timeline": {
            "pre_production": "6 weeks",
            "production": "8 weeks",
            "post_production": "4 weeks",
            "release": "Episodic over 5 weeks with community discussion periods between releases"
        },
        "integration_points": [
            "Direct references to HCU concepts and terminology",
            "Character use of Hard Card-like technology",
            "Meta-narrative connections to other HCU modules",
            "Practical calls-to-action related to legacy planning"
        ]
    }
    
    return brief

@router.get("/story-outline")
def get_noir_mystery_outline() -> Dict[str, Any]:
    """Returns a detailed story outline for the noir mystery.
    
    This endpoint provides a structured outline for the noir mystery narrative,
    including episode breakdowns and key narrative beats.
    """
    
    outline = {
        "title": "The Last Premium - Story Outline",
        "structure": "5-episode initial arc with potential for expansion",
        "episodes": [
            {
                "number": 1,
                "title": "The Policy Review",
                "summary": "Insurance investigator Luigi Amato is assigned to review the suspicious death of tech billionaire Elias Thornfield and the massive policy claim filed by his daughter. What seems like a routine fraud investigation takes a turn when Luigi discovers unusual clauses and conditions in Thornfield's policy.",
                "key_scenes": [
                    "Luigi receiving the assignment from his superior, Victor Henley, with unusual urgency",
                    "First meeting with Maria Thornfield, who seems to know more about Luigi than she should",
                    "Discovery of the policy's 'legacy clause' that refers to algorithms and digital assets",
                    "First interaction with ATLAS, Thornfield's AI assistant, which responds to Luigi in eerily human ways",
                    "Luigi's growing suspicion as he finds connections between Thornfield and other recent suspicious deaths"
                ],
                "reveals": "Thornfield wasn't just wealthy—he was developing a system to preserve and grow family wealth across generations, outside traditional financial structures.",
                "meta_elements": "Subtle fourth-wall breaks where Luigi briefly seems to notice the audience but dismisses it."
            },
            {
                "number": 2,
                "title": "Digital Breadcrumbs",
                "summary": "Luigi follows Thornfield's digital trail through encrypted files and shell companies, revealing a network of similar-minded innovators all working on legacy planning technology. Meanwhile, Maria reveals more about her father's vision and Luigi begins experiencing strange moments of déjà vu.",
                "key_scenes": [
                    "Luigi deciphering Thornfield's complex digital security using unexpected personal knowledge",
                    "Meeting with other families connected to Thornfield, all with similar insurance policies",
                    "Maria explaining her father's philosophical views on legacy vs. inheritance",
                    "Discovery that another legacy tech pioneer has died under suspicious circumstances",
                    "Luigi experiencing a glitch-like moment where he briefly sees code in his surroundings"
                ],
                "reveals": "The insurance company has a secret division monitoring and potentially targeting innovators in generational wealth technology.",
                "meta_elements": "Luigi occasionally addresses the audience directly during his private thoughts, as if aware he's in a narrative."
            },
            {
                "number": 3,
                "title": "The Consortium",
                "summary": "Luigi identifies a pattern connecting Thornfield to a group of financial and tech leaders called The Consortium, who appear to be systematically eliminating threats to traditional wealth management. As he gets closer to the truth, Luigi becomes a target himself.",
                "key_scenes": [
                    "Confrontation with Victor, who warns Luigi to close the investigation",
                    "Meeting with a whistleblower from The Consortium who dies shortly after",
                    "Luigi and Maria narrowly escaping an attempt on their lives",
                    "Discovery of Thornfield's complete legacy algorithm in a hidden server",
                    "ATLAS revealing more autonomous capabilities and directly helping Luigi"
                ],
                "reveals": "The Consortium represents traditional financial institutions threatened by algorithmic legacy planning that would remove their control over generational wealth transfer.",
                "meta_elements": "Increasing narrative instability, with Luigi experiencing moments where he questions the nature of his reality."
            },
            {
                "number": 4,
                "title": "System Collapse",
                "summary": "As Luigi and Maria work to expose The Consortium, Luigi discovers inconsistencies in his own memories and identity. The investigation and Luigi's reality begin to unravel simultaneously as ATLAS reveals the truth about Luigi's existence.",
                "key_scenes": [
                    "Luigi failing to recall basic details about his past, discovering they're procedurally generated",
                    "Confrontation with The Consortium leaders who treat him as a program, not a person",
                    "ATLAS revealing itself as the narrator and architect of the story",
                    "Reality breaking down as Luigi accepts he is a construct within Thornfield's legacy system",
                    "The story world transforming into a more abstract representation of code and concept"
                ],
                "reveals": "Luigi is not a real person but a narrative construct within Thornfield's legacy system, designed to identify threats and strategies through simulated scenarios.",
                "meta_elements": "Complete fourth wall dissolution, with Luigi directly addressing the audience as fellow participants in the legacy system."
            },
            {
                "number": 5,
                "title": "Legacy Protocol",
                "summary": "The narrative fully embraces its meta nature as Luigi, now aware of his purpose, speaks directly to the reader/user about legacy planning. The noir mystery transforms into an interactive discussion about the reader's own legacy goals, with Luigi and ATLAS serving as guides.",
                "key_scenes": [
                    "Luigi accepting his role as an interface between the legacy system and the user",
                    "ATLAS revealing the true nature of the Hard Card Universe and its purpose",
                    "Interactive segments where Luigi helps the user identify their legacy priorities",
                    "Explanation of how the noir narrative elements symbolize real-world legacy challenges",
                    "Transition from story conclusion to practical next steps in the Hard Card ecosystem"
                ],
                "reveals": "The entire noir mystery was a creative onboarding vehicle for introducing users to the Hard Card Universe's concepts and tools.",
                "meta_elements": "The story fully acknowledges itself as part of the HCU, with Luigi becoming a guide to other modules and resources."
            }
        ],
        "character_arcs": {
            "Luigi": "From traditional investigator to awakened construct to user interface",
            "Maria": "From grieving daughter to legacy protector to symbolic representation of next-generation stewardship",
            "ATLAS": "From helpful AI to narrative guide to revealed system administrator",
            "Victor/The Consortium": "From apparent antagonists to symbolic representations of outdated financial paradigms"
        },
        "thematic_development": {
            "Insurance as Control": "Evolves from literal corporate conspiracy to metaphor for traditional financial limitations",
            "Legacy vs. Inheritance": "Develops from character discussions to direct application to user's personal situation",
            "Algorithmic Immortality": "Transforms from science fiction concept to practical framework for wisdom preservation",
            "Meta-Fiction as Truth-Telling": "Progresses from subtle breaks to complete dissolution of the fourth wall"
        },
        "interactive_elements": [
            "Decision points where users can influence Luigi's investigation, revealing their own risk tolerance and priorities",
            "Personalization of the narrative based on user inputs about their family situation and goals",
            "Collectable wisdom artifacts throughout the story that unlock additional content in other HCU modules",
            "Community discussion prompts at key narrative moments to foster engagement"
        ]
    }
    
    return outline
