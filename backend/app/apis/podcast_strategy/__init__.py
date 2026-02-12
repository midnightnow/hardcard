from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date, datetime

router = APIRouter()

class PodcastTopic(BaseModel):
    id: str
    title: str
    description: str
    target_audience: List[str]
    key_talking_points: List[str]
    potential_guests: List[Dict[str, str]]
    business_value: str
    alignment_to_hcu: str

class EpisodeIdea(BaseModel):
    id: str
    topic_id: str
    title: str
    description: str
    format: str
    estimated_duration: str
    key_takeaways: List[str]
    guest_requirements: Optional[str] = None
    preparation_resources: Optional[List[str]] = None

class ContentCalendarEntry(BaseModel):
    episode_id: str
    planned_release_date: str
    production_status: str
    production_start_date: str
    recording_date: Optional[str] = None
    editing_deadline: str
    promotional_assets_deadline: str
    promotional_channels: List[str]
    notes: Optional[str] = None

class FeedbackMechanism(BaseModel):
    name: str
    type: str
    description: str
    implementation_details: Dict[str, Any]
    metrics_tracked: List[str]
    integration_points: List[str]

class PodcastTopicsResponse(BaseModel):
    topics: List[PodcastTopic]
    primary_niches: List[Dict[str, str]]
    selection_criteria: List[str]
    strategic_focus: str

class ContentCalendarResponse(BaseModel):
    episodes: List[EpisodeIdea]
    calendar: List[ContentCalendarEntry]
    production_workflow: Dict[str, Any]
    editorial_guidelines: Dict[str, str]

class FeedbackMechanismsResponse(BaseModel):
    mechanisms: List[FeedbackMechanism]
    feedback_integration_process: List[str]
    success_metrics: Dict[str, str]
    
class BusinessBook(BaseModel):
    id: str
    title: str
    author: str
    publication_year: int
    summary: str
    key_themes: List[str]
    relevance_to_hcu: str
    interview_angles: List[str]

class BusinessBooksResponse(BaseModel):
    methodology: str
    episode_template: Dict[str, Dict[str, str]]
    books: List[BusinessBook]

@router.get("/topics")
def get_podcast_topics() -> PodcastTopicsResponse:
    """Returns the initial podcast topics and niches.
    
    This endpoint provides the finalized list of initial podcast topics/niches
    for the Hard Card Universe podcast series, including target audiences,
    talking points, and strategic alignment.
    """
    
    topics_data = {
        "topics": [
            {
                "id": "automation-ai",
                "title": "Automation & AI in Legacy Planning",
                "description": "Exploring how automation and artificial intelligence are transforming the way families and businesses approach long-term planning and wealth preservation.",
                "target_audience": [
                    "Tech-forward financial planners",
                    "Family office administrators",
                    "Tech entrepreneurs with growing wealth",
                    "AI and automation professionals seeking personal applications"
                ],
                "key_talking_points": [
                    "Algorithmic decision-making for multi-generational asset allocation",
                    "AI-driven risk assessment across decades-long timeframes",
                    "Automation of knowledge transfer between generations",
                    "Ethical considerations of delegating legacy decisions to AI",
                    "Case studies of successful AI integration in family offices"
                ],
                "potential_guests": [
                    {"name": "Dr. Sarah Chen", "expertise": "AI Ethics Researcher", "relevance": "Pioneer in ethical frameworks for automated decision-making in financial contexts"},
                    {"name": "Marcus Wright", "expertise": "Family Office Technology Director", "relevance": "Implemented AI systems for three major family offices"},
                    {"name": "Prof. Rajan Patel", "expertise": "Intergenerational Economics", "relevance": "Research on technology-enabled wealth transfer"}    
                ],
                "business_value": "Positions HCU as forward-thinking while connecting with tech-focused high-net-worth individuals and family offices - prime potential clients for premium services.",
                "alignment_to_hcu": "Directly supports the core HCU value proposition of leveraging technology for more effective legacy planning and wisdom transfer."
            },
            {
                "id": "storytelling-legacy",
                "title": "Narrative Economics: Storytelling as Legacy",
                "description": "Examining how the stories we tell about wealth, success, and purpose shape economic behaviors and legacy outcomes across generations.",
                "target_audience": [
                    "Family business owners",
                    "Wealth psychology professionals",
                    "Creative entrepreneurs",
                    "Parents interested in values-based inheritance planning"
                ],
                "key_talking_points": [
                    "The neuroscience of narrative and its impact on financial decision-making",
                    "How family stories create lasting frameworks for wealth management",
                    "Techniques for intentional story crafting to support legacy goals",
                    "Cross-cultural approaches to narrative-based wealth wisdom",
                    "The danger of unconscious narratives in disrupting intended legacies"
                ],
                "potential_guests": [
                    {"name": "Dr. Eleanor Banks", "expertise": "Narrative Psychology", "relevance": "Author of 'The Stories We Live By: Personal Myths and the Making of Self'"},
                    {"name": "James Harington", "expertise": "Multigenerational Family Business Consultant", "relevance": "Works with families to craft cohesive narratives that support business continuity"},
                    {"name": "Leila Washington", "expertise": "Documentary Filmmaker", "relevance": "Creates family legacy documentaries for high-net-worth clients"}    
                ],
                "business_value": "Appeals to the emotional and meaning-making aspects of wealth planning, attracting clients seeking deeper purpose beyond financial growth.",
                "alignment_to_hcu": "Reinforces the meta-narrative structure of HCU itself while providing practical frameworks for wisdom transfer."
            },
            {
                "id": "business-literature",
                "title": "Business Canon: Essential Wisdom for Generational Success",
                "description": "A deep-dive analysis series exploring the most impactful business books of all time, extracting practical wisdom for multi-generational application.",
                "target_audience": [
                    "Business book enthusiasts seeking deeper application",
                    "Entrepreneurs building legacy businesses",
                    "Parents wanting to pass business wisdom to children",
                    "Academic business researchers"
                ],
                "key_talking_points": [
                    "Timeless principles vs. contextual strategies in business literature",
                    "How business wisdom evolves and adapts across generations",
                    "Practical frameworks for applying canonical business concepts",
                    "The hidden connections between seemingly disparate business philosophies",
                    "Strategies for distilling and transferring business wisdom to heirs"
                ],
                "potential_guests": [
                    {"name": "Prof. Michaela Johnson", "expertise": "Business Literature Historian", "relevance": "Specializes in tracing the evolution of management theory through literature"},
                    {"name": "Alex Rivera", "expertise": "Business Book Publisher", "relevance": "Editorial director for major business press with insights on changing knowledge consumption"},
                    {"name": "Thomas Kwan", "expertise": "Family Business Education Director", "relevance": "Develops curriculum for next-generation family business leaders"}    
                ],
                "business_value": "Establishes HCU as an intellectual authority while reaching the business book market - a proven audience of action-takers and potential clients.",
                "alignment_to_hcu": "Directly supports the 'Top 100 Business Books' podcast series concept and strengthens the knowledge repository aspect of the platform."
            },
            {
                "id": "multi-gen-investing",
                "title": "Long Arc Investing: The Multi-Generational Portfolio",
                "description": "Exploring investment strategies, asset classes, and portfolio construction specifically designed for 50+ year time horizons and multi-generational wealth transfer.",
                "target_audience": [
                    "High-net-worth individuals with long-term planning horizons",
                    "Investment advisors to family offices",
                    "Parents planning significant inheritance structures",
                    "Financial educators and academics"
                ],
                "key_talking_points": [
                    "Time-horizon arbitrage: Exploiting opportunities only available to genuinely long-term capital",
                    "Psychological barriers to true multi-generational investment thinking",
                    "Asset classes optimized for intergenerational wealth transfer",
                    "Governance structures that maintain investment discipline across generations",
                    "The mathematics of compounding across 50+ year periods"
                ],
                "potential_guests": [
                    {"name": "Sophia Rodriguez", "expertise": "Ultra-Long-Term Investment Strategist", "relevance": "Developed the '100-Year Portfolio' framework used by sovereign wealth funds"},
                    {"name": "Dr. Kenneth Liu", "expertise": "Behavioral Finance Researcher", "relevance": "Studies cognitive biases affecting multi-generational financial planning"},
                    {"name": "Victoria Blackwell", "expertise": "Family Trust Governance Expert", "relevance": "Advises on structures to maintain investment discipline across generations"}    
                ],
                "business_value": "Directly addresses core financial concerns of high-net-worth target market while positioning HCU as genuinely long-term in perspective, unlike typical financial services.",
                "alignment_to_hcu": "Addresses the core financial component of the Hard Card mission while reinforcing the multi-generational timeframe central to the concept."
            },
            {
                "id": "digital-inheritance",
                "title": "Digital DNA: Inheritance in the Information Age",
                "description": "Investigating how digital assets, personal data, and online identities are transforming inheritance planning and creating new challenges and opportunities for legacy building.",
                "target_audience": [
                    "Tech-savvy professionals with digital assets",
                    "Digital estate planning attorneys",
                    "Cryptocurrency and NFT investors",
                    "Online business owners"
                ],
                "key_talking_points": [
                    "Legal frameworks governing digital asset inheritance across jurisdictions",
                    "Technical approaches to secure yet accessible digital legacy transfer",
                    "Cryptocurrency and tokenized asset inheritance planning",
                    "Personal data as legacy: ethical and practical considerations",
                    "Digital identity continuity and memorialization options"
                ],
                "potential_guests": [
                    {"name": "Benjamin Torres", "expertise": "Digital Estate Attorney", "relevance": "Specializes in legal frameworks for digital asset inheritance"},
                    {"name": "Dr. Michelle Zhang", "expertise": "Digital Memory Researcher", "relevance": "Studies how digital artifacts shape family memory and legacy"},
                    {"name": "Cameron Walker", "expertise": "Cryptocurrency Security Consultant", "relevance": "Develops protocols for secure crypto asset transfer upon death or incapacity"}    
                ],
                "business_value": "Addresses an emerging high-anxiety area for many potential clients while positioning HCU at the cutting edge of inheritance planning.",
                "alignment_to_hcu": "Connects to the Hard Card physical/digital bridge concept and reinforces the technology-enabled approach to legacy planning."
            },
            {
                "id": "scaling-family",
                "title": "Scale Up, Family Style: Building Business Dynasties",
                "description": "Analyzing how family businesses can implement advanced scaling techniques while preserving core values and building structures for multi-generational leadership.",
                "target_audience": [
                    "Family business owners",
                    "Next-generation family business leaders",
                    "Family business advisors and consultants",
                    "Entrepreneurs aiming to build multi-generational enterprises"
                ],
                "key_talking_points": [
                    "Adapting modern scaling frameworks (Scaling Up, Blitzscaling) to family business contexts",
                    "Governance models that balance family control with growth requirements",
                    "Talent management across family and non-family executives",
                    "Capital strategies that maintain family ownership through expansion phases",
                    "Case studies of successful multi-generational scaling efforts"
                ],
                "potential_guests": [
                    {"name": "Rebecca Morales", "expertise": "Family Business Scaling Coach", "relevance": "Helped 30+ family businesses grow while maintaining family control"},
                    {"name": "Peter Goldstein", "expertise": "Family Business Governance Architect", "relevance": "Designs governance structures enabling professional management while preserving family vision"},
                    {"name": "Anil Sharma", "expertise": "Second-Generation CEO", "relevance": "Scaled family business from $10M to $250M while maintaining family ownership"}    
                ],
                "business_value": "Connects HCU to the high-value family business market while showcasing practical implementation of key business scaling concepts.",
                "alignment_to_hcu": "Directly applies the business scaling strategies identified in the HCU strategic foundation while maintaining focus on familial legacy."
            }
        ],
        
        "primary_niches": [
            {"name": "Automation & AI", "strategic_value": "Growing field with intersection of technology and finance, attracting forward-thinking high-net-worth individuals"},
            {"name": "Storytelling & Narrative", "strategic_value": "Aligns with the meta-narrative structure of HCU while appealing to meaning-focused clients"},
            {"name": "Business Literature Analysis", "strategic_value": "Positions HCU as intellectual authority and connects to proven business book consumer market"},
            {"name": "Multi-Generational Investment", "strategic_value": "Directly addresses core concerns of target market with distinctive long-term approach"},
            {"name": "Digital Assets & Inheritance", "strategic_value": "Emerging high-anxiety area where guidance is scarce and demand is growing"},
            {"name": "Family Business Scaling", "strategic_value": "Connects to high-value family business market with practical implementation focus"}
        ],
        
        "selection_criteria": [
            "Alignment with core HCU philosophy of legacy-focused planning",
            "Distinctive positioning versus conventional financial content",
            "Addressable existing audience with proven interest",
            "Availability of credible, interesting guests",
            "Connection to practical HCU platform features",
            "Balance of abstract/philosophical and concrete/actionable content",
            "Potential for serialization and ongoing exploration"
        ],
        
        "strategic_focus": "The initial podcast topics create a portfolio approach to audience building, with each niche targeting a distinct but overlapping segment of the potential HCU client base. The topics are deliberately designed to position HCU at the intersection of cutting-edge technology, timeless wealth wisdom, and practical implementation - differentiating from both traditional financial content and futurist speculation. By establishing authority in these carefully selected niches first, HCU can build credibility before expanding to broader topics, following the beachhead strategy of focused excellence before expansion."
    }
    
    return PodcastTopicsResponse(**topics_data)

@router.get("/content-calendar")
def get_content_calendar() -> ContentCalendarResponse:
    """Returns the podcast content calendar.
    
    This endpoint provides a detailed content calendar for the first 10+ episodes
    of the Hard Card Universe podcast series, including production timelines,
    episode details, and editorial guidelines.
    """
    
    calendar_data = {
        "episodes": [
            {
                "id": "ep001",
                "topic_id": "multi-gen-investing",
                "title": "The 100-Year Portfolio: Investing on a Generational Timeline",
                "description": "Introducing the concept of truly long-term investing that spans generations, examining how investment principles change when the time horizon extends beyond a single lifetime.",
                "format": "Interview with expert + host commentary",
                "estimated_duration": "52 minutes",
                "key_takeaways": [
                    "Why conventional 'long-term' investing isn't actually long-term",
                    "The mathematical power of multi-generational compounding",
                    "Asset classes that outperform only on 50+ year timelines",
                    "Psychological barriers to implementing truly long-term strategies",
                    "Practical first steps for creating a multi-generational portfolio"
                ],
                "guest_requirements": "Investment strategist with expertise in ultra-long-term portfolio construction",
                "preparation_resources": [
                    "Research brief on historical 50+ year asset class performance",
                    "Talking points on generational wealth transfer statistics",
                    "Case studies of family offices with 100+ year investment horizons"
                ]
            },
            {
                "id": "ep002",
                "topic_id": "storytelling-legacy",
                "title": "The Story In Your Wealth: Narrative Economics and Family Legacy",
                "description": "Exploring how the stories we tell about money shape financial behaviors across generations, and how intentional narrative crafting can strengthen family legacy.",
                "format": "Expert interview + listener question segment",
                "estimated_duration": "48 minutes",
                "key_takeaways": [
                    "How family stories create mental models about wealth and success",
                    "Identifying destructive money narratives passed between generations",
                    "Techniques for intentional story crafting to support legacy goals",
                    "The neuroscience of narrative and its impact on financial decision-making",
                    "Practical exercise for documenting and analyzing your wealth story"
                ],
                "guest_requirements": "Narrative psychologist with expertise in family wealth dynamics",
                "preparation_resources": [
                    "Academic research on narrative economics",
                    "Interview guide with scenario-based questions",
                    "Collection of illustrative family wealth stories (anonymous)"
                ]
            },
            {
                "id": "ep003",
                "topic_id": "automation-ai",
                "title": "Algorithmic Legacy: AI as Your Family's Financial Guardian",
                "description": "Investigating how artificial intelligence and automation technologies are transforming long-term financial planning and creating new possibilities for wealth guardianship across generations.",
                "format": "Panel discussion with multiple experts",
                "estimated_duration": "58 minutes",
                "key_takeaways": [
                    "Current capabilities and limitations of AI in multi-generational financial planning",
                    "Ethical considerations when delegating legacy decisions to algorithms",
                    "How AI can adapt to changing conditions across decades while maintaining principles",
                    "Case studies of early AI adoption in family office settings",
                    "Practical guidance on evaluating AI financial tools for legacy planning"
                ],
                "guest_requirements": "Panel including AI ethics researcher, family office technology director, and intergenerational economics expert",
                "preparation_resources": [
                    "Technical briefing on current AI financial planning capabilities",
                    "Ethics framework for automated decision-making in wealth contexts",
                    "Family office AI implementation case studies"
                ]
            },
            {
                "id": "ep004",
                "topic_id": "business-literature",
                "title": "Good to Great to Legacy: Jim Collins Across Generations",
                "description": "First in the Business Canon series, examining Jim Collins' 'Good to Great' principles through the lens of multi-generational application, exploring how these concepts evolve beyond the founder's lifetime.",
                "format": "Literature analysis + expert commentary",
                "estimated_duration": "45 minutes",
                "key_takeaways": [
                    "The evolution of Collins' key concepts across different business eras",
                    "How 'Level 5 Leadership' principles can be cultivated across generations",
                    "Adapting the Hedgehog Concept for family business continuity",
                    "The special challenges of maintaining a culture of discipline across generations",
                    "Practical framework for applying Collins' principles in family succession planning"
                ],
                "guest_requirements": "Business literature expert with family business expertise",
                "preparation_resources": [
                    "In-depth analysis of Good to Great and Jim Collins' other works",
                    "Research on family businesses that have applied Collins' principles",
                    "Interview request to Collins' organization for comments on generational application"
                ]
            },
            {
                "id": "ep005",
                "topic_id": "digital-inheritance",
                "title": "Inheriting the Cloud: Digital Estate Planning for the 21st Century",
                "description": "Addressing the rapidly evolving landscape of digital asset inheritance, from practical account access issues to complex cryptocurrency governance models for heirs.",
                "format": "Expert interview + technical demonstration",
                "estimated_duration": "50 minutes",
                "key_takeaways": [
                    "Current legal frameworks governing digital asset inheritance",
                    "Technical approaches to secure yet accessible digital legacy transfer",
                    "Cryptocurrency inheritance planning strategies and tools",
                    "Privacy considerations when designating digital heirs",
                    "Step-by-step digital estate planning process"
                ],
                "guest_requirements": "Digital estate planning attorney with cryptocurrency expertise",
                "preparation_resources": [
                    "Legal brief on digital inheritance laws across major jurisdictions",
                    "Technical overview of digital legacy tools and services",
                    "Cryptocurrency inheritance case studies and common pitfalls"
                ]
            },
            {
                "id": "ep006",
                "topic_id": "scaling-family",
                "title": "The Family Scaling Playbook: Growth Without Losing Control",
                "description": "Analyzing how family businesses can implement advanced scaling techniques while preserving core values and building structures for multi-generational leadership.",
                "format": "Case study deep-dive + expert analysis",
                "estimated_duration": "55 minutes",
                "key_takeaways": [
                    "Adapting Scaling Up framework specifically for family business contexts",
                    "Governance models that balance family control with growth requirements",
                    "Talent development strategy spanning family and non-family executives",
                    "Capital structures that maintain family ownership through expansion",
                    "Practical implementation plan with generational transition points"
                ],
                "guest_requirements": "Family business scaling expert and successful second-generation CEO",
                "preparation_resources": [
                    "Detailed case studies of successfully scaled family businesses",
                    "Scaling Up framework adapted for family business context",
                    "Governance models comparison chart"
                ]
            },
            {
                "id": "ep007",
                "topic_id": "storytelling-legacy",
                "title": "The Art of Legacy Letters: Writing to Future Generations",
                "description": "Exploring the tradition and impact of legacy letters (ethical wills), with guidance on crafting meaningful written wisdom for heirs and descendants.",
                "format": "Workshop-style episode with exercises",
                "estimated_duration": "46 minutes",
                "key_takeaways": [
                    "Historical context and evolution of ethical wills across cultures",
                    "Psychological benefits for both writer and recipients",
                    "Structured approach to legacy letter writing with prompts and examples",
                    "Common pitfalls and how to avoid them",
                    "Options for preservation and meaningful delivery to future generations"
                ],
                "guest_requirements": "Expert in legacy writing and intergenerational communication",
                "preparation_resources": [
                    "Collection of powerful legacy letter excerpts (with permission)",
                    "Legacy letter writing prompt guide",
                    "Research on psychological impact of intergenerational written communication"
                ]
            },
            {
                "id": "ep008",
                "topic_id": "multi-gen-investing",
                "title": "Time Arbitrage: Investment Opportunities Only Available to Multigenerational Capital",
                "description": "Examining unique investment strategies and asset classes that only become viable with truly long-term (50+ year) capital, including specialized forestry, land banking, and intellectual property portfolios.",
                "format": "Investment expert roundtable",
                "estimated_duration": "62 minutes",
                "key_takeaways": [
                    "Asset classes with optimal performance only on 50+ year timelines",
                    "Structures for maintaining investment discipline across generations",
                    "Risk assessment models adapted for multi-generational time horizons",
                    "Liquidity management across multiple generations",
                    "Practical examples of actual multi-generational investment strategies"
                ],
                "guest_requirements": "Panel of specialized ultra-long-term investment managers",
                "preparation_resources": [
                    "Analyst reports on ultra-long-term asset performance",
                    "Case studies of multi-generational investment portfolios",
                    "Expert roundtable discussion guide"
                ]
            },
            {
                "id": "ep009",
                "topic_id": "business-literature",
                "title": "The 7 Habits Across Generations: Applying Covey Through Time",
                "description": "Second in the Business Canon series, examining Stephen Covey's '7 Habits of Highly Effective People' principles and how they can be applied and adapted across multiple generations of a family.",
                "format": "Literature analysis + family application stories",
                "estimated_duration": "49 minutes",
                "key_takeaways": [
                    "Intergenerational application of each of Covey's 7 habits",
                    "Adapting 'Begin with the End in Mind' for legacy planning",
                    "How 'Think Win/Win' changes family business dynamics",
                    "Multi-generational 'Sharpening the Saw' practices",
                    "Framework for teaching Covey principles to the next generation"
                ],
                "guest_requirements": "Covey organization representative and family business advisor",
                "preparation_resources": [
                    "In-depth analysis of 7 Habits and Covey's legacy-focused work",
                    "Interview with families who have applied Covey principles across generations",
                    "Visual framework for multi-generational habit application"
                ]
            },
            {
                "id": "ep010",
                "topic_id": "automation-ai",
                "title": "The Algorithmic Family Office: AI as Steward and Strategist",
                "description": "A deep dive into cutting-edge applications of artificial intelligence in family office management, wealth preservation, and legacy planning.",
                "format": "Case study analysis + technology demonstration",
                "estimated_duration": "54 minutes",
                "key_takeaways": [
                    "Current implementation of AI in sophisticated family offices",
                    "How AI can maintain family values and principles in financial decisions",
                    "Technology architecture for multi-generational decision support systems",
                    "Balancing algorithmic discipline with human judgment",
                    "Practical roadmap for gradually implementing AI in wealth management"
                ],
                "guest_requirements": "Family office technology innovator and AI implementation specialist",
                "preparation_resources": [
                    "Technical demonstration of family office AI systems",
                    "Case studies of successful AI implementations",
                    "Simplified technical architecture diagrams"
                ]
            },
            {
                "id": "ep011",
                "topic_id": "digital-inheritance",
                "title": "Crypto Across Generations: Building a Bitcoin Legacy",
                "description": "Focusing specifically on cryptocurrency inheritance planning, technical security considerations, and governance models for responsible transfer to heirs.",
                "format": "Technical tutorial + expert panel",
                "estimated_duration": "56 minutes",
                "key_takeaways": [
                    "Technical approaches to secure yet accessible cryptocurrency inheritance",
                    "Multisignature governance models involving multiple generations",
                    "Education strategies for preparing heirs to manage cryptocurrency assets",
                    "Tax and legal considerations across different jurisdictions",
                    "Step-by-step implementation of a cryptocurrency inheritance plan"
                ],
                "guest_requirements": "Cryptocurrency security expert and estate planning attorney with crypto specialization",
                "preparation_resources": [
                    "Technical security briefing on cryptocurrency inheritance options",
                    "Legal analysis of cryptocurrency inheritance by jurisdiction",
                    "Case studies of cryptocurrency inheritance successes and failures"
                ]
            },
            {
                "id": "ep012",
                "topic_id": "scaling-family",
                "title": "From Founder to Dynasty: Building the Hundred-Year Company",
                "description": "Examining how founder-led businesses can be structured from the beginning with multi-generational longevity in mind, avoiding common succession pitfalls.",
                "format": "Expert interview + founder stories",
                "estimated_duration": "53 minutes",
                "key_takeaways": [
                    "Why most founder-led companies fail to survive beyond the founder",
                    "Governance and ownership structures optimized for generational transition",
                    "Leadership development pathways for family and non-family executives",
                    "Culture preservation mechanisms that maintain founder vision",
                    "Practical early-stage decisions that enable later multi-generational success"
                ],
                "guest_requirements": "Family business succession expert and founder who successfully transitioned to next generation",
                "preparation_resources": [
                    "Family business longevity research summary",
                    "Comparative analysis of governance structures",
                    "Founder interview preparation guide"
                ]
            }
        ],
        
        "calendar": [
            {
                "episode_id": "ep001",
                "planned_release_date": "2023-07-03",
                "production_status": "Complete",
                "production_start_date": "2023-05-22",
                "recording_date": "2023-06-05",
                "editing_deadline": "2023-06-19",
                "promotional_assets_deadline": "2023-06-26",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Investment Forums"],
                "notes": "Flagship first episode - extra promotion budget allocated"
            },
            {
                "episode_id": "ep002",
                "planned_release_date": "2023-07-10",
                "production_status": "Complete",
                "production_start_date": "2023-05-29",
                "recording_date": "2023-06-12",
                "editing_deadline": "2023-06-26",
                "promotional_assets_deadline": "2023-07-03",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Psychology Forums"],
                "notes": "Guest has requested additional approval of final edit"
            },
            {
                "episode_id": "ep003",
                "planned_release_date": "2023-07-17",
                "production_status": "In Editing",
                "production_start_date": "2023-06-05",
                "recording_date": "2023-06-19",
                "editing_deadline": "2023-07-03",
                "promotional_assets_deadline": "2023-07-10",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "AI/Tech Forums"],
                "notes": "Complex panel scheduling - backup recording date on June 20 if needed"
            },
            {
                "episode_id": "ep004",
                "planned_release_date": "2023-07-24",
                "production_status": "In Production",
                "production_start_date": "2023-06-12",
                "recording_date": "2023-06-26",
                "editing_deadline": "2023-07-10",
                "promotional_assets_deadline": "2023-07-17",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Business Book Forums"],
                "notes": "First in Business Canon series - extra promotion through business literature channels"
            },
            {
                "episode_id": "ep005",
                "planned_release_date": "2023-07-31",
                "production_status": "In Planning",
                "production_start_date": "2023-06-19",
                "recording_date": "2023-07-03",
                "editing_deadline": "2023-07-17",
                "promotional_assets_deadline": "2023-07-24",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Crypto Forums", "Legal Tech Groups"],
                "notes": "Technical demonstration needs additional rehearsal time"
            },
            {
                "episode_id": "ep006",
                "planned_release_date": "2023-08-07",
                "production_status": "Initial Research",
                "production_start_date": "2023-06-26",
                "recording_date": "2023-07-10",
                "editing_deadline": "2023-07-24",
                "promotional_assets_deadline": "2023-07-31",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Family Business Forums"],
                "notes": "Case study company has requested pre-approval of discussion points"
            },
            {
                "episode_id": "ep007",
                "planned_release_date": "2023-08-14",
                "production_status": "Initial Research",
                "production_start_date": "2023-07-03",
                "recording_date": "2023-07-17",
                "editing_deadline": "2023-07-31",
                "promotional_assets_deadline": "2023-08-07",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Writing Communities"],
                "notes": "Workshop format requires additional prep materials for listeners"
            },
            {
                "episode_id": "ep008",
                "planned_release_date": "2023-08-21",
                "production_status": "Not Started",
                "production_start_date": "2023-07-10",
                "recording_date": "2023-07-24",
                "editing_deadline": "2023-08-07",
                "promotional_assets_deadline": "2023-08-14",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Investment Forums"],
                "notes": "Coordinating multiple investment experts with limited availability"
            },
            {
                "episode_id": "ep009",
                "planned_release_date": "2023-08-28",
                "production_status": "Not Started",
                "production_start_date": "2023-07-17",
                "recording_date": "2023-07-31",
                "editing_deadline": "2023-08-14",
                "promotional_assets_deadline": "2023-08-21",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Personal Development Communities"],
                "notes": "Second in Business Canon series - cross-promotion with Covey organization possible"
            },
            {
                "episode_id": "ep010",
                "planned_release_date": "2023-09-04",
                "production_status": "Not Started",
                "production_start_date": "2023-07-24",
                "recording_date": "2023-08-07",
                "editing_deadline": "2023-08-21",
                "promotional_assets_deadline": "2023-08-28",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Family Office Networks", "AI Forums"],
                "notes": "Technology demonstration requires additional technical testing"
            },
            {
                "episode_id": "ep011",
                "planned_release_date": "2023-09-11",
                "production_status": "Not Started",
                "production_start_date": "2023-07-31",
                "recording_date": "2023-08-14",
                "editing_deadline": "2023-08-28",
                "promotional_assets_deadline": "2023-09-04",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Cryptocurrency Communities"],
                "notes": "Security-sensitive content requires additional legal review"
            },
            {
                "episode_id": "ep012",
                "planned_release_date": "2023-09-18",
                "production_status": "Not Started",
                "production_start_date": "2023-08-07",
                "recording_date": "2023-08-21",
                "editing_deadline": "2023-09-04",
                "promotional_assets_deadline": "2023-09-11",
                "promotional_channels": ["Email Newsletter", "LinkedIn", "Twitter", "Entrepreneur Communities", "Family Business Forums"],
                "notes": "Potential for founder guest to share sensitive succession details"
            }
        ],
        
        "production_workflow": {
            "phases": [
                {
                    "name": "Initial Research & Planning",
                    "duration": "2 weeks",
                    "key_activities": [
                        "Topic research and angle refinement",
                        "Guest identification and preliminary outreach",
                        "Resource gathering and content outline development",
                        "Cross-reference with other episodes for continuity"
                    ],
                    "deliverables": [
                        "Detailed episode brief",
                        "Confirmed guest commitments",
                        "Initial interview question set",
                        "Production timeline"
                    ]
                },
                {
                    "name": "Pre-Production",
                    "duration": "1 week",
                    "key_activities": [
                        "Final guest preparation",
                        "Technical setup and testing",
                        "Interview question refinement",
                        "Supplementary material preparation"
                    ],
                    "deliverables": [
                        "Final interview guide",
                        "Technical setup confirmation",
                        "Host preparation notes",
                        "Episode running order"
                    ]
                },
                {
                    "name": "Recording",
                    "duration": "1 day",
                    "key_activities": [
                        "Primary interview/discussion recording",
                        "Additional host commentary recording",
                        "Sound effects and special segment recording",
                        "Initial quality check"
                    ],
                    "deliverables": [
                        "Raw episode audio files",
                        "Recording notes",
                        "Retake requirements (if any)",
                        "Initial timestamp log"
                    ]
                },
                {
                    "name": "Post-Production",
                    "duration": "2 weeks",
                    "key_activities": [
                        "Audio editing and enhancement",
                        "Segment arrangement and music integration",
                        "Fact-checking and legal review",
                        "Guest approval if required"
                    ],
                    "deliverables": [
                        "Edited episode draft",
                        "Show notes draft",
                        "Timestamped key moments",
                        "Legal clearance confirmation"
                    ]
                },
                {
                    "name": "Finalization & Delivery",
                    "duration": "1 week",
                    "key_activities": [
                        "Final edits based on feedback",
                        "Audio mastering",
                        "Show notes and transcript finalization",
                        "Upload and scheduling"
                    ],
                    "deliverables": [
                        "Final episode audio file",
                        "Complete show notes and transcript",
                        "Promotional clips and quotes",
                        "Scheduled release confirmation"
                    ]
                },
                {
                    "name": "Promotion",
                    "duration": "1 week before & 1 week after release",
                    "key_activities": [
                        "Social media campaign execution",
                        "Newsletter feature development",
                        "Guest cross-promotion coordination",
                        "Community engagement"
                    ],
                    "deliverables": [
                        "Social media assets and schedule",
                        "Newsletter content",
                        "Guest promotion kit",
                        "Community discussion prompts"
                    ]
                },
                {
                    "name": "Analysis & Integration",
                    "duration": "1 week after release",
                    "key_activities": [
                        "Performance metrics analysis",
                        "Listener feedback review",
                        "Content repurposing",
                        "Learning integration into future episodes"
                    ],
                    "deliverables": [
                        "Episode performance report",
                        "Content repurposing plan",
                        "Feedback synthesis",
                        "Recommendations for future episodes"
                    ]
                }
            ],
            "team_roles": {
                "Host": "Primary content presenter, interviewer, and narrative voice",
                "Producer": "Overall episode planning, guest coordination, and quality control",
                "Researcher": "Background material preparation, fact-checking, and content development",
                "Audio Engineer": "Recording supervision, editing, and sound quality management",
                "Community Manager": "Listener engagement, feedback collection, and community building",
                "Content Strategist": "Cross-episode continuity, HCU alignment, and narrative development"
            },
            "tools": [
                {"name": "Riverside.fm", "purpose": "High-quality remote recording"},
                {"name": "Descript", "purpose": "Audio editing and transcript generation"},
                {"name": "Asana", "purpose": "Production workflow management"},
                {"name": "Airtable", "purpose": "Content calendar and guest database"},
                {"name": "Headliner", "purpose": "Promotional clip generation"},
                {"name": "Chartable", "purpose": "Podcast analytics"}
            ]
        },
        
        "editorial_guidelines": {
            "tone": "Sophisticated but accessible - imagine a conversation between accomplished professionals who can translate complex concepts without unnecessary jargon. Thoughtful, nuanced, and occasionally philosophical, but always grounded in practical application.",
            
            "structure": "Each episode should follow a clear narrative arc with a consistent structure: 1) Compelling hook connecting to listener priorities, 2) Problem or opportunity framing, 3) Context and educational content, 4) Expert insights and practical application, 5) Connection to broader HCU themes, 6) Specific action steps or takeaways.",
            
            "content_priorities": "Prioritize timeless principles over tactical trends. Focus on content that will remain relevant for years, not months. Every episode must balance theoretical understanding with practical application. Include at least one specific, actionable framework or tool in each episode.",
            
            "hcu_integration": "Organically reference the Hard Card Universe concept at natural points, particularly when discussing implementation of concepts. Avoid forced plugs or promotional language. The content itself should demonstrate the value of the HCU approach rather than explicitly selling it.",
            
            "guest_management": "Guests should be thoroughly briefed on the multigenerational focus of the content. Redirect conversations that drift toward conventional short-term thinking. Ensure guests provide specific examples and applications, not just theory. Maintain a respectful but directive interviewing approach.",
            
            "language_guidelines": "Use inclusive language accessible to diverse listeners. Avoid insider terminology without explanation. Define specialized terms on first use. Use concrete metaphors and analogies to explain complex concepts. Frame financial concepts in terms of purpose and impact, not just numerical outcomes."
        }
    }
    
    return ContentCalendarResponse(**calendar_data)

@router.get("/feedback-mechanisms")
def get_feedback_mechanisms() -> FeedbackMechanismsResponse:
    """Returns the listener feedback mechanisms.
    
    This endpoint provides details about the various feedback mechanisms
    implemented to gather listener input and measure engagement with the
    Hard Card Universe podcast series.
    """
    
    feedback_data = {
        "mechanisms": [
            {
                "name": "Interactive Episode Polls",
                "type": "In-content Engagement",
                "description": "Time-stamped interactive polls embedded in podcast episodes that listeners can respond to via the HCU platform while listening.",
                "implementation_details": {
                    "technology": "Custom implementation in HCU platform podcast player",
                    "user_experience": "Non-disruptive overlay that appears at strategic points during playback",
                    "data_collection": "Anonymous responses aggregated by segment and episode",
                    "activation_schedule": "3-5 poll points per episode, triggered at specific timestamps"
                },
                "metrics_tracked": [
                    "Response rate by poll and episode",
                    "Response distribution across options",
                    "Time spent considering before responding",
                    "Correlation between poll engagement and overall episode completion"
                ],
                "integration_points": [
                    "Results mentioned in subsequent episodes",
                    "Aggregate insights shared in newsletter",
                    "Trend analysis across multiple episodes",
                    "Content planning for future episodes"
                ]
            },
            {
                "name": "Episode Discussion Forums",
                "type": "Community Engagement",
                "description": "Dedicated discussion spaces for each episode where listeners can share insights, ask questions, and engage with hosts, guests, and other community members.",
                "implementation_details": {
                    "technology": "Discord server with episode-specific channels",
                    "user_experience": "Threaded conversations with rich media support and host participation",
                    "data_collection": "Qualitative conversation analysis and engagement metrics",
                    "moderation": "Community guidelines with light-touch professional moderation"
                },
                "metrics_tracked": [
                    "Comments per episode",
                    "Active participants per discussion",
                    "Thread depth and conversation longevity",
                    "Question types and frequency",
                    "Host/guest engagement levels"
                ],
                "integration_points": [
                    "Selected comments read in subsequent episodes",
                    "Direct listener questions addressed by hosts",
                    "Community-driven topic suggestions",
                    "Guest recruitment from active community members"
                ]
            },
            {
                "name": "Implementation Journeys",
                "type": "Applied Learning Tracking",
                "description": "Structured process for listeners to document their application of episode concepts to their own legacy planning, with templated frameworks and progress tracking.",
                "implementation_details": {
                    "technology": "Dedicated section in HCU platform user accounts",
                    "user_experience": "Episode-linked action templates with progress tracking",
                    "data_collection": "Anonymized implementation data and completion rates",
                    "support": "Community sharing options and expert feedback on request"
                },
                "metrics_tracked": [
                    "Framework adoption rate by episode",
                    "Completion percentage of implementation steps",
                    "Time from listening to implementation",
                    "Correlation between implementation and platform engagement",
                    "Most common adaptation patterns"
                ],
                "integration_points": [
                    "Anonymous case studies in future episodes",
                    "Implementation challenges addressed in Q&A segments",
                    "Framework refinement based on user patterns",
                    "Pathway to full HCU platform onboarding"
                ]
            },
            {
                "name": "Listener Research Panel",
                "type": "Structured Feedback Group",
                "description": "Opt-in panel of dedicated listeners who participate in regular research activities including surveys, interviews, and content testing to provide deeper qualitative feedback.",
                "implementation_details": {
                    "technology": "Combination of survey platform, video interviews, and content testing portal",
                    "user_experience": "Maximum monthly time commitment with incentive structure",
                    "data_collection": "Mix of quantitative ratings and qualitative insights",
                    "panel_management": "Rotating membership with demographic balancing"
                },
                "metrics_tracked": [
                    "Episode satisfaction ratings",
                    "Content comprehension assessment",
                    "Implementation intention and barriers",
                    "Topic interest prioritization",
                    "Brand perception evolution"
                ],
                "integration_points": [
                    "Content testing prior to full production",
                    "In-depth concept validation",
                    "Format experimentation",
                    "Long-term impact assessment"
                ]
            },
            {
                "name": "Analytics Integration",
                "type": "Behavioral Data Collection",
                "description": "Comprehensive listener analytics across distribution platforms, capturing detailed engagement patterns without requiring active listener participation.",
                "implementation_details": {
                    "technology": "Chartable, Spotify for Podcasters, Apple Podcast Analytics, and custom HCU platform tracking",
                    "user_experience": "Invisible to listeners with appropriate privacy notices",
                    "data_collection": "Anonymous aggregate listening patterns",
                    "analysis": "Weekly reports with trend identification"
                },
                "metrics_tracked": [
                    "Audience growth rate by episode and topic",
                    "Listen-through rate and drop-off points",
                    "Episode completion percentages",
                    "Listening device and context data",
                    "Subscription and follow-up content engagement",
                    "Cross-episode listening patterns"
                ],
                "integration_points": [
                    "Content length optimization",
                    "Segment structure refinement",
                    "Topic performance assessment",
                    "Targeted promotion strategy"
                ]
            },
            {
                "name": "One-Click Feedback Tool",
                "type": "Friction-Minimized Input",
                "description": "Ultra-simple feedback mechanism allowing listeners to provide instant reaction to episode segments with a single interaction, plus optional elaboration.",
                "implementation_details": {
                    "technology": "Mobile app and web interface with timestamp-linked reactions",
                    "user_experience": "Always-available reaction buttons during playback",
                    "data_collection": "Timestamped reactions with content correlation",
                    "analysis": "Heat-mapping of episode content by reaction type"
                },
                "metrics_tracked": [
                    "Positive/negative reaction distribution",
                    "Content sections with highest engagement",
                    "Reaction patterns by topic and format",
                    "Correlation between reactions and other engagement metrics",
                    "Frequency of expanded comments after reactions"
                ],
                "integration_points": [
                    "Content pacing optimization",
                    "Identification of high-impact moments",
                    "Guest and topic assessment",
                    "Format effectiveness analysis"
                ]
            }
        ],
        
        "feedback_integration_process": [
            "Weekly Feedback Synthesis - Aggregation and analysis of feedback across all mechanisms into actionable insights report",
            "Bi-weekly Content Planning Review - Formal integration of feedback insights into upcoming episode planning",
            "Monthly Metrics Dashboard - Comprehensive view of all feedback mechanisms with trend analysis",
            "Quarterly Listener Experience Audit - Deep dive review of feedback systems effectiveness and listener journey mapping",
            "Cross-Functional Feedback Sessions - Regular meetings with content, technology, and business teams to align feedback to overall HCU development",
            "Direct Implementation Reports - Transparent communication to listeners about how their feedback has shaped content and features"
        ],
        
        "success_metrics": {
            "engagement_depth": "Percentage of listeners who engage with at least one feedback mechanism per episode",
            "actionable_insights": "Number of specific content or format changes implemented based on feedback per quarter",
            "feedback_diversity": "Distribution of feedback across different listener segments and mechanisms",
            "response_closure": "Percentage of identified issues or questions that receive direct response or resolution",
            "implementation_tracking": "Number of listeners documenting actual application of episode concepts",
            "community_growth": "Increase in active participation in community discussion spaces",
            "feedback_to_engagement": "Correlation between feedback provision and subsequent platform engagement"
        }
    }
    
    return FeedbackMechanismsResponse(**feedback_data)

@router.get("/business-books-podcast")
def get_business_books_podcast() -> BusinessBooksResponse:
    """Returns the business books podcast series data.
    
    This endpoint provides the research framework, episode template, and initial
    book selections for the 'Top 100 Business Books' deep-dive podcast series,
    which forms a core content pillar of the HCU ecosystem.
    """
    
    books_data = {
        "methodology": "The Top 100 Business Books series applies a rigorous multi-dimensional analysis to classic and contemporary business literature, extracting principles specifically relevant to multi-generational success. Each book is evaluated not just for its business insights, but for its applicability across time horizons, cultural contexts, and family dynamics. The series deliberately balances tactical execution guides with strategic frameworks and philosophical approaches, creating a comprehensive knowledge repository for HCU members. Books are selected based on historical impact, continuing relevance, practical applicability, and alignment with HCU core values of legacy-focused planning. Episodes follow a consistent format to help listeners build a mental model that connects insights across different works.",
        
        "episode_template": {
            "book_analysis": {
                "historical_context": "Places the book in its original business environment and outlines the problems it was addressing",
                "core_frameworks": "Breaks down the key mental models and actionable frameworks presented in the book",
                "generational_application": "Examines how the principles have evolved over time and can be applied across different generational contexts",
                "critical_evaluation": "Balanced assessment of strengths and limitations when applied to modern legacy planning"
            },
            "practical_implementation": {
                "adaptation_guidelines": "Specific guidance on how to adapt the book's principles for family business and legacy contexts",
                "case_examples": "Real-world examples of how families have successfully implemented these principles",
                "common_pitfalls": "Typical mistakes made when applying these concepts in a multi-generational context",
                "implementation_timeline": "Recommended staging of implementation across different time horizons"
            },
            "guest_segment": {
                "expert_perspective": "Interview with domain expert offering deeper insights on specific aspects of the book",
                "practitioner_experience": "Conversation with someone who has implemented the book's principles in a family or legacy context",
                "cross_disciplinary_connections": "Exploration of how the book's ideas connect to other domains like psychology, technology, or governance"
            },
            "action_guide": {
                "reflection_questions": "Thoughtful prompts to help listeners process the ideas in relation to their own situation",
                "next_steps": "3-5 concrete actions listeners can take to begin applying the key principles",
                "resources": "Additional learning materials, tools, and resources to support implementation",
                "hcu_platform_integration": "How these concepts connect to specific features and capabilities within the HCU platform"
            }
        },
        
        "books": [
            {
                "id": "good-to-great",
                "title": "Good to Great",
                "author": "Jim Collins",
                "publication_year": 2001,
                "summary": "Collins' research-based examination of how companies transition from average to exceptional performance, with principles like Level 5 Leadership, the Hedgehog Concept, and building a culture of discipline.",
                "key_themes": [
                    "Level 5 Leadership - humble yet determined leaders",
                    "First Who, Then What - getting the right people on the bus",
                    "The Hedgehog Concept - focused excellence at the intersection of passion, economic engine, and capability",
                    "Culture of Discipline - rigorous thinking and execution without bureaucracy",
                    "Technology Accelerators - selective technology adoption"
                ],
                "relevance_to_hcu": "Provides a foundational framework for building lasting institutional excellence that can be applied to family business governance and succession planning. The principles of disciplined people, thought, and action translate directly to legacy structure building.",
                "interview_angles": [
                    "Evolving the Hedgehog Concept across generations while maintaining focus",
                    "Developing Level 5 Leadership qualities in next-generation family members",
                    "Building and maintaining a culture of discipline through ownership transitions",
                    "Adapting Collins' 'First Who' principle to family dynamics where 'getting off the bus' isn't always an option"
                ]
            },
            {
                "id": "7-habits",
                "title": "The 7 Habits of Highly Effective People",
                "author": "Stephen R. Covey",
                "publication_year": 1989,
                "summary": "Covey's principle-centered paradigm for personal and interpersonal effectiveness, emphasizing proactivity, beginning with the end in mind, and thinking win-win in a framework of character ethics.",
                "key_themes": [
                    "Be Proactive - taking responsibility for your choices and their consequences",
                    "Begin with the End in Mind - defining clear vision and principles",
                    "Put First Things First - prioritizing based on importance, not urgency",
                    "Think Win-Win - seeking mutual benefit in human interactions",
                    "Seek First to Understand, Then to Be Understood - empathic listening",
                    "Synergize - cooperative creative process",
                    "Sharpen the Saw - balanced self-renewal"
                ],
                "relevance_to_hcu": "Offers a values-based approach to effectiveness that creates a common language for multi-generational planning. The habit of 'beginning with the end in mind' perfectly aligns with legacy planning, while habits like 'think win-win' provide frameworks for navigating complex family dynamics in wealth distribution.",
                "interview_angles": [
                    "Applying 'Begin with the End in Mind' to 100+ year legacy planning",
                    "Using the 4 Quadrants to prioritize actions for both short and long-term legacy building",
                    "Developing emotional bank accounts across generational boundaries",
                    "Creating family mission statements that endure across generations"
                ]
            },
            {
                "id": "innovators-dilemma",
                "title": "The Innovator's Dilemma",
                "author": "Clayton Christensen",
                "publication_year": 1997,
                "summary": "Christensen's analysis of how successful companies can fail precisely because they do everything 'right' according to established management principles, but miss disruptive innovations that eventually upend their markets.",
                "key_themes": [
                    "Sustaining vs. Disruptive Technologies - the difference between incremental and revolutionary change",
                    "Value Networks - why organizations struggle to value innovations that don't serve existing customers",
                    "Small Markets Don't Solve Growth Needs - why big companies ignore emerging opportunities",
                    "Capabilities vs. Disabilities - how strengths become weaknesses",
                    "Technology Supply vs. Market Demand - the mismatch that creates opportunity"
                ],
                "relevance_to_hcu": "Provides critical insight into why successful family businesses often fail in subsequent generations - they continue doing what made them successful initially, even as markets and technologies change. Offers a framework for balancing respect for tradition with openness to disruptive innovation.",
                "interview_angles": [
                    "Creating separate structures for disruptive innovation within family businesses",
                    "Balancing preservation of core business with exploration of new opportunities across generations",
                    "Developing next-generation leadership that can both respect and challenge established business models",
                    "Applying resource allocation theories to family business capital decisions"
                ]
            },
            {
                "id": "crossing-chasm",
                "title": "Crossing the Chasm",
                "author": "Geoffrey Moore",
                "publication_year": 1991,
                "summary": "Moore's marketing strategy framework for high-tech products, identifying the critical gap between early adopters and mainstream markets, with strategies for successfully crossing this 'chasm'.",
                "key_themes": [
                    "Technology Adoption Life Cycle - the bell curve of innovation adoption",
                    "The Chasm - the gap between early adopters and the early majority",
                    "Whole Product Concept - extending beyond core product to everything needed for mainstream success",
                    "Bowling Alley Strategy - targeting niche markets as entry points",
                    "Tornado Phase - rapid mainstream adoption"
                ],
                "relevance_to_hcu": "Offers a strategic framework for family businesses navigating major market transitions or launching new ventures. Particularly valuable for multi-generational businesses that need to evolve beyond their core markets while maintaining their fundamental identities and values.",
                "interview_angles": [
                    "Applying the chasm model to generational transitions in family businesses",
                    "Using the bowling alley strategy for controlled expansion of family business into new domains",
                    "Developing the 'whole product' concept for comprehensive legacy planning",
                    "Managing the tornado phase of rapid growth while maintaining family control and values"
                ]
            },
            {
                "id": "5-dysfunctions",
                "title": "The Five Dysfunctions of a Team",
                "author": "Patrick Lencioni",
                "publication_year": 2002,
                "summary": "Lencioni's leadership fable identifying five interconnected dysfunctions that undermine team effectiveness: absence of trust, fear of conflict, lack of commitment, avoidance of accountability, and inattention to results.",
                "key_themes": [
                    "Building Trust - vulnerability-based trust as the foundation",
                    "Mastering Conflict - engaging in productive ideological debate",
                    "Achieving Commitment - clarity and buy-in despite initial disagreement",
                    "Embracing Accountability - peer-to-peer accountability for performance",
                    "Focusing on Results - collective outcomes over individual recognition"
                ],
                "relevance_to_hcu": "Directly applicable to family business dynamics, where team dysfunction is often magnified by familial relationships. Provides a framework for developing healthy team cultures that can sustain across generational transitions and prevent destructive family business patterns.",
                "interview_angles": [
                    "Adapting Lencioni's trust-building approaches for family business contexts",
                    "Developing constructive conflict norms that work across generations",
                    "Creating accountability systems that function despite family hierarchies",
                    "Balancing family harmony with organizational results focus"
                ]
            }
        ]
    }
    
    return BusinessBooksResponse(**books_data)
