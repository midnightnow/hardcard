from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import databutton as db
import os
import json
from app.libs.storage_utils import sanitize_storage_key

router = APIRouter()

# Claude.md content
CLAUDE_MD_CONTENT = """# Project Context for Claude Code

## Bash commands
- `npm run dev`  
  Starts the development server (e.g., Next.js).
- `npm run build`  
  Builds the application for production.
- `npm run typecheck`  
  Runs the TypeScript type checker.
- `npm test`  
  Executes automated tests.
- `git checkout <branch>`  
  Switches to an existing branch.
- `git checkout -b <branch>`  
  Creates and switches to a new branch.
- `git commit -m "message"`  
  Commits staged changes.
- `git push origin <branch>`  
  Pushes commits to the remote repository.
- `gh pr create --fill`  
  Creates a GitHub Pull Request.

## Code style
- Use ES modules (`import` / `export`), not CommonJS (`require`).
- Destructure imports when possible:
  ```ts
  import { foo } from 'bar';
  ```
- Follow configured ESLint & Prettier rules; run linters before committing.
- Prefer TypeScript for type safety.
- In React/Next.js, use functional components with Hooks.

## Workflow guidelines
1. **Feature Development**  
   - Create a feature branch (`feature/...`).  
   - Implement, write tests, ensure lint/type checks pass.  
   - Create a PR for review; merge upon approval.
2. **Test-Driven Development (TDD)**  
   - Write failing tests first.  
   - Write code to make tests pass.  
   - Refactor and commit tests & implementation clearly.
3. **Plan-then-Code**  
   - Ask Claude to `think` and draft a plan before coding.  
   - Review the plan before proceeding.
4. **Commits**  
   - Clear, concise commit messages using Conventional Commits (e.g., `feat:`, `fix:`, `chore:`).
5. **GitHub Issues**  
   - Use `/fix-github-issue <number>` to triage.  
   - Ensure the `gh` CLI is installed and authenticated.
"""

# .claude/settings.json content
CLAUDE_SETTINGS_CONTENT = {
  "tool_allowlist": [
    {
      "tool_name": "Edit",
      "allowed": True
    },
    {
      "tool_name": "Bash(git commit:*)",
      "allowed": True
    },
    {
      "tool_name": "gh",
      "allowed": True
    }
  ]
}

# .claude/commands/fix-github-issue.md content
FIX_GITHUB_ISSUE_CONTENT = """# fix-github-issue

Please analyze and fix GitHub issue: $ARGUMENTS

**Steps:**
1. `gh issue view $ARGUMENTS`
2. Investigate the described problem
3. Search the codebase for relevant files
4. Implement the necessary changes
5. Write & run tests to verify the fix
6. `git commit -m "fix: issue $ARGUMENTS"`
7. `gh pr create --fill`

*Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks.*
"""

# .claude/commands/tdd-workflow.md content
TDD_WORKFLOW_CONTENT = """Let's implement a feature using Test-Driven Development: $ARGUMENTS

Steps:
1. Think through the feature requirements and expected behavior
2. Write tests that define the expected behavior (they should fail initially)
3. Commit the tests: git commit -m "test: adding tests for $ARGUMENTS"
4. Implement the minimal code required to pass the tests
5. Run tests to verify implementation
6. Refactor if needed while keeping tests passing
7. Commit implementation: git commit -m "feat: implement $ARGUMENTS"
"""

# .claude/commands/visual-dev.md content
VISUAL_DEV_CONTENT = """Implement UI component based on visual design: $ARGUMENTS

Steps:
1. Analyze the design or mockup provided
2. Plan the component structure and styling approach
3. Implement the component following our styling conventions
4. Take a screenshot of the result
5. Compare with the original design and iterate until matching
6. Ensure component is responsive and accessible
7. Commit the implementation: git commit -m "feat: implement UI for $ARGUMENTS"
"""

# .claude/commands/codebase-explore.md content
CODEBASE_EXPLORE_CONTENT = """Help me understand this codebase aspect: $ARGUMENTS

Explore the following:
1. Relevant files and their purposes
2. Architecture patterns being used
3. Data flow between components
4. Key interfaces and abstractions
5. Common patterns and conventions
6. Potential areas for improvement

Provide a clear, concise explanation suitable for someone learning the codebase.
"""

# .claude/commands/code-review.md content
CODE_REVIEW_CONTENT = """Review this code implementation: $ARGUMENTS

Consider the following aspects:
1. Correctness - Does it work as intended?
2. Code quality - Is it readable, maintainable, and follows best practices?
3. Performance - Are there any obvious bottlenecks?
4. Security - Are there potential vulnerabilities?
5. Testing - Is the code adequately tested?
6. Suggestions for improvement

Provide constructive feedback and specific recommendations.
"""

# README.md content for the Getting Started section
README_GETTING_STARTED = """
## Getting Started with Claude Code

This project is configured for use with Claude Code, an AI coding assistant.

1. **Install the GitHub CLI**  
   Follow instructions at https://cli.github.com and run `gh auth login`.
2. **Install Claude Code**  
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
3. **Using the slash command**  
   In the Claude Code interface, run:  
   ```
   /fix-github-issue <issue_number>
   ```
4. **For help**  
   - Run `claude --help` in your terminal, or  
   - Inside Claude Code, use `/help`.

Consult **CLAUDE.md** for project-specific context, style guidelines, and workflows.
"""

from app.libs.storage_utils import sanitize_storage_key

class FileContent(BaseModel):
    path: str
    content: str

class FileRequest(BaseModel):
    path: str
    
class FileResponse(BaseModel):
    path: str
    content: str
    exists: bool

class InitResponse(BaseModel):
    success: bool
    message: str
    files_created: list[str]

@router.post("/initialize-claude-code")
def initialize_claude_code() -> InitResponse:
    """Initialize the repository with Claude Code best practices files."""
    
    files_to_create = [
        FileContent(path="CLAUDE.md", content=CLAUDE_MD_CONTENT),
        FileContent(path=".claude/settings.json", content=json.dumps(CLAUDE_SETTINGS_CONTENT, indent=2)),
        FileContent(path=".claude/commands/fix-github-issue.md", content=FIX_GITHUB_ISSUE_CONTENT),
        FileContent(path=".claude/commands/tdd-workflow.md", content=TDD_WORKFLOW_CONTENT),
        FileContent(path=".claude/commands/visual-dev.md", content=VISUAL_DEV_CONTENT),
        FileContent(path=".claude/commands/codebase-explore.md", content=CODEBASE_EXPLORE_CONTENT),
        FileContent(path=".claude/commands/code-review.md", content=CODE_REVIEW_CONTENT)
    ]
    
        # Check if README.md exists and update it, or create a new one
    try:
        readme_content = db.storage.text.get("README.md")
        if "## Getting Started with Claude Code" not in readme_content:
            if "## Getting Started" in readme_content:
                # Replace existing Getting Started section
                readme_content = readme_content.replace("## Getting Started", README_GETTING_STARTED)
            else:
                # Add new section
                readme_content += "\n\n" + README_GETTING_STARTED
            files_to_create.append(FileContent(path="README.md", content=readme_content))
    except Exception:
        # README.md doesn't exist, create a new one
        files_to_create.append(FileContent(path="README.md", content="# DevHelper\n\nA project for frontend AI agent development on the Databutton platform.\n\n" + README_GETTING_STARTED))
    
    # Save all files to storage
    created_files = []
    for file in files_to_create:
        try:
            # Sanitize the path for storage
            storage_key = sanitize_storage_key(file.path)
            db.storage.text.put(storage_key, file.content)
            created_files.append(file.path)
        except Exception as e:
            return InitResponse(
                success=False,
                message=f"Failed to create {file.path}: {str(e)}",
                files_created=created_files
            )
    
    return InitResponse(
        success=True,
        message="Successfully initialized Claude Code best practices files",
        files_created=created_files
    )

@router.post("/get-claude-code-file")
def get_claude_code_file(body: FileRequest) -> FileResponse:
    """Retrieve a Claude Code file from storage."""
    
    path = body.path
    storage_key = sanitize_storage_key(path)
    
    try:
        content = db.storage.text.get(storage_key)
        return FileResponse(
            path=path,
            content=content,
            exists=True
        )
    except Exception:
        return FileResponse(
            path=path,
            content=f"File {path} not found.",
            exists=False
        )
