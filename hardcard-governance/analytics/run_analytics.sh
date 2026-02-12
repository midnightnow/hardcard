#!/bin/bash
set -e

# Hardcard Governance Analytics Runner
# Automated analytics generation and reporting

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
OUTPUT_DIR="${OUTPUT_DIR:-./output}"
WEB3_URL="${WEB3_URL:-}"
CONTRACT_ADDRESS="${CONTRACT_ADDRESS:-}"
EXPORT_FORMAT="${EXPORT_FORMAT:-csv}"
GENERATE_CHARTS="${GENERATE_CHARTS:-true}"
MOCK_DATA="${MOCK_DATA:-true}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

usage() {
    echo "Hardcard Governance Analytics Runner"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  generate     - Generate analytics report (default)"
    echo "  api          - Start analytics API server"
    echo "  export       - Export raw data only"
    echo "  charts       - Generate charts only"
    echo "  clean        - Clean output directories"
    echo "  setup        - Install dependencies"
    echo ""
    echo "Options:"
    echo "  --output-dir DIR     Output directory (default: ./output)"
    echo "  --web3-url URL       Web3 RPC endpoint"
    echo "  --contract ADDR      Governance contract address"
    echo "  --format FORMAT      Export format: csv|json|excel (default: csv)"
    echo "  --mock-data          Use mock data for demonstration"
    echo "  --real-data          Use real blockchain data"
    echo ""
    echo "Environment Variables:"
    echo "  OUTPUT_DIR           Output directory"
    echo "  WEB3_URL             Web3 RPC endpoint"
    echo "  CONTRACT_ADDRESS     Governance contract address"
    echo "  EXPORT_FORMAT        Export format"
    echo "  API_HOST             API host (default: 0.0.0.0)"
    echo "  API_PORT             API port (default: 5000)"
    echo ""
    exit 1
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        log_warning "Python 3 is not installed"
        return 1
    fi
    
    if ! python3 -c "import pandas, matplotlib, plotly, web3" &> /dev/null; then
        log_warning "Some Python dependencies are missing"
        echo "Run: $0 setup"
        return 1
    fi
    
    log_success "Dependencies check passed"
    return 0
}

setup_dependencies() {
    log_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        log_success "Dependencies installed"
    else
        log_warning "requirements.txt not found"
        return 1
    fi
}

generate_analytics() {
    log_info "Generating governance analytics..."
    
    # Prepare arguments
    args=(
        "--output-dir" "$OUTPUT_DIR"
        "--export-format" "$EXPORT_FORMAT"
    )
    
    if [ -n "$WEB3_URL" ]; then
        args+=("--web3-url" "$WEB3_URL")
    fi
    
    if [ -n "$CONTRACT_ADDRESS" ]; then
        args+=("--contract-address" "$CONTRACT_ADDRESS")
    fi
    
    if [ "$GENERATE_CHARTS" = "true" ]; then
        args+=("--generate-charts")
    fi
    
    if [ "$MOCK_DATA" = "true" ]; then
        args+=("--mock-data")
    fi
    
    # Run analytics
    python3 governance-analytics.py "${args[@]}"
    
    if [ $? -eq 0 ]; then
        log_success "Analytics generation completed"
        
        # Display results
        echo ""
        echo "📊 Generated Files:"
        find "$OUTPUT_DIR" -type f -name "*.md" -o -name "*.html" -o -name "*.png" -o -name "*.json" | sort
        
        # Open report if on macOS
        if command -v open &> /dev/null; then
            report_file=$(find "$OUTPUT_DIR" -name "governance_report_*.md" | head -1)
            if [ -n "$report_file" ]; then
                echo ""
                echo "Opening report: $report_file"
                open "$report_file"
            fi
        fi
    else
        log_warning "Analytics generation failed"
        return 1
    fi
}

start_api() {
    log_info "Starting Analytics API server..."
    
    # Set environment variables
    export ANALYTICS_DB_PATH="${OUTPUT_DIR}/governance_analytics.db"
    export API_HOST="${API_HOST:-0.0.0.0}"
    export API_PORT="${API_PORT:-5000}"
    export API_DEBUG="${API_DEBUG:-false}"
    
    if [ -n "$WEB3_URL" ]; then
        export WEB3_URL="$WEB3_URL"
    fi
    
    # Start API server
    cd api/
    python3 governance_api.py
}

export_data_only() {
    log_info "Exporting governance data..."
    
    python3 governance-analytics.py \
        --output-dir "$OUTPUT_DIR" \
        --export-format "$EXPORT_FORMAT" \
        --mock-data
    
    log_success "Data export completed"
    echo "📁 Data files: $OUTPUT_DIR/data/"
}

generate_charts_only() {
    log_info "Generating charts..."
    
    python3 governance-analytics.py \
        --output-dir "$OUTPUT_DIR" \
        --generate-charts \
        --mock-data
    
    log_success "Charts generation completed"
    echo "📊 Chart files: $OUTPUT_DIR/"
}

clean_output() {
    log_info "Cleaning output directories..."
    
    if [ -d "$OUTPUT_DIR" ]; then
        rm -rf "$OUTPUT_DIR"
        log_success "Output directory cleaned"
    fi
    
    # Clean temporary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -delete
    
    log_success "Cleanup completed"
}

# Parse arguments
COMMAND="generate"
while [[ $# -gt 0 ]]; do
    case $1 in
        generate|api|export|charts|clean|setup)
            COMMAND="$1"
            shift
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --web3-url)
            WEB3_URL="$2"
            shift 2
            ;;
        --contract)
            CONTRACT_ADDRESS="$2"
            shift 2
            ;;
        --format)
            EXPORT_FORMAT="$2"
            shift 2
            ;;
        --mock-data)
            MOCK_DATA="true"
            shift
            ;;
        --real-data)
            MOCK_DATA="false"
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Main execution
echo "🏛️ Hardcard Governance Analytics"
echo "Command: $COMMAND"
echo "Output: $OUTPUT_DIR"
echo "=" .repeat(50)

case "$COMMAND" in
    "setup")
        setup_dependencies
        ;;
    "generate")
        if check_dependencies; then
            generate_analytics
        else
            echo "Run: $0 setup"
            exit 1
        fi
        ;;
    "api")
        if check_dependencies; then
            start_api
        else
            echo "Run: $0 setup"
            exit 1
        fi
        ;;
    "export")
        if check_dependencies; then
            export_data_only
        else
            echo "Run: $0 setup"
            exit 1
        fi
        ;;
    "charts")
        if check_dependencies; then
            generate_charts_only
        else
            echo "Run: $0 setup"
            exit 1
        fi
        ;;
    "clean")
        clean_output
        ;;
    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac