from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class Concept(BaseModel):
    title: str
    description: str

class EpisodeConcept(BaseModel):
    number: int
    title: str
    description: str
    duration: str
    segments: List[Dict[str, str]]
    guests: Optional[List[Dict[str, str]]] = None

class MetaNarrativeResponse(BaseModel):
    title: str
    tagline: str
    description: str
    approach: str
    format: str
    core_concepts: List[Concept]
    layers: List[Dict[str, str]]
    interactive_elements: List[Dict[str, str]]
    integration_with_noir: str

class PodcastSeriesResponse(BaseModel):
    title: str
    description: str
    format: str
    episode_length: str
    release_schedule: str
    target_audience: List[str]
    distribution_platforms: List[str]
    pilot_episodes: List[EpisodeConcept]
    production_requirements: Dict[str, Any]

class ArgComponentsResponse(BaseModel):
    title: str
    description: str
    mechanics: List[Dict[str, str]]
    user_journey: Dict[str, Any]
    integration_points: List[Dict[str, str]]
    technologies: List[str]
    success_metrics: List[str]

@router.get("/meta-framework")
def get_meta_narrative_framework() -> MetaNarrativeResponse:
    """Returns the meta-narrative framework concept.
    
    This endpoint provides details about the meta-narrative approach that spans the
    Hard Card Universe, blending fiction, documentary, and practical application.
    """
    
    concept = {
        "title": "The Hard Card Chronicles: Between Fiction and Reality",
        "tagline": "The story behind the story of legacy building.",
        "description": "A multi-layered narrative experience that blends fictional storytelling, behind-the-scenes documentary, and direct audience engagement to explore the concepts of legacy, wealth preservation, and wisdom transfer in an innovative format.",
        "approach": "The meta-narrative framework operates on multiple simultaneous narrative planes, creating a rich tapestry where fiction and reality interweave. At its core is a podcast series that appears to document the creation of the Hard Card Universe, but gradually reveals itself to be part of the creative experience itself. This approach allows listeners/users to engage at their preferred depth - as entertainment, education, or practical application.",
        "format": "Primary delivery through an episodic podcast series with supplementary multimedia elements, interactive web components, and optional ARG (Alternate Reality Game) participation.",
        
        "core_concepts": [
            {
                "title": "Narrative Layering",
                "description": "Creating multiple simultaneous story planes that interact with and comment on each other, allowing the audience to engage at different levels of depth and commitment."
            },
            {
                "title": "Reality Blurring",
                "description": "Strategic ambiguity about which elements are fiction, which are documentary, and which are actual products/services, creating an engaging puzzle that drives deeper exploration."
            },
            {
                "title": "Participatory Storytelling",
                "description": "Incorporating audience interaction and contributions that genuinely shape the narrative direction and development of the Hard Card Universe."
            },
            {
                "title": "Wisdom Revelation Through Context",
                "description": "Using the meta-framework to gradually shift from entertainment to practical application, revealing deeper truths about legacy planning through narrative context rather than direct instruction."
            },
            {
                "title": "Structured Unveiling",
                "description": "A carefully orchestrated release of information, concepts, and interactive elements that builds comprehension and investment over time rather than overwhelming the audience."
            }
        ],
        
        "layers": [
            {
                "name": "Fiction Layer",
                "description": "The noir mystery and other creative narratives that serve as the surface-level engagement point for new audience members. Fully scripted and produced as entertainment."
            },
            {
                "name": "Making-Of Layer",
                "description": "Documentary-style segments that purport to show the creation process of the Hard Card Universe, including interviews with creators, challenges faced, and evolution of concepts."
            },
            {
                "name": "Meta-Commentary Layer",
                "description": "Analysis and discussion of the concepts presented in the fiction layer, connecting them to real-world legacy building and wealth preservation strategies."
            },
            {
                "name": "Reality Layer",
                "description": "Actual information about the Hard Card Universe platform, its features, and how users can apply its tools and frameworks to their own legacy planning."
            },
            {
                "name": "Participation Layer",
                "description": "Interactive elements that invite the audience to contribute to the universe, solve puzzles, and potentially shape future content development."
            }
        ],
        
        "interactive_elements": [
            {
                "name": "Digital Breadcrumbs",
                "description": "Hidden clues, codes, and references embedded throughout the podcast and associated materials that lead engaged listeners to additional content and interactive experiences."
            },
            {
                "name": "Legacy Challenges",
                "description": "Structured activities presented within the narrative that invite listeners to begin their own legacy planning process in parallel with story developments."
            },
            {
                "name": "Community Theorizing",
                "description": "Facilitated discussion spaces where audience members can share theories about the narrative, collaborate on puzzle-solving, and connect concepts to their own experiences."
            },
            {
                "name": "Influencer Integration",
                "description": "Strategic partnerships with finance, technology, and storytelling influencers who appear within both the fiction and documentary layers while promoting real engagement."
            },
            {
                "name": "Timeline Anomalies",
                "description": "Deliberate inconsistencies in the chronology and details between layers that reward close attention and repeat engagement with new insights and understanding."
            }
        ],
        
        "integration_with_noir": "The noir mystery serves as the primary fictional narrative within the meta-framework, providing an accessible entry point for new audience members. The meta-narrative podcast series uses the noir story as its ostensible subject matter, purporting to document its creation while actually expanding its themes. Characters from the noir mystery occasionally 'break character' to address the audience directly, creating moments where the layers explicitly overlap and interact. The noir mystery's theme of simulation and reality-questioning directly mirrors the meta-narrative's blending of fiction and documentary, creating resonant thematic harmony between the layers."
    }
    
    return MetaNarrativeResponse(**concept)

@router.get("/podcast-series")
def get_podcast_series_concept() -> PodcastSeriesResponse:
    """Returns the concept for the meta-narrative podcast series.
    
    This endpoint provides details about the podcast series that serves as the
    primary delivery vehicle for the meta-narrative framework.
    """
    
    podcast = {
        "title": "The Hard Card Chronicles",
        "description": "A podcast series that appears to document the creation of an ambitious multimedia project called 'The Hard Card Universe,' but gradually reveals itself to be an integral part of that very universe. Through interviews, behind-the-scenes content, and narrative segments, the podcast explores the concepts of legacy building, wealth preservation, and wisdom transfer while blurring the lines between documentation and creation.",
        "format": "Narrative documentary with scripted elements, interviews, and interactive components",
        "episode_length": "45-60 minutes",
        "release_schedule": "Weekly for initial 10-episode season",
        
        "target_audience": [
            "Finance and investment enthusiasts interested in novel approaches to wealth management",
            "Podcast listeners who enjoy complex, multi-layered storytelling (fans of shows like Serial, S-Town, or Welcome to Night Vale)",
            "Parents and family planners thinking about generational wealth and wisdom transfer",
            "Tech-savvy individuals interested in innovative digital platforms",
            "ARG (Alternate Reality Game) communities who enjoy participatory narrative experiences"
        ],
        
        "distribution_platforms": [
            "Apple Podcasts", 
            "Spotify", 
            "Google Podcasts", 
            "YouTube (with minimal visual elements)", 
            "HCU Platform (with enhanced interactive features)"
        ],
        
        "pilot_episodes": [
            {
                "number": 1,
                "title": "Origin Story: The Birth of Hard Card",
                "description": "Introduces the creators of the Hard Card Universe and their vision for a revolutionary approach to legacy building. Includes the first mentions of the noir mystery project as a creative vehicle they're developing.",
                "duration": "53 minutes",
                "segments": [
                    {"name": "Introduction to HCU", "length": "8 minutes"},
                    {"name": "Creator Interviews", "length": "15 minutes"},
                    {"name": "Legacy Concept Exploration", "length": "12 minutes"},
                    {"name": "Noir Mystery Teaser", "length": "10 minutes"},
                    {"name": "First Interactive Challenge", "length": "8 minutes"}
                ],
                "guests": [
                    {"name": "Dallas McMillan", "role": "HCU Creator"},
                    {"name": "Financial Psychology Expert", "role": "Guest Commentator"}
                ]
            },
            {
                "number": 2,
                "title": "The Last Premium: Crafting Fiction from Financial Reality",
                "description": "Dives into the development of the noir mystery narrative, introducing key creative decisions and character development. Features readings from the script and discussions of how financial concepts are translated into narrative elements.",
                "duration": "48 minutes",
                "segments": [
                    {"name": "Noir Mystery Development Update", "length": "10 minutes"},
                    {"name": "Script Reading: Luigi's First Scene", "length": "8 minutes"},
                    {"name": "Writer's Room Discussion", "length": "14 minutes"},
                    {"name": "Finance to Fiction Translation", "length": "12 minutes"},
                    {"name": "Listener Theories and Feedback", "length": "4 minutes"}
                ],
                "guests": [
                    {"name": "Voice Actor for Luigi", "role": "Creative Collaborator"},
                    {"name": "Insurance Industry Insider", "role": "Technical Consultant"}
                ]
            },
            {
                "number": 3,
                "title": "Meta Matters: The Philosophy Behind Hard Card",
                "description": "Explores the philosophical underpinnings of the HCU approach, introducing concepts of meta-narrative and participatory storytelling. Features the first subtle hints that the podcast itself may not be what it appears.",
                "duration": "51 minutes",
                "segments": [
                    {"name": "Recap and Community Growth", "length": "7 minutes"},
                    {"name": "Meta-Narrative Theory Discussion", "length": "13 minutes"},
                    {"name": "Interview: Philosophy of Legacy", "length": "15 minutes"},
                    {"name": "Unusual Recording Incident", "length": "6 minutes"},
                    {"name": "Interactive Segment: Legacy Questionnaire", "length": "10 minutes"}
                ],
                "guests": [
                    {"name": "Narrative Design Expert", "role": "Academic Contributor"},
                    {"name": "Philosopher of Technology", "role": "Guest Commentator"}
                ]
            },
            {
                "number": 4,
                "title": "Digital Breadcrumbs: Following the Trail",
                "description": "Documents the growing community engagement with the Hard Card Universe, featuring listener theories and solutions to previous challenges. Introduces more complex interactive elements and the first significant narrative anomaly.",
                "duration": "55 minutes",
                "segments": [
                    {"name": "Community Spotlight", "length": "12 minutes"},
                    {"name": "Challenge Solutions and Winners", "length": "8 minutes"},
                    {"name": "Mystery Audio File Analysis", "length": "7 minutes"},
                    {"name": "Host Investigation Segment", "length": "15 minutes"},
                    {"name": "New Interactive Challenge Reveal", "length": "13 minutes"}
                ],
                "guests": [
                    {"name": "Community Member", "role": "Challenge Winner"},
                    {"name": "Audio Forensics Expert", "role": "Technical Analyst"}
                ]
            },
            {
                "number": 5,
                "title": "The Revelation: Layers Within Layers",
                "description": "Features the first major revelation that the podcast is itself part of the Hard Card Universe narrative experience. Includes meta-commentary on the previous episodes and reframes the entire project for the audience.",
                "duration": "62 minutes",
                "segments": [
                    {"name": "The Revelation", "length": "18 minutes"},
                    {"name": "Creator Explanation", "length": "14 minutes"},
                    {"name": "Revisiting Previous Content", "length": "10 minutes"},
                    {"name": "HCU Platform Introduction", "length": "12 minutes"},
                    {"name": "Next Phase Announcement", "length": "8 minutes"}
                ],
                "guests": [
                    {"name": "Full HCU Creator Team", "role": "Project Reveal"},
                    {"name": "Early Platform User", "role": "Testimonial"}
                ]
            }
        ],
        
        "production_requirements": {
            "team": [
                "Host/Narrator",
                "Producer",
                "Audio Engineer",
                "Script Writer",
                "Researcher",
                "Community Manager"
            ],
            "equipment": [
                "Professional audio recording setup",
                "Remote interview capabilities",
                "Audio mixing and editing software",
                "Sound effect and music libraries",
                "Secure file sharing and collaboration platform"
            ],
            "production_schedule": {
                "pre_production": "4 weeks for season planning and initial scripting",
                "production": "12 weeks rolling schedule (producing episodes while releasing others)",
                "post_production": "2 weeks per episode for editing, mixing, and preparing interactive elements",
                "community_management": "Ongoing throughout release schedule and between seasons"
            },
            "budget_categories": [
                "Talent (host, voice actors, guests)",
                "Production team",
                "Equipment and software",
                "Music and sound licensing",
                "Marketing and promotion",
                "Interactive platform development",
                "Community management tools"
            ]
        }
    }
    
    return PodcastSeriesResponse(**podcast)

@router.get("/arg-components")
def get_arg_components() -> ArgComponentsResponse:
    """Returns the ARG (Alternate Reality Game) components of the meta-narrative.
    
    This endpoint provides details about the interactive ARG elements that extend
    the meta-narrative beyond passive consumption into active participation.
    """
    
    arg = {
        "title": "The Legacy Labyrinth",
        "description": "An Alternate Reality Game component that extends the Hard Card Universe from passive consumption into active participation. The Legacy Labyrinth creates a parallel interactive experience where participants solve puzzles, uncover hidden content, and potentially influence the development of the overall narrative while engaging with core concepts of legacy planning in a gamified context.",
        
        "mechanics": [
            {
                "name": "Embedded Codes",
                "description": "Steganographic and cryptographic puzzles hidden within podcast audio, website elements, and social media content that, when solved, reveal additional narrative content and game progression."
            },
            {
                "name": "Dispersed Narrative",
                "description": "Story elements intentionally scattered across multiple platforms and media formats, requiring community collaboration to assemble the complete picture."
            },
            {
                "name": "Real-World Anchors",
                "description": "Physical items or locations that connect the digital experience to tangible reality, such as limited edition Hard Cards with embedded puzzles or QR-coded promotional materials."
            },
            {
                "name": "Time-Released Challenges",
                "description": "New puzzles and content that unlock according to a predetermined schedule or when community milestones are reached, creating shared experiences and synchronized discovery."
            },
            {
                "name": "Character Interaction",
                "description": "Fictional characters from the Hard Card Universe who maintain social media presences, email accounts, or other channels through which participants can communicate and receive personalized responses."
            },
            {
                "name": "Legacy Simulators",
                "description": "Interactive tools that allow participants to model different approaches to wealth preservation and knowledge transfer, with results that affect their personal narrative path."
            }
        ],
        
        "user_journey": {
            "entry_points": [
                "Subtle audio anomalies in the podcast that, when analyzed, reveal URLs or messages",
                "'Accidental' glimpses of documents or screens in video content with hidden information",
                "Social media 'glitches' that briefly reveal game content before returning to normal",
                "Promotional materials with hidden elements visible only under certain conditions",
                "Word-of-mouth and community discovery"
            ],
            "progression_path": [
                "Initial Discovery: Participant encounters and recognizes a puzzle element",
                "First Engagement: Solving a simple puzzle reveals the existence of the ARG layer",
                "Community Connection: Participant finds and joins others working on similar challenges",
                "Narrative Immersion: Deeper puzzles reveal significant story content not available elsewhere",
                "Legacy Application: Puzzles begin incorporating actual legacy planning principles and tools",
                "Personal Relevance: Participant receives customized content based on their previous choices",
                "Contribution Opportunity: Advanced participants help shape future Hard Card Universe development"
            ],
            "engagement_levels": [
                "Casual: Participants who enjoy occasional puzzles but primarily follow the main narrative",
                "Active: Regular participants who solve most puzzles and engage with the community",
                "Core: Dedicated players who lead community efforts and may have direct creator interaction",
                "Legacy Planners: Those who transition from game participation to actual legacy platform usage"
            ]
        },
        
        "integration_points": [
            {
                "touchpoint": "Podcast Episodes",
                "description": "Each episode contains multiple hidden elements that launch or advance ARG storylines"
            },
            {
                "touchpoint": "HCU Platform",
                "description": "ARG puzzles that, when solved, unlock exclusive features or content within the actual platform"
            },
            {
                "touchpoint": "Social Media",
                "description": "Character accounts that interact with participants and distribute time-sensitive challenges"
            },
            {
                "touchpoint": "Email Communication",
                "description": "Opt-in narrative content delivered directly to participants, with embedded puzzles and decision points"
            },
            {
                "touchpoint": "Community Forums",
                "description": "Monitored spaces where developers can observe group problem-solving and seed new content"
            },
            {
                "touchpoint": "Physical Events",
                "description": "Optional in-person gatherings (when possible) that advance the narrative and strengthen community"
            }
        ],
        
        "technologies": [
            "Audio steganography for embedding codes in podcast content",
            "Web-based puzzle interfaces with progress tracking",
            "Automated response systems for character interactions",
            "Community collaboration tools with gamification elements",
            "Personalized content delivery based on participant history",
            "QR and NFC integration for physical components",
            "Secure validation systems for puzzle solutions"
        ],
        
        "success_metrics": [
            "Total participation numbers across different engagement levels",
            "Puzzle completion rates and community solution times",
            "Cross-platform journey completion (following narrative threads across media)",
            "Community growth and user-generated content volume",
            "Conversion rate from ARG participation to HCU platform exploration",
            "Retention metrics throughout the narrative experience",
            "Qualitative feedback on narrative immersion and concept understanding"
        ]
    }
    
    return ArgComponentsResponse(**arg)
