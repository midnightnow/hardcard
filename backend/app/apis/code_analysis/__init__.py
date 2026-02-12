from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
import openai
import databutton as db
import re
import json
import time

# Create APIRouter
router = APIRouter(prefix="/code-analysis", tags=["code"])

# Set up OpenAI client
client = openai.OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))

# Request and response models
class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="The code snippet to analyze")
    language: str = Field(..., description="The programming language of the code")
    context: Optional[str] = Field(None, description="Additional context about the code")
    analysis_type: List[str] = Field(
        default=["best_practices", "bugs", "optimization"],
        description="Types of analysis to perform"
    )
    
class Suggestion(BaseModel):
    type: str = Field(..., description="Type of suggestion (best_practice, bug, optimization, security, accessibility)")
    line_numbers: Optional[List[int]] = Field(None, description="Line numbers related to the suggestion")
    severity: str = Field(..., description="Severity of the issue (info, warning, error)")
    title: str = Field(..., description="Short title describing the suggestion")
    description: str = Field(..., description="Detailed description of the suggestion")
    code_sample: Optional[str] = Field(None, description="Example code that addresses the suggestion")

class CodeAnalysisResponse(BaseModel):
    suggestions: List[Suggestion] = Field(..., description="List of code suggestions")
    summary: str = Field(..., description="Summary of the analysis")
    execution_time: float = Field(..., description="Time taken to analyze the code in seconds")

# Language-specific analysis helpers
def get_language_specific_prompt(language: str) -> str:
    """Return language-specific analysis guidance for the AI"""
    language_guides = {
        "javascript": """
        For JavaScript code, focus on:
        - ES6+ best practices and modern syntax
        - Common pitfalls like variable hoisting and scope issues
        - Performance issues such as inefficient DOM manipulation
        - Potential memory leaks, especially in closures and event handlers
        - Security concerns like XSS vulnerabilities and unsafe eval usage
        - React/Vue/Angular specific patterns if frameworks are detected
        """,
        
        "typescript": """
        For TypeScript code, focus on:
        - Proper type usage and avoiding 'any' type
        - Interface vs Type usage patterns
        - Effective use of generics and utility types
        - Strict null checking issues
        - ES6+ best practices and modern syntax
        - React/Vue/Angular specific patterns if frameworks are detected
        """,
        
        "python": """
        For Python code, focus on:
        - PEP 8 compliance and Pythonic coding style
        - Common anti-patterns and code smells
        - Performance issues like inefficient list operations
        - Potential bugs in exception handling
        - Type hints usage and correctness
        - Security issues like SQL injection, command injection, etc.
        """,
        
        "java": """
        For Java code, focus on:
        - Design patterns and code organization
        - Exception handling best practices
        - Concurrency and thread safety issues
        - Performance bottlenecks in collections and loops
        - Modern Java features (Java 8+) usage
        - Resource management and memory leaks
        """,
        
        "csharp": """
        For C# code, focus on:
        - .NET best practices and coding standards
        - LINQ optimizations and proper usage
        - Async/await patterns and common mistakes
        - Resource management with IDisposable
        - Modern C# features usage
        - Performance considerations in collections and LINQ
        """,

        "go": """
        For Go code, focus on:
        - Idiomatic Go patterns and practices
        - Error handling patterns
        - Goroutine and channel usage
        - Memory management and efficiency
        - Interface implementation and composition
        - Potential race conditions
        """,

        "rust": """
        For Rust code, focus on:
        - Ownership and borrowing patterns
        - Lifetime annotations and issues
        - Proper error handling with Result and Option
        - Safe vs unsafe code usage
        - Concurrency and thread safety
        - Performance optimizations
        """,

        "ruby": """
        For Ruby code, focus on:
        - Ruby idioms and best practices
        - Performance considerations
        - Ruby style guide compliance
        - Rails-specific patterns if detected
        - Potential security issues
        - Metaprogramming usage and pitfalls
        """,

        "php": """
        For PHP code, focus on:
        - Modern PHP best practices
        - Security vulnerabilities (SQL injection, XSS, CSRF)
        - Performance optimization
        - PSR standards compliance
        - Framework-specific patterns if detected
        - Type declarations and proper error handling
        """,

        "swift": """
        For Swift code, focus on:
        - Swift idioms and best practices
        - Memory management (ARC) issues
        - Proper use of optionals
        - Protocol-oriented programming
        - Performance considerations
        - SwiftUI patterns if detected
        """,

        "kotlin": """
        For Kotlin code, focus on:
        - Kotlin idioms and best practices
        - Null safety usage
        - Coroutines and concurrency patterns
        - Java interoperability issues
        - Android-specific concerns if detected
        - Functional programming features usage
        """,

        "css": """
        For CSS code, focus on:
        - Browser compatibility issues
        - Performance and rendering optimizations
        - Responsive design patterns
        - CSS organization and maintainability
        - Accessibility concerns
        - Modern CSS features usage
        """,

        "html": """
        For HTML code, focus on:
        - Semantic HTML usage
        - Accessibility (WCAG) compliance
        - SEO best practices
        - Proper nesting and structure
        - HTML5 feature usage
        - Common rendering issues
        """,
    }
    
    return language_guides.get(language.lower(), "Focus on standard code quality, bugs, and optimization opportunities.")

def get_analysis_type_prompt(analysis_types: List[str]) -> str:
    """Return guidance based on requested analysis types"""
    type_guides = {
        "best_practices": "Suggest improvements based on language-specific conventions, design patterns, and community standards.",
        "bugs": "Identify potential bugs, logical errors, edge cases, and runtime exceptions.",
        "optimization": "Point out performance bottlenecks, memory issues, and suggest optimizations.",
        "security": "Identify security vulnerabilities like injection attacks, authentication issues, and insecure data handling.",
        "accessibility": "Highlight accessibility issues and suggest improvements for inclusive user experiences.",
        "maintainability": "Suggest improvements for code organization, documentation, and long-term maintenance."
    }
    
    prompts = [type_guides.get(analysis_type.lower(), "") for analysis_type in analysis_types if analysis_type.lower() in type_guides]
    return "\n".join(prompts)

# Define models for batch and quick analysis
class BatchCodeAnalysisRequest(BaseModel):
    code_snippets: List[CodeAnalysisRequest] = Field(..., description="List of code snippets to analyze")
    max_suggestions_per_snippet: int = Field(5, description="Maximum number of suggestions per code snippet")

class BatchCodeAnalysisResponse(BaseModel):
    results: List[CodeAnalysisResponse] = Field(..., description="Analysis results for each code snippet")
    total_execution_time: float = Field(..., description="Total time taken for the batch analysis")

class QuickAnalysisResponse(BaseModel):
    summary: str = Field(..., description="Summary of code quality and issues")
    key_issues: List[str] = Field(..., description="List of key issues identified")
    score: int = Field(..., description="Overall code quality score (0-100)")
    execution_time: float = Field(..., description="Time taken for the analysis")

# Helper function to perform the actual code analysis
def _perform_code_analysis(code: str, language: str, analysis_types: List[str], context: Optional[str] = None, detailed: bool = True) -> dict:
    """Internal helper to perform code analysis and return raw results"""
    # Get language-specific guidance
    language_guide = get_language_specific_prompt(language)
    
    # Get analysis type guidance
    analysis_guide = get_analysis_type_prompt(analysis_types)
    
    # Extract line numbers for reference
    lines = code.split('\n')
    line_count = len(lines)
    
    # Define the system prompt based on whether we want detailed or quick analysis
    if detailed:
        system_prompt = f"""
        You are an expert code reviewer specialized in {language} programming. 
        Analyze the following code snippet and provide specific, actionable suggestions for improvements.
        
        {language_guide}
        
        {analysis_guide}
        
        For each suggestion, provide:
        1. The type of suggestion (best_practice, bug, optimization, security, accessibility)
        2. The line number(s) related to the suggestion (can be null if not applicable)
        3. Severity (info, warning, error)
        4. A concise title
        5. A detailed description that explains the issue and why it matters
        6. A code sample showing how to implement the suggestion
        
        Format your response in JSON with the following structure:
        {{
            "suggestions": [
                {{
                    "type": "best_practice|bug|optimization|security|accessibility",
                    "line_numbers": [1, 2],  # can be null if not applicable
                    "severity": "info|warning|error",
                    "title": "Short title",
                    "description": "Detailed description",
                    "code_sample": "Example code that addresses the suggestion" # can be null
                }}
            ],
            "summary": "Overall summary of the code and main issues"
        }}
        
        Be thorough but focus on meaningful improvements. If the code is already well-written,
        still provide at least 1-2 suggestions for improvement or acknowledge good practices.
        """
    else:
        # Quick analysis mode, simplified output
        system_prompt = f"""
        You are an expert code reviewer specialized in {language} programming. 
        Perform a quick analysis of the following code snippet.
        
        {language_guide}
        
        {analysis_guide}
        
        Format your response in JSON with the following structure:
        {{
            "summary": "Concise overall quality assessment in 1-2 sentences",
            "key_issues": ["Issue 1", "Issue 2", "Issue 3"],  # List of 3-5 main issues, ordered by importance
            "score": 85  # Overall code quality score from 0-100
        }}
        
        Be concise but insightful. The key_issues should be specific and actionable.
        """
    
    # Include context if provided
    user_prompt = f"""Code to analyze ({line_count} lines):
```{language}
{code}
```
"""
    
    if context:
        user_prompt += f"\nContext: {context}"
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using a suitable model for code analysis
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    # Extract JSON response
    result = response.choices[0].message.content
    return json.loads(result)

@router.post("/analyze", response_model=CodeAnalysisResponse)
def analyze_code(request: CodeAnalysisRequest) -> CodeAnalysisResponse:
    """
    Analyze code and provide suggestions for improvements.
    
    This endpoint takes a code snippet and returns formatted suggestions related to best practices,
    potential bugs, and optimization opportunities.
    """
    start_time = time.time()
    
    try:
        # Use helper function to perform analysis
        analysis_result = _perform_code_analysis(
            code=request.code,
            language=request.language,
            analysis_types=request.analysis_type,
            context=request.context,
            detailed=True
        )
        
        # Create suggestions from the response
        suggestions = []
        for suggestion in analysis_result.get("suggestions", []):
            suggestions.append(Suggestion(
                type=suggestion.get("type", "best_practice"),
                line_numbers=suggestion.get("line_numbers"),
                severity=suggestion.get("severity", "info"),
                title=suggestion.get("title", "Suggestion"),
                description=suggestion.get("description", ""),
                code_sample=suggestion.get("code_sample")
            ))
        
        execution_time = time.time() - start_time
        return CodeAnalysisResponse(
            suggestions=suggestions,
            summary=analysis_result.get("summary", "Code analysis complete"),
            execution_time=execution_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}") from e

@router.post("/analyze/quick", response_model=QuickAnalysisResponse)
def quick_analyze_code(request: CodeAnalysisRequest) -> QuickAnalysisResponse:
    """
    Perform a quick analysis of code with simplified results.
    
    This endpoint provides a faster analysis with an overall quality score,
    summary, and list of key issues, without detailed suggestions.
    """
    start_time = time.time()
    
    try:
        # Use helper function with detailed=False for quick analysis
        analysis_result = _perform_code_analysis(
            code=request.code,
            language=request.language,
            analysis_types=request.analysis_type,
            context=request.context,
            detailed=False
        )
        
        execution_time = time.time() - start_time
        return QuickAnalysisResponse(
            summary=analysis_result.get("summary", "Quick analysis complete"),
            key_issues=analysis_result.get("key_issues", []),
            score=analysis_result.get("score", 50),  # Default to middle score if not provided
            execution_time=execution_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}") from e

@router.post("/analyze/batch", response_model=BatchCodeAnalysisResponse)
def batch_analyze_code(request: BatchCodeAnalysisRequest) -> BatchCodeAnalysisResponse:
    """
    Analyze multiple code snippets in a single batch request.
    
    This endpoint processes multiple code snippets and returns results for each one.
    The number of suggestions per snippet can be limited for efficiency.
    """
    start_time = time.time()
    
    try:
        results = []
        
        for snippet_request in request.code_snippets:
            # Process each snippet individually
            snippet_start_time = time.time()
            
            try:
                # Use helper function to perform analysis
                analysis_result = _perform_code_analysis(
                    code=snippet_request.code,
                    language=snippet_request.language,
                    analysis_types=snippet_request.analysis_type,
                    context=snippet_request.context,
                    detailed=True
                )
                
                # Create suggestions from the response, limiting to max_suggestions_per_snippet
                suggestions = []
                for suggestion in analysis_result.get("suggestions", [])[:request.max_suggestions_per_snippet]:
                    suggestions.append(Suggestion(
                        type=suggestion.get("type", "best_practice"),
                        line_numbers=suggestion.get("line_numbers"),
                        severity=suggestion.get("severity", "info"),
                        title=suggestion.get("title", "Suggestion"),
                        description=suggestion.get("description", ""),
                        code_sample=suggestion.get("code_sample")
                    ))
                
                snippet_execution_time = time.time() - snippet_start_time
                results.append(CodeAnalysisResponse(
                    suggestions=suggestions,
                    summary=analysis_result.get("summary", "Code analysis complete"),
                    execution_time=snippet_execution_time
                ))
                
            except Exception as snippet_error:
                # If one snippet fails, include an error message but continue processing others
                results.append(CodeAnalysisResponse(
                    suggestions=[],
                    summary=f"Error analyzing snippet: {str(snippet_error)}",
                    execution_time=time.time() - snippet_start_time
                ))
        
        total_execution_time = time.time() - start_time
        return BatchCodeAnalysisResponse(
            results=results,
            total_execution_time=total_execution_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch analysis: {str(e)}") from e

