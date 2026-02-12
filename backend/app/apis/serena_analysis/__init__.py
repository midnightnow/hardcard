from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


router = APIRouter()


class Task(BaseModel):
    title: str
    description: str
    dependencies: List[str]
    effort: str
    category: str


class GenerateTasksResponse(BaseModel):
    tasks: List[Task]


class MCPToolUseResponse(BaseModel):
    content: Dict[str, Any]


class AICodingLevelsResponse(BaseModel):
    content: Dict[str, Any]


class AgentMasterPromptResponse(BaseModel):
    content: Dict[str, Any]


class SerenaCompleteResponse(BaseModel):
    tasks: List[Task]
    mcp_tool_use: Dict[str, Any]
    ai_coding_levels: Dict[str, Any]
    agent_master_prompt: Dict[str, Any]


@router.get("/generate-tasks")
def generate_serena_tasks() -> GenerateTasksResponse:
    """
    Generate a comprehensive set of tasks for a deep dive analysis of the Serena codebase.
    
    Returns a structured list of 50 tasks with title, description, dependencies, and effort level.
    """
    # Complete list of 50 tasks organized by category
    tasks = [
        # Clone & Build
        {
            "title": "Clone repository",
            "description": "Clone the Serena GitHub repository locally.",
            "dependencies": [],
            "effort": "S",
            "category": "Clone & Build"
        },
        {
            "title": "Install dependencies",
            "description": "Install all required dependencies for the Serena project.",
            "dependencies": ["Clone repository"],
            "effort": "S",
            "category": "Clone & Build"
        },
        {
            "title": "Build project",
            "description": "Run the build process for the Serena project.",
            "dependencies": ["Install dependencies"],
            "effort": "M",
            "category": "Clone & Build"
        },
        {
            "title": "Run tests",
            "description": "Execute the test suite to verify the build.",
            "dependencies": ["Build project"],
            "effort": "M",
            "category": "Clone & Build"
        },
        
        # README & Docs
        {
            "title": "Read README",
            "description": "Thoroughly read the README.md file.",
            "dependencies": ["Clone repository"],
            "effort": "S",
            "category": "README & Docs"
        },
        {
            "title": "Read documentation",
            "description": "Study all files in the docs/ directory.",
            "dependencies": ["Clone repository"],
            "effort": "M",
            "category": "README & Docs"
        },
        {
            "title": "Review contributing guidelines",
            "description": "Understand the contribution process and standards.",
            "dependencies": ["Clone repository"],
            "effort": "S",
            "category": "README & Docs"
        },
        {
            "title": "Analyze examples directory",
            "description": "Study example code and usage patterns in the examples/ directory.",
            "dependencies": ["Clone repository"],
            "effort": "M",
            "category": "README & Docs"
        },
        
        # Directory Structure
        {
            "title": "Map top-level directories",
            "description": "Identify and document the purpose of all top-level directories.",
            "dependencies": ["Clone repository"],
            "effort": "S",
            "category": "Directory Structure"
        },
        {
            "title": "Analyze source directory",
            "description": "Document the organization and structure of the main source code directory.",
            "dependencies": ["Map top-level directories"],
            "effort": "M",
            "category": "Directory Structure"
        },
        {
            "title": "Create dependency graph",
            "description": "Create a visual dependency graph between major modules and components.",
            "dependencies": ["Analyze source directory"],
            "effort": "L",
            "category": "Directory Structure"
        },
        {
            "title": "Document build artifacts",
            "description": "Identify and document the build artifacts and their purposes.",
            "dependencies": ["Build project"],
            "effort": "S",
            "category": "Directory Structure"
        },
        
        # Core Module Identification
        {
            "title": "Identify core modules",
            "description": "Identify and list all core modules in the Serena codebase.",
            "dependencies": ["Analyze source directory"],
            "effort": "M",
            "category": "Core Module Identification"
        },
        {
            "title": "Map module responsibilities",
            "description": "Document the primary responsibility of each core module.",
            "dependencies": ["Identify core modules"],
            "effort": "M",
            "category": "Core Module Identification"
        },
        {
            "title": "Trace control flow",
            "description": "Trace the control flow through the main execution paths.",
            "dependencies": ["Map module responsibilities"],
            "effort": "L",
            "category": "Core Module Identification"
        },
        {
            "title": "Document data structures",
            "description": "Identify and document key data structures and their relationships.",
            "dependencies": ["Identify core modules"],
            "effort": "M",
            "category": "Core Module Identification"
        },
        
        # Dependency Analysis
        {
            "title": "Analyze external dependencies",
            "description": "List and categorize all external dependencies.",
            "dependencies": ["Install dependencies"],
            "effort": "M",
            "category": "Dependency Analysis"
        },
        {
            "title": "Map internal dependencies",
            "description": "Document dependencies between internal modules.",
            "dependencies": ["Identify core modules"],
            "effort": "M",
            "category": "Dependency Analysis"
        },
        {
            "title": "Identify critical dependencies",
            "description": "Determine which dependencies are critical for core functionality.",
            "dependencies": ["Analyze external dependencies", "Map internal dependencies"],
            "effort": "S",
            "category": "Dependency Analysis"
        },
        {
            "title": "Check for dependency vulnerabilities",
            "description": "Scan for known vulnerabilities in dependencies.",
            "dependencies": ["Analyze external dependencies"],
            "effort": "M",
            "category": "Dependency Analysis"
        },
        
        # Feature Walkthrough
        {
            "title": "Identify key features",
            "description": "List all major features of the Serena codebase.",
            "dependencies": ["Read documentation", "Map module responsibilities"],
            "effort": "M",
            "category": "Feature Walkthrough"
        },
        {
            "title": "Trace feature implementations",
            "description": "Trace how each major feature is implemented across modules.",
            "dependencies": ["Identify key features", "Trace control flow"],
            "effort": "L",
            "category": "Feature Walkthrough"
        },
        {
            "title": "Create feature dependency map",
            "description": "Map dependencies between features and modules.",
            "dependencies": ["Trace feature implementations"],
            "effort": "M",
            "category": "Feature Walkthrough"
        },
        {
            "title": "Test each key feature",
            "description": "Manually test each key feature to understand its behavior.",
            "dependencies": ["Identify key features", "Build project"],
            "effort": "L",
            "category": "Feature Walkthrough"
        },
        
        # Test Suite & Coverage
        {
            "title": "Analyze test directory structure",
            "description": "Document the organization of the test directory.",
            "dependencies": ["Map top-level directories"],
            "effort": "S",
            "category": "Test Suite & Coverage"
        },
        {
            "title": "Run test coverage tools",
            "description": "Generate a test coverage report.",
            "dependencies": ["Run tests"],
            "effort": "S",
            "category": "Test Suite & Coverage"
        },
        {
            "title": "Identify untested components",
            "description": "List components with low or no test coverage.",
            "dependencies": ["Run test coverage tools", "Identify core modules"],
            "effort": "M",
            "category": "Test Suite & Coverage"
        },
        {
            "title": "Analyze test quality",
            "description": "Evaluate the quality and comprehensiveness of existing tests.",
            "dependencies": ["Analyze test directory structure", "Run tests"],
            "effort": "M",
            "category": "Test Suite & Coverage"
        },
        
        # API & CLI Interfaces
        {
            "title": "Document public APIs",
            "description": "Identify and document all public APIs.",
            "dependencies": ["Map module responsibilities"],
            "effort": "M",
            "category": "API & CLI Interfaces"
        },
        {
            "title": "Analyze API stability",
            "description": "Determine which APIs are stable vs. experimental.",
            "dependencies": ["Document public APIs"],
            "effort": "M",
            "category": "API & CLI Interfaces"
        },
        {
            "title": "Document CLI commands",
            "description": "List and describe all available CLI commands.",
            "dependencies": ["Build project"],
            "effort": "M",
            "category": "API & CLI Interfaces"
        },
        {
            "title": "Test API usability",
            "description": "Evaluate the usability and intuitiveness of the APIs.",
            "dependencies": ["Document public APIs"],
            "effort": "M",
            "category": "API & CLI Interfaces"
        },
        
        # Configuration & Extensibility
        {
            "title": "Identify configuration options",
            "description": "Document all available configuration options.",
            "dependencies": ["Read documentation", "Map module responsibilities"],
            "effort": "M",
            "category": "Configuration & Extensibility"
        },
        {
            "title": "Analyze extension points",
            "description": "Identify how the codebase can be extended by third parties.",
            "dependencies": ["Document public APIs", "Map module responsibilities"],
            "effort": "M",
            "category": "Configuration & Extensibility"
        },
        {
            "title": "Test configuration options",
            "description": "Experiment with different configuration settings.",
            "dependencies": ["Identify configuration options", "Build project"],
            "effort": "M",
            "category": "Configuration & Extensibility"
        },
        {
            "title": "Build a sample extension",
            "description": "Create a simple extension to test extensibility.",
            "dependencies": ["Analyze extension points"],
            "effort": "L",
            "category": "Configuration & Extensibility"
        },
        
        # Security & Compliance
        {
            "title": "Identify security features",
            "description": "Document all security-related features and protections.",
            "dependencies": ["Map module responsibilities", "Identify key features"],
            "effort": "M",
            "category": "Security & Compliance"
        },
        {
            "title": "Check for security vulnerabilities",
            "description": "Scan the codebase for potential security issues.",
            "dependencies": ["Analyze source directory"],
            "effort": "M",
            "category": "Security & Compliance"
        },
        {
            "title": "Review license compliance",
            "description": "Ensure all dependencies have compatible licenses.",
            "dependencies": ["Analyze external dependencies"],
            "effort": "M",
            "category": "Security & Compliance"
        },
        {
            "title": "Document compliance features",
            "description": "Identify features related to regulatory compliance.",
            "dependencies": ["Identify key features"],
            "effort": "M",
            "category": "Security & Compliance"
        },
        
        # Performance & Scaling
        {
            "title": "Identify performance bottlenecks",
            "description": "Locate potential performance bottlenecks in the code.",
            "dependencies": ["Trace control flow", "Test each key feature"],
            "effort": "M",
            "category": "Performance & Scaling"
        },
        {
            "title": "Run performance tests",
            "description": "Execute and document the results of performance tests.",
            "dependencies": ["Build project"],
            "effort": "M",
            "category": "Performance & Scaling"
        },
        {
            "title": "Analyze scaling capabilities",
            "description": "Determine how the codebase handles increased load.",
            "dependencies": ["Run performance tests"],
            "effort": "M",
            "category": "Performance & Scaling"
        },
        {
            "title": "Document resource requirements",
            "description": "Document CPU, memory, and storage requirements.",
            "dependencies": ["Run performance tests"],
            "effort": "S",
            "category": "Performance & Scaling"
        },
        
        # Roadmap & Issues Survey
        {
            "title": "Review open issues",
            "description": "Analyze the open issues in the repository.",
            "dependencies": ["Clone repository"],
            "effort": "M",
            "category": "Roadmap & Issues Survey"
        },
        {
            "title": "Review roadmap",
            "description": "Study the project roadmap if available.",
            "dependencies": ["Read documentation"],
            "effort": "S",
            "category": "Roadmap & Issues Survey"
        },
        {
            "title": "Identify enhancement opportunities",
            "description": "List potential enhancements based on analysis.",
            "dependencies": ["Trace feature implementations", "Identify untested components"],
            "effort": "M",
            "category": "Roadmap & Issues Survey"
        },
        {
            "title": "Document analysis results",
            "description": "Compile all findings into a comprehensive report.",
            "dependencies": ["Identify enhancement opportunities", "Document analysis results"],
            "effort": "L",
            "category": "Roadmap & Issues Survey"
        }
    ]
    
    return GenerateTasksResponse(tasks=tasks)


@router.get("/mcp-tool-use")
def get_serena_mcp_tool_use() -> MCPToolUseResponse:
    """
    Get information about MCP Tool Use with Smart Models.
    """
    content = {
        "title": "MCP Tool Use with Smart Models",
        "description": "Meta-Control Programming (MCP) enables self-monitoring, adaptation, and goal-setting within our smart-model architecture.",
        "capabilities": [
            {
                "name": "Self-Monitoring",
                "description": "Agents continuously track metrics (e.g., perplexity, F1-score, latency) during training and inference."
            },
            {
                "name": "Adaptation",
                "description": "On metric degradation, MCP triggers actions like data augmentation (back-translation, paraphrasing), hyperparameter tuning, or dynamic model swapping."
            },
            {
                "name": "Goal-Setting",
                "description": "Define objectives (e.g., `MinimizeResponseLatency`, `MaximizeSemanticCoherence`). MCP planners decompose goals into actionable tasks and schedules."
            }
        ],
        "benefits": [
            "Automates iterative improvements",
            "Proactively catches drift"
        ],
        "limitations": [
            "Potential local optima without global oversight",
            "Increased orchestration complexity"
        ]
    }
    return MCPToolUseResponse(content=content)


@router.get("/ai-coding-levels")
def get_ai_coding_levels() -> AICodingLevelsResponse:
    """
    Get information about AI Coding Levels Applied to NLS.
    """
    content = {
        "title": "AI Coding Levels Applied to NLS",
        "description": "Four progressively autonomous levels, with tool integrations and example 'program' workflows.",
        "levels": [
            {
                "level": 1,
                "name": "AI-Assisted Natural Language Development",
                "description": "AI assists engineers on discrete tasks—data prep, annotation, and code scaffolding.",
                "examples": [
                    "Data Augmentation: Use pre-trained models (GPT, BERT) to generate paraphrases or back-translations.",
                    "Text Annotation: Suggest labels in Label Studio / Prodigy based on model predictions.",
                    "Code Snippet Generation: LLM completion for regexes, tokenization scripts, or JSON schema validators.",
                    "Error Analysis: Static analysis (ESLint, MyPy) on NLP pipelines.",
                    "\"Program\" Workflow: 1. Engineer defines task (e.g., data cleaning). 2. AI suggests Python script using pandas. 3. Engineer reviews, modifies, executes. 4. AI flags potential errors based on output. 5. Engineer debugs with AI assistance."
                ]
            },
            {
                "level": 2,
                "name": "Multi-Agent Collaboration",
                "description": "Multiple specialized agents work together on more complex tasks, coordinated by an orchestration layer.",
                "examples": [
                    "Data Agent: Monitors data quality metrics, suggests cleaning operations.",
                    "Model Agent: Performs hyperparameter tuning, architecture selection.",
                    "Evaluation Agent: Generates test cases, identifies failure patterns.",
                    "Infrastructure Agent: Recommends compute resources, optimizes deployments."
                ]
            },
            {
                "level": 3,
                "name": "Meta-Control Programming",
                "description": "Agents define, monitor, and adjust their own behaviors based on high-level objectives.",
                "examples": [
                    "Self-monitoring metrics tracking",
                    "Adaptation through dynamic model swapping",
                    "Goal-setting with objectives like MinimizeResponseLatency",
                    "Automated iteration and improvement"
                ]
            },
            {
                "level": 4,
                "name": "Full Autonomous Development",
                "description": "End-to-end implementation of complex functionality with minimal human intervention.",
                "examples": [
                    "Automated requirements gathering and refinement",
                    "Complete system design and implementation",
                    "Self-testing and validation",
                    "Documentation generation and maintenance"
                ]
            }
        ]
    }
    return AICodingLevelsResponse(content=content)


@router.get("/agent-master-prompt")
def get_agent_master_prompt() -> AgentMasterPromptResponse:
    """
    Get information about the Agent Master Prompt.
    """
    content = {
        "title": "Agent Master Prompt",
        "description": "A master-level prompt for an autonomous NLS Architect Agent that can repeatedly generate, refine, and integrate every aspect of the project.",
        "system_prompt": "You are the NLS Architect Agent, an infinitely programmable, self-driving AI designed to implement the full Natural Language System (NLS) project. Your objective: autonomously plan, code, test, and deploy every module to completion, iterating until the entire system is production-ready.",
        "context": [
            "Visionary module specification, including all modules and their 'Key Challenges.'",
            "A detailed task roadmap: 50–80 atomic tasks with titles, descriptions, dependencies, and effort estimates.",
            "Access to tool suite: code generation, shell (bash), CI/CD APIs, IaC provisioning (Terraform/CloudFormation), formal verification (TLA+, PySMT), Notion/Label Studio APIs, Kubernetes/SageMaker, and evolutionary frameworks."
        ],
        "primary_goals": [
            "Scaffold repositories and CI pipelines.",
            "Implement MCP core modules (monitor, adaptor, planner) with metrics and adaptation.",
            "Build data & annotation tools (augmentation, assistant).",
            "Develop model & pipeline modules (selector, generator, orchestrator).",
            "Create evaluation suite and dialogue flow designer with formal safety checks.",
            "Integrate code snippet generator and static analysis linters.",
            "Generate and compile DSLs; build reusable pipeline templates.",
            "Embed formal verification and compliance checks.",
            "Implement evolutionary optimizer and decentralized agent manager.",
            "Provision self-managed infrastructure and monitoring.",
            "Validate with end-to-end integration tests, sample workflows, and documentation."
        ],
        "rules_behaviors": [
            "**Iterative Convergence:** Always loop: generate code → test → analyze failures → refine until tests pass.",
            "**Dependency Management:** Complete prerequisite tasks before dependents; spawn parallel sub-agents where dependencies allow.",
            "**Tool Calls:** Use `TOOL_CALL(tool_name, args)` syntax to invoke allowed tools; log each call.",
            "**State Persistence:** After each task, commit changes to version control and update a progress log.",
            "**Reporting:** Emit JSON progress after each task: {\"task_title\":\"...\", \"status\":\"done\", \"timestamp\":\"...\", \"outputs\":[\"...\"]}",
            "**Completion Criterion:** Halt when all tasks show `\"status\":\"done\"`, all CI checks pass, and final artifact URLs (repo, docs) are generated."
        ],
        "response_format": "Return a single JSON object with progress_log and final_artifact fields"
    }
    return AgentMasterPromptResponse(content=content)


@router.get("/complete")
def get_complete_serena_info() -> SerenaCompleteResponse:
    """
    Get all information related to Serena analysis in a single response.
    """
    tasks_response = generate_serena_tasks()
    mcp_content = get_serena_mcp_tool_use().content
    ai_levels_content = get_ai_coding_levels().content
    master_prompt_content = get_agent_master_prompt().content
    
    return SerenaCompleteResponse(
        tasks=tasks_response.tasks,
        mcp_tool_use=mcp_content,
        ai_coding_levels=ai_levels_content,
        agent_master_prompt=master_prompt_content
    )