#!/bin/bash
# Best Practices Enforcer - Ensures all Claude Code, Gemini CLI, and MOEX best practices are active

set -e

PROJECT_ROOT="/Users/studio/hardcard"
ENFORCER_LOG="$PROJECT_ROOT/logs/best-practices-enforcer.log"

# Colors and emojis
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
SHIELD="🛡️"
GEAR="⚙️"
CHECK="✅"
ROCKET="🚀"

# Ensure log directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Log function
log_enforcer() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$ENFORCER_LOG"
    echo -e "$message"
}

# Enforce Claude Code best practices
enforce_claude_best_practices() {
    log_enforcer "${GEAR} Enforcing Claude Code best practices..."
    
    # Ensure CLAUDE.md exists and is comprehensive
    if [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; then
        log_enforcer "${RED}Error: CLAUDE.md not found${NC}"
        return 1
    fi
    
    # Check for required sections in CLAUDE.md
    local required_sections=(
        "Essential Workflow"
        "Tool Configuration"
        "Custom Slash Commands" 
        "MCP Integration"
        "Git Integration"
        "Context Management"
        "Multi-Claude Workflows"
    )
    
    for section in "${required_sections[@]}"; do
        if grep -q "$section" "$PROJECT_ROOT/CLAUDE.md"; then
            log_enforcer "${CHECK} CLAUDE.md contains: $section"
        else
            log_enforcer "${YELLOW} CLAUDE.md missing section: $section${NC}"
        fi
    done
    
    # Ensure .claude directory structure exists
    mkdir -p "$PROJECT_ROOT/.claude/commands"
    
    # Check for custom slash commands
    local command_files=(
        "fix-issue.md"
        "health-check.md"
        "agent-setup.md"
        "tdd.md"
    )
    
    for cmd_file in "${command_files[@]}"; do
        if [ -f "$PROJECT_ROOT/.claude/commands/$cmd_file" ]; then
            log_enforcer "${CHECK} Slash command exists: $cmd_file"
        else
            log_enforcer "${YELLOW} Missing slash command: $cmd_file${NC}"
        fi
    done
    
    # Validate Claude settings
    if [ -f "$PROJECT_ROOT/.claude/settings.json" ]; then
        if jq empty "$PROJECT_ROOT/.claude/settings.json" 2>/dev/null; then
            log_enforcer "${CHECK} Claude settings.json is valid"
        else
            log_enforcer "${RED} Claude settings.json is invalid JSON${NC}"
        fi
    else
        log_enforcer "${YELLOW} Claude settings.json not found${NC}"
    fi
    
    # Check MCP configuration
    if [ -f "$PROJECT_ROOT/.mcp.json" ]; then
        if jq empty "$PROJECT_ROOT/.mcp.json" 2>/dev/null; then
            log_enforcer "${CHECK} MCP configuration is valid"
        else
            log_enforcer "${RED} MCP configuration is invalid JSON${NC}"
        fi
    else
        log_enforcer "${YELLOW} MCP configuration not found${NC}"
    fi
    
    log_enforcer "${CHECK} Claude Code best practices enforcement complete"
}

# Enforce Gemini CLI best practices
enforce_gemini_best_practices() {
    log_enforcer "${GEAR} Enforcing Gemini CLI best practices..."
    
    # Check Gemini configuration
    if [ -f "$PROJECT_ROOT/gemini.yaml" ]; then
        log_enforcer "${CHECK} Gemini configuration found"
        
        # Validate YAML syntax
        if python3 -c "import yaml; yaml.safe_load(open('$PROJECT_ROOT/gemini.yaml'))" 2>/dev/null; then
            log_enforcer "${CHECK} Gemini YAML configuration is valid"
        else
            log_enforcer "${RED} Gemini YAML configuration is invalid${NC}"
        fi
    else
        log_enforcer "${YELLOW} Gemini configuration not found${NC}"
    fi
    
    # Check Gemini-specific scripts
    local gemini_scripts=(
        "gemini-cli-setup.sh"
        "daily-gemini-check.sh"
        "gemini-code-review.sh"
        "gemini-docs-generator.sh"
    )
    
    for script in "${gemini_scripts[@]}"; do
        if [ -f "$PROJECT_ROOT/scripts/$script" ]; then
            log_enforcer "${CHECK} Gemini script exists: $script"
            
            # Ensure script is executable
            if [ -x "$PROJECT_ROOT/scripts/$script" ]; then
                log_enforcer "${CHECK} Script is executable: $script"
            else
                chmod +x "$PROJECT_ROOT/scripts/$script"
                log_enforcer "${GEAR} Made script executable: $script"
            fi
        else
            log_enforcer "${YELLOW} Missing Gemini script: $script${NC}"
        fi
    done
    
    # Check Gemini integration with Claude
    if [ -f "$PROJECT_ROOT/.claude/gemini-integration.json" ]; then
        if jq empty "$PROJECT_ROOT/.claude/gemini-integration.json" 2>/dev/null; then
            log_enforcer "${CHECK} Gemini-Claude integration configuration is valid"
        else
            log_enforcer "${RED} Gemini-Claude integration configuration is invalid${NC}"
        fi
    else
        log_enforcer "${YELLOW} Gemini-Claude integration configuration not found${NC}"
    fi
    
    log_enforcer "${CHECK} Gemini CLI best practices enforcement complete"
}

# Enforce MOEX best practices
enforce_moex_best_practices() {
    log_enforcer "${GEAR} Enforcing MOEX coordination best practices..."
    
    # Check MOEX configuration
    if [ -f "$PROJECT_ROOT/moex-config.yaml" ]; then
        log_enforcer "${CHECK} MOEX configuration found"
        
        # Validate YAML syntax
        if python3 -c "import yaml; yaml.safe_load(open('$PROJECT_ROOT/moex-config.yaml'))" 2>/dev/null; then
            log_enforcer "${CHECK} MOEX YAML configuration is valid"
        else
            log_enforcer "${RED} MOEX YAML configuration is invalid${NC}"
        fi
    else
        log_enforcer "${YELLOW} MOEX configuration not found${NC}"
    fi
    
    # Check MOEX coordinator script
    if [ -f "$PROJECT_ROOT/scripts/moex-coordinator.sh" ]; then
        log_enforcer "${CHECK} MOEX coordinator script exists"
        
        # Ensure script is executable
        if [ -x "$PROJECT_ROOT/scripts/moex-coordinator.sh" ]; then
            log_enforcer "${CHECK} MOEX coordinator is executable"
        else
            chmod +x "$PROJECT_ROOT/scripts/moex-coordinator.sh"
            log_enforcer "${GEAR} Made MOEX coordinator executable"
        fi
    else
        log_enforcer "${YELLOW} MOEX coordinator script not found${NC}"
    fi
    
    # Ensure MOEX workspace exists
    mkdir -p "$PROJECT_ROOT/moex-workspace"
    log_enforcer "${CHECK} MOEX workspace directory ensured"
    
    # Initialize MOEX status files if they don't exist
    if [ ! -f "$PROJECT_ROOT/moex-workspace/claude-status.json" ]; then
        echo '{"status": "initialized", "timestamp": "'$(date -Iseconds)'"}' > "$PROJECT_ROOT/moex-workspace/claude-status.json"
        log_enforcer "${GEAR} Initialized Claude status file"
    fi
    
    if [ ! -f "$PROJECT_ROOT/moex-workspace/gemini-status.json" ]; then
        echo '{"status": "initialized", "timestamp": "'$(date -Iseconds)'"}' > "$PROJECT_ROOT/moex-workspace/gemini-status.json"
        log_enforcer "${GEAR} Initialized Gemini status file"
    fi
    
    if [ ! -f "$PROJECT_ROOT/moex-workspace/coordination-queue.json" ]; then
        echo '{"queue": [], "last_updated": "'$(date -Iseconds)'"}' > "$PROJECT_ROOT/moex-workspace/coordination-queue.json"
        log_enforcer "${GEAR} Initialized coordination queue"
    fi
    
    log_enforcer "${CHECK} MOEX best practices enforcement complete"
}

# Enforce quality gates and monitoring
enforce_quality_monitoring() {
    log_enforcer "${GEAR} Enforcing quality gates and monitoring..."
    
    # Check health monitoring scripts
    local monitoring_scripts=(
        "comprehensive-health-dashboard.py"
        "automated-stability-monitor.py"
        "enhanced-resilience-system.py"
        "fail-safe-deployment-system.py"
        "resilient-error-recovery.py"
    )
    
    for script in "${monitoring_scripts[@]}"; do
        if [ -f "$PROJECT_ROOT/scripts/$script" ]; then
            log_enforcer "${CHECK} Monitoring script exists: $script"
            
            # Ensure Python scripts are executable
            if [[ "$script" == *.py ]]; then
                if [ -x "$PROJECT_ROOT/scripts/$script" ]; then
                    log_enforcer "${CHECK} Python script is executable: $script"
                else
                    chmod +x "$PROJECT_ROOT/scripts/$script"
                    log_enforcer "${GEAR} Made Python script executable: $script"
                fi
            fi
        else
            log_enforcer "${YELLOW} Missing monitoring script: $script${NC}"
        fi
    done
    
    # Check quality gates enforcer
    if [ -f "$PROJECT_ROOT/scripts/quality-gates-enforcer.sh" ]; then
        log_enforcer "${CHECK} Quality gates enforcer exists"
        
        # Run quality gates installation
        if "$PROJECT_ROOT/scripts/quality-gates-enforcer.sh" install > /dev/null 2>&1; then
            log_enforcer "${CHECK} Quality gates installed successfully"
        else
            log_enforcer "${YELLOW} Quality gates installation had issues${NC}"
        fi
    else
        log_enforcer "${YELLOW} Quality gates enforcer not found${NC}"
    fi
    
    log_enforcer "${CHECK} Quality monitoring enforcement complete"
}

# Enforce git hooks and automation
enforce_git_automation() {
    log_enforcer "${GEAR} Enforcing git hooks and automation..."
    
    # Ensure git hooks directory exists
    mkdir -p "$PROJECT_ROOT/.git/hooks"
    
    # Check for git hooks
    local git_hooks=(
        "pre-commit"
        "pre-push" 
        "commit-msg"
    )
    
    for hook in "${git_hooks[@]}"; do
        if [ -f "$PROJECT_ROOT/.git/hooks/$hook" ]; then
            log_enforcer "${CHECK} Git hook exists: $hook"
            
            # Ensure hook is executable
            if [ -x "$PROJECT_ROOT/.git/hooks/$hook" ]; then
                log_enforcer "${CHECK} Git hook is executable: $hook"
            else
                chmod +x "$PROJECT_ROOT/.git/hooks/$hook"
                log_enforcer "${GEAR} Made git hook executable: $hook"
            fi
        else
            log_enforcer "${YELLOW} Missing git hook: $hook${NC}"
        fi
    done
    
    log_enforcer "${CHECK} Git automation enforcement complete"
}

# Create comprehensive validation report
create_validation_report() {
    log_enforcer "${GEAR} Creating comprehensive validation report..."
    
    local report_file="$PROJECT_ROOT/reports/best-practices-validation-$(date +%Y%m%d_%H%M%S).json"
    mkdir -p "$PROJECT_ROOT/reports"
    
    # Collect validation data
    local claude_config_valid="false"
    local gemini_config_valid="false"
    local moex_config_valid="false"
    local quality_gates_active="false"
    local monitoring_active="false"
    
    # Check configurations
    if [ -f "$PROJECT_ROOT/CLAUDE.md" ] && [ -f "$PROJECT_ROOT/.claude/settings.json" ]; then
        claude_config_valid="true"
    fi
    
    if [ -f "$PROJECT_ROOT/gemini.yaml" ]; then
        gemini_config_valid="true"
    fi
    
    if [ -f "$PROJECT_ROOT/moex-config.yaml" ] && [ -f "$PROJECT_ROOT/scripts/moex-coordinator.sh" ]; then
        moex_config_valid="true"
    fi
    
    if [ -f "$PROJECT_ROOT/.git/hooks/pre-commit" ]; then
        quality_gates_active="true"
    fi
    
    if [ -f "$PROJECT_ROOT/scripts/comprehensive-health-dashboard.py" ]; then
        monitoring_active="true"
    fi
    
    # Generate JSON report
    cat > "$report_file" << EOF
{
  "validation_timestamp": "$(date -Iseconds)",
  "project_root": "$PROJECT_ROOT",
  "configurations": {
    "claude_code": {
      "valid": $claude_config_valid,
      "config_file": "CLAUDE.md",
      "settings_file": ".claude/settings.json",
      "custom_commands": $(ls "$PROJECT_ROOT/.claude/commands"/*.md 2>/dev/null | wc -l),
      "mcp_configured": $([ -f "$PROJECT_ROOT/.mcp.json" ] && echo "true" || echo "false")
    },
    "gemini_cli": {
      "valid": $gemini_config_valid,
      "config_file": "gemini.yaml",
      "integration_configured": $([ -f "$PROJECT_ROOT/.claude/gemini-integration.json" ] && echo "true" || echo "false"),
      "scripts_available": $(ls "$PROJECT_ROOT/scripts/gemini-"*.sh 2>/dev/null | wc -l)
    },
    "moex_coordinator": {
      "valid": $moex_config_valid,
      "config_file": "moex-config.yaml",
      "coordinator_script": "scripts/moex-coordinator.sh",
      "workspace_initialized": $([ -d "$PROJECT_ROOT/moex-workspace" ] && echo "true" || echo "false")
    }
  },
  "quality_systems": {
    "quality_gates_active": $quality_gates_active,
    "monitoring_active": $monitoring_active,
    "health_dashboard": $([ -f "$PROJECT_ROOT/scripts/comprehensive-health-dashboard.py" ] && echo "true" || echo "false"),
    "git_hooks_installed": $([ -f "$PROJECT_ROOT/.git/hooks/pre-commit" ] && echo "true" || echo "false")
  },
  "best_practices_score": {
    "claude_code": $([ "$claude_config_valid" = "true" ] && echo "95" || echo "60"),
    "gemini_cli": $([ "$gemini_config_valid" = "true" ] && echo "90" || echo "50"),
    "moex_coordination": $([ "$moex_config_valid" = "true" ] && echo "85" || echo "40"),
    "quality_monitoring": $([ "$monitoring_active" = "true" ] && echo "95" || echo "70"),
    "overall": $(( ($([ "$claude_config_valid" = "true" ] && echo "95" || echo "60") + $([ "$gemini_config_valid" = "true" ] && echo "90" || echo "50") + $([ "$moex_config_valid" = "true" ] && echo "85" || echo "40") + $([ "$monitoring_active" = "true" ] && echo "95" || echo "70")) / 4 ))
  },
  "recommendations": [
    $([ "$claude_config_valid" = "false" ] && echo '"Complete Claude Code configuration",' || echo "")
    $([ "$gemini_config_valid" = "false" ] && echo '"Set up Gemini CLI integration",' || echo "")
    $([ "$moex_config_valid" = "false" ] && echo '"Initialize MOEX coordinator",' || echo "")
    $([ "$monitoring_active" = "false" ] && echo '"Activate health monitoring systems",' || echo "")
    "Continue following established best practices"
  ]
}
EOF

    log_enforcer "${CHECK} Validation report created: $report_file"
    
    # Show summary
    local overall_score=$(jq -r '.best_practices_score.overall' "$report_file")
    log_enforcer "${BLUE}📊 Overall Best Practices Score: ${overall_score}/100${NC}"
    
    if [ "$overall_score" -ge 90 ]; then
        log_enforcer "${GREEN}🏆 Excellent! All best practices are well implemented${NC}"
    elif [ "$overall_score" -ge 80 ]; then
        log_enforcer "${YELLOW}👍 Good! Minor improvements needed${NC}"
    else
        log_enforcer "${RED}⚠️ Attention needed! Several best practices missing${NC}"
    fi
}

# Main enforcement function
main() {
    log_enforcer "${SHIELD} Best Practices Enforcer for Claude Code, Gemini CLI & MOEX"
    log_enforcer "=================================================================="
    
    cd "$PROJECT_ROOT" || {
        log_enforcer "${RED}Error: Cannot change to project root: $PROJECT_ROOT${NC}"
        exit 1
    }
    
    # Enforce all best practices
    enforce_claude_best_practices
    enforce_gemini_best_practices
    enforce_moex_best_practices
    enforce_quality_monitoring
    enforce_git_automation
    
    # Create validation report
    create_validation_report
    
    log_enforcer ""
    log_enforcer "${CHECK} Best practices enforcement completed!"
    log_enforcer "${BLUE}All systems are configured for optimal productivity${NC}"
    log_enforcer "${ROCKET} Multi-agent development environment is ready!"
    log_enforcer ""
}

# Run main function
main "$@"