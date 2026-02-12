#!/bin/bash

echo "🔥 Installing Kimi Heavy MOEX Terminal System"
echo "============================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r moex_requirements.txt

# Check for required API keys
echo "🔑 Checking API keys..."
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "⚠️ OPENAI_API_KEY not found"
    echo "Please set: export OPENAI_API_KEY=your_key_here"
fi

if [[ -z "$OPENROUTER_API_KEY" ]]; then
    echo "⚠️ OPENROUTER_API_KEY not found"  
    echo "Please set: export OPENROUTER_API_KEY=your_key_here"
fi

# Make scripts executable
chmod +x moex_terminal.py
chmod +x kimi_heavy_moex_terminal.py

echo "✅ Installation complete!"
echo ""
echo "🚀 To run the basic MOEX terminal:"
echo "   python3 moex_terminal.py"
echo ""
echo "🔥 To run the Kimi Heavy MOEX terminal:"
echo "   python3 kimi_heavy_moex_terminal.py"
echo ""
echo "📚 Available conversation patterns:"
echo "   - COMPETE: Agents compete, winner takes all"
echo "   - BUILD: Build upon each other's responses"  
echo "   - DEBATE: Highlight disagreements and perspectives"
echo "   - CONSENSUS: Find common ground and agreements"
echo "   - SYNTHESIZE: Combine all responses into unified answer"
echo "   - HEAVY_RESEARCH: Deep multi-agent research with parallel processing"
echo "   - PARALLEL_CREATION: Multiple agents creating different solutions simultaneously"
echo ""
echo "🧪 Test with: 'build a snake game'"