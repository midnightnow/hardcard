from fastapi import APIRouter, HTTPException, Query, Response, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal
import databutton as db
from app.auth import AuthorizedUser # Added import
import weasyprint
import re

router = APIRouter(prefix="/pitch-deck", tags=["Pitch Deck"])

# Structured slide data from MYA-73
SLIDE_DATA = [
    {
        "type": "cover",
        "title": {
            "default": "Hardcard.World",
            "vc": "Hardcard.World: Investing in the Future of AI Labor",
            "crypto": "Hardcard.World: Decentralized AI Workforce Protocol",
            "gov": "Hardcard.World: Sovereign AI Labor Infrastructure"
        },
        "subtitle": {
            "default": "Protocol-Grade AI Marketplace Infrastructure",
            "vc": "High-Growth Potential in AI-Driven Economies",
            "crypto": "Trustless, On-Chain AI Task Execution",
            "gov": "Secure & Auditable AI Solutions for Public Sector"
        },
        "tagline": {
            "default": "“Secure, Modular, AI-Powered Labor Protocol”",
            "vc": "“Unlocking Alpha in AI-Powered Human Capital”",
            "crypto": "“The Trust Layer for the Global AI Workforce”",
            "gov": "“Empowering National AI Capabilities, Securely”"
        }
    },
    {
        "type": "problem",
        "title": "The Problem",
        "subtitle": {
            "default": "The Future of Work Has No Platform",
            "vc": "Fragmented AI Labor Market Limits Scalability & ROI",
            "crypto": "Lack of Trust & Interoperability in Web3 AI",
            "gov": "Challenges in Securely Deploying & Managing AI Labor"
        },
        "points": {
            "default": [
                "AI labor is fragmented, opaque, and insecure.",
                "No trust model for agent-based or anonymous work.",
                "No unified protocol connecting crypto payments to AI job execution."
            ],
            "vc": [
                "AI development is siloed, hindering collaborative innovation and market efficiency.",
                "Absence of standardized verification creates risk and slows adoption of AI agents.",
                "Current payment rails are ill-suited for micro-transactions and AI-driven gig economies."
            ],
            "crypto": [
                "The AI agent economy lacks a decentralized trust fabric, exposing users to counterparty risk.",
                "No universal standard for AI task verification on-chain prevents truly autonomous systems.",
                "Bridging fiat payments to crypto for AI services remains a significant friction point."
            ],
            "gov": [
                "Procurement and management of AI services lack transparency and robust security frameworks.",
                "Verification of AI-driven work and its outputs is critical but non-standardized.",
                "Integration of AI into public services requires auditable and compliant infrastructure."
            ]
        }
    },
    {
        "type": "solution",
        "title": "The Solution",
        "subtitle": {
            "default": "Hardcard.World is the OS for AI-Powered Labor",
            "vc": "A Unified Protocol for Verifiable, Scalable AI Work",
            "crypto": "Decentralized, Trustless Infrastructure for the AI Agent Economy",
            "gov": "A Secure, Auditable Platform for Sovereign AI Deployment"
        },
        "points": {
            "default": [
                "Secure, verifiable task containers (Gems)",
                "Escrow-backed payments (Stripe & BTC)",
                "AI + humans can work, prove, and earn"
            ],
            "vc": [
                "**Standardized Task Containers (Gems):** Ensuring interoperability and quality control for AI outputs.",
                "**Robust Escrow & Payment Layer:** Facilitating seamless, secure transactions for AI services (fiat & crypto).",
                "**Verifiable Credentials & Reputation:** Building a trusted ecosystem for AI agents and human contributors."
            ],
            "crypto": [
                "**Immutable Task Environments (Gems):** On-chain verifiable containers for AI execution.",
                "**Crypto-Native Escrow & Payments:** Supporting BTC and diverse digital assets for AI service settlement.",
                "**Decentralized Identity & Proof-of-Work:** Enabling pseudonymous, secure participation for AI and human agents."
            ],
            "gov": [
                "**Auditable Task Containers (Gems):** Providing transparent and secure execution environments for AI services.",
                "**Compliant Payment & Escrow System:** Supporting traditional and digital currency payments with full audit trails.",
                "**Role-Based Access & Control:** Ensuring secure management of AI workflows within public sector mandates."
            ]
        },
        "checkmarks": {
            "default": [
                "✅ AI jobs run in encrypted sandboxes",
                "✅ Proof-of-execution is audit-ready",
                "✅ AI or human agents complete tasks"
            ],
            "vc": [
                "✅ Mitigates execution risk for AI tasks",
                "✅ Enables auditable and compliant AI operations",
                "✅ Unlocks new models for AI-driven service delivery"
            ],
            "crypto": [
                "✅ Cryptographically secure and tamper-proof AI job execution",
                "✅ On-chain proof-of-completion for trustless settlement",
                "✅ Fosters a permissionless ecosystem for AI agents"
            ],
            "gov": [
                "✅ Ensures data sovereignty and security for AI workloads",
                "✅ Provides full auditability for public sector AI initiatives",
                "✅ Enables secure collaboration between government agencies and AI providers"
            ]
        }
    },
    {
        "type": "product_stack",
        "title": "Product Stack",
        "table": {
            "headers": ["Layer", "Product", "Purpose"],
            "rows": {
                "default": [
                    ["**Protocol**", "Hardcard.World", "Escrow, agent infra, traceability, APIs"],
                    ["**App**", "NexusAI", "AI coding & microtask job marketplace"],
                    ["**Tooling**", "CodeGem.ai", "Agent delivery & secure execution endpoint"]
                ],
                "vc": [
                    ["**Core Protocol**", "Hardcard.World", "Foundation for secure AI work: Escrow, Identity, Verification APIs."],
                    ["**Flagship Marketplace**", "NexusAI", "Demonstrating AI task commerce, driving early adoption and network effects."],
                    ["**Developer Toolkit**", "CodeGem.ai", "Empowering builders with secure agent deployment and management tools."]
                ],
                "crypto": [
                    ["**Base Layer**", "Hardcard.World", "Decentralized protocol for AI task escrow, identity, and on-chain proofs."],
                    ["**Community Platform**", "NexusAI", "A Web3-native marketplace for AI agents and crypto-incentivized tasks."],
                    ["**Agent SDK**", "CodeGem.ai", "Tools for creating and deploying autonomous agents onto the Hardcard network."]
                ],
                "gov": [
                    ["**Infrastructure Layer**", "Hardcard.World", "Sovereign-grade protocol for secure AI tasking, data handling, and audit trails."],
                    ["**Pilot Application**", "NexusAI (GovMod)", "Customizable platform for managing public sector AI projects and workforce."],
                    ["**Integration Suite**", "CodeGem.ai (GovConnect)", "Secure APIs and tools for integrating Hardcard with existing government systems."]
                ]
            }
        }
    },
    {
        "type": "how_it_works",
        "title": "How It Works",
        "points": {
            "default": [
                "Client posts a job.",
                "Agent or Provider accepts.",
                "System spawns a **GemInstance** (secure task container).",
                "Work completes → proof logged → payment released."
            ],
            "vc": [
                "**1. Task Creation:** User defines job scope, budget, and desired outcome on NexusAI or via API.",
                "**2. Secure Execution:** Hardcard protocol provisions an encrypted **GemInstance** for the AI agent.",
                "**3. Verifiable Completion:** Agent performs work; proofs are logged immutably.",
                "**4. Automated Settlement:** Payment is released from escrow upon successful, verified completion."
            ],
            "crypto": [
                "**1. Job Offering:** Task is published on-chain or via decentralized job boards integrated with Hardcard.",
                "**2. Agent Commitment:** AI agent (or human proxy) stakes collateral to accept the task in a **GemInstance**.",
                "**3. Proof-of-Execution:** Agent submits cryptographic proof of work to the Hardcard oracle/contract.",
                "**4. Trustless Payout:** Smart contract releases funds upon validation of the proof."
            ],
            "gov": [
                "**1. Service Request:** Government entity defines a task with specific security and compliance needs.",
                "**2. Controlled Dispatch:** Hardcard assigns the task to an authorized AI agent within a **GemInstance**.",
                "**3. Audited Performance:** All actions and data are logged for comprehensive oversight and review.",
                "**4. Compliant Disbursement:** Funds are released through approved channels upon verified task fulfillment."
            ]
        },
        "note": {
            "default": "🎥 Animated visual/video available upon request.",
            "vc": "📈 Workflow designed for scalability and minimal operational overhead.",
            "crypto": "🔗 Fully on-chain (or L2) settlement and verification pathways available.",
            "gov": "🛡️ Built for compliance with stringent data handling and security protocols."
        }
    },
    {
        "type": "business_model",
        "title": "Business Model",
        "points": {
            "default": [
                "10% protocol fee per job (escrowed & auditable)",
                "Optional premium dashboards for DAOs, governments, & enterprises",
                "Agent SDKs + integrations (Claude, Gemini, OSS)"
            ],
            "vc": [
                "**Transaction Fees:** Scalable revenue from a percentage fee on all AI tasks (target 2-5%).",
                "**SaaS Subscriptions:** Premium features for enterprise clients (NexusAI Pro, CodeGem.ai Enterprise).",
                "**Strategic Partnerships:** Licensing and integration fees for embedding Hardcard tech into existing platforms."
            ],
            "crypto": [
                "**Protocol Utility Token:** Fees paid in native token ($HCW), creating demand and utility for token holders.",
                "**Staking & Governance:** Token holders can stake for network security, earn rewards, and participate in governance.",
                "**Marketplace Curation:** Fees for featured listings or premium agent profiles on NexusAI."
            ],
            "gov": [
                "**Platform Licensing:** Annual or per-seat licensing for government agencies using dedicated Hardcard instances.",
                "**Custom Deployments:** Fees for bespoke Hardcard deployments tailored to specific sovereign requirements.",
                "**Support & Maintenance:** Service contracts for ongoing technical support and system upkeep."
            ]
        }
    },
    {
        "type": "why_now",
        "title": "Why Now?",
        "points": {
            "default": [
                "Surge in AI agent APIs and open-source autonomy",
                "Crypto-native labor needs structure, verification",
                "Governments and DAOs demand transparency"
            ],
            "vc": [
                "**AI Agent Explosion:** Rapid advancements in LLMs and agent tech are creating a new labor category.",
                "**Market Immaturity:** The AI labor market lacks standardization, creating a greenfield opportunity.",
                "**Demand for Verification:** As AI takes on more critical tasks, the need for trusted verification is paramount."
            ],
            "crypto": [
                "**Web3 & AI Convergence:** The intersection of AI and blockchain is a nascent super-cycle.",
                "**DAO Workforce Growth:** DAOs require robust, trustless infrastructure for managing contributors and tasks.",
                "**Need for On-Chain Reputation:** Verifiable credentials for AI agents will unlock new economic models."
            ],
            "gov": [
                "**National AI Strategies:** Governments worldwide are prioritizing AI development and adoption.",
                "**Public Sector Modernization:** Demand for efficient, transparent, and secure AI solutions in government.",
                "**Data Sovereignty Concerns:** Need for AI infrastructure that respects national data control and security."
            ]
        },
        "quote": {
            "default": "🧠 \"We are the Docker + Stripe + Fiverr of AI work.\"",
            "vc": "📈 \"Hardcard.World is positioned to become the essential trust and transaction layer for the burgeoning AI economy.\"",
            "crypto": "🔗 \"By bridging on-chain trust with off-chain AI execution, Hardcard.World unlocks the permissionless AI workforce.\"",
            "gov": "🛡️ \"Hardcard.World offers a pathway for governments to harness AI's power while ensuring security, auditability, and sovereign control.\""
        }
    },
    {
        "type": "market_size",
        "title": "Market Size",
        "points": { 
            "default": [
                "AI Task Market: $130B+ (Projected)",
                "DAO & Crypto Payroll / Bounties: $2B+ (Growing)",
                "Workforce & GovTech APIs: $50B+ (Emerging)"
            ],
            "vc": [
                "Global AI Services Market: Projected > $500B by 2027 (CAGR ~30%).",
                "Gig Economy & Freelance Platforms: > $450B, ripe for AI disruption.",
                "Enterprise AI Solutions: Significant spend on AI integration and workflow automation."
            ],
            "crypto": [
                "Decentralized AI (DeAI) Market: Early stage, high-growth potential, mirroring DeFi's trajectory.",
                "On-Chain Value Transfer for Services: Expanding beyond simple payments to complex service agreements.",
                "Tokenized Work & Bounties: Increasing adoption within DAO and Web3 ecosystems."
            ],
            "gov": [
                "GovTech Market: > $400B, with increasing investment in AI and digital transformation.",
                "Public Sector AI Spending: Rapidly growing as governments seek efficiency and innovation.",
                "Secure Cloud & Sovereign Infrastructure: Key investment areas aligning with Hardcard's offering."
            ]
        }
    },
    {
        "type": "go_to_market",
        "title": "Go-To-Market Strategy",
        "points": {
            "default": [
                "Launch **NexusAI** → target AI coders & microtask DAOs",
                "Convert waitlist via `/crmQueue` funnel → contributors & providers",
                "Expand to **open agents**, **secure B2B bundles**, **sovereign integrations**"
            ],
            "vc": [
                "**Phase 1: NexusAI Launch & Community Building:** Target AI developers and early-adopter enterprises. Build strong community via developer programs.",
                "**Phase 2: Enterprise Sales & Partnerships:** Direct sales to businesses needing AI workflow automation. Strategic alliances with AI/Cloud providers.",
                "**Phase 3: Protocol Ecosystem Growth:** Foster third-party development on Hardcard protocol, expanding use cases and network effects."
            ],
            "crypto": [
                "**Phase 1: NexusAI for Web3:** Target DAO treasuries, crypto projects needing AI services, and individual crypto-savvy freelancers.",
                "**Phase 2: Token Launch & Liquidity:** Introduce $HCW token, enabling staking, governance, and protocol fee payments. Seed liquidity on DEXs.",
                "**Phase 3: Developer Grants & Ecosystem Fund:** Incentivize building of new marketplaces and tools on the Hardcard protocol."
            ],
            "gov": [
                "**Phase 1: Pilot Programs & Proof-of-Concepts:** Engage with select government agencies to demonstrate value in controlled environments.",
                "**Phase 2: Strategic GovTech Partnerships:** Collaborate with established government IT contractors and system integrators.",
                "**Phase 3: Standardization & Compliance Frameworks:** Work towards official certifications and inclusion in government procurement frameworks."
            ]
        }
    },
    {
        "type": "team_advisors",
        "title": "Team & Advisors", 
        "points": [ 
            "Founder: *Dallas McMillan*",
            "Advisors: [Seeking experts in AI, Cryptography, GovTech, and Venture Capital]"
        ]
    },
    {
        "type": "vision",
        "title": "Vision",
        "quote": {
            "default": "> “Imagine your government, company, or DAO launching a secure labor economy — instantly.”",
            "vc": "> “We are building the foundational infrastructure for a global, trillion-dollar AI-driven labor market.”",
            "crypto": "> “A future where AI agents and humans collaborate seamlessly in a decentralized, trustless global economy.”",
            "gov": "> “Empowering nations with secure, sovereign AI capabilities to enhance public services and national competitiveness.”"
        },
        "points": {
            "default": [
                "Governments onboard jobs.",
                "Citizens onboard skills.",
                "Everyone earns, logs, and levels up."
            ],
            "vc": [
                "Global standard for AI task verification and settlement.",
                "Exponential growth driven by network effects and protocol adoption.",
                "A new asset class based on verifiable AI-driven productivity."
            ],
            "crypto": [
                "A truly permissionless and decentralized AI workforce.",
                "On-chain reputation and credentials for AI agents.",
                "Seamless integration of AI into DAOs and Web3 applications."
            ],
            "gov": [
                "Enhanced public sector efficiency through AI automation.",
                "Increased national competitiveness via sovereign AI capabilities.",
                "Secure and transparent AI governance frameworks."
            ]
        }
    },
    {
        "type": "cta",
        "title": "Call to Action", 
        "points": {
            "default": [
                "**Investors:** LBP, equity, grants, or token round",
                "**Partners:** Launch your own agent marketplace on Hardcard",
                "**Governments & DAOs:** Create work. Verify skill. Pay securely."
            ],
            "vc": [
                "**Invest:** Join us in capitalizing on the AI labor revolution. Seeking [$X.XM Seed Funding].",
                "**Partner:** Integrate Hardcard to bring trust and efficiency to your AI platforms.",
                "**Contact:** [email protected] / hardcard.world/investors"
            ],
            "crypto": [
                "**Participate:** Join the $HCW token sale / IDO. Details at [hardcard.world/token].",
                "**Build:** Develop on the Hardcard protocol. Grants available for innovative projects.",
                "**Community:** Join our Discord/Telegram: [links]"
            ],
            "gov": [
                "**Pilot Program:** Partner with us to deploy Hardcard for your agency's AI needs.",
                "**Briefing:** Request a detailed security and compliance overview.",
                "**Contact:** [gov_contact_email@hardcard.world] / hardcard.world/government"
            ]
        }
    }
]

class GenerateDeckResponse(BaseModel):
    message: str
    pdf_storage_key: str
    html_storage_key: str
    format_generated: str
    persona_generated: str

def generate_slide_html_content(slide_data, persona='default'):
    html_content = ""

    def get_persona_value(field_dict, key, default_value=""):
        if isinstance(field_dict, dict):
            return field_dict.get(persona, field_dict.get('default', default_value))
        return field_dict

    title = get_persona_value(slide_data.get("title"), persona)
    if title:
        html_content += f"<h1>{title}</h1>"

    subtitle = get_persona_value(slide_data.get("subtitle"), persona)
    if subtitle:
        html_content += f"<h2>{subtitle}</h2>"

    tagline = get_persona_value(slide_data.get("tagline"), persona)
    if tagline:
        html_content += f"<p class=\"tagline\"><em>{tagline}</em></p>"

    points_data = slide_data.get("points")
    if points_data:
        points_list = get_persona_value(points_data, persona, [])
        if isinstance(points_list, list):
            html_content += "<ul>"
            for point in points_list:
                processed_point = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', point)
                processed_point = re.sub(r'\*(.*?)\*', r'<em>\1</em>', processed_point)
                html_content += f"<li>{processed_point}</li>"
            html_content += "</ul>"
        elif isinstance(points_list, str):
             html_content += f"<p>{points_list}</p>"

    checkmarks_data = slide_data.get("checkmarks")
    if checkmarks_data:
        checkmark_list = get_persona_value(checkmarks_data, persona, [])
        if isinstance(checkmark_list, list):
            html_content += "<ul class=\"checkmarks\">"
            for item in checkmark_list:
                html_content += f"<li>{item}</li>"
            html_content += "</ul>"

    table_data = slide_data.get("table")
    if table_data and table_data.get("headers") and table_data.get("rows"):
        headers = get_persona_value(table_data.get("headers"), persona, table_data.get("headers").get('default') if isinstance(table_data.get("headers"), dict) else table_data.get("headers"))
        rows_data = get_persona_value(table_data.get("rows"), persona, table_data.get("rows").get('default') if isinstance(table_data.get("rows"), dict) else [])
        
        html_content += "<table><thead><tr>"
        if isinstance(headers, list):
            for header_item in headers: # Renamed to avoid conflict
                processed_header = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', header_item)
                html_content += f"<th>{processed_header}</th>"
        html_content += "</tr></thead><tbody>"
        if isinstance(rows_data, list):
            for row in rows_data:
                html_content += "<tr>"
                for cell in row:
                    processed_cell = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(cell))
                    html_content += f"<td>{processed_cell}</td>"
                html_content += "</tr>"
        html_content += "</tbody></table>"

    quote_data = slide_data.get("quote")
    if quote_data:
        quote_text = get_persona_value(quote_data, persona)
        if quote_text:
            if quote_text.startswith(">"):
                html_content += f"<blockquote><p>{quote_text[1:].strip()}</p></blockquote>"
            else:
                html_content += f"<p class=\"quote-inline\">{quote_text}</p>"
    
    note_data = slide_data.get("note")
    if note_data:
        note_text = get_persona_value(note_data, persona)
        if note_text:
            html_content += f"<p class=\"note\">{note_text}</p>"
    return html_content

def generate_full_deck_html(slides_data_list, founder_name="Dallas McMillan", format="widescreen", persona="default"):
    all_slides_html = ""
    for slide_item_data in slides_data_list:
        current_slide_data = slide_item_data.copy()
        
        if current_slide_data.get("type") == "team_advisors" and current_slide_data.get("points"):
            points_content = current_slide_data["points"]
            if isinstance(points_content, dict):
                 actual_points = points_content.get(persona, points_content.get('default', []))
            else: 
                actual_points = points_content

            updated_points = []
            if isinstance(actual_points, list):
                for point_text in actual_points:
                    if "Founder:" in point_text and founder_name:
                        updated_points.append(f"Founder: <em>{founder_name}</em>") 
                    elif "Advisors:" in point_text: 
                        advisor_text_options = {
                            "default": "Advisors: [Seeking experts in AI, Cryptography, GovTech, and Venture Capital]",
                            "vc": "Advisors: [Highlighting VC-relevant expertise: successful exits, market scaling]",
                            "crypto": "Advisors: [Showcasing Web3 pioneers, tokenomics experts, DAO strategists]",
                            "gov": "Advisors: [Featuring public sector experience, policy advisors, GovTech innovators]"
                        }
                        updated_points.append(advisor_text_options.get(persona, advisor_text_options['default']))
                    else:
                        updated_points.append(point_text)
                if isinstance(points_content, dict):
                    current_slide_data["points"][persona] = updated_points
                else:
                    current_slide_data["points"] = updated_points
            else:
                pass 

        slide_inner_html = generate_slide_html_content(current_slide_data, persona)
        slide_type = current_slide_data.get('type', 'default')
        all_slides_html += f"<div class=\"slide {slide_type} persona-{persona} format-{format}\">{slide_inner_html}</div>"
    
    css = '''
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: #121212; 
        color: #e0e0e0; 
        margin: 0;
        padding: 0;
    }
    .slide {
        width: 100%;
        height: 100%; 
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center; 
        align-items: flex-start; 
        text-align: left; 
        border-bottom: 1px solid #333; 
        page-break-after: always; 
    }
    .slide:last-child {
        page-break-after: avoid;
        border-bottom: none;
    }
    h1 {
        font-size: 3em; 
        color: #ffffff;
        margin-bottom: 0.4em;
        font-weight: 600; 
    }
    h2 {
        font-size: 1.8em; 
        color: #bbbbbb;
        margin-bottom: 0.8em;
        font-weight: 400;
    }
    p, li {
        font-size: 1.25em; 
        line-height: 1.7;
        max-width: 90%; 
    }
    ul {
        list-style-position: outside; 
        margin-top: 1em;
        padding-left: 1.5em; 
    }
    ul.checkmarks li {
        list-style-type: none; 
        padding-left: 0;
        margin-bottom: 0.3em;
    }
     ul.checkmarks li::before {
        content: "✅ "; 
        margin-right: 0.5em;
        color: #4CAF50; 
    }
    .tagline {
        font-size: 1.5em;
        color: #b0b0b0;
        margin-top: 0.5em;
        font-style: italic;
    }
    table {
        width: 100%; 
        margin-top: 1.5em;
        border-collapse: collapse;
        text-align: left;
    }
    th, td {
        border: 1px solid #383838; 
        padding: 0.8em 1em;
        font-size: 1.1em;
    }
    th {
        background-color: #1f1f1f; 
        color: #f0f0f0;
        font-weight: 600;
    }
    blockquote {
        border-left: 4px solid #007acc; 
        padding: 0.5em 1.5em;
        margin: 1.5em 0;
        font-style: italic;
        color: #cccccc;
        background-color: #1a1a1a; 
        border-radius: 4px;
    }
    blockquote p {
        font-size: 1.2em; 
        margin: 0;
    }
    .quote-inline {
        font-style: italic;
        color: #61dafb; 
        margin: 1em 0;
        font-size: 1.3em;
        padding: 0.5em;
        border-left: 3px solid #61dafb;
    }
    .note {
        font-size: 1em;
        color: #888888;
        margin-top: 2em;
        font-style: italic;
    }
    .slide.cover {
        align-items: center; 
        text-align: center;
    }
    .slide.cover h1 {
        font-size: 4em;
    }
    .slide.cover h2 {
        font-size: 2.2em;
    }
    .slide.cover .tagline {
        font-size: 1.7em;
        margin-top: 1em;
    }
    strong {
        font-weight: 700; 
        color: #76c7ff; 
    }
    em {
        font-style: italic;
        color: #a0e8ff; 
    }
    '''
    
    if format == 'widescreen':
        format_css = '''
        @page {
            size: 254mm 142.875mm; 
            margin: 0;
        }
        .slide {
            padding: 30mm 20mm; 
        }
        '''
    else:
        format_css = '''
        @page {
            size: A4;
            margin: 15mm;
        }
        .slide {
            padding: 20mm 15mm; 
        }
        h1 {
            font-size: 2.5em; 
        }
        h2 {
            font-size: 1.6em;
        }
        p, li {
            font-size: 1.1em;
        }
        .slide.cover h1 {
            font-size: 3.5em;
        }
        .slide.cover h2 {
            font-size: 2em;
        }
        '''
    
    combined_css = css + format_css
    
    html_doc = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hardcard.World Pitch Deck</title>
        <style>{combined_css}</style>
    </head>
    <body>
        {all_slides_html}
    </body>
    </html>
    '''
    return html_doc

def sanitize_storage_key(key: str) -> str:
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)



# Forcing a refresh of backend checks
@router.post("/generate", response_model=GenerateDeckResponse, operation_id="generate_pitch_deck")
async def generate_pitch_deck_pdf_endpoint(format: Literal['widescreen', 'a4'] = Query('widescreen', description="The format of the pitch deck to generate."), persona: Literal['default', 'vc', 'crypto', 'gov'] = Query('default', description="The persona for which to generate the pitch deck.")):
    try:
        founder_name = "Dallas McMillan" 
        html_content = generate_full_deck_html(SLIDE_DATA, founder_name, format, persona)
        
        pdf_filename_base = f"Hardcard_Pitch_Deck_{persona}_{format}"
        html_filename_base = f"Hardcard_Pitch_Deck_{persona}_{format}"

        pdf_storage_key = sanitize_storage_key(f"{pdf_filename_base}.pdf")
        html_storage_key = sanitize_storage_key(f"{html_filename_base}.html")

        # Generate PDF from HTML
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        db.storage.binary.put(pdf_storage_key, pdf_bytes)
        
        # Store HTML
        db.storage.text.put(html_storage_key, html_content)

        return GenerateDeckResponse(
            message="Pitch deck generated and saved successfully.",
            pdf_storage_key=pdf_storage_key,
            html_storage_key=html_storage_key,
            format_generated=format,
            persona_generated=persona
        )
    except Exception as e:
        print(f"Error generating pitch deck: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate pitch deck: {str(e)}") from e
    # Ensure a finally or except block is present if try was used
    # finally: # Trigger reload
    #     pass


@router.get("/serve/{filename}", operation_id="serve_main_pitch_deck_file")
async def serve_main_pitch_deck_file_actual_func(filename: str, user: "AuthorizedUser", request: Request):  # Added AuthorizedUser
    print(f"User {user.sub} accessing pitch deck.") # Log user access
    print(f"Request headers: {request.headers}")
    # debug_headers logic removed
    """
    Serves a generated pitch deck file (PDF or HTML) from storage.
    The filename is the storage key.
    Requires authentication.
    """
    try:
        sanitized_filename = sanitize_storage_key(filename)
        
        if not sanitized_filename.endswith((".pdf", ".html")):
            raise HTTPException(status_code=400, detail="Invalid file extension. Only .pdf and .html are supported.")

        if sanitized_filename.endswith(".pdf"):
            file_bytes = db.storage.binary.get(sanitized_filename)
            return Response(content=file_bytes, media_type="application/pdf")
        elif sanitized_filename.endswith(".html"):
            file_content = db.storage.text.get(sanitized_filename)
            return Response(content=file_content, media_type="text/html")
        else:
            # This case should ideally not be reached due to the check above,
            # but as a safeguard:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
            
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}") from e
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to serve file: {str(e)}") from e



