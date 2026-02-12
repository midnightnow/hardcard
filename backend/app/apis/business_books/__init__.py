from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

router = APIRouter()

class ExpertItem(BaseModel):
    name: str
    expertise: str
    contribution: str

class GuestExpert(BaseModel):
    name: str
    expertise: str
    potential_books: List[str]

class Book(BaseModel):
    id: str
    title: str
    author: str
    category: str
    year: int
    summary: str
    key_principles: List[str]
    generational_relevance: str
    expert_insights: List[str]
    family_office_applications: List[str]

class Category(BaseModel):
    id: str
    name: str
    description: str
    book_count: int

class BooksListResponse(BaseModel):
    books: List[Book]
    categories: List[Category]

class MethodologyResponse(BaseModel):
    selection_criteria: List[str]
    analysis_framework: str
    expert_panel: List[ExpertItem]
    application_process: str

class PodcastPlanResponse(BaseModel):
    episode_structure: str
    interview_approach: str
    release_schedule: str
    guest_experts: List[GuestExpert]
    distribution_channels: List[str]

@router.get("/books-list")
def get_business_books_list_legacy() -> BooksListResponse:
    """Returns the list of books in the Business Canon.
    
    This endpoint provides the current list of books included in the Business Canon,
    organized by categories and with detailed information about each book.
    """
    
    return BooksListResponse(
        books=[
            Book(
                id="1",
                title="Principles",
                author="Ray Dalio",
                category="Wealth Building",
                year=2017,
                summary="A comprehensive framework for decision-making in both life and business, drawing on Dalio's experience as the founder of Bridgewater Associates.",
                key_principles=[
                    "Radical transparency in organizations",
                    "Believability-weighted decision making",
                    "Pain + Reflection = Progress",
                    "Use principles to guide decisions"
                ],
                generational_relevance="Provides systematic frameworks for families to evaluate investments and transfer decision-making wisdom across generations.",
                expert_insights=[
                    "Prof. Jane Richardson: 'Dalio's meritocratic approach to idea evaluation can revolutionize family office governance structures.'",
                    "Thomas Kwan: 'The principles-based approach creates a common language for multi-generational collaboration.'"
                ],
                family_office_applications=[
                    "Establishing family investment committees with clear decision frameworks",
                    "Implementing systematic risk management across generations",
                    "Creating family constitutions with clear principles"
                ],
            ),
            Book(
                id="2",
                title="The Intelligent Investor",
                author="Benjamin Graham",
                category="Investing",
                year=1949,
                summary="The definitive book on value investing that has shaped generations of investors, including Warren Buffett.",
                key_principles=[
                    "Margin of Safety",
                    "Mr. Market analogy",
                    "Difference between investing and speculation",
                    "Focus on intrinsic value over market price"
                ],
                generational_relevance="Provides timeless principles of wealth preservation that remain relevant despite changing market conditions.",
                expert_insights=[
                    "Prof. Michael Jensen: 'Graham's emphasis on psychological discipline creates a foundation for multi-generational investing success.'",
                    "Alex Rivera: 'The concept of margin of safety becomes increasingly important when stewarding family wealth across market cycles.'"
                ],
                family_office_applications=[
                    "Creating investment policy statements with value-oriented principles",
                    "Developing family education programs around fundamental investing concepts",
                    "Establishing procedures to capitalize on market volatility"
                ],
            ),
            Book(
                id="3",
                title="Zero to One",
                author="Peter Thiel",
                category="Innovation",
                year=2014,
                summary="Thiel's insights on building companies that create new things rather than iterating on existing ideas.",
                key_principles=[
                    "The importance of creating monopolies through innovation",
                    "The contrarian question: What important truth do few people agree with you on?",
                    "The last mover advantage",
                    "The importance of secrets in business"
                ],
                generational_relevance="Frames technological progress in ways that help families position capital for long-term exponential returns rather than incremental gains.",
                expert_insights=[
                    "Prof. Michaela Johnson: 'Thiel's contrarian thinking framework is particularly valuable for family offices seeking alpha across generations.'",
                    "Thomas Kwan: 'The concepts in Zero to One help families distinguish between true innovation and mere iteration in their venture portfolios.'"
                ],
                family_office_applications=[
                    "Developing venture capital allocation strategies for disruptive technologies",
                    "Creating family office innovation labs",
                    "Establishing frameworks for evaluating technological paradigm shifts"
                ],
            )
        ],
        categories=[
            Category(
                id="wealth-building",
                name="Wealth Building",
                description="Foundational texts on building and preserving multi-generational wealth",
                book_count=12
            ),
            Category(
                id="investing",
                name="Investing",
                description="Strategic approaches to capital allocation and portfolio management",
                book_count=18
            ),
            Category(
                id="innovation",
                name="Innovation",
                description="Texts focused on disruptive thinking and technological innovation",
                book_count=15
            ),
            Category(
                id="leadership",
                name="Leadership",
                description="Guidance on leading organizations and navigating succession",
                book_count=14
            ),
            Category(
                id="family-dynamics",
                name="Family Dynamics",
                description="Managing complex family relationships in business contexts",
                book_count=8
            )
        ]
    )

@router.get("/methodology-legacy")
def get_business_books_methodology_legacy() -> MethodologyResponse:
    """Returns the methodology used for the Business Canon.
    
    This endpoint provides details about the selection criteria, analysis framework,
    expert panel, and application process used in the Business Canon project.
    """
    
    return MethodologyResponse(
        selection_criteria=[
            "Longevity of principles (tested across multiple market cycles)",
            "Expert consensus on foundational importance",
            "Practical applicability to family wealth contexts",
            "Multi-generational perspective",
            "Diverse representation of thought and approach"
        ],
        analysis_framework="Each book is analyzed through three lenses: historical context and original intent, contemporary relevance, and multi-generational application. This structured analysis extracts both timeless principles and evolving applications across different economic and social environments.",
        expert_panel=[
            ExpertItem(
                name="Prof. Michaela Johnson",
                expertise="Business Literature Historian",
                contribution="Historical contextualization and evolution of management principles"
            ),
            ExpertItem(
                name="Alex Rivera",
                expertise="Business Book Publisher",
                contribution="Contemporary relevance and emerging thought leadership"
            ),
            ExpertItem(
                name="Thomas Kwan",
                expertise="Family Business Education Director",
                contribution="Multi-generational application and succession planning"
            ),
            ExpertItem(
                name="Dr. Sarah Lindstrom",
                expertise="Behavioral Finance Researcher",
                contribution="Psychological aspects of wealth management across generations"
            )
        ],
        application_process="Each book's principles are translated into concrete family office applications through a collaborative process involving wealth managers, family office directors, and next-generation family members. Case studies are developed to illustrate practical implementation while respecting privacy through anonymization."
    )

@router.get("/podcast-plan-legacy")
def get_business_books_podcast_plan_legacy() -> PodcastPlanResponse:
    """Returns the podcast plan for the Business Canon series.
    
    This endpoint provides details about the podcast series structure, episode format,
    interview approach, release schedule, guest experts, and distribution channels.
    """
    
    return PodcastPlanResponse(
        episode_structure="Each episode follows a four-part structure: historical context and author intent, principle extraction and analysis, expert commentary on contemporary application, and family office implementation framework. Episodes range from 45-60 minutes with supplemental written materials.",
        interview_approach="Episodes feature a combination of subject matter experts, practitioners who have implemented the book's principles, and where possible, authors or their direct intellectual successors. The interview style is Socratic rather than promotional, focusing on practical wisdom extraction.",
        release_schedule="The series follows a thematic release schedule with books grouped in related clusters of 5-7 titles. This approach allows listeners to develop comprehensive understanding of related principles before moving to new domains. New episodes release weekly with in-depth discussions every two weeks.",
        guest_experts=[
            GuestExpert(
                name="Prof. Michaela Johnson",
                expertise="Business Literature Historian",
                potential_books=["The Intelligent Investor", "Security Analysis", "Reminiscences of a Stock Operator"]
            ),
            GuestExpert(
                name="Alex Rivera",
                expertise="Business Book Publisher",
                potential_books=["Zero to One", "The Innovator's Dilemma", "Built to Last"]
            ),
            GuestExpert(
                name="Thomas Kwan",
                expertise="Family Business Education Director",
                potential_books=["Principles", "Family Wealth", "The Family Office"]  
            ),
            GuestExpert(
                name="Dr. Sarah Lindstrom",
                expertise="Behavioral Finance Researcher",
                potential_books=["Thinking, Fast and Slow", "Nudge", "Predictably Irrational"]
            )
        ],
        distribution_channels=[
            "Dedicated Hard Card Universe podcast feed",
            "Business book analysis YouTube channel with visual summaries",
            "Private RSS feed for family office professionals with additional commentary",
            "Members-only discussion forum for implementation questions",
            "Quarterly live virtual roundtables with authors and practitioners"
        ]
    )
