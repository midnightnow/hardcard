#!/bin/bash

# 🤖 Kimi Workspace Setup Script
# Establishes Kimi as primary coding agent with Claude Code coordination

echo "🤖 Setting up Kimi-First Development Environment..."
echo "=================================================="

# Create Kimi workspace directories
KIMI_WORKSPACE="/Users/studio/kimi-workspace"
CLAUDE_COORDINATION="/Users/studio/claude-coordination"

echo "📁 Creating workspace directories..."
mkdir -p "$KIMI_WORKSPACE"/{tasks,projects,communication,tools,logs}
mkdir -p "$CLAUDE_COORDINATION"/{reviews,integrations,architecture,deployments}

# Set up Kimi configuration
cat > "$KIMI_WORKSPACE/kimi-config.json" << 'EOF'
{
  "agent_role": "primary_coder",
  "coordinator": "claude_code",
  "responsibilities": [
    "feature_implementation",
    "bug_fixes",
    "api_development", 
    "frontend_development",
    "testing",
    "documentation",
    "performance_optimization"
  ],
  "escalation_triggers": [
    "complex_architecture_decisions",
    "system_integration_issues",
    "deployment_coordination",
    "security_implementations"
  ],
  "quality_gates": {
    "test_coverage": 90,
    "code_quality": "eslint_zero_errors",
    "performance": "no_regression",
    "documentation": "complete"
  },
  "communication_protocol": {
    "progress_updates": "every_2_hours",
    "blocker_reporting": "immediate",
    "completion_notification": "automatic"
  }
}
EOF

# Set up Claude Code coordination configuration
cat > "$CLAUDE_COORDINATION/claude-coordination-config.json" << 'EOF'
{
  "role": "orchestrator_specialist",
  "primary_agent": "kimi",
  "responsibilities": [
    "project_planning",
    "architecture_decisions",
    "task_coordination", 
    "quality_assurance",
    "integration_management",
    "deployment_coordination",
    "specialized_debugging"
  ],
  "review_criteria": {
    "architecture_compliance": true,
    "integration_readiness": true,
    "security_validation": true,
    "performance_standards": true
  },
  "escalation_handling": {
    "complex_bugs": "immediate_intervention",
    "architecture_conflicts": "design_review_session",
    "integration_failures": "coordination_meeting"
  }
}
EOF

# Create Kimi task templates
echo "📋 Creating task templates..."

cat > "$KIMI_WORKSPACE/templates/feature-task-template.md" << 'EOF'
# Feature Implementation Task

## Task Information
- **Task ID**: TASK_{{TIMESTAMP}}
- **Assigned Agent**: Kimi
- **Coordinator**: Claude Code
- **Priority**: {{PRIORITY}}
- **Estimated Hours**: {{HOURS}}

## Description
{{DESCRIPTION}}

## Acceptance Criteria
- [ ] Code follows project standards
- [ ] All tests pass with >90% coverage  
- [ ] Documentation complete
- [ ] Performance benchmarks met
- [ ] Security review passed

## Implementation Plan
1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}

## Dependencies
{{DEPENDENCIES}}

## Communication
- Progress updates every 2 hours
- Report blockers immediately
- Notify Claude Code when ready for review
EOF

cat > "$KIMI_WORKSPACE/templates/api-task-template.md" << 'EOF'
# API Development Task

## Task Information
- **Task ID**: TASK_{{TIMESTAMP}}
- **Type**: API Development
- **Assigned Agent**: Kimi
- **Coordinator**: Claude Code

## API Specification
- **Endpoint**: {{ENDPOINT}}
- **Method**: {{METHOD}}
- **Purpose**: {{PURPOSE}}

## Implementation Requirements
- [ ] Pydantic models for validation
- [ ] Comprehensive error handling
- [ ] Input validation and sanitization
- [ ] Rate limiting implementation
- [ ] API documentation (OpenAPI)
- [ ] Unit and integration tests

## Quality Gates
- [ ] OpenAPI documentation generated
- [ ] All edge cases tested
- [ ] Performance within SLA (<200ms)
- [ ] Security validation passed
EOF

# Create communication scripts
echo "📞 Setting up communication protocols..."

cat > "$KIMI_WORKSPACE/tools/kimi-status-update.py" << 'EOF'
#!/usr/bin/env python3
"""
Kimi Status Update Tool
Report progress to Claude Code coordination system
"""

import json
import datetime
import sys
from pathlib import Path

def update_status(task_id, progress, notes=""):
    """Update task status for Claude Code coordination"""
    
    status_update = {
        "timestamp": datetime.datetime.now().isoformat(),
        "task_id": task_id,
        "agent": "kimi",
        "progress": progress,
        "notes": notes,
        "status": "in_progress" if progress < 100 else "complete"
    }
    
    # Save to coordination directory
    coord_dir = Path("/Users/studio/claude-coordination/updates")
    coord_dir.mkdir(exist_ok=True)
    
    update_file = coord_dir / f"kimi_update_{task_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(update_file, 'w') as f:
        json.dump(status_update, f, indent=2)
    
    print(f"✅ Status updated: {progress}% - {notes}")
    print(f"📝 Update logged: {update_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python kimi-status-update.py <task_id> <progress> [notes]")
        sys.exit(1)
    
    task_id = sys.argv[1]
    progress = int(sys.argv[2])
    notes = sys.argv[3] if len(sys.argv) > 3 else ""
    
    update_status(task_id, progress, notes)
EOF

cat > "$KIMI_WORKSPACE/tools/kimi-blocker-report.py" << 'EOF'
#!/usr/bin/env python3
"""
Kimi Blocker Reporting Tool
Escalate blockers to Claude Code for resolution
"""

import json
import datetime
import sys
from pathlib import Path

def report_blocker(task_id, blocker_type, description):
    """Report blocker that requires Claude Code intervention"""
    
    blocker_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "task_id": task_id,
        "agent": "kimi",
        "blocker_type": blocker_type,
        "description": description,
        "urgency": "high",
        "requires_claude_intervention": True
    }
    
    # Save to escalation directory
    escalation_dir = Path("/Users/studio/claude-coordination/escalations")
    escalation_dir.mkdir(exist_ok=True)
    
    blocker_file = escalation_dir / f"kimi_blocker_{task_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(blocker_file, 'w') as f:
        json.dump(blocker_report, f, indent=2)
    
    print(f"🚨 BLOCKER REPORTED: {blocker_type}")
    print(f"📋 Description: {description}")
    print(f"🔗 Escalation file: {blocker_file}")
    print(f"⏰ Claude Code intervention requested")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python kimi-blocker-report.py <task_id> <blocker_type> <description>")
        print("Blocker types: architecture, integration, dependency, technical, specification")
        sys.exit(1)
    
    task_id = sys.argv[1]
    blocker_type = sys.argv[2]
    description = sys.argv[3]
    
    report_blocker(task_id, blocker_type, description)
EOF

# Make scripts executable
chmod +x "$KIMI_WORKSPACE/tools/"*.py
chmod +x "$CLAUDE_COORDINATION/"*.py 2>/dev/null || true

# Create development environment aliases
echo "⚙️ Setting up development aliases..."

cat > "$KIMI_WORKSPACE/kimi-aliases.sh" << 'EOF'
#!/bin/bash
# Kimi Development Aliases

# Navigation
alias kimi-workspace="cd /Users/studio/kimi-workspace"
alias claude-coord="cd /Users/studio/claude-coordination"

# Task management
alias kimi-status='python /Users/studio/kimi-workspace/tools/kimi-status-update.py'
alias kimi-blocker='python /Users/studio/kimi-workspace/tools/kimi-blocker-report.py'
alias kimi-tasks='ls /Users/studio/kimi-workspace/tasks/'

# Development workflow
alias kimi-test='npm test && python -m pytest'
alias kimi-lint='eslint . && pylint **/*.py'
alias kimi-format='prettier --write . && black **/*.py'

# Communication
alias kimi-log='tail -f /Users/studio/kimi-workspace/logs/kimi.log'
alias claude-updates='ls /Users/studio/claude-coordination/updates/'

echo "🤖 Kimi development environment loaded!"
echo "Available commands:"
echo "  kimi-status <task_id> <progress> [notes]"
echo "  kimi-blocker <task_id> <type> <description>"
echo "  kimi-test, kimi-lint, kimi-format"
EOF

# Set up project-specific configurations
echo "🎯 Configuring project-specific settings..."

# MUSE project configuration
mkdir -p "$KIMI_WORKSPACE/projects/muse"
cat > "$KIMI_WORKSPACE/projects/muse/kimi-muse-config.json" << 'EOF'
{
  "project": "muse_validation_system",
  "primary_technologies": ["python", "fastapi", "react", "typescript"],
  "kimi_focus_areas": [
    "validation_algorithm_optimization",
    "dashboard_component_development", 
    "api_performance_enhancement",
    "test_coverage_improvement"
  ],
  "claude_coordination_areas": [
    "system_architecture_review",
    "complex_statistical_integration",
    "deployment_orchestration"
  ],
  "quality_standards": {
    "test_coverage": 95,
    "api_response_time": "< 100ms",
    "ui_load_time": "< 1s"
  }
}
EOF

# VetSorcery project configuration  
mkdir -p "$KIMI_WORKSPACE/projects/vetsorcery"
cat > "$KIMI_WORKSPACE/projects/vetsorcery/kimi-vetsorcery-config.json" << 'EOF'
{
  "project": "vetsorcery_management_system",
  "primary_technologies": ["react", "typescript", "fastapi", "postgresql"],
  "kimi_focus_areas": [
    "inventory_system_enhancement",
    "patient_management_development",
    "api_optimization",
    "frontend_component_development"
  ],
  "claude_coordination_areas": [
    "medical_compliance_validation",
    "security_implementation",
    "integration_coordination"
  ],
  "compliance_requirements": {
    "hipaa": true,
    "data_encryption": true,
    "audit_logging": true
  }
}
EOF

# Initialize coordination system
echo "🔄 Initializing coordination system..."
python3 "/Users/studio/hardcard/scripts/kimi-claude-coordinator.py" > "$KIMI_WORKSPACE/logs/coordinator-init.log" 2>&1 &

# Create startup script
cat > "$KIMI_WORKSPACE/start-kimi-session.sh" << 'EOF'
#!/bin/bash
echo "🤖 Starting Kimi Development Session..."

# Load aliases
source /Users/studio/kimi-workspace/kimi-aliases.sh

# Start coordination system
python3 /Users/studio/hardcard/scripts/kimi-claude-coordinator.py &

# Show current tasks
echo "📋 Current Kimi Tasks:"
python3 -c "
import sys
sys.path.append('/Users/studio/hardcard/scripts')
from kimi_claude_coordinator import KimiClaudeCoordinator
coord = KimiClaudeCoordinator()
dashboard = coord.get_kimi_dashboard()
print(f'Active: {dashboard[\"active_tasks\"]}')
print(f'Completed: {dashboard[\"completed_tasks\"]}')
print(f'Blocked: {dashboard[\"blocked_tasks\"]}')
"

echo "✅ Kimi development environment ready!"
echo "🎯 Focus: Primary coding with Claude Code coordination"
EOF

chmod +x "$KIMI_WORKSPACE/start-kimi-session.sh"

# Create success summary
echo ""
echo "🎉 Kimi-First Development Framework Established!"
echo "=============================================="
echo ""
echo "📁 Workspaces Created:"
echo "  • Kimi: $KIMI_WORKSPACE"
echo "  • Claude Coordination: $CLAUDE_COORDINATION"
echo ""
echo "🔧 Tools Configured:"
echo "  • Task coordination system"
echo "  • Communication protocols"  
echo "  • Quality gates"
echo "  • Project-specific configs"
echo ""
echo "🚀 Next Steps:"
echo "  1. Source aliases: source $KIMI_WORKSPACE/kimi-aliases.sh"
echo "  2. Start session: $KIMI_WORKSPACE/start-kimi-session.sh"
echo "  3. Begin Kimi-first development!"
echo ""
echo "🤖 Kimi = Primary Coder | Claude Code = Orchestrator"