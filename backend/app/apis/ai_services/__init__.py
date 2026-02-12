from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import random
import json

router = APIRouter()


class InvestmentRecommendationRequest(BaseModel):
    profile_id: str
    query: str
    context: Optional[str] = "{}"


class Resource(BaseModel):
    title: str
    url: Optional[str] = None
    description: Optional[str] = None


class ActionItem(BaseModel):
    action: str
    description: str
    priority: str  # "high", "medium", or "low"


class InvestmentRecommendationResponse(BaseModel):
    type: str
    response: str
    suggestions: Optional[List[str]] = None
    resources: Optional[List[Resource]] = None
    actionItems: Optional[List[ActionItem]] = None


@router.post("/generate-investment-recommendations")
def generate_investment_recommendations_service(
    body: InvestmentRecommendationRequest
) -> InvestmentRecommendationResponse:
    """Generate personalized investment recommendations based on profile and query.
    
    Creates tailored investment guidance by analyzing the user's specific query in the context of
    their family profile information. The system intelligently identifies investment themes in the query
    and provides targeted advice across asset classes including cryptocurrencies, equities, real estate,
    fixed income, and time-horizon planning.
    
    This endpoint is particularly valuable for Legacy Vault users seeking contextual investment
    advice for their family wealth management and legacy planning activities.
    
    Args:
        body (InvestmentRecommendationRequest): Contains profile ID, query text, and optional context
        
    Returns:
        InvestmentRecommendationResponse: Comprehensive response containing:
            - Detailed recommendation text
            - Follow-up suggestion questions
            - Educational resources with descriptions
            - Prioritized action items with implementation details
    """
    try:
        # Parse context if provided
        context = {}
        if body.context:
            try:
                context = json.loads(body.context)
            except json.JSONDecodeError:
                pass
        
        # In a real implementation, this would use profile data and possibly call an LLM
        # For now, we'll return simulated responses based on the query
        
        # Basic categorization of query intent
        query_lower = body.query.lower()
        
        if "bitcoin" in query_lower or "crypto" in query_lower:
            response_type = "crypto"
        elif "stock" in query_lower or "equity" in query_lower:
            response_type = "stocks"
        elif "bond" in query_lower or "fixed income" in query_lower:
            response_type = "bonds"
        elif "real estate" in query_lower or "property" in query_lower:
            response_type = "real_estate"
        elif "retire" in query_lower or "pension" in query_lower:
            response_type = "retirement"
        elif "diversif" in query_lower or "allocat" in query_lower:
            response_type = "allocation"
        else:
            response_type = "general"
        
        # Generate response based on type
        if response_type == "crypto":
            response = (
                "For cryptocurrency investments, I recommend a cautious approach with no more than "
                "5-10% of your portfolio. Bitcoin remains the safest crypto asset for long-term "
                "holding, with Ethereum as a secondary option. Consider dollar-cost averaging "
                "through monthly purchases rather than lump-sum investments."
            )
            suggestions = [
                "What is your recommended Bitcoin acquisition strategy?",
                "How do you secure cryptocurrency investments?",
                "Should I consider other cryptocurrencies besides Bitcoin?"
            ]
            resources = [
                Resource(
                    title="Bitcoin Storage Security Guide",
                    description="Best practices for securing cryptocurrency assets"
                ),
                Resource(
                    title="Dollar-Cost Averaging Calculator",
                    description="Tool to plan systematic Bitcoin purchases"
                )
            ]
            action_items = [
                ActionItem(
                    action="Set up hardware wallet",
                    description="Purchase and configure a hardware wallet for secure storage",
                    priority="high"
                ),
                ActionItem(
                    action="Establish monthly purchase plan",
                    description="Set up automatic monthly purchases at a reputable exchange",
                    priority="medium"
                )
            ]
        elif response_type == "stocks":
            response = (
                "For stock investments, I recommend a portfolio of dividend aristocrats combined "
                "with select growth stocks in AI, biotechnology, and renewable energy sectors. "
                "For your family trust structure, consider setting up custodial accounts that "
                "transition to beneficiaries at predetermined milestones."
            )
            suggestions = [
                "What dividend stocks do you recommend?",
                "Which growth sectors look promising for the next decade?",
                "How should I structure stock holdings in my family trust?"
            ]
            resources = [
                Resource(
                    title="Dividend Aristocrat Analysis",
                    description="Companies with 25+ years of dividend increases"
                ),
                Resource(
                    title="Family Trust Stock Transfer Strategies",
                    description="Tax-efficient methods for transferring equities"
                )
            ]
            action_items = [
                ActionItem(
                    action="Diversify sector allocation",
                    description="Ensure portfolio has exposure across multiple sectors",
                    priority="high"
                ),
                ActionItem(
                    action="Set up DRIP program",
                    description="Establish dividend reinvestment plans for core holdings",
                    priority="medium"
                )
            ]
        elif response_type == "bonds":
            response = (
                "In the current interest rate environment, I recommend a laddered approach to bond "
                "investments with exposure to both government and high-quality corporate bonds. "
                "For your family trust, consider tax-free municipal bonds in your state of residence "
                "to maximize after-tax returns for wealth preservation."
            )
            suggestions = [
                "How do I set up a bond ladder?",
                "Are municipal bonds appropriate for my situation?",
                "What bond durations do you recommend in the current environment?"
            ]
            resources = [
                Resource(
                    title="Bond Ladder Construction Guide",
                    description="Step-by-step approach to creating a diversified bond ladder"
                ),
                Resource(
                    title="Municipal Bond Tax Advantage Calculator",
                    description="Compare taxable vs. tax-free bond yields"
                )
            ]
            action_items = [
                ActionItem(
                    action="Build bond ladder",
                    description="Allocate fixed income investments across different maturities",
                    priority="medium"
                ),
                ActionItem(
                    action="Review municipal bond offerings",
                    description="Evaluate tax-exempt bonds in your state of residence",
                    priority="medium"
                )
            ]
        elif response_type == "real_estate":
            response = (
                "For real estate investments, I recommend a combination of direct ownership "
                "and REITs for diversification. Consider establishing a family limited partnership "
                "for direct property investments to facilitate fractional ownership and simplified "
                "transfer to trust beneficiaries while maintaining centralized management."
            )
            suggestions = [
                "What types of properties are best for generational wealth?",
                "How do I structure real estate in my family trust?",
                "Are REITs appropriate for my investment goals?"
            ]
            resources = [
                Resource(
                    title="Family Limited Partnership Guide",
                    description="Legal structures for family real estate holdings"
                ),
                Resource(
                    title="Commercial vs. Residential Analysis",
                    description="Comparison of different real estate investment types"
                )
            ]
            action_items = [
                ActionItem(
                    action="Consult with real estate attorney",
                    description="Discuss optimal entity structure for property holdings",
                    priority="high"
                ),
                ActionItem(
                    action="Diversify REIT holdings",
                    description="Add exposure to different property types through REITs",
                    priority="medium"
                )
            ]
        elif response_type == "retirement":
            response = (
                "For retirement planning within your family trust, I recommend establishing "
                "multiple layers of income sources. Consider a combination of annuities for "
                "guaranteed income, dividend-paying stocks for growth and inflation protection, "
                "and strategic Roth conversions to minimize future tax burdens for beneficiaries."
            )
            suggestions = [
                "How do annuities work with a family trust?",
                "What's the optimal Social Security strategy for my situation?",
                "How should I plan for healthcare costs in retirement?"
            ]
            resources = [
                Resource(
                    title="Retirement Income Layering Strategy",
                    description="Creating multiple income streams for retirement security"
                ),
                Resource(
                    title="Roth Conversion Analysis for Trusts",
                    description="Tax considerations for Roth conversions within trust structures"
                )
            ]
            action_items = [
                ActionItem(
                    action="Calculate retirement income gap",
                    description="Determine shortfall between guaranteed income and expenses",
                    priority="high"
                ),
                ActionItem(
                    action="Evaluate annuity options",
                    description="Compare immediate and deferred annuity products",
                    priority="medium"
                )
            ]
        elif response_type == "allocation":
            response = (
                "For your family trust's portfolio allocation, I recommend a core-satellite approach "
                "with 70% in a diversified core of index funds and blue-chip stocks, and 30% in tactical "
                "satellite investments targeting specific opportunities. This structure balances "
                "wealth preservation with growth potential while accommodating different risk "
                "tolerances across generations."
            )
            suggestions = [
                "What's the ideal asset allocation for multigenerational wealth?",
                "How should allocation change as beneficiaries age?",
                "What rebalancing strategy do you recommend?"
            ]
            resources = [
                Resource(
                    title="Core-Satellite Portfolio Construction",
                    description="Framework for building a balanced multi-generational portfolio"
                ),
                Resource(
                    title="Dynasty Trust Allocation Strategy",
                    description="Asset allocation considerations for long-term family trusts"
                )
            ]
            action_items = [
                ActionItem(
                    action="Define allocation targets",
                    description="Establish target percentages for each asset class",
                    priority="high"
                ),
                ActionItem(
                    action="Create rebalancing policy",
                    description="Develop rules for when and how to rebalance the portfolio",
                    priority="medium"
                )
            ]
        else:  # general
            response = (
                "Based on your family's profile, I recommend a diversified investment approach with "
                "40% in global equities, 30% in fixed income, 15% in real assets (including real estate "
                "and precious metals), 10% in alternative investments, and 5% in digital assets like "
                "Bitcoin. This allocation provides a balance of growth potential, income generation, "
                "and inflation protection across multiple asset classes and geographies."
            )
            suggestions = [
                "What investment vehicles do you recommend for each asset class?",
                "How should I think about risk management across generations?",
                "What tax strategies should I consider for my investments?"
            ]
            resources = [
                Resource(
                    title="Multi-Generational Investment Framework",
                    description="Balancing current needs with long-term legacy planning"
                ),
                Resource(
                    title="Tax-Efficient Investing Guide",
                    description="Strategies to minimize tax impact on investment returns"
                )
            ]
            action_items = [
                ActionItem(
                    action="Complete risk tolerance assessment",
                    description="Determine appropriate risk levels for different portions of portfolio",
                    priority="high"
                ),
                ActionItem(
                    action="Establish investment policy statement",
                    description="Document investment objectives, constraints, and guidelines",
                    priority="medium"
                )
            ]
        
        return InvestmentRecommendationResponse(
            type="financial",
            response=response,
            suggestions=suggestions,
            resources=resources,
            actionItems=action_items
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}") from e


class ContentGenerationRequest(BaseModel):
    profile_id: str
    query: str
    context: Optional[str] = "{}"


class ContentGenerationResponse(BaseModel):
    type: str
    response: str
    suggestions: Optional[List[str]] = None
    resources: Optional[List[Resource]] = None
    actionItems: Optional[List[ActionItem]] = None


@router.post("/generate-content")
def generate_content_service(
    body: ContentGenerationRequest
) -> ContentGenerationResponse:
    """
    Generate various types of content based on profile and specifications
    """
    try:
        # Parse context if provided
        context_data = {}
        if body.context:
            try:
                context_data = json.loads(body.context)
            except json.JSONDecodeError:
                pass
        
        # In a real implementation, this would use profile data and possibly call an LLM
        # For now, we'll return simulated responses based on the query
        
        # Basic categorization of content request
        query_lower = body.query.lower()
        
        if "newsletter" in query_lower or "update" in query_lower:
            content_type = "newsletter"
        elif "education" in query_lower or "learn" in query_lower or "teach" in query_lower:
            content_type = "educational"
        elif "legacy" in query_lower or "statement" in query_lower or "vision" in query_lower:
            content_type = "legacy_statement"
        elif "letter" in query_lower or "message" in query_lower:
            content_type = "letter"
        elif "policy" in query_lower or "guideline" in query_lower or "rule" in query_lower:
            content_type = "policy"
        elif "summary" in query_lower or "report" in query_lower:
            content_type = "report"
        else:
            content_type = "general"
        
        # Generate response based on type
        if content_type == "newsletter":
            response = (
                "# McMillan Family Trust - Quarterly Newsletter\n\n"
                "## Investment Highlights\n\n"
                "This quarter has seen significant growth in our alternative investment portfolio, "
                "particularly in the emerging technologies sector. Bitcoin investments have shown "
                "a steady increase despite market volatility, reinforcing our long-term approach "
                "to digital asset allocation.\n\n"
                "## Trust Updates\n\n"
                "We've completed the annual review of beneficiary designations and educational fund "
                "allocations. The automated contribution system continues to perform as expected, "
                "with monthly Bitcoin purchases executing on schedule.\n\n"
                "## Educational Corner\n\n"
                "Understanding Generational Wealth Transfer: This quarter's educational focus is on "
                "the psychological aspects of inheritance. We've included resources for discussing "
                "financial responsibility with younger family members as they approach key age milestones.\n\n"
                "## Upcoming Events\n\n"
                "* Annual Family Financial Review: December 15th\n"
                "* Educational Workshop: 'Cryptocurrency Fundamentals': November 5th\n"
                "* Legacy Planning Session: January 10th"
            )
            suggestions = [
                "Add a section on market outlook",
                "Include portfolio performance metrics",
                "Add personalized messages for each family member"
            ]
            resources = [
                Resource(
                    title="Newsletter Templates",
                    description="Additional formats for family financial communications"
                ),
                Resource(
                    title="Effective Family Communication Guide",
                    description="Best practices for financial transparency in family trusts"
                )
            ]
            action_items = [
                ActionItem(
                    action="Review newsletter content",
                    description="Ensure all information is accurate and appropriate for all recipients",
                    priority="medium"
                ),
                ActionItem(
                    action="Schedule distribution",
                    description="Set date for newsletter distribution to all family members",
                    priority="low"
                )
            ]
        elif content_type == "educational":
            response = (
                "# Understanding Bitcoin: A Guide for Future Generations\n\n"
                "## What is Bitcoin?\n\n"
                "Bitcoin is a decentralized digital currency that operates without a central authority "
                "or single administrator. Created in 2009 by an unknown person or group using the name "
                "Satoshi Nakamoto, it introduced the concept of cryptocurrency to the world. Bitcoin "
                "transactions occur directly between users without intermediaries, and these transactions "
                "are verified through network nodes and recorded on a public distributed ledger called "
                "a blockchain.\n\n"
                "## Why Bitcoin Matters for Generational Wealth\n\n"
                "1. **Scarcity**: There will only ever be 21 million Bitcoin, making it a deflationary asset unlike traditional currencies.\n\n"
                "2. **Sovereignty**: Bitcoin provides financial sovereignty, allowing full control over your assets without third-party permissions.\n\n"
                "3. **Portability**: Wealth can be transferred instantly across borders without limitations.\n\n"
                "4. **Divisibility**: Each Bitcoin can be divided into 100 million satoshis, enabling precision in allocation.\n\n"
                "## How We Invest in Bitcoin\n\n"
                "Our family trust employs a systematic approach to Bitcoin acquisition:\n\n"
                "* **Dollar-Cost Averaging**: Regular purchases regardless of price, reducing impact of volatility\n"
                "* **Cold Storage Security**: All holdings secured in hardware wallets with multi-signature protection\n"
                "* **Generational Planning**: Bitcoin allocations designated for specific age milestones\n\n"
                "## Learning Resources\n\n"
                "To deepen your understanding, we recommend starting with 'The Bitcoin Standard' by Saifedean Ammous "
                "and exploring educational platforms like Khan Academy's cryptocurrency section."
            )
            suggestions = [
                "Create an interactive Bitcoin learning module",
                "Add a glossary of cryptocurrency terms",
                "Include case studies of Bitcoin's historical performance"
            ]
            resources = [
                Resource(
                    title="The Bitcoin Standard",
                    description="Recommended reading on Bitcoin economics"
                ),
                Resource(
                    title="Cryptocurrency Learning Path",
                    description="Structured curriculum for understanding digital assets"
                )
            ]
            action_items = [
                ActionItem(
                    action="Develop quiz on Bitcoin fundamentals",
                    description="Create interactive assessment to test knowledge retention",
                    priority="medium"
                ),
                ActionItem(
                    action="Schedule family learning session",
                    description="Set up group discussion on educational materials",
                    priority="low"
                )
            ]
        elif content_type == "legacy_statement":
            response = (
                "# McMillan Family Legacy Statement\n\n"
                "## Our Purpose\n\n"
                "The McMillan Family Trust exists to nurture financial security and opportunity "
                "across generations. We believe in balancing wealth preservation with forward-looking "
                "investments in emerging technologies and ideas. Our commitment extends beyond "
                "financial assets to include the transmission of knowledge, values, and financial "
                "wisdom.\n\n"
                "## Core Principles\n\n"
                "1. **Long-term Perspective**: We make decisions with a multi-generational timeframe, "
                "   prioritizing sustainable growth over short-term gains.\n\n"
                "2. **Balanced Innovation**: We maintain a foundation of proven investment vehicles while "
                "   allocating resources to emerging opportunities that may reshape the future.\n\n"
                "3. **Educational Empowerment**: We believe financial education is as valuable as financial "
                "   inheritance, and we commit to providing both.\n\n"
                "4. **Adaptive Strategy**: Our approach evolves with changing markets, technologies, and "
                "   family needs while maintaining core principles.\n\n"
                "## Vision for Future Generations\n\n"
                "We envision each generation building upon the foundation laid before them, adding their "
                "insights and adaptations while honoring established wisdom. The trust should provide "
                "security without creating complacency, opportunity without encouraging recklessness, "
                "and guidance without imposing rigid constraints.\n\n"
                "Each family member is encouraged to develop their own relationship with wealth—using it "
                "as a tool for creating value, pursuing meaningful work, and contributing to society "
                "while maintaining financial resilience across generations."
            )
            suggestions = [
                "Add specific values important to your family",
                "Include guidance on charitable giving",
                "Add section on family governance structure"
            ]
            resources = [
                Resource(
                    title="Legacy Statement Workshop",
                    description="Interactive process for refining your family legacy vision"
                ),
                Resource(
                    title="Values-Based Wealth Planning",
                    description="Aligning financial decisions with core family values"
                )
            ]
            action_items = [
                ActionItem(
                    action="Family discussion on legacy statement",
                    description="Gather input from family members on values and vision",
                    priority="high"
                ),
                ActionItem(
                    action="Create visual representation",
                    description="Develop graphic or artistic expression of family legacy",
                    priority="low"
                )
            ]
        elif content_type == "letter":
            response = (
                "Dear Future Beneficiary,\n\n"
                "As you reach your 18th birthday and gain access to the first portion of your trust, "
                "I want to share some thoughts on the responsibility that comes with financial resources.\n\n"
                "This Bitcoin allocation began on your first birthday and has grown through consistent "
                "contributions each year. The technology behind these digital assets represents more than "
                "just an investment—it embodies principles of financial sovereignty, transparent systems, "
                "and long-term thinking that I hope will guide your own approach to wealth.\n\n"
                "The purpose of this trust is not merely to provide money, but to offer opportunity, security, "
                "and freedom to pursue meaningful work and relationships. Remember that these resources "
                "represent years of disciplined saving and careful stewardship, with the explicit intention "
                "of giving you a foundation upon which to build.\n\n"
                "I encourage you to approach these funds with both gratitude and responsibility. Consider taking "
                "time to develop your own investment philosophy before making significant decisions. The "
                "financial education resources included in your Legacy Vault will provide valuable guidance, "
                "but your own judgment, developed through study and experience, will ultimately be your best asset.\n\n"
                "While these resources are now yours to direct, I hope you'll consider maintaining some "
                "portion in long-term, growth-oriented investments that might similarly benefit your own "
                "children someday. The true power of generational wealth lies in its thoughtful transfer "
                "and growth across decades and centuries.\n\n"
                "I'm always available to discuss financial matters or provide perspective, but never to judge "
                "or direct. Your relationship with wealth is yours to define, and I trust in your capacity "
                "to use these resources wisely.\n\n"
                "With confidence in your future,\n\n"
                "[Your Name]"
            )
            suggestions = [
                "Personalize with specific memories or stories",
                "Add guidance on specific financial decisions",
                "Include family history related to wealth creation"
            ]
            resources = [
                Resource(
                    title="Letter Templates for Financial Milestones",
                    description="Additional formats for messages to beneficiaries"
                ),
                Resource(
                    title="Communicating Values Across Generations",
                    description="Guide to meaningful financial conversations with inheritors"
                )
            ]
            action_items = [
                ActionItem(
                    action="Schedule letter delivery",
                    description="Set future date for letter to be shared with beneficiary",
                    priority="medium"
                ),
                ActionItem(
                    action="Create video companion",
                    description="Record personal message to accompany written letter",
                    priority="low"
                )
            ]
        elif content_type == "policy":
            response = (
                "# McMillan Family Trust: Investment Policy Guidelines\n\n"
                "## Purpose\n\n"
                "This document establishes the investment policy for the McMillan Family Trust, providing "
                "a framework for managing trust assets in alignment with our long-term objectives and values.\n\n"
                "## Investment Objectives\n\n"
                "1. **Capital Preservation**: Protect the real (inflation-adjusted) value of trust assets\n"
                "2. **Growth**: Generate long-term capital appreciation exceeding inflation by at least 3%\n"
                "3. **Income Generation**: Produce sufficient income for trust distributions and expenses\n"
                "4. **Legacy Development**: Build assets for future generations and charitable purposes\n\n"
                "## Asset Allocation Guidelines\n\n"
                "### Foundation Allocation (70% of portfolio)\n\n"
                "* Global Equities: 40-50%\n"
                "* Fixed Income: 15-25%\n"
                "* Real Assets (Real Estate, Commodities): 10-20%\n\n"
                "### Growth & Innovation Allocation (30% of portfolio)\n\n"
                "* Emerging Technologies: 10-15%\n"
                "* Digital Assets (Bitcoin): 5-10%\n"
                "* Venture Capital/Private Equity: 5-10%\n\n"
                "## Risk Management Principles\n\n"
                "* Diversification across asset classes, geographies, sectors, and time horizons\n"
                "* Regular rebalancing to maintain target allocations (quarterly review)\n"
                "* Liquidity management ensuring 5% of assets available within 30 days\n"
                "* Focus on quality investments with sustainable competitive advantages\n\n"
                "## Digital Asset Policy\n\n"
                "* Bitcoin acquisitions made using dollar-cost averaging approach\n"
                "* Cold storage with multisignature security and geographic distribution\n"
                "* Annual security audit and protocol review\n"
                "* Designated allocation for each beneficiary with scheduled distribution points\n\n"
                "## Policy Review\n\n"
                "This investment policy shall be reviewed annually and updated as needed to reflect changes "
                "in trust objectives, family circumstances, or market conditions."
            )
            suggestions = [
                "Add specific benchmarks for performance evaluation",
                "Include guidelines for sustainable/ESG investing",
                "Add section on approved investment vehicles"
            ]
            resources = [
                Resource(
                    title="Family Trust Investment Policy Templates",
                    description="Additional frameworks for trust investment governance"
                ),
                Resource(
                    title="Implementing Investment Policies",
                    description="Practical guide to enacting policy guidelines"
                )
            ]
            action_items = [
                ActionItem(
                    action="Review policy with financial advisor",
                    description="Ensure alignment with current market conditions and trust needs",
                    priority="high"
                ),
                ActionItem(
                    action="Distribute to trustees",
                    description="Share policy with all relevant decision-makers",
                    priority="medium"
                )
            ]
        elif content_type == "report":
            response = (
                "# McMillan Family Trust: Annual Performance Summary\n\n"
                "## Portfolio Performance\n\n"
                "**Time Period**: January 1, 2024 - December 31, 2024\n\n"
                "**Overall Portfolio Return**: +12.4% (vs. benchmark of +10.1%)\n\n"
                "### Asset Class Performance\n\n"
                "* Global Equities: +15.2%\n"
                "* Fixed Income: +3.8%\n"
                "* Real Assets: +7.9%\n"
                "* Digital Assets (Bitcoin): +46.2%\n"
                "* Alternative Investments: +8.5%\n\n"
                "## Key Metrics\n\n"
                "* Current Total Assets: $4,867,340\n"
                "* Net Contributions: $124,000\n"
                "* Net Growth: $536,200 (+12.4%)\n"
                "* Dividend & Interest Income: $94,530\n"
                "* Expenses & Fees: $32,450 (0.67% of assets)\n\n"
                "## Bitcoin Acquisition Program\n\n"
                "* Annual Contributions: $12,000 ($1,000/month)\n"
                "* Total Bitcoin Acquired: 0.317 BTC\n"
                "* Average Purchase Price: $37,855\n"
                "* Current Bitcoin Holdings: 3.842 BTC\n"
                "* Current Bitcoin Value: $193,108\n\n"
                "## Trust Distribution Activity\n\n"
                "* Educational Distributions: $45,000\n"
                "* Age-Based Milestone Distributions: $25,000\n"
                "* Charitable Giving: $15,000\n\n"
                "## Looking Ahead\n\n"
                "The coming year will focus on rebalancing our fixed income allocation given the changing "
                "interest rate environment and increasing our exposure to artificial intelligence and "
                "computational biology sectors within our emerging technologies allocation."
            )
            suggestions = [
                "Add visual charts showing performance trends",
                "Include comparison to broader market indices",
                "Add projection for next year based on current trends"
            ]
            resources = [
                Resource(
                    title="Investment Performance Metrics Guide",
                    description="Understanding key performance indicators for family trusts"
                ),
                Resource(
                    title="Effective Financial Reporting",
                    description="Best practices for clear financial communication"
                )
            ]
            action_items = [
                ActionItem(
                    action="Schedule performance review meeting",
                    description="Present annual results to family stakeholders",
                    priority="high"
                ),
                ActionItem(
                    action="Update financial projections",
                    description="Revise long-term forecasts based on current performance",
                    priority="medium"
                )
            ]
        else:  # general
            response = (
                "I'd be happy to help create content for your needs. Please specify what type of content "
                "you're looking for. I can assist with:\n\n"
                "* Family newsletters and updates\n"
                "* Educational materials about investing and wealth management\n"
                "* Legacy statements and family mission documents\n"
                "* Letters to beneficiaries for milestone events\n"
                "* Investment policies and guidelines\n"
                "* Financial reports and summaries\n"
                "* Custom content based on your specific requirements\n\n"
                "Let me know what you'd like to create, and I can generate a draft tailored to your family's "
                "specific situation and values."
            )
            suggestions = [
                "Create a family newsletter",
                "Draft an educational guide on Bitcoin",
                "Write a legacy statement",
                "Generate an investment policy document"
            ]
            resources = [
                Resource(
                    title="Content Types for Family Wealth Communication",
                    description="Overview of effective content formats for trust management"
                ),
                Resource(
                    title="Effective Communication for Family Wealth",
                    description="Best practices for clear financial documentation"
                )
            ]
            action_items = [
                ActionItem(
                    action="Define content calendar",
                    description="Establish regular schedule for different content types",
                    priority="medium"
                ),
                ActionItem(
                    action="Gather family preferences",
                    description="Survey family members on desired content and formats",
                    priority="low"
                )
            ]
        
        return ContentGenerationResponse(
            type="content",
            response=response,
            suggestions=suggestions,
            resources=resources,
            actionItems=action_items
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate content: {str(e)}") from e
