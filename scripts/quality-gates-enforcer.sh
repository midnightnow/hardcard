#!/bin/bash
# 🚦 Quality Gates Enforcer - Prevents deployment of incomplete/unsafe code
# Integrates with Git hooks and CI/CD to enforce quality standards

set -e

PROJECT_ROOT="/Users/studio/hardcard"
QUALITY_CONFIG="$PROJECT_ROOT/.github/quality-gates.json"
ENFORCEMENT_LOG="$PROJECT_ROOT/logs/quality-enforcement.log"
ENFORCEMENT_DIR="$PROJECT_ROOT/quality-enforcement"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Emojis
GATE="🚦"
SHIELD="🛡️"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/logs" "$ENFORCEMENT_DIR"

# Log with timestamp
log_enforcement() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$ENFORCEMENT_LOG"
    echo -e "$message"
}

# Load quality configuration
load_quality_config() {
    if [ ! -f "$QUALITY_CONFIG" ]; then
        log_enforcement "${WARNING} Quality gates config not found: $QUALITY_CONFIG"
        return 1
    fi
    
    # Extract key thresholds
    COMPLETION_THRESHOLD=$(jq -r '.quality_thresholds.code_coverage.minimum' "$QUALITY_CONFIG" 2>/dev/null || echo "70")
    MEDICAL_COMPLETION_THRESHOLD=$(jq -r '.quality_thresholds.code_coverage.medical_critical' "$QUALITY_CONFIG" 2>/dev/null || echo "100")
    SECURITY_THRESHOLD=$(jq -r '.security_requirements.dependency_audit.severity_threshold' "$QUALITY_CONFIG" 2>/dev/null || echo "moderate")
    
    log_enforcement "${GATE} Quality gates loaded: completion $COMPLETION_THRESHOLD%, medical $MEDICAL_COMPLETION_THRESHOLD%, security $SECURITY_THRESHOLD"
    return 0
}

# Check file completion before commit
check_file_completion() {
    local files_to_check=("$@")
    local violations=()
    local temp_report="$ENFORCEMENT_DIR/pre-commit-analysis.json"
    
    log_enforcement "${GATE} Checking completion for ${#files_to_check[@]} files..."
    
    # Run targeted analysis on specific files
    for file in "${files_to_check[@]}"; do
        if [[ "$file" =~ \.(tsx|ts)$ ]] && [[ ! "$file" =~ \.d\.ts$ ]]; then
            # Analyze individual file
            local analysis=$(python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" --file "$file" 2>/dev/null || echo "{}")
            
            if [ "$analysis" != "{}" ]; then
                local completion_score=$(echo "$analysis" | jq -r '.completion_score // 0')
                local completion_level=$(echo "$analysis" | jq -r '.completion_level // "UNKNOWN"')
                local issues=$(echo "$analysis" | jq -r '.issues // []' | jq length)
                
                # Check against thresholds
                local required_threshold=$COMPLETION_THRESHOLD
                
                # Higher threshold for medical files
                if echo "$file" | grep -qE "(medical|patient|drug|pharmacy|emergency)"; then
                    required_threshold=$MEDICAL_COMPLETION_THRESHOLD
                fi
                
                # Check completion level
                if [ "$completion_score" -lt "$required_threshold" ]; then
                    violations+=("$file: Completion $completion_score% below required $required_threshold%")
                fi
                
                # Check for placeholder indicators
                if [ "$completion_level" = "PLACEHOLDER" ]; then
                    violations+=("$file: File is still a placeholder")
                fi
                
                # Check for critical issues
                if [ "$issues" -gt 0 ]; then
                    local critical_issues=$(echo "$analysis" | jq -r '.issues[]' | grep -E "(debugger|alert|security)" | wc -l)
                    if [ "$critical_issues" -gt 0 ]; then
                        violations+=("$file: Contains $critical_issues critical issues")
                    fi
                fi
            fi
        fi
    done
    
    # Report violations
    if [ ${#violations[@]} -gt 0 ]; then
        log_enforcement "${CROSS} Quality gate violations found:"
        for violation in "${violations[@]}"; do
            log_enforcement "  - $violation"
        done
        return 1
    else
        log_enforcement "${CHECK} All files passed quality gates"
        return 0
    fi
}

# Security enforcement
enforce_security_standards() {
    local files=("$@")
    local violations=()
    
    log_enforcement "${SHIELD} Enforcing security standards..."
    
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            # Check for security violations
            local content=$(cat "$file")
            
            # Forbidden patterns
            if echo "$content" | grep -q "console.log"; then
                violations+=("$file: Contains console.log statements")
            fi
            
            if echo "$content" | grep -q "alert("; then
                violations+=("$file: Contains alert() statements")
            fi
            
            if echo "$content" | grep -q "debugger"; then
                violations+=("$file: Contains debugger statements")
            fi
            
            if echo "$content" | grep -q "innerHTML.*="; then
                violations+=("$file: Potential XSS risk with innerHTML")
            fi
            
            # TypeScript any usage
            if echo "$content" | grep -E ": any\b" | grep -v "//.*: any"; then
                violations+=("$file: Contains TypeScript 'any' type")
            fi
            
            # Hardcoded secrets patterns
            if echo "$content" | grep -iE "(password|secret|key|token).*=.*['\"][^'\"]{8,}"; then
                violations+=("$file: Possible hardcoded credentials")
            fi
        fi
    done
    
    if [ ${#violations[@]} -gt 0 ]; then
        log_enforcement "${CROSS} Security violations found:"
        for violation in "${violations[@]}"; do
            log_enforcement "  - $violation"
        done
        return 1
    else
        log_enforcement "${CHECK} Security standards passed"
        return 0
    fi
}

# Medical compliance check
check_medical_compliance() {
    local files=("$@")
    local violations=()
    
    log_enforcement "${GATE} Checking medical compliance..."
    
    for file in "${files[@]}"; do
        # Check if file is medical-related
        if echo "$file" | grep -qE "(medical|patient|drug|pharmacy|emergency|dosage|treatment)"; then
            if [[ -f "$file" ]]; then
                local content=$(cat "$file")
                
                # Medical files must have proper error handling
                if ! echo "$content" | grep -qE "(try|catch|Error|throw)"; then
                    violations+=("$file: Medical file lacks error handling")
                fi
                
                # Must have validation
                if ! echo "$content" | grep -qE "(validate|validation|schema)"; then
                    violations+=("$file: Medical file lacks input validation")
                fi
                
                # Must have logging for audit trails
                if ! echo "$content" | grep -qE "(log|audit|track)"; then
                    violations+=("$file: Medical file lacks audit logging")
                fi
                
                # Check for drug calculation safety
                if echo "$file" | grep -qE "(drug|dosage|medication)" && echo "$content" | grep -qE "calculation|formula|dose"; then
                    if ! echo "$content" | grep -qE "(precision|round|toFixed|Math\.round)"; then
                        violations+=("$file: Drug calculation lacks precision handling")
                    fi
                fi
            fi
        fi
    done
    
    if [ ${#violations[@]} -gt 0 ]; then
        log_enforcement "${CROSS} Medical compliance violations found:"
        for violation in "${violations[@]}"; do
            log_enforcement "  - $violation"
        done
        return 1
    else
        log_enforcement "${CHECK} Medical compliance passed"
        return 0
    fi
}

# Test coverage enforcement
enforce_test_coverage() {
    local files=("$@")
    local violations=()
    
    log_enforcement "${GATE} Checking test coverage requirements..."
    
    for file in "${files[@]}"; do
        if [[ "$file" =~ \.(tsx|ts)$ ]] && [[ ! "$file" =~ \.test\. ]] && [[ ! "$file" =~ \.spec\. ]]; then
            # Check if test file exists
            local base_name=$(basename "$file" .tsx)
            base_name=$(basename "$base_name" .ts)
            local dir_name=$(dirname "$file")
            
            local test_patterns=(
                "$dir_name/$base_name.test.tsx"
                "$dir_name/$base_name.test.ts"
                "$dir_name/$base_name.spec.tsx"
                "$dir_name/$base_name.spec.ts"
                "$dir_name/__tests__/$base_name.test.tsx"
                "$dir_name/__tests__/$base_name.test.ts"
            )
            
            local test_exists=false
            for pattern in "${test_patterns[@]}"; do
                if [[ -f "$pattern" ]]; then
                    test_exists=true
                    break
                fi
            done
            
            # Higher requirements for medical files
            if echo "$file" | grep -qE "(medical|patient|drug|pharmacy|emergency)"; then
                if [ "$test_exists" = false ]; then
                    violations+=("$file: Medical file requires test coverage")
                fi
            elif echo "$file" | grep -qE "pages/.*\.tsx$"; then
                # Page components should have basic tests
                if [ "$test_exists" = false ]; then
                    violations+=("$file: Page component should have tests")
                fi
            fi
        fi
    done
    
    if [ ${#violations[@]} -gt 0 ]; then
        log_enforcement "${WARNING} Test coverage recommendations:"
        for violation in "${violations[@]}"; do
            log_enforcement "  - $violation"
        done
        # Don't fail for test coverage, just warn
        return 0
    else
        log_enforcement "${CHECK} Test coverage requirements met"
        return 0
    fi
}

# Generate enforcement report
generate_enforcement_report() {
    local operation="$1"
    local files=("${@:2}")
    local timestamp=$(date -Iseconds)
    local report_file="$ENFORCEMENT_DIR/enforcement-report-$(date +%Y%m%d-%H%M%S).json"
    
    # Run all checks and collect results
    local completion_result="unknown"
    local security_result="unknown"
    local medical_result="unknown"
    local test_result="unknown"
    
    # Run checks without exiting on failure
    set +e
    check_file_completion "${files[@]}" > /dev/null 2>&1
    completion_result=$?
    
    enforce_security_standards "${files[@]}" > /dev/null 2>&1
    security_result=$?
    
    check_medical_compliance "${files[@]}" > /dev/null 2>&1
    medical_result=$?
    
    enforce_test_coverage "${files[@]}" > /dev/null 2>&1
    test_result=$?
    set -e
    
    # Generate report
    local files_json=$(printf '%s\n' "${files[@]}" | jq -R . | jq -s .)
    cat > "$report_file" << EOF
{
  "timestamp": "$timestamp",
  "operation": "$operation",
  "files_checked": $files_json,
  "results": {
    "completion_check": $([ $completion_result -eq 0 ] && echo "true" || echo "false"),
    "security_check": $([ $security_result -eq 0 ] && echo "true" || echo "false"),
    "medical_compliance": $([ $medical_result -eq 0 ] && echo "true" || echo "false"),
    "test_coverage": $([ $test_result -eq 0 ] && echo "true" || echo "false")
  },
  "overall_passed": $([ $completion_result -eq 0 ] && [ $security_result -eq 0 ] && [ $medical_result -eq 0 ] && echo "true" || echo "false"),
  "enforcement_config": {
    "completion_threshold": $COMPLETION_THRESHOLD,
    "medical_threshold": $MEDICAL_COMPLETION_THRESHOLD,
    "security_level": "$SECURITY_THRESHOLD"
  }
}
EOF
    
    log_enforcement "${GATE} Enforcement report generated: $report_file"
    echo "$report_file"
}

# Install Git hooks
install_git_hooks() {
    log_enforcement "${GATE} Installing Git hooks for quality enforcement..."
    
    local hooks_dir="$PROJECT_ROOT/.git/hooks"
    
    # Pre-commit hook
    cat > "$hooks_dir/pre-commit" << 'EOF'
#!/bin/bash
# Quality Gates Pre-commit Hook
# Automatically enforces quality standards before commits

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
ENFORCER="$PROJECT_ROOT/scripts/quality-gates-enforcer.sh"

# Get list of staged files
STAGED_FILES=($(git diff --cached --name-only --diff-filter=ACM))

if [ ${#STAGED_FILES[@]} -eq 0 ]; then
    echo "No files to check"
    exit 0
fi

echo "🚦 Running quality gates enforcement..."

# Run enforcement
if ! "$ENFORCER" pre-commit "${STAGED_FILES[@]}"; then
    echo ""
    echo "❌ Quality gates failed. Fix issues before committing."
    echo "💡 Use 'git commit --no-verify' to bypass (not recommended)"
    exit 1
fi

echo "✅ Quality gates passed"
exit 0
EOF
    
    # Pre-push hook
    cat > "$hooks_dir/pre-push" << 'EOF'
#!/bin/bash
# Quality Gates Pre-push Hook
# Runs comprehensive checks before pushing

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
ENFORCER="$PROJECT_ROOT/scripts/quality-gates-enforcer.sh"

echo "🚦 Running pre-push quality checks..."

# Get list of files changed in this branch
CHANGED_FILES=($(git diff --name-only origin/main..HEAD))

if [ ${#CHANGED_FILES[@]} -eq 0 ]; then
    echo "No files changed"
    exit 0
fi

# Run comprehensive enforcement
if ! "$ENFORCER" pre-push "${CHANGED_FILES[@]}"; then
    echo ""
    echo "❌ Pre-push quality gates failed"
    exit 1
fi

echo "✅ Pre-push quality gates passed"
exit 0
EOF
    
    # Make hooks executable
    chmod +x "$hooks_dir/pre-commit" "$hooks_dir/pre-push"
    
    log_enforcement "${CHECK} Git hooks installed successfully"
}

# Main enforcement function
main() {
    local operation="${1:-check}"
    shift
    local files=("$@")
    
    log_enforcement "${GATE} Quality Gates Enforcer - Operation: $operation"
    
    # Load configuration
    if ! load_quality_config; then
        log_enforcement "${WARNING} Using default quality thresholds"
        COMPLETION_THRESHOLD=70
        MEDICAL_COMPLETION_THRESHOLD=100
        SECURITY_THRESHOLD="moderate"
    fi
    
    case "$operation" in
        "pre-commit")
            log_enforcement "${GATE} Running pre-commit enforcement..."
            
            local passed=true
            
            # Run all checks
            if ! check_file_completion "${files[@]}"; then
                passed=false
            fi
            
            if ! enforce_security_standards "${files[@]}"; then
                passed=false
            fi
            
            if ! check_medical_compliance "${files[@]}"; then
                passed=false
            fi
            
            # Test coverage is advisory only
            enforce_test_coverage "${files[@]}"
            
            # Generate report
            generate_enforcement_report "pre-commit" "${files[@]}"
            
            if [ "$passed" = true ]; then
                log_enforcement "${CHECK} Pre-commit enforcement passed"
                exit 0
            else
                log_enforcement "${CROSS} Pre-commit enforcement failed"
                exit 1
            fi
            ;;
            
        "pre-push")
            log_enforcement "${GATE} Running pre-push enforcement..."
            
            # More comprehensive checks for push
            local passed=true
            
            if ! check_file_completion "${files[@]}"; then
                passed=false
            fi
            
            if ! enforce_security_standards "${files[@]}"; then
                passed=false
            fi
            
            if ! check_medical_compliance "${files[@]}"; then
                passed=false
            fi
            
            # Generate report
            generate_enforcement_report "pre-push" "${files[@]}"
            
            if [ "$passed" = true ]; then
                log_enforcement "${CHECK} Pre-push enforcement passed"
                exit 0
            else
                log_enforcement "${CROSS} Pre-push enforcement failed"
                exit 1
            fi
            ;;
            
        "install-hooks")
            install_git_hooks
            ;;
            
        "check")
            log_enforcement "${GATE} Running quality gates check..."
            
            if [ ${#files[@]} -eq 0 ]; then
                # Check all TypeScript files if none specified
                mapfile -t files < <(find "$PROJECT_ROOT" -name "*.tsx" -o -name "*.ts" | grep -v node_modules | grep -v ".d.ts")
            fi
            
            check_file_completion "${files[@]}"
            enforce_security_standards "${files[@]}"
            check_medical_compliance "${files[@]}"
            enforce_test_coverage "${files[@]}"
            
            generate_enforcement_report "check" "${files[@]}"
            ;;
            
        *)
            echo "Usage: $0 {pre-commit|pre-push|check|install-hooks} [files...]"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"