#!/bin/bash

# Quick Start Script for MacAgent Pro + HardCard
# Sets up the basic environment and runs a demo

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║        MacAgent Pro + HardCard Quick Start       ║"
echo "║   AI-Powered macOS Automation with Encryption    ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is required. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Create directories
echo -e "\n${CYAN}Setting up directories...${NC}"
mkdir -p macagent-llm/{models,curriculum,inference,evaluation}
mkdir -p build/macagent-pro
mkdir -p dist/macagent-pro

# Check for required files
echo -e "\n${CYAN}Checking required files...${NC}"
REQUIRED_FILES=(
    "deploy_macagent_pro.sh"
    "macagent_hardcard_unified.py"
    "test_macagent_integration.py"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${YELLOW}✗ $file (missing)${NC}"
        MISSING_FILES+=("$file")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo -e "\n${YELLOW}Warning: Some files are missing. The system may not work properly.${NC}"
fi

# Create minimal config
echo -e "\n${CYAN}Creating default configuration...${NC}"
if [[ ! -f "macagent-llm/macagent_config.json" ]]; then
    cat > macagent-llm/macagent_config.json << 'EOF'
{
  "models": {
    "macagent-4b": {
      "base_model": "microsoft/Phi-3-mini-4k-instruct",
      "description": "Fast model for real-time responses"
    }
  },
  "inference": {
    "port": 8000,
    "max_tokens": 512
  },
  "integration": {
    "hardcard_encryption": true,
    "local_only": true
  }
}
EOF
    echo -e "${GREEN}✓ Configuration created${NC}"
else
    echo -e "${GREEN}✓ Configuration exists${NC}"
fi

# Create sample training data
echo -e "\n${CYAN}Creating sample training data...${NC}"
mkdir -p macagent-llm/training_data
if [[ ! -f "macagent-llm/training_data/sample.jsonl" ]]; then
    cat > macagent-llm/training_data/sample.jsonl << 'EOF'
{"input": "Empty the trash", "output": "osascript -e 'tell application \"Finder\" to empty trash'", "reasoning": ["User wants to empty trash", "Use Finder via AppleScript"]}
{"input": "Take a screenshot", "output": "screencapture ~/Desktop/screenshot_$(date +%Y%m%d_%H%M%S).png", "reasoning": ["Capture screen", "Save with timestamp"]}
{"input": "Show disk usage", "output": "df -h", "reasoning": ["Display disk usage", "Human readable format"]}
EOF
    echo -e "${GREEN}✓ Sample data created${NC}"
fi

# Run integration test
echo -e "\n${CYAN}Running integration test...${NC}"
if [[ -f "test_macagent_integration.py" ]]; then
    python3 test_macagent_integration.py
else
    echo -e "${YELLOW}Integration test script not found${NC}"
fi

# Show next steps
echo -e "\n${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Quick Start Complete!${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "\n${CYAN}Next Steps:${NC}"
echo -e "1. Deploy the 4B model for testing:"
echo -e "   ${GREEN}./deploy_macagent_pro.sh --action deploy --model 4b --skip-training${NC}"
echo -e "\n2. Run the unified system demo:"
echo -e "   ${GREEN}python3 macagent_hardcard_unified.py${NC}"
echo -e "\n3. Read the documentation:"
echo -e "   ${GREEN}cat MACAGENT_HARDCARD_README.md${NC}"
echo -e "\n${CYAN}════════════════════════════════════════════════════${NC}"