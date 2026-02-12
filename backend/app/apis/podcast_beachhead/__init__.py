from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class BeachheadEpisode(BaseModel):
    """Model for a single episode in the beachhead podcast series"""
    title: str
    description: str
    key_topics: List[str]
    guest_options: List[str]
    target_audience_segments: List[str]
    estimated_duration: str
    production_complexity: str
    key_takeaways: List[str]

class ProductionTimeline(BaseModel):
    """Model for the podcast production timeline"""
    phase: str
    tasks: List[str]
    duration: str
    dependencies: List[str]
    resource_requirements: Dict[str, str]
    deliverables: List[str]

class FeedbackLoop(BaseModel):
    """Model for podcast feedback loop mechanism"""
    channel: str
    description: str
    metrics: List[str]
    integration_process: str
    implementation_timeline: str

class PilotSeriesResponse(BaseModel):
    """Response model for the pilot podcast series"""
    series_title: str
    concept_summary: str
    chosen_niche: str
    niche_justification: str
    target_audience: Dict[str, Any]
    format_specifications: Dict[str, Any]
    episodes: List[BeachheadEpisode]
    production_timeline: List[ProductionTimeline]
    feedback_loops: List[FeedbackLoop]
    success_metrics: Dict[str, str]
    expansion_pathway: str

@router.get("/pilot-series")
def get_pilot_series() -> PilotSeriesResponse:
    """Returns the pilot podcast series plan for the HCU ecosystem.
    
    This endpoint provides a comprehensive plan for the initial 4-5 episode
    podcast series that serves as the beachhead product for the Hard Card Universe,
    including episode concepts, production timeline, and feedback mechanisms.
    """
    
    pilot_series = {
        "series_title": "Legacy Decoded: Building Wealth That Lasts",
        "concept_summary": "A podcast series exploring the intersection of multi-generational wealth planning, emerging technology, and timeless wisdom. Each episode blends practical insights from experts with compelling narratives that illustrate key concepts in action.",
        "chosen_niche": "Multi-generational Wealth Strategy",
        "niche_justification": "This niche was selected as an optimal beachhead because it: 1) Directly aligns with the core HCU mission of legacy-building, 2) Addresses an underserved intersection between traditional wealth management and emerging technologies, 3) Appeals to both established family offices and forward-thinking individual investors, 4) Positions the HCU brand as a thought leader in an evolving space, and 5) Creates natural pathways to expand into both deeper technical content and broader narrative offerings.",
        
        "target_audience": {
            "primary_segments": [
                "Family office directors and wealth managers seeking innovative preservation strategies",
                "High-net-worth parents concerned with effective generational transfer of both assets and values",
                "Next-generation inheritors looking to understand and modernize family wealth structures",
                "Financial technology professionals interested in long-horizon applications"
            ],
            "psychographic_profile": {
                "values": ["Long-term thinking", "Prudence balanced with innovation", "Family cohesion", "Knowledge preservation", "Ethical wealth deployment"],
                "concerns": ["Technology disruption of established wealth", "Cultural shifts affecting inheritance structures", "Information security across generations", "Maintaining relevance of advice through time"],
                "information_seeking_behavior": "Typically consumes multiple in-depth sources, values both historical context and cutting-edge insight, prefers content that respects complexity rather than oversimplifying."
            },
            "content_preferences": "Sophisticated but not academic; practical while still addressing deeper principles; values both storytelling and actionable frameworks; appreciates production quality without flashiness."
        },
        
        "format_specifications": {
            "episode_length": "35-45 minutes",
            "structure": "Three-part format including expert interview, case narrative, and practical application segment",
            "production_style": "Premium audio quality with minimal but effective sound design; conversational but substantive tone",
            "release_cadence": "Weekly for the pilot series, with potential to shift to bi-weekly for subsequent series depending on production complexity and audience engagement patterns",
            "supplementary_materials": "Each episode accompanied by episode guide with key concept summary, recommended resources, and reflection questions"
        },
        
        "episodes": [
            {
                "title": "The 100-Year Portfolio: Designing for True Long-Term Performance",
                "description": "Exploring investment frameworks specifically designed for multi-generational performance rather than quarterly or even annual returns. This episode challenges conventional portfolio theory by examining what truly constitutes long-term thinking in investment strategy.",
                "key_topics": [
                    "The mathematical differences between 5-year, 20-year, and 100-year investment horizons",
                    "Historical analysis of assets that have maintained value across centuries",
                    "The role of technological adaptation in preserving wealth through disruption periods",
                    "Balancing security and growth over extended timeframes"
                ],
                "guest_options": [
                    "Katherine Collins (Head of Sustainable Investing at Putnam Investments)",
                    "Gregory Zuckerman (Special Writer at The Wall Street Journal, author of 'The Man Who Solved the Market')",
                    "Dr. Ashby Monk (Executive Director of Stanford Global Projects Center)"
                ],
                "target_audience_segments": [
                    "Investment committee members for family offices",
                    "Financial advisors managing generational wealth transitions",
                    "Parents establishing long-term trusts for children"
                ],
                "estimated_duration": "40 minutes",
                "production_complexity": "Medium - requires data visualization companion content",
                "key_takeaways": [
                    "Mathematical frameworks for evaluating truly long-term investments",
                    "Practical portfolio construction principles for generational wealth preservation",
                    "How to balance established wealth preservation vehicles with emerging technological options",
                    "Communication strategies for aligning family expectations around long-term performance metrics"
                ]
            },
            {
                "title": "Digital Immortality: Securing Knowledge Across Generations",
                "description": "An examination of how critical knowledge and wisdom can be preserved and protected across generations using both technological and human systems. This episode bridges practical digital security with the philosophical aspects of meaningful knowledge transfer.",
                "key_topics": [
                    "Beyond passwords: comprehensive digital estate planning",
                    "Knowledge categorization frameworks for family wisdom preservation",
                    "Technological approaches to time-locked information release",
                    "Balancing accessibility with security in long-term knowledge storage"
                ],
                "guest_options": [
                    "Daniel Weitzner (Director of the MIT Internet Policy Research Initiative)",
                    "Pamela Samuelson (Professor at Berkeley Law, specialist in digital copyright and intellectual property)",
                    "Doc Searls (Co-author of 'The Cluetrain Manifesto' and advocate for user-controlled digital identity)"
                ],
                "target_audience_segments": [
                    "Family business owners concerned with knowledge continuity",
                    "Estate planning attorneys handling complex digital assets",
                    "Technology officers at family offices"
                ],
                "estimated_duration": "42 minutes",
                "production_complexity": "High - includes demonstration of actual digital preservation tools",
                "key_takeaways": [
                    "Practical framework for categorizing family knowledge by type, sensitivity, and intended recipients",
                    "Technical overview of current and emerging digital preservation mechanisms",
                    "Legal considerations for digital knowledge transfer across jurisdictions",
                    "Methods for preserving context alongside content in knowledge archives"
                ]
            },
            {
                "title": "The Trust Paradox: Building Certainty in Uncertain Times",
                "description": "Investigating how trust mechanisms—both technological and interpersonal—can create islands of certainty in an increasingly uncertain world. This episode connects cryptographic trust with governance structures and interpersonal relationships in wealth preservation.",
                "key_topics": [
                    "The evolution of trust from handshakes to smart contracts",
                    "How cryptographic certainty can enhance rather than replace human relationships",
                    "Designing governance systems that remain valid through cultural shifts",
                    "The role of continuous adaptation in maintaining trust frameworks"
                ],
                "guest_options": [
                    "Nick Szabo (Computer scientist, legal scholar, cryptographer known for pioneering smart contracts)",
                    "Rachel Botsman (Trust expert and author of 'Who Can You Trust?')",
                    "John Clippinger (Scientist at MIT Media Lab focused on trust frameworks)"
                ],
                "target_audience_segments": [
                    "Trustees and fiduciaries",
                    "Family governance specialists",
                    "Technology integrators for wealth management platforms"
                ],
                "estimated_duration": "38 minutes",
                "production_complexity": "Medium - requires clear visual explanations of cryptographic concepts",
                "key_takeaways": [
                    "How to build complementary human and technological trust systems",
                    "Methods for evaluating the long-term viability of trust mechanisms",
                    "Practical approaches to introducing new trust technologies to traditional family structures",
                    "Future-proofing governance frameworks against technological and social change"
                ]
            },
            {
                "title": "Values as Assets: The Hidden Portfolio Every Family Manages",
                "description": "Exploring how family values and principles can be cultivated, preserved, and transferred with the same intentionality as financial assets. This episode makes the case for explicit values management as a critical component of legacy planning.",
                "key_topics": [
                    "Methodologies for making implicit family values explicit",
                    "Creating governance structures that reflect and reinforce core values",
                    "Measuring values transmission success across generations",
                    "Balancing value preservation with evolution to maintain relevance"
                ],
                "guest_options": [
                    "James E. Hughes Jr. (Author of 'Family Wealth: Keeping It in the Family')",
                    "Dr. Dennis Jaffe (Research Associate at Wise Counsel Research and family business consultant)",
                    "Holly Isdale (Founder of Wealthaven, specializing in family governance)"
                ],
                "target_audience_segments": [
                    "Family meeting facilitators",
                    "Multi-generational business owners",
                    "Philanthropy advisors"
                ],
                "estimated_duration": "45 minutes",
                "production_complexity": "Low - conversation-driven with minimal production elements",
                "key_takeaways": [
                    "Practical tools for documenting and communicating family values",
                    "Frameworks for integrating values into governance and decision-making processes",
                    "Approaches to resolving values conflicts between generations",
                    "Methods for adapting core values to changing social contexts without losing essence"
                ]
            },
            {
                "title": "The Innovation Mandate: Adapting Legacy Structures for Technological Change",
                "description": "Examining how traditional wealth preservation vehicles and strategies must evolve to remain effective in the face of accelerating technological change. This episode provides a roadmap for thoughtful innovation in legacy planning.",
                "key_topics": [
                    "Evaluating emerging technologies through a legacy preservation lens",
                    "Building adaptability into long-term financial and governance structures",
                    "Case studies of successful and failed adaptation to technological shifts",
                    "The next horizon: AI, blockchain, and virtual assets in legacy planning"
                ],
                "guest_options": [
                    "Amy Webb (Futurist and Founder of Future Today Institute)",
                    "Alvin Roth (Nobel Prize economist specializing in market design)",
                    "Ari Paul (CIO of BlockTower Capital and cryptocurrency expert)"
                ],
                "target_audience_segments": [
                    "Forward-thinking estate planners",
                    "Family office innovation officers",
                    "Next-generation family members with technology interests"
                ],
                "estimated_duration": "44 minutes",
                "production_complexity": "High - requires scenario illustrations and technology demonstrations",
                "key_takeaways": [
                    "Framework for evaluating which technologies represent fundamental shifts requiring structural adaptation",
                    "Practical approaches to building experimental capacity into traditional structures",
                    "Methods for involving next-generation perspectives in legacy innovation",
                    "Balancing technological opportunity with security and continuity requirements"
                ]
            }
        ],
        
        "production_timeline": [
            {
                "phase": "Pre-Production Planning",
                "tasks": [
                    "Finalize episode concepts and sequencing",
                    "Secure guest commitments",
                    "Develop detailed episode guides and interview questions",
                    "Create production standards document",
                    "Establish workflow and team responsibilities"
                ],
                "duration": "3 weeks",
                "dependencies": ["Final approval of series concept"],
                "resource_requirements": {
                    "personnel": "Series producer, content researcher, production coordinator",
                    "technology": "Project management software, collaborative document system",
                    "budget": "$5,000-$7,500 for planning phase"
                },
                "deliverables": [
                    "Detailed production schedule",
                    "Complete episode briefs",
                    "Signed guest agreements",
                    "Production standards guide"
                ]
            },
            {
                "phase": "Content Production",
                "tasks": [
                    "Conduct and record guest interviews",
                    "Develop narrative segments and case studies",
                    "Record host segments and transitions",
                    "Produce any additional content elements (sound design, etc.)",
                    "Draft accompanying written materials"
                ],
                "duration": "6 weeks",
                "dependencies": ["Completed pre-production planning", "Guest availability"],
                "resource_requirements": {
                    "personnel": "Host, producer, audio engineer, content writer",
                    "technology": "Professional recording equipment, audio production software",
                    "facilities": "Recording studio or high-quality remote recording setup",
                    "budget": "$15,000-$20,000 for full series production"
                },
                "deliverables": [
                    "Raw interview recordings",
                    "Narrative segment recordings",
                    "Host track recordings",
                    "Draft episode guides and supplementary content"
                ]
            },
            {
                "phase": "Post-Production",
                "tasks": [
                    "Edit and mix episodes",
                    "Conduct quality review",
                    "Finalize supplementary content",
                    "Prepare distribution packages",
                    "Create promotional assets"
                ],
                "duration": "4 weeks",
                "dependencies": ["Completed content production"],
                "resource_requirements": {
                    "personnel": "Audio editor, quality control reviewer, graphic designer",
                    "technology": "Audio editing software, content management system",
                    "budget": "$8,000-$10,000 for post-production"
                },
                "deliverables": [
                    "Final mixed episodes",
                    "Complete episode guides",
                    "Distribution-ready files",
                    "Promotional graphics and clips"
                ]
            },
            {
                "phase": "Launch and Distribution",
                "tasks": [
                    "Setup podcast hosting and distribution",
                    "Implement promotional campaign",
                    "Release episodes according to schedule",
                    "Monitor performance metrics",
                    "Activate feedback channels"
                ],
                "duration": "Initial 5 weeks (continuing through series)",
                "dependencies": ["Completed post-production"],
                "resource_requirements": {
                    "personnel": "Marketing specialist, community manager, data analyst",
                    "technology": "Podcast hosting platform, analytics tools, survey system",
                    "budget": "$7,000-$12,000 for launch campaign"
                },
                "deliverables": [
                    "Active podcast presence on major platforms",
                    "Promotional campaign implementation",
                    "Initial listener data",
                    "Established feedback collection system"
                ]
            },
            {
                "phase": "Evaluation and Iteration",
                "tasks": [
                    "Analyze performance data",
                    "Compile and synthesize feedback",
                    "Conduct team retrospective",
                    "Develop recommendations for future series",
                    "Document lessons learned"
                ],
                "duration": "2 weeks (following completion of pilot series)",
                "dependencies": ["Complete series release", "Sufficient feedback collection"],
                "resource_requirements": {
                    "personnel": "Full production team, data analyst, external reviewer",
                    "technology": "Analytics platform, survey analysis tools",
                    "budget": "$3,000-$5,000 for evaluation process"
                },
                "deliverables": [
                    "Comprehensive performance report",
                    "Listener feedback analysis",
                    "Documented lessons learned",
                    "Recommendations for series continuation and expansion"
                ]
            }
        ],
        
        "feedback_loops": [
            {
                "channel": "Post-Episode Surveys",
                "description": "Short, focused surveys delivered to listeners immediately after episode completion, designed to capture immediate reactions and specific episode feedback.",
                "metrics": [
                    "Episode satisfaction rating",
                    "Most valuable content elements",
                    "Least valuable content elements",
                    "Topic comprehension self-assessment",
                    "Implementation intention"
                ],
                "integration_process": "Weekly review of survey data with production team, tagging of actionable insights for immediate implementation in upcoming episodes when possible.",
                "implementation_timeline": "48-hour response time for critical feedback; weekly integration cycle for substantive content adjustments."
            },
            {
                "channel": "Private Discord Community",
                "description": "Moderated community space for listeners to discuss episodes, share implementation experiences, and engage directly with the production team and selected guests.",
                "metrics": [
                    "Active member count",
                    "Topical discussion engagement",
                    "Question frequency and types",
                    "Implementation sharing",
                    "Community-generated content"
                ],
                "integration_process": "Community manager tags notable discussions for production team review; bi-weekly community insight report shared with content creators; direct question threads for upcoming episodes.",
                "implementation_timeline": "Continuous monitoring with formal review sessions before each new episode planning phase."
            },
            {
                "channel": "Implementation Check-ins",
                "description": "Structured follow-up process that invites listeners to share their experience applying concepts from episodes to their actual legacy planning activities.",
                "metrics": [
                    "Implementation attempt rate",
                    "Success/challenge patterns",
                    "Adaptation strategies",
                    "Long-term value assessment",
                    "Resource utilization"
                ],
                "integration_process": "Anonymized case studies compiled from implementation experiences; challenge patterns analyzed for content gaps; success stories integrated into future episodes with permission.",
                "implementation_timeline": "30-day and 90-day structured check-in points after each episode release."
            }
        ],
        
        "success_metrics": {
            "audience_growth": "20% episode-over-episode listener growth through the pilot series",
            "engagement_depth": "Average consumption of 80%+ of episode length",
            "implementation_rate": "25%+ of surveyed listeners report taking specific actions based on episode content",
            "community_activity": "10%+ of listeners participating in Discord community",
            "quality_perception": "Average rating of 4.5+ on 5-point quality scale",
            "referral_rate": "30%+ of new listeners coming from word-of-mouth referrals",
            "feedback_quality": "Receiving substantive, actionable feedback on 75%+ of feedback requests"
        },
        
        "expansion_pathway": "Following successful completion of the pilot series, expansion will proceed along two simultaneous tracks: 1) Depth - Developing the 'Top 100 Business Books' deep-dive series that applies classic business wisdom to legacy contexts, and 2) Breadth - Creating the meta-narrative documentary series that explores the real-world development of the Hard Card Universe while connecting to the fictional noir mystery storyline. This dual approach leverages the production capabilities established during the pilot while addressing both practical implementation needs and broader narrative engagement."
    }
    
    return PilotSeriesResponse(**pilot_series)
