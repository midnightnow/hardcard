from typing import List, Dict, Optional, Any
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class BeachheadMarket(BaseModel):
    """Model for a beachhead market in the scaling playbook"""
    id: str
    name: str
    description: str
    target_audience: Dict[str, Any]
    market_size: Dict[str, Any]
    acquisition_channels: List[Dict[str, Any]]
    indicators: Dict[str, Any]
    competitive_landscape: List[Dict[str, Any]]
    rationale: str

class BigRockPriority(BaseModel):
    """Model for a 'Big Rock' priority in the scaling playbook"""
    id: str
    name: str
    description: str
    success_criteria: List[str]
    dependencies: Optional[List[str]] = None
    timeline: Dict[str, Any]
    resources_required: Dict[str, Any]
    owner: str
    status: str
    metrics: List[Dict[str, Any]]

class TaskItem(BaseModel):
    """Model for a task item in the backlog"""
    id: str
    title: str
    description: str
    priority: str
    effort: str
    impact: str
    category: str
    owner: Optional[str] = None
    dependencies: Optional[List[str]] = None
    status: str

class BudgetItem(BaseModel):
    """Model for a budget item in the scaling playbook"""
    id: str
    category: str
    description: str
    amount: float
    timeframe: str
    flexibility: str
    notes: Optional[str] = None

class KpiItem(BaseModel):
    """Model for a KPI in the scaling playbook"""
    id: str
    name: str
    description: str
    target: Any
    measurement_frequency: str
    data_source: str
    owner: str
    rationale: str

class BlitzscalingPhase(BaseModel):
    """Model for a blitzscaling phase in the scaling playbook"""
    id: str
    name: str
    description: str
    key_focus: List[str]
    trigger_metrics: Dict[str, Any]
    primary_challenges: List[Dict[str, str]]
    structural_changes: List[Dict[str, str]]
    investment_profile: Dict[str, Any]

class BusinessScalingPlaybookResponse(BaseModel):
    """Response model for the business scaling playbook"""
    overview: Dict[str, Any]
    beachhead_market: BeachheadMarket
    big_rock_priorities: List[BigRockPriority]
    task_backlog: List[TaskItem]
    budget_sketch: List[BudgetItem]
    kpis: List[KpiItem]
    scaling_phases: List[BlitzscalingPhase]
    lean_methodology: Dict[str, Any]
    blitzscaling_approach: Dict[str, Any]

@router.get("/business-scaling-playbook")
def get_business_scaling_playbook() -> BusinessScalingPlaybookResponse:
    """Returns the Business Scaling Playbook for the HCU ecosystem.
    
    This endpoint provides a comprehensive plan that integrates Lean and Blitzscaling 
    methodologies to guide the strategic growth of the Hard Card Universe ecosystem, 
    including beachhead market selection, key priorities, task backlog, budget 
    allocation, KPIs, and scaling phases.
    """
    
    playbook_data = {
        "overview": {
            "vision": "The Hard Card Universe Business Scaling Playbook provides a strategic framework for rapidly scaling the HCU ecosystem while maintaining coherence across modules and narrative vehicles. By integrating Lean Methodology principles with Blitzscaling approaches, this playbook enables aggressive yet sustainable growth that preserves the core values of legacy-building and intergenerational wealth transfer while creating a vibrant business ecosystem.",
            
            "guiding_principles": [
                "Speed + Learning: Prioritize rapid execution with embedded feedback loops",
                "Coherence at Scale: Maintain narrative and technical consistency across growing modules",
                "Beachhead Focus: Concentrate resources on dominating specific niches before expanding",
                "80/20 Prioritization: Relentlessly focus on the vital few activities that drive disproportionate results",
                "Module Independence: Design for independent scaling while preserving ecosystem benefits",
                "Legacy First: Ensure all scaling decisions reinforce the core legacy-building mission"
            ],
            
            "scaling_strategy": "The HCU scaling approach follows a deliberate three-horizon model: (1) Establish the podcast beachhead with deep audience engagement and partnership network, (2) Expand into complementary content and community offerings leveraging established audience and partnerships, and (3) Develop full-featured technical and financial products once narrative foundation and audience are established. This sequencing allows for progressive scaling of complexity and resource requirements while building on proven success."
        },
        
        "beachhead_market": {
            "id": "beachhead-1",
            "name": "High-Net-Worth Family Decision-Makers",
            "description": "High-net-worth individuals (primarily 35-55 years old) who are actively making legacy planning decisions for their families and seeking sophisticated approaches that balance wealth preservation with forward-thinking investments for future generations.",
            "target_audience": {
                "demographics": {
                    "age_range": "35-55",
                    "income_level": "High net worth ($5M+ investable assets)",
                    "education": "Advanced degrees or equivalent experience",
                    "family_status": "Parents with minor children or young adults"
                },
                "psychographics": {
                    "values": ["Legacy creation", "Family security", "Innovation", "Long-term thinking"],
                    "interests": ["Wealth management", "Technology trends", "Future planning", "Education"],
                    "pain_points": ["Traditional inheritance models feel outdated", "Concern about preparing next generation", "Seeking balance between security and innovation", "Desire for meaningful legacy beyond financial assets"]
                },
                "behavior_patterns": {
                    "information_consumption": ["Premium podcasts", "Curated newsletters", "Executive education", "Private wealth forums"],
                    "decision_making": "Research-intensive, advisor-influenced, values-aligned",
                    "relationship_preferences": "High-touch, exclusive, community-oriented"
                }
            },
            "market_size": {
                "total_addressable_market": {
                    "households": "1.8 million in US",
                    "assets_under_consideration": "$10+ trillion in intergenerational transfer over next decade"
                },
                "serviceable_available_market": {
                    "households": "350,000 actively seeking advanced legacy planning",
                    "annual_spending": "$3.5B on legacy planning services and solutions"
                },
                "serviceable_obtainable_market": {
                    "year_1": "5,000 active podcast listeners, 500 community members",
                    "year_3": "50,000 active users across ecosystem"
                }
            },
            "acquisition_channels": [
                {
                    "channel": "Wealth Management Partnerships",
                    "strategy": "Collaborate with forward-thinking wealth management firms seeking differentiation",
                    "cost_structure": "Revenue share and co-marketing",
                    "expected_conversion": "3-5% of introduced clients"
                },
                {
                    "channel": "Executive Podcast Networks",
                    "strategy": "Secure placement and cross-promotion on existing high-end podcast networks",
                    "cost_structure": "$2-5K per episode placement",
                    "expected_conversion": "2% of listeners to HCU podcast"
                },
                {
                    "channel": "Educational Webinars and Events",
                    "strategy": "Host exclusive content with strategic partners on future-focused legacy topics",
                    "cost_structure": "$5-10K per event production",
                    "expected_conversion": "10-15% of attendees to HCU community"
                },
                {
                    "channel": "Thought Leadership Content",
                    "strategy": "Place original research and perspective in publications targeting HNW audience",
                    "cost_structure": "$3-7K per content piece production and placement",
                    "expected_conversion": "1-2% of readers to email subscribers"
                }
            ],
            "indicators": {
                "positive_signals": [
                    "High completion rates (>80%) for legacy-focused podcast episodes",
                    "Above-benchmark engagement in community discussions on intergenerational topics",
                    "Inbound partnership inquiries from wealth management services",
                    "Willingness to participate in exclusive research and feedback sessions"
                ],
                "watch_outs": [
                    "Low conversion from general content to legacy-specific offerings",
                    "Resistance to technological aspects of modern legacy concepts",
                    "Price sensitivity for premium community offerings",
                    "Preference for traditional advisor relationships over community models"
                ]
            },
            "competitive_landscape": [
                {
                    "competitor_type": "Traditional Wealth Management Firms",
                    "strengths": ["Established trust", "Regulatory compliance", "Full-service offering"],
                    "weaknesses": ["Innovation lag", "Outdated legacy concepts", "Limited community engagement"],
                    "differentiation": "HCU combines traditional security with innovative approaches and community learning"
                },
                {
                    "competitor_type": "Digital Estate Planning Platforms",
                    "strengths": ["Technological efficiency", "Lower cost structure", "Modern interfaces"],
                    "weaknesses": ["Limited human guidance", "Narrow focus on documents/assets", "Minimal narrative elements"],
                    "differentiation": "HCU weaves technical solutions into meaningful narrative frameworks with human guidance"
                },
                {
                    "competitor_type": "Legacy/Memoir Services",
                    "strengths": ["Emotional resonance", "Storytelling expertise", "Personalization"],
                    "weaknesses": ["Limited financial integration", "One-time service vs. platform", "Scale limitations"],
                    "differentiation": "HCU integrates narrative with substantive financial and technological infrastructure"
                }
            ],
            "rationale": "This beachhead market offers the ideal combination of financial capacity, motivation (family legacy planning), and receptiveness to innovation within a traditional space. Their influence as early adopters will create both immediate sustainability and pathways to adjacent markets. Most importantly, their goals align perfectly with HCU's mission of meaningful intergenerational legacy building enhanced by technology and community. Starting with this focused audience allows for depth of value delivery and learning before expanding to broader markets."
        },
        
        "big_rock_priorities": [
            {
                "id": "big-rock-1",
                "name": "Podcast Launch and Growth",
                "description": "Establish the podcast as the primary content vehicle and audience acquisition channel for the ecosystem, with a focus on rapid production quality improvement, audience growth, and community conversion.",
                "success_criteria": [
                    "5,000+ regular listeners within 90 days of launch",
                    "15% conversion rate from listeners to email subscribers",
                    "3% conversion rate from email subscribers to community members",
                    "80%+ episode completion rate",
                    "Consistent 5-star rating average with 50+ reviews"
                ],
                "timeline": {
                    "phase_1": "Weeks 1-4: Production infrastructure and pilot episodes",
                    "phase_2": "Weeks 5-8: Initial release and audience building",
                    "phase_3": "Weeks 9-12: Optimization and conversion focus",
                    "phase_4": "Weeks 13+: Scaling and guest expansion"
                },
                "resources_required": {
                    "team": ["Content Director (lead)", "Production Lead", "Marketing Coordinator"],
                    "budget": "$50,000 initial investment (equipment, production, promotion)",
                    "tools": ["Professional recording setup", "Editing software", "Distribution platform", "Analytics suite"]
                },
                "owner": "Content Director",
                "status": "In Progress",
                "metrics": [
                    {
                        "metric": "Weekly Listener Growth Rate",
                        "target": "20% week-over-week for first 8 weeks",
                        "current": "N/A - Pre-launch"
                    },
                    {
                        "metric": "Production Efficiency",
                        "target": "7 days from recording to publication",
                        "current": "14 days - pilot phase"
                    },
                    {
                        "metric": "Audience Engagement Score",
                        "target": "8.5/10 composite score based on retention, sharing, and interaction",
                        "current": "N/A - Pre-launch"
                    }
                ]
            },
            {
                "id": "big-rock-2",
                "name": "Community Hub Development",
                "description": "Build and nurture an active, engaged community platform that serves as both a value delivery mechanism for members and a source of insight and co-creation for the HCU ecosystem.",
                "success_criteria": [
                    "500+ active members within 90 days of launch",
                    "70%+ weekly active user retention",
                    "10+ hours average monthly engagement per active user",
                    "25%+ of discussions initiated by community members (not team)",
                    "Net Promoter Score of 50+ from community survey"
                ],
                "dependencies": ["Podcast Launch and Initial Audience"],
                "timeline": {
                    "phase_1": "Weeks 1-3: Platform selection and configuration",
                    "phase_2": "Weeks 4-6: Soft launch with founding members",
                    "phase_3": "Weeks 7-10: Public launch and growth initiatives",
                    "phase_4": "Weeks 11+: Programming optimization and member leadership"
                },
                "resources_required": {
                    "team": ["Community Manager (lead)", "Content Contributor(s)", "Technical Support"],
                    "budget": "$30,000 initial investment (platform, moderation, programming)",
                    "tools": ["Community platform subscription", "Moderation tools", "Analytics dashboard", "Content creation assets"]
                },
                "owner": "Community Manager",
                "status": "Planning",
                "metrics": [
                    {
                        "metric": "Member Growth Rate",
                        "target": "15% week-over-week for first 12 weeks",
                        "current": "N/A - Pre-launch"
                    },
                    {
                        "metric": "Engagement Depth",
                        "target": "60% of members posting/commenting at least weekly",
                        "current": "N/A - Pre-launch"
                    },
                    {
                        "metric": "Value Perception",
                        "target": "85% of surveyed members rate community as 'highly valuable'",
                        "current": "N/A - Pre-launch"
                    }
                ]
            },
            {
                "id": "big-rock-3",
                "name": "Strategic Partnerships",
                "description": "Develop and formalize key strategic partnerships that extend the reach, enhance the credibility, and expand the resources available to the HCU ecosystem.",
                "success_criteria": [
                    "3+ established partnerships with wealth management firms/platforms",
                    "1+ major media/publishing partnership",
                    "1+ technological infrastructure partnership",
                    "25%+ of new audience acquisition from partner channels",
                    "$100K+ value creation (direct or indirect) from partnerships"
                ],
                "timeline": {
                    "phase_1": "Weeks 1-4: Partnership strategy and target identification",
                    "phase_2": "Weeks 5-12: Initial outreach and relationship building",
                    "phase_3": "Weeks 13-16: Proposal development and negotiation",
                    "phase_4": "Weeks 17+: Implementation and optimization"
                },
                "resources_required": {
                    "team": ["Partnership Director (lead)", "Strategic Lead", "Content Director"],
                    "budget": "$25,000 initial investment (outreach, materials, relationship development)",
                    "tools": ["CRM system", "Proposal templates", "Value analysis framework", "Partnership dashboard"]
                },
                "owner": "Partnership Director",
                "status": "Early Planning",
                "metrics": [
                    {
                        "metric": "Partnership Pipeline Value",
                        "target": "$500K potential annual value in negotiation pipeline",
                        "current": "$50K - Initial discussions"
                    },
                    {
                        "metric": "Partner Satisfaction Score",
                        "target": "9/10 average partner satisfaction rating",
                        "current": "N/A - No formal partnerships yet"
                    },
                    {
                        "metric": "Audience Referral Rate",
                        "target": "100+ new audience members weekly from partner channels",
                        "current": "N/A - Pre-partnership launch"
                    }
                ]
            },
            {
                "id": "big-rock-4",
                "name": "Business Books Series Development",
                "description": "Create the foundation for the Top 100 Business Books podcast series as a cornerstone content vehicle that demonstrates intellectual depth while building audience and partnership opportunities.",
                "success_criteria": [
                    "Complete curriculum and selection criteria for 100 books",
                    "Episode template and production approach standardized",
                    "10+ guest experts confirmed for initial episodes",
                    "Production capacity established for consistent release schedule",
                    "Promotional strategy and partner tie-ins developed"
                ],
                "dependencies": ["Podcast Launch and Initial Production Learning"],
                "timeline": {
                    "phase_1": "Weeks 1-6: Research and book selection methodology",
                    "phase_2": "Weeks 7-12: Curriculum development and sequencing",
                    "phase_3": "Weeks 13-18: Production approach and template creation",
                    "phase_4": "Weeks 19+: Guest outreach and initial episode planning"
                },
                "resources_required": {
                    "team": ["Editorial Lead (lead)", "Content Director", "Research Support"],
                    "budget": "$35,000 initial investment (research, content development, guest acquisition)",
                    "tools": ["Research database access", "Content management system", "Expert network platform"]
                },
                "owner": "Editorial Lead",
                "status": "Not Started",
                "metrics": [
                    {
                        "metric": "Research Completion",
                        "target": "100% of book list researched with clear selection rationale",
                        "current": "15% - Initial research phase"
                    },
                    {
                        "metric": "Expert Engagement",
                        "target": "30+ subject matter experts contributing to curriculum",
                        "current": "3 - Initial advisors only"
                    },
                    {
                        "metric": "Production Readiness",
                        "target": "Complete production system capable of 2 episodes weekly",
                        "current": "10% - Conceptual planning only"
                    }
                ]
            }
        ],
        
        "task_backlog": [
            {
                "id": "task-1",
                "title": "Define Podcast Format and Structure",
                "description": "Develop the detailed format, structure, and segments for the main podcast series, including intro/outro, recurring segments, and episode flow.",
                "priority": "Critical",
                "effort": "Medium",
                "impact": "High",
                "category": "Content Development",
                "owner": "Content Director",
                "status": "In Progress"
            },
            {
                "id": "task-2",
                "title": "Develop Brand Identity System",
                "description": "Create comprehensive brand identity including visual language, messaging framework, and tone guidelines for consistent application across all touchpoints.",
                "priority": "High",
                "effort": "High",
                "impact": "High",
                "category": "Marketing",
                "owner": "Brand Director",
                "status": "Not Started"
            },
            {
                "id": "task-3",
                "title": "Build Initial Content Calendar",
                "description": "Develop 90-day content calendar for podcast episodes, community programming, and supporting content with themes, topics, and resource assignments.",
                "priority": "High",
                "effort": "Medium",
                "impact": "High",
                "category": "Content Development",
                "owner": "Content Director",
                "dependencies": ["task-1"],
                "status": "Not Started"
            },
            {
                "id": "task-4",
                "title": "Configure Analytics Infrastructure",
                "description": "Set up comprehensive analytics tracking across podcast, website, community, and other touchpoints for unified data collection and reporting.",
                "priority": "High",
                "effort": "Medium",
                "impact": "Medium",
                "category": "Technology",
                "owner": "Technology Lead",
                "status": "Not Started"
            },
            {
                "id": "task-5",
                "title": "Develop Partnership Prospectus",
                "description": "Create compelling partnership overview document detailing value proposition, audience, opportunities, and success metrics for potential strategic partners.",
                "priority": "Medium",
                "effort": "Medium",
                "impact": "High",
                "category": "Partnerships",
                "owner": "Partnership Director",
                "status": "Not Started"
            },
            {
                "id": "task-6",
                "title": "Select and Configure Community Platform",
                "description": "Research, select, and configure the optimal community platform based on functionality requirements, user experience, and scalability needs.",
                "priority": "High",
                "effort": "High",
                "impact": "High",
                "category": "Community",
                "owner": "Community Manager",
                "status": "Not Started"
            },
            {
                "id": "task-7",
                "title": "Develop Community Guidelines and Governance",
                "description": "Create comprehensive community guidelines, moderation approach, and governance structure for maintaining healthy, valuable community environment.",
                "priority": "Medium",
                "effort": "Medium",
                "impact": "High",
                "category": "Community",
                "owner": "Community Manager",
                "dependencies": ["task-6"],
                "status": "Not Started"
            },
            {
                "id": "task-8",
                "title": "Create Audience Growth Strategy",
                "description": "Develop comprehensive strategy for audience acquisition and growth across channels, including targeting, messaging, and conversion optimization.",
                "priority": "High",
                "effort": "Medium",
                "impact": "Critical",
                "category": "Marketing",
                "owner": "Marketing Lead",
                "status": "Not Started"
            },
            {
                "id": "task-9",
                "title": "Develop Feedback Collection System",
                "description": "Create systematic approach to collecting, analyzing, and implementing audience feedback across all touchpoints of the ecosystem.",
                "priority": "Medium",
                "effort": "Medium",
                "impact": "High",
                "category": "Product Development",
                "owner": "Product Lead",
                "status": "Not Started"
            },
            {
                "id": "task-10",
                "title": "Research Business Books Curriculum",
                "description": "Conduct comprehensive research to identify and evaluate potential books for inclusion in the Top 100 Business Books series, including selection criteria development.",
                "priority": "Medium",
                "effort": "High",
                "impact": "High",
                "category": "Content Development",
                "owner": "Editorial Lead",
                "status": "Not Started"
            }
        ],
        
        "budget_sketch": [
            {
                "id": "budget-1",
                "category": "Content Production",
                "description": "Podcast production equipment, software, services, production team time, and associated content creation costs",
                "amount": 75000.00,
                "timeframe": "First 6 months",
                "flexibility": "Medium",
                "notes": "Front-loaded for equipment acquisition, expected to decrease after initial setup"
            },
            {
                "id": "budget-2",
                "category": "Community Platform",
                "description": "Platform subscription, customization, moderation tools, and community management resources",
                "amount": 35000.00,
                "timeframe": "First 6 months",
                "flexibility": "Low",
                "notes": "Critical infrastructure element, limited flexibility once platform is selected"
            },
            {
                "id": "budget-3",
                "category": "Marketing & Audience Growth",
                "description": "Promotion, partnership development, content distribution, and audience acquisition initiatives",
                "amount": 60000.00,
                "timeframe": "First 6 months",
                "flexibility": "High",
                "notes": "Highly adaptable based on channel performance and growth opportunities"
            },
            {
                "id": "budget-4",
                "category": "Research & Development",
                "description": "Business books research, curriculum development, guest expert coordination, and content planning",
                "amount": 40000.00,
                "timeframe": "First 6 months",
                "flexibility": "Medium",
                "notes": "Can be accelerated or decelerated based on other priorities"
            },
            {
                "id": "budget-5",
                "category": "Team & Operations",
                "description": "Core team resources, project management, tools, and operational expenses",
                "amount": 90000.00,
                "timeframe": "First 6 months",
                "flexibility": "Low",
                "notes": "Essential foundation for execution capability"
            },
            {
                "id": "budget-6",
                "category": "Technology Infrastructure",
                "description": "Website, analytics, integration tools, automation, and technical development",
                "amount": 45000.00,
                "timeframe": "First 6 months",
                "flexibility": "Medium",
                "notes": "Some elements can be phased, but core infrastructure is critical"
            },
            {
                "id": "budget-7",
                "category": "Contingency & Opportunity Fund",
                "description": "Reserved funds for unexpected needs, emergent opportunities, or strategic pivots",
                "amount": 30000.00,
                "timeframe": "First 6 months",
                "flexibility": "High",
                "notes": "Designed for maximum adaptability to unforeseen circumstances"
            }
        ],
        
        "kpis": [
            {
                "id": "kpi-1",
                "name": "Audience Growth Rate",
                "description": "Weekly percentage growth in podcast listeners and content consumers across the ecosystem",
                "target": "20% week-over-week for first 12 weeks, then 10% week-over-week for next 12 weeks",
                "measurement_frequency": "Weekly",
                "data_source": "Podcast analytics, website analytics, email list growth",
                "owner": "Marketing Lead",
                "rationale": "Primary indicator of market resonance and acquisition effectiveness"
            },
            {
                "id": "kpi-2",
                "name": "Engagement Depth",
                "description": "Average time spent engaging with content and community per active user",
                "target": "60 minutes weekly per active user across all touchpoints",
                "measurement_frequency": "Weekly",
                "data_source": "Podcast completion rates, community time, website time",
                "owner": "Content Director",
                "rationale": "Measures value delivery and audience relationship strength"
            },
            {
                "id": "kpi-3",
                "name": "Conversion Funnel Performance",
                "description": "Conversion rates between key stages of audience journey from discovery to community membership",
                "target": "Listener to Subscriber: 15%, Subscriber to Community Member: 10%",
                "measurement_frequency": "Weekly",
                "data_source": "Cross-platform analytics and user journey tracking",
                "owner": "Marketing Lead",
                "rationale": "Indicates effectiveness of value proposition and experience design"
            },
            {
                "id": "kpi-4",
                "name": "Partnership Value Creation",
                "description": "Total value (direct revenue, audience acquisition, resource access) generated through strategic partnerships",
                "target": "$250K equivalent value in first 6 months",
                "measurement_frequency": "Monthly",
                "data_source": "Partnership reporting, attribution tracking, valuation model",
                "owner": "Partnership Director",
                "rationale": "Measures effectiveness of leverage strategy and ecosystem development"
            },
            {
                "id": "kpi-5",
                "name": "Content Production Efficiency",
                "description": "Time and resource requirements to produce standardized unit of high-quality content",
                "target": "7 days from concept to publication, $1,000 fully-loaded cost per episode",
                "measurement_frequency": "Per Production Cycle",
                "data_source": "Production tracking, resource allocation, time tracking",
                "owner": "Production Lead",
                "rationale": "Critical for scaling content output while maintaining quality"
            },
            {
                "id": "kpi-6",
                "name": "Net Promoter Score",
                "description": "Likelihood of audience to recommend HCU content and community to others",
                "target": "50+ NPS for podcast, 60+ NPS for community",
                "measurement_frequency": "Monthly",
                "data_source": "User surveys, feedback collection",
                "owner": "Community Manager",
                "rationale": "Leading indicator of organic growth potential and satisfaction"
            },
            {
                "id": "kpi-7",
                "name": "Learning Cycle Time",
                "description": "Time required to collect feedback, analyze, implement changes, and measure impact",
                "target": "14 days from identification to implemented solution",
                "measurement_frequency": "Per Learning Cycle",
                "data_source": "Project management tracking, improvement logs",
                "owner": "Product Lead",
                "rationale": "Fundamental to adaptation speed and competitive advantage"
            }
        ],
        
        "scaling_phases": [
            {
                "id": "phase-1",
                "name": "Family - Foundation Building",
                "description": "Establish core audience, content production capability, and community foundation with sustainable operations and clear product-market fit.",
                "key_focus": [
                    "Content quality and consistency",
                    "Audience relationships and insights",
                    "Operational foundations and processes",
                    "Initial partnership development"
                ],
                "trigger_metrics": {
                    "audience_size": "5,000+ regular listeners",
                    "engagement": "60+ minutes weekly per active user",
                    "team_capacity": "Core functions staffed with defined processes",
                    "unit_economics": "Clear path to sustainable content economics"
                },
                "primary_challenges": [
                    {
                        "challenge": "Production Consistency",
                        "mitigation": "Build buffer of content, documented processes, backup resources"
                    },
                    {
                        "challenge": "Audience Growth",
                        "mitigation": "Test multiple acquisition channels, optimize for highest ROI"
                    },
                    {
                        "challenge": "Focus Maintenance",
                        "mitigation": "Clear prioritization framework, regular strategic alignment"
                    }
                ],
                "structural_changes": [
                    {
                        "area": "Team Structure",
                        "approach": "Functional specialists with cross-training"
                    },
                    {
                        "area": "Decision Making",
                        "approach": "Centralized with input from all functions"
                    },
                    {
                        "area": "Planning Horizon",
                        "approach": "90-day cycles with weekly adaptations"
                    }
                ],
                "investment_profile": {
                    "focus": "Building foundation and proving concept",
                    "burn_rate": "Conservative with runway preservation",
                    "resource_allocation": "Content production and audience development"
                }
            },
            {
                "id": "phase-2",
                "name": "Tribe - Exponential Growth",
                "description": "Rapidly scale audience, content production, and community engagement through optimized channels and processes while maintaining quality and engagement.",
                "key_focus": [
                    "Audience acquisition acceleration",
                    "Content production scaling",
                    "Community growth and activity density",
                    "Partnership expansion"
                ],
                "trigger_metrics": {
                    "audience_size": "25,000+ regular listeners",
                    "growth_rate": "Consistent 10%+ week-over-week growth",
                    "unit_economics": "Profitable on fully-loaded content cost",
                    "team_readiness": "Scalable processes documented and tested"
                },
                "primary_challenges": [
                    {
                        "challenge": "Quality Maintenance",
                        "mitigation": "Strong quality assurance processes, feedback loops, training"
                    },
                    {
                        "challenge": "Team Scaling",
                        "mitigation": "Advance hiring, documentation, training systems"
                    },
                    {
                        "challenge": "Communication Complexity",
                        "mitigation": "Structured communication protocols, information architecture"
                    }
                ],
                "structural_changes": [
                    {
                        "area": "Team Structure",
                        "approach": "Functional teams with clear interfaces"
                    },
                    {
                        "area": "Decision Making",
                        "approach": "Distributed within guardrails and principles"
                    },
                    {
                        "area": "Planning Horizon",
                        "approach": "Mixed timeframes with clear dependencies"
                    }
                ],
                "investment_profile": {
                    "focus": "Growth acceleration and infrastructure scaling",
                    "burn_rate": "Increased with clear CAC/LTV metrics",
                    "resource_allocation": "Marketing, team expansion, systems"
                }
            },
            {
                "id": "phase-3",
                "name": "Village - Sustainable Scale",
                "description": "Establish sustainable, efficient scale with optimized operations, diversified revenue, and expanded ecosystem of content, community, and products.",
                "key_focus": [
                    "Operational efficiency and unit economics",
                    "Revenue diversification and optimization",
                    "Product expansion beyond core offerings",
                    "Ecosystem connectivity and flywheel effects"
                ],
                "trigger_metrics": {
                    "audience_size": "100,000+ regular participants",
                    "revenue_streams": "3+ established revenue channels",
                    "profitability": "Positive overall unit economics",
                    "team_structure": "Functional departments with leadership layer"
                },
                "primary_challenges": [
                    {
                        "challenge": "Organizational Complexity",
                        "mitigation": "Clear organizational design, communication systems, alignment tools"
                    },
                    {
                        "challenge": "Cultural Consistency",
                        "mitigation": "Values reinforcement, leadership development, recognition systems"
                    },
                    {
                        "challenge": "Market Evolution Response",
                        "mitigation": "Dedicated innovation capacity, market sensing systems"
                    }
                ],
                "structural_changes": [
                    {
                        "area": "Team Structure",
                        "approach": "Functional departments with cross-functional initiatives"
                    },
                    {
                        "area": "Decision Making",
                        "approach": "Balanced centralization/decentralization with clear domains"
                    },
                    {
                        "area": "Planning Horizon",
                        "approach": "Rolling 12-month strategy with quarterly execution"
                    }
                ],
                "investment_profile": {
                    "focus": "Efficiency optimization and capability expansion",
                    "burn_rate": "Decreasing toward breakeven",
                    "resource_allocation": "Systems, specialization, new initiatives"
                }
            },
            {
                "id": "phase-4",
                "name": "City - Full Ecosystem Realization",
                "description": "Fully realized multimedia ecosystem with integrated products, multiple audience segments, and sophisticated monetization across a coherent empire of content and community.",
                "key_focus": [
                    "Multi-product integration and synergy",
                    "Enterprise-level partnerships and operations",
                    "Multiple audience segments with tailored experiences",
                    "Full narrative universe realization"
                ],
                "trigger_metrics": {
                    "audience_size": "500,000+ ecosystem participants",
                    "product_portfolio": "5+ distinct product/service lines",
                    "organizational_maturity": "Established leadership team and governance",
                    "market_position": "Recognized category leader"
                },
                "primary_challenges": [
                    {
                        "challenge": "Innovation Balance",
                        "mitigation": "Portfolio approach to innovation, separate exploration units"
                    },
                    {
                        "challenge": "Ecosystem Coherence",
                        "mitigation": "Centralized narrative/experience guardianship, strong principles"
                    },
                    {
                        "challenge": "Legacy System Constraints",
                        "mitigation": "Technical debt management, strategic refactoring"
                    }
                ],
                "structural_changes": [
                    {
                        "area": "Team Structure",
                        "approach": "Business units with shared services"
                    },
                    {
                        "area": "Decision Making",
                        "approach": "Multi-level with clear autonomy boundaries"
                    },
                    {
                        "area": "Planning Horizon",
                        "approach": "3-5 year strategic, annual tactical, quarterly execution"
                    }
                ],
                "investment_profile": {
                    "focus": "Balanced portfolio of established and emerging initiatives",
                    "burn_rate": "Profitable with reinvestment allocation formula",
                    "resource_allocation": "Strategic initiatives, innovation, optimization"
                }
            }
        ],
        
        "lean_methodology": {
            "principles": [
                {
                    "principle": "Build-Measure-Learn Cycle",
                    "application": "Every initiative follows rapid experimentation cycles with clear hypotheses, minimum viable tests, and defined learning goals. The podcast and community launch will use 'Minimum Viable Content' approach - releasing early with sufficient quality but rapid iteration based on audience feedback.",
                    "key_practices": [
                        "Weekly hypothesis review meetings",
                        "Documented learning from each experiment",
                        "Regular pivot-or-persevere decisions",
                        "Progressive refinement of audience understanding"
                    ]
                },
                {
                    "principle": "Validated Learning",
                    "application": "Focus on generating actionable insights about audience needs, content resonance, and business model viability through direct testing rather than theoretical planning. Community engagement will be considered a primary learning tool, not just a service delivery mechanism.",
                    "key_practices": [
                        "Systematic feedback collection from all touchpoints",
                        "Regular audience interaction and co-creation sessions",
                        "A/B testing of content approaches and formats",
                        "Rapid implementation of insights into next iteration"
                    ]
                },
                {
                    "principle": "Innovation Accounting",
                    "application": "Establish clear metrics that demonstrate real progress in audience building, engagement, and monetization potential. Vanity metrics are replaced with actionable indicators of sustainable growth.",
                    "key_practices": [
                        "Cohort analysis of audience engagement over time",
                        "Quality-adjusted metrics (not just raw numbers)",
                        "Leading indicators for long-term objectives",
                        "Regular review and refinement of key metrics"
                    ]
                },
                {
                    "principle": "Minimum Viable Product",
                    "application": "Launch core offerings with minimal features needed for valuable feedback rather than perfected products. The initial podcast will focus on content quality and audience relationship rather than perfect production or comprehensive features.",
                    "key_practices": [
                        "Feature prioritization based on learning value",
                        "Concierge MVP approach for community features",
                        "Wizard of Oz testing for complex functionality",
                        "Progressive enhancement based on validated needs"
                    ]
                }
            ],
            "tools": [
                {
                    "tool": "Assumption Mapping",
                    "purpose": "Systematically identify and test critical assumptions about audience, content value, and business model",
                    "implementation": "Monthly assumption review sessions with prioritization of tests based on risk and uncertainty"
                },
                {
                    "tool": "Lean Canvas",
                    "purpose": "Maintain living document of current business model hypotheses and validation status",
                    "implementation": "Updated bi-weekly with insights from testing and learning cycles"
                },
                {
                    "tool": "Split Testing Framework",
                    "purpose": "Efficiently test content variations, messaging approaches, and engagement tactics",
                    "implementation": "Infrastructure for continuous testing across all audience touchpoints"
                },
                {
                    "tool": "Customer Development Interviews",
                    "purpose": "Deep qualitative understanding of audience needs, pains, and value perception",
                    "implementation": "Ongoing program of structured interviews with different audience segments"
                },
                {
                    "tool": "Cohort Analysis Dashboard",
                    "purpose": "Track engagement and conversion metrics across audience acquisition cohorts",
                    "implementation": "Weekly updating dashboard with key metrics by acquisition source and time"
                }
            ],
            "waste_elimination": [
                {
                    "waste_type": "Overproduction",
                    "identification": "Creating content or features without validated audience demand",
                    "elimination_approach": "Just-in-time content production based on validated topics and formats"
                },
                {
                    "waste_type": "Inventory",
                    "identification": "Backlog of unused content or features not delivering current value",
                    "elimination_approach": "Small batch content production with rapid release cycles"
                },
                {
                    "waste_type": "Extra Processing",
                    "identification": "Perfecting aspects of content or features beyond audience value perception",
                    "elimination_approach": "Value-based quality thresholds for different content types"
                },
                {
                    "waste_type": "Motion",
                    "identification": "Inefficient workflows or excess coordination in content production",
                    "elimination_approach": "Streamlined production processes with clear handoffs"
                },
                {
                    "waste_type": "Waiting",
                    "identification": "Delays between production stages or feedback incorporation",
                    "elimination_approach": "Continuous flow production system with minimal waiting states"
                }
            ]
        },
        
        "blitzscaling_approach": {
            "core_principles": [
                {
                    "principle": "Business Model Innovation",
                    "application": "HCU will innovate on the traditional media/content business model by integrating community, education, and financial legacy components into a coherent ecosystem with multiple reinforcing revenue streams.",
                    "key_decisions": [
                        "Initially prioritize audience growth over monetization",
                        "Create foundation for multiple revenue models in parallel",
                        "Design for network effects across ecosystem components",
                        "Balance free content for growth with premium offerings"
                    ]
                },
                {
                    "principle": "Massive Market Focus",
                    "application": "While starting with a focused beachhead, the HCU approach is designed for expansion into the massive intergenerational wealth transfer market ($30+ trillion in the US alone) with multiple entry points.",
                    "key_decisions": [
                        "Sequence market expansion based on adjacent capabilities",
                        "Build infrastructure that can scale to millions of users",
                        "Design modular content approach for different segments",
                        "Create brand architecture supporting multiple audiences"
                    ]
                },
                {
                    "principle": "Network Effects",
                    "application": "Design the community and content ecosystem to become more valuable as more people participate, with particular emphasis on the compounding value of shared legacy stories and strategies.",
                    "key_decisions": [
                        "Community feature prioritization based on network value",
                        "User contribution and co-creation from early stages",
                        "Recognition and incentive systems for valuable participation",
                        "Cross-pollination between different ecosystem components"
                    ]
                },
                {
                    "principle": "Efficient Distribution",
                    "application": "Leverage existing channels, partnerships, and platforms to rapidly expand reach while building direct audience relationships for long-term control.",
                    "key_decisions": [
                        "Multi-platform distribution strategy from day one",
                        "Partnership-driven growth as core strategy",
                        "Balanced owned vs. third-party channel approach",
                        "Progressive audience migration to owned platforms"
                    ]
                }
            ],
            "growth_factors": [
                {
                    "factor": "Viral Growth",
                    "strategy": "Design content and community experiences that naturally drive sharing and referral through their inherent value and shareability.",
                    "key_tactics": [
                        "Shareable insights and frameworks within content",
                        "Family-oriented legacy discussions that prompt sharing",
                        "Community achievements and contributions with social visibility",
                        "Referral mechanisms built into core experience"
                    ]
                },
                {
                    "factor": "Paid Growth",
                    "strategy": "Strategically deploy paid acquisition once audience value and conversion metrics are validated, focusing on channels with proven efficiency.",
                    "key_tactics": [
                        "Test multiple channels with minimum viable budgets",
                        "Scale investment in highest performing channels",
                        "Continuously optimize conversion from paid acquisition",
                        "Balance paid growth with organic for sustainability"
                    ]
                },
                {
                    "factor": "Strategic Partnerships",
                    "strategy": "Leverage existing platforms, communities, and brands to accelerate audience acquisition through strategic collaborations.",
                    "key_tactics": [
                        "Co-created content with established partners",
                        "Integration into existing wealth management offerings",
                        "Educational institution partnerships",
                        "Media and publishing collaborations"
                    ]
                },
                {
                    "factor": "Platform Utilization",
                    "strategy": "Maximize visibility and discovery on existing platforms while building direct relationship with audience.",
                    "key_tactics": [
                        "Platform-optimized content versions",
                        "Strategic participation in trending conversations",
                        "Creator economy integration where relevant",
                        "Cross-platform content strategy"
                    ]
                }
            ],
            "rule_breaking": [
                {
                    "conventional_wisdom": "Perfect Production Quality First",
                    "blitzscaling_approach": "Start with 'good enough' quality that serves core value proposition, then improve based on audience feedback and as scale justifies. For HCU, this means focusing on insightful content and meaningful connection over perfect production initially."
                },
                {
                    "conventional_wisdom": "Linear Channel Expansion",
                    "blitzscaling_approach": "Launch on multiple platforms simultaneously with tailored approaches for each, gathering data on performance and optimizing resource allocation dynamically. This allows HCU to discover unexpected growth channels early."
                },
                {
                    "conventional_wisdom": "Complete Product Before Scaling",
                    "blitzscaling_approach": "Begin scaling core offerings while developing complementary components in parallel, using audience growth to fuel expansion into adjacent offerings. HCU will build audience with podcast while developing community and education components simultaneously."
                },
                {
                    "conventional_wisdom": "Solve All Problems Before Growing",
                    "blitzscaling_approach": "Prioritize fixing only the problems that threaten core value delivery or growth trajectory, accepting some inefficiency and imperfection in non-critical areas. Focus resources on removing critical constraints to growth rather than optimizing everything."
                }
            ],
            "risk_management": {
                "competitive_threats": {
                    "strategy": "Balance first-mover advantages with fast-follower learning by continuously monitoring competitive landscape while staying focused on unique value proposition.",
                    "key_actions": [
                        "Regular competitive intelligence gathering and analysis",
                        "Clear differentiation strategy for core offerings",
                        "Relationship-based defensibility through community",
                        "Intellectual property development around key frameworks"
                    ]
                },
                "operational_challenges": {
                    "strategy": "Build robust but flexible operational foundation that can scale rapidly while maintaining sufficient quality and reliability.",
                    "key_actions": [
                        "Documentation of core processes from early stage",
                        "Progressive automation of repetitive workflows",
                        "Regular operational stress testing and scenario planning",
                        "Clear quality thresholds for different growth stages"
                    ]
                },
                "financial_management": {
                    "strategy": "Maintain sufficient runway while deploying capital aggressively for growth opportunities with validated potential.",
                    "key_actions": [
                        "Regular cash flow forecasting with multiple scenarios",
                        "Clear thresholds for increasing investment in growth",
                        "Continuous monitoring of unit economics",
                        "Balanced portfolio of growth initiatives with different risk profiles"
                    ]
                }
            }
        }
    }
    
    return BusinessScalingPlaybookResponse(**playbook_data)
