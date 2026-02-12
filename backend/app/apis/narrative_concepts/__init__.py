from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CharacterSketch(BaseModel):
    """A character sketch for the noir mystery narrative"""
    name: str
    role: str
    description: str
    motivations: List[str]
    arc: str
    quotes: List[str]


class NoirMysteryResponse(BaseModel):
    """Response model for the Insurance Noir mystery concept"""
    title: str
    tagline: str
    premise: str
    themes: List[Dict[str, str]]
    setting: str
    plot_synopsis: str
    characters: List[CharacterSketch]
    tone_guide: Dict[str, Any]


class MetaNarrativeElement(BaseModel):
    """A meta-narrative element that connects fiction to reality"""
    name: str
    description: str
    touchpoints: List[str]
    implementation: str


class PodcastEpisode(BaseModel):
    """A concept for a podcast episode in the meta-narrative"""
    title: str
    description: str
    topics: List[str]
    format: str
    duration: str
    guests: Optional[List[str]] = None


class MetaNarrativeResponse(BaseModel):
    """Response model for the meta-narrative concept"""
    title: str
    concept_summary: str
    goal: str 
    target_audience: List[str]
    formats: List[Dict[str, str]]
    elements: List[MetaNarrativeElement]
    pilot_episodes: List[PodcastEpisode]
    arg_components: List[Dict[str, Any]]


@router.get("/noir-mystery")
def get_noir_mystery_brief_concepts() -> Dict[str, Any]:
    """Provides a brief overview of the Noir Mystery (\"Insurance Noir\") concept
    
    This endpoint returns a simplified version of the noir mystery narrative concept,
    which explores themes of legacy, trust, and inheritance through a
    creative storytelling vehicle.
    """
    return {
        "title": "The Legacy Contract",
        "tagline": "When certainty dies, who inherits the truth?",
        "premise": "A detective investigates the suspicious death of a security expert who created an unbreakable 'legacy contract' for a wealthy family.",
        "key_themes": ["Legacy vs. Commerce", "Security and Uncertainty", "Trust Mechanisms", "Inheritance Ethics", "Digital Immortality"],
        "main_characters": ["Eva Mercer (Detective)", "James Hardcastle (Victim)", "Lawrence Devereux (Client)", "Katherine Devereux (Heir)"]  
    }


@router.get("/noir-mystery/outline")
def get_noir_mystery_outline_concepts() -> NoirMysteryResponse:
    """Provides the full Noir Mystery (\"Insurance Noir\") concept outline
    
    This endpoint returns comprehensive details about the noir mystery narrative concept,
    including full character profiles, plot synopsis, and thematic elements.
    """
    noir_mystery = {
        "title": "The Legacy Contract",
        "tagline": "When certainty dies, who inherits the truth?",
        "premise": "When renowned crypto security expert James Hardcastle is found dead after creating an unbreakable 'legacy contract' for a wealthy family, detective Eva Mercer is drawn into a labyrinth of encrypted secrets, family betrayals, and the shadowy intersection of finance and immortality. As Eva navigates this world where wealth transcends generations and security is both physical and digital, she discovers the murder is just the first move in a much deeper game—one that questions the very nature of legacy and trust.",
        
        "themes": [
            {
                "name": "Legacy vs. Commerce",
                "description": "Exploration of the tension between genuine legacy building and the commercialization of inheritance and family wealth preservation."
            },
            {
                "name": "Security and Uncertainty",
                "description": "Examining the paradox of seeking absolute security in an inherently uncertain world, reflected in both cryptographic systems and human relationships."
            },
            {
                "name": "Trust Mechanisms",
                "description": "Contrasting human trust with technological trust mechanisms, questioning which is more reliable across generational time spans."
            },
            {
                "name": "Inheritance Ethics",
                "description": "Confronting the moral complexities of wealth transfer and what responsibilities come with inherited assets and knowledge."
            },
            {
                "name": "Digital Immortality",
                "description": "Examining the allure and pitfalls of attempting to extend influence beyond death through technology and financial instruments."
            }
        ],
        
        "setting": "Present day with near-future technological elements, primarily set in a fictional financial district known as 'The Trust Corridor'—a nexus of old money, new tech, and secretive family offices.",
        
        "plot_synopsis": "Detective Eva Mercer, formerly a digital forensics specialist before joining homicide, is called to investigate when James Hardcastle—founder of security firm HardSec—is found dead in his office. The apparent suicide doesn't convince Eva, especially when she learns Hardcastle had just completed his magnum opus: an unbreakable 'legacy contract' for the secretive Devereux family.\n\nAs Eva investigates, she discovers Hardcastle had created a revolutionary system combining physical security devices ('hard cards') with cryptographic protocols designed to transfer and preserve wealth and knowledge across generations with mathematical certainty. The Devereux patriarch, facing terminal illness, had commissioned this system to ensure his complex empire would transfer to his heirs exactly as he intended—with conditions that would maintain his control years after his death.\n\nThe investigation leads Eva through a world where wealth, technology, and family secrets intersect. She encounters Katherine Devereux, the rebellious heir who questions the ethics of her father's posthumous control; Simon Whittaker, a legacy planning advisor whose philosophical approach clashes with Hardcastle's technological solutions; and Elias Crane, a competitor who believes legacy should be earned, not engineered.\n\nAs bodies begin accumulating—each killed with methods that reference different inheritance traditions—Eva realizes she's dealing with someone who's not just eliminating rivals but making a statement about the very concept of legacy planning. The killer leaves cryptic messages referencing both ancient inheritance practices and cutting-edge blockchain technology.\n\nThe mystery deepens when Eva discovers Hardcastle had embedded a fundamental flaw in the legacy contract—one that would eventually transfer the entire Devereux fortune to an unknown entity. This revelation transforms the case from murder to something far more complex: a philosophical battle over who has the right to determine how wealth and wisdom transfer across generations.\n\nThe story climaxes when Eva discovers the true killer's identity and motivation, revealing a critique of legacy planning that forces all characters—and the audience—to question their assumptions about immortality through wealth, the ethics of posthumous control, and what truly constitutes a meaningful legacy.",
        
        "characters": [
            CharacterSketch(
                name="Eva Mercer",
                role="Lead Detective",
                description="Former digital forensics expert turned homicide detective with a skeptical view of wealth preservation after witnessing how inheritance disputes destroyed her own family.",
                motivations=[
                    "Seeking truth beyond appearances",
                    "Reconciling technical knowledge with human intuition",
                    "Understanding the true meaning of legacy after her own disinheritance"
                ],
                arc="From seeing legacy as purely financial to recognizing the multiple dimensions of what we leave behind",
                quotes=[
                    "The dead don't get to rule the living. At least, they shouldn't.",
                    "Security isn't in the lock. It's in knowing who holds the key.",
                    "The more perfect the system, the more devastating its inevitable failure."
                ]
            ),
            CharacterSketch(
                name="James Hardcastle",
                role="Murder Victim / Security Innovator",
                description="Brilliant and uncompromising founder of HardSec, devoted to creating 'mathematical certainty' in a world of human unpredictability.",
                motivations=[
                    "Achieving technological immortality through his work",
                    "Proving that systems can be more trustworthy than people",
                    "Secretly undermining the legacy planning industry from within"
                ],
                arc="From true believer in technological solutions to harboring doubts about the ethics of his life's work",
                quotes=[
                    "Trust is a vulnerability. Verification is strength.",
                    "The best security doesn't rely on secrets but on mathematical impossibility.",
                    "A proper legacy continues working exactly as intended, long after its creator is dust."
                ]
            ),
            CharacterSketch(
                name="Lawrence Devereux",
                role="Dying Patriarch / Client",
                description="Calculating patriarch of the Devereux financial empire, using his impending death to design a system that ensures his will is followed for generations.",
                motivations=[
                    "Maintaining control beyond death",
                    "Protecting his heirs from themselves",
                    "Ensuring his life's work isn't dismantled"
                ],
                arc="From believing in absolute control to questioning whether true legacy comes from freedom rather than constraints",
                quotes=[
                    "Death is merely a transition of authority, not its conclusion.",
                    "Trust is for those without the means to ensure compliance.",
                    "A family fortune without proper governance becomes a family misfortune within three generations."
                ]
            ),
            CharacterSketch(
                name="Katherine Devereux",
                role="Heir / Rebel",
                description="Brilliant but rebellious daughter of Lawrence, with expertise in both finance and ethics, questioning the morality of engineered inheritance systems.",
                motivations=[
                    "Establishing her own identity outside her father's shadow",
                    "Reforming rather than rejecting the family's wealth and influence",
                    "Finding the humanity within legacy planning"
                ],
                arc="From rejecting her inheritance to reimagining what it could become",
                quotes=[
                    "Legacy isn't what's locked in a vault; it's what changes in the world.",
                    "The tighter you grip wealth, the less valuable it becomes.",
                    "I don't want to inherit a prison, even if it's made of gold."
                ]
            ),
            CharacterSketch(
                name="Simon Whittaker",
                role="Legacy Philosophy Advisor",
                description="Former ethics professor turned legacy planning consultant who advocates for wisdom transfer over mere wealth preservation.",
                motivations=[
                    "Humanizing the legacy planning industry",
                    "Promoting philosophical over financial inheritance",
                    "Reconciling traditional values with modern wealth management"
                ],
                arc="From academic theorist to active participant in reshaping how legacy is understood",
                quotes=[
                    "A true inheritance is measured in wisdom, not dollars.",
                    "The best security isn't a better lock, but raising children who wouldn't steal from you.",
                    "Every generation should rewrite its own contract with wealth."
                ]
            ),
            CharacterSketch(
                name="Elias Crane",
                role="Rival Security Expert / Suspect",
                description="Hardcastle's former partner and now bitter rival, advocating for 'earned legacy' over engineered inheritance, with a mysterious past connected to failed inheritance systems.",
                motivations=[
                    "Discrediting Hardcastle's approach to legacy planning",
                    "Proving the superiority of merit-based inheritance",
                    "Hiding his own involvement in legacy contract failures"
                ],
                arc="From seeking to destroy legacy planning to reinventing it",
                quotes=[
                    "Inheritance is the enemy of innovation.",
                    "A fortune passed down becomes a burden, not a blessing.",
                    "Security doesn't exist. There are only varying levels of insecurity."
                ]
            )
        ],
        
        "tone_guide": {
            "narrative_voice": "Detached but introspective third-person limited perspective that balances technical precision with philosophical depth.",
            "atmosphere": "Modern noir with clinical, almost antiseptic settings contrasted with the messy reality of human emotions and relationships.",
            "visual_elements": [
                "Stark contrasts between ultra-modern security installations and traditional symbols of wealth",
                "Recurring motif of keys, locks, and barriers—both physical and digital",
                "Visualizations of inheritance structures as architectural spaces",
                "Time-lapse elements showing the passage of generations"
            ],
            "dialogue_style": "Layered conversations where characters discuss inheritance mechanics on the surface while addressing deeper philosophical questions through subtext.",
            "thematic_progression": "Beginning with a focus on the technical aspects of legacy planning before gradually revealing the human costs and ethical questions behind each system."
        }
    }
    
    return NoirMysteryResponse(**noir_mystery)


@router.get("/meta-narrative")
def get_narrative_meta_concept_for_noir() -> MetaNarrativeResponse:
    """Provides the Meta-Narrative concept
    
    This endpoint returns details about the meta-narrative framework,
    including podcast concepts, ARG components, and the overall approach
    to weaving together fiction and reality.
    """
    meta_narrative = {
        "title": "The Hard Card Chronicles: Legacy Decoded",
        "concept_summary": "A multi-layered narrative experience that weaves together fictional storytelling, documentary-style podcasts, and interactive elements to explore the real-world inspirations, implications, and applications of the Hard Card Universe concepts.",
        "goal": "To create an immersive narrative ecosystem that both entertains and educates, using the noir mystery as a creative vehicle while simultaneously documenting the actual development of the Hard Card Universe through meta-commentary and real-world exploration.",
        
        "target_audience": [
            "Forward-thinking investors and wealth managers interested in next-generation legacy planning",
            "Technology enthusiasts fascinated by the intersection of cryptography, inheritance, and digital identity",
            "Podcast listeners who enjoy both fictional storytelling and behind-the-scenes creative insights",
            "Families navigating complex inheritance and knowledge transfer challenges",
            "Individuals interested in philosophical questions about legacy, mortality, and posthumous influence"
        ],
        
        "formats": [
            {
                "name": "Dual-Reality Podcast",
                "description": "A podcast series that alternates between fictional episodes set in 'The Legacy Contract' universe and documentary episodes exploring the real-world concepts, challenges, and people in the legacy planning space."
            },
            {
                "name": "Companion Website",
                "description": "An interactive website that serves as both an in-world artifact from the mystery and a real resource for Hard Card Universe concepts, blurring the line between fiction and reality."
            },
            {
                "name": "Mixed-Media Social Elements",
                "description": "Character social media accounts that interact with real experts and commentators, creating a conversation that spans the fictional/factual divide."
            },
            {
                "name": "Interactive Timeline",
                "description": "A visualization tool showing both the fictional murder mystery timeline alongside the actual development timeline of the HCU ecosystem."
            }
        ],
        
        "elements": [
            MetaNarrativeElement(
                name="The Fourth Wall Journal",
                description="A recurring podcast segment where the creators step out of the narrative to discuss the real-world inspirations, technical details, and philosophical questions raised by the story.",
                touchpoints=[
                    "End-of-episode commentary tracks",
                    "Special 'behind the curtain' episodes between major story arcs",
                    "Written companion pieces on the website that expand on concepts"
                ],
                implementation="Recorded conversations between writers, technical advisors, and guest experts that acknowledge the fictional nature of the main story while exploring its real-world foundations."
            ),
            MetaNarrativeElement(
                name="Parallel Development Documentaries",
                description="A series that documents the actual creation of the Hard Card Universe ecosystem, featuring real developers, financial experts, and potential users discussing the challenges and possibilities.",
                touchpoints=[
                    "'Making of' episodes released between fiction episodes",
                    "Technical deep-dives featuring actual prototype demonstrations",
                    "Interviews with experts in relevant fields (cryptography, inheritance law, etc.)"
                ],
                implementation="Documentary-style production following the real development process, with challenges and breakthroughs that sometimes influence the direction of the fictional narrative."
            ),
            MetaNarrativeElement(
                name="Concept Mirroring",
                description="Deliberate parallels between fictional plot developments and real-world HCU milestones, creating resonance between the story and actual progress.",
                touchpoints=[
                    "Fictional breakthroughs that coincide with actual technical achievements",
                    "Character dilemmas that reflect real ethical questions facing the team",
                    "Story elements that test audience reaction to potential features or approaches"
                ],
                implementation="Coordinated storytelling that uses fiction as both a proving ground for concepts and a way to make technical developments more accessible and engaging."
            ),
            MetaNarrativeElement(
                name="Reality Crossover Events",
                description="Special episodes or events where fictional characters interact with real-world experts, or where real developments directly influence the murder mystery plot.",
                touchpoints=[
                    "Expert guest appearances 'in character' within the fiction",
                    "Live events that blend storyline advancement with actual product demonstrations",
                    "Community challenges that affect both story outcomes and product development"
                ],
                implementation="Carefully scripted interactions that maintain narrative integrity while allowing meaningful connection to actual HCU development and community."
            )
        ],
        
        "pilot_episodes": [
            PodcastEpisode(
                title="The Hard Contract (Fiction)",
                description="The discovery of James Hardcastle's body and the introduction of Detective Eva Mercer as she begins to unravel the mysterious 'legacy contract' at the center of the case.",
                topics=["Murder mystery setup", "Introduction to legacy contracts", "Character foundations"],
                format="Fully produced audio drama with voice actors, sound design, and atmospheric scoring",
                duration="35-40 minutes"
            ),
            PodcastEpisode(
                title="Legacy by Design (Documentary)",
                description="An exploration of the real-world inspiration behind the Hard Card Universe concept, featuring interviews with the creator and technical experts about the challenges of intergenerational wealth and knowledge transfer.",
                topics=["HCU origin story", "Technical foundations", "Market need analysis"],
                format="Interview-based documentary with expert commentary and conceptual explanations",
                duration="25-30 minutes",
                guests=["Dallas McMillan (Creator)", "Cryptography Expert", "Estate Planning Professional"]
            ),
            PodcastEpisode(
                title="The Devereux Directive (Fiction)",
                description="Eva's investigation leads her deeper into the Devereux family dynamics and the ethical questions surrounding posthumous control mechanisms in inheritance.",
                topics=["Family dynamics in wealth transfer", "Ethics of posthumous control", "Security vs. freedom tension"],
                format="Audio drama continuing the mystery with increased character development",
                duration="35-40 minutes"
            ),
            PodcastEpisode(
                title="Hard Problems: Cryptography Across Time (Documentary)",
                description="A technical but accessible exploration of the cryptographic challenges involved in creating truly long-lasting digital security, especially across generational timeframes.",
                topics=["Cryptographic time guarantees", "Physical vs. digital security", "HardCard prototype concepts"],
                format="Technical deep-dive with practical examples and historical context",
                duration="30-35 minutes",
                guests=["Cryptography Researcher", "Hardware Security Expert", "Digital Preservation Specialist"]
            ),
            PodcastEpisode(
                title="Behind The Narrative (Meta-Commentary)",
                description="A special episode where the creators discuss the development of both the fictional story and the real Hard Card Universe, exploring how they inform and influence each other.",
                topics=["Creative process insights", "Technical implementation challenges", "Community feedback integration"],
                format="Informal roundtable discussion with creators, developers, and selected audience members",
                duration="45-50 minutes",
                guests=["Story Writers", "Technical Team Members", "Early Audience Representatives"]
            )
        ],
        
        "arg_components": [
            {
                "name": "The HardSec Archives",
                "description": "A collection of in-world documents, emails, and files from the fictional HardSec company that contain both story elements and actual technical concepts relevant to the real HCU development.",
                "interaction_method": "Web-based repository with puzzles that unlock additional content",
                "reality_connection": "Documents contain usable insights about legacy planning and security that apply in the real world"
            },
            {
                "name": "Devereux Family Legacy Test",
                "description": "An interactive assessment tool presented as the fictional test used by the Devereux family to evaluate inheritance worthiness, but actually providing valuable insights about personal values and approaches to legacy.",
                "interaction_method": "Online questionnaire with detailed analysis of results",
                "reality_connection": "Results include actionable recommendations for real-world legacy planning based on individual priorities"
            },
            {
                "name": "Detective's Evidence Board",
                "description": "A community collaborative space framed as Eva Mercer's investigation board, where audience members help connect clues and solve puzzles.",
                "interaction_method": "Digital corkboard with social features for collaborative investigation",
                "reality_connection": "Some puzzles require research into actual inheritance mechanisms, cryptography concepts, or historical legacy practices"
            },
            {
                "name": "Prototype Testing Program",
                "description": "A program where selected participants receive prototype 'hard cards' presented as props from the story but actually functioning as early test versions of the real technology.",
                "interaction_method": "Physical hardware combined with special podcast content and online challenges",
                "reality_connection": "Provides real user testing data while advancing the narrative through exclusive content"
            }
        ]
    }
    
    return MetaNarrativeResponse(**meta_narrative)
