#!/bin/bash
# Post-create script for devcontainer
# Runs after the container is created but before VS Code connects

set -e

echo "🚀 Running post-create setup for HardCard development environment..."

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p /workspace/{logs,temp,cache}
mkdir -p /home/vscode/{.config,.cache,.local/bin}

# Set up Git
echo "🔧 Configuring Git..."
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.editor "code --wait"
git config --global diff.tool "code"
git config --global difftool.code.cmd 'code --wait --diff $LOCAL $REMOTE'

# Install Python dependencies for all modules
echo "🐍 Installing Python dependencies..."
if [ -f "/workspace/modules/agentauth/requirements.txt" ]; then
    pip install --user -r /workspace/modules/agentauth/requirements.txt
fi

if [ -f "/workspace/modules/agentauth/requirements-dev.txt" ]; then
    pip install --user -r /workspace/modules/agentauth/requirements-dev.txt
fi

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
if [ -f "/workspace/.pre-commit-config.yaml" ]; then
    pre-commit install --install-hooks
    pre-commit install --hook-type commit-msg
fi

# Set up database
echo "🗄️ Setting up databases..."
# Wait for PostgreSQL to be ready
until pg_isready -h localhost -p 5432 -U hardcard; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# Create databases for each module
psql -h localhost -U hardcard -d hardcard_dev << EOF
CREATE DATABASE IF NOT EXISTS agentauth_dev;
CREATE DATABASE IF NOT EXISTS agentauth_test;
CREATE DATABASE IF NOT EXISTS legacy_vault_dev;
CREATE DATABASE IF NOT EXISTS legacy_vault_test;
CREATE DATABASE IF NOT EXISTS vetsorcery_dev;
CREATE DATABASE IF NOT EXISTS vetsorcery_test;
GRANT ALL PRIVILEGES ON DATABASE agentauth_dev TO hardcard;
GRANT ALL PRIVILEGES ON DATABASE agentauth_test TO hardcard;
GRANT ALL PRIVILEGES ON DATABASE legacy_vault_dev TO hardcard;
GRANT ALL PRIVILEGES ON DATABASE legacy_vault_test TO hardcard;
GRANT ALL PRIVILEGES ON DATABASE vetsorcery_dev TO hardcard;
GRANT ALL PRIVILEGES ON DATABASE vetsorcery_test TO hardcard;
EOF

# Run database migrations
echo "🔄 Running database migrations..."
if [ -f "/workspace/modules/agentauth/alembic.ini" ]; then
    cd /workspace/modules/agentauth && alembic upgrade head
fi

# Install VS Code extensions (if not already installed by devcontainer features)
echo "🧩 Verifying VS Code extensions..."
code --list-extensions || true

# Create test fixtures and sample data
echo "🧪 Setting up test data..."
python << EOF
import os
import json

# Create sample .env file if it doesn't exist
env_example = '/workspace/.env.example'
env_file = '/workspace/.env'

if os.path.exists(env_example) and not os.path.exists(env_file):
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Update with development values
    content = content.replace('your-secret-key-at-least-32-bytes-long-change-this', 
                            'dev-secret-key-for-local-development-only-32b')
    content = content.replace('password', 'hardcard')
    content = content.replace('APP_ENV=production', 'APP_ENV=development')
    content = content.replace('DEBUG=false', 'DEBUG=true')
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")

print("✅ Test data setup complete")
EOF

# Download and cache commonly used dependencies
echo "📦 Pre-caching dependencies..."
pip download -d /home/vscode/.cache/pip/wheels \
    fastapi uvicorn sqlalchemy alembic redis \
    pytest pytest-asyncio pytest-cov \
    black isort mypy pylint \
    2>/dev/null || true

# Set up shell aliases and functions
echo "🐚 Configuring shell environment..."
cat >> /home/vscode/.zshrc << 'EOF'

# HardCard development aliases
alias hc='cd /workspace'
alias hca='cd /workspace/modules/agentauth'
alias hcl='cd /workspace/modules/legacy-vault'
alias hcv='cd /workspace/modules/vetsorcery'

# Python aliases
alias pytest='python -m pytest'
alias ipy='ipython'
alias black='python -m black'
alias mypy='python -m mypy'

# Docker aliases
alias dc='docker-compose'
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# Git aliases
alias gs='git status'
alias gd='git diff'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --graph'

# Testing shortcuts
alias test-unit='pytest tests/unit -v'
alias test-integration='pytest tests/integration -v'
alias test-all='pytest -v --cov=. --cov-report=html'
alias test-watch='pytest-watch -- -v'

# Database shortcuts
alias db-shell='psql -h localhost -U hardcard -d hardcard_dev'
alias db-migrate='alembic upgrade head'
alias db-rollback='alembic downgrade -1'
alias redis-cli='redis-cli -a hardcard_dev'

# Development server shortcuts
alias run-auth='cd /workspace/modules/agentauth && uvicorn main:app --reload --host 0.0.0.0 --port 8000'
alias run-vault='cd /workspace/modules/legacy-vault && uvicorn main:app --reload --host 0.0.0.0 --port 8001'
alias run-vet='cd /workspace/modules/vetsorcery && uvicorn main:app --reload --host 0.0.0.0 --port 8002'

# Quality checks
alias quality='black . && isort . && mypy . && pylint src/'
alias security='bandit -r . && safety check'

# Load testing
alias load-test='k6 run tests/load/script.js'

# Monitoring
alias logs='tail -f logs/*.log'
alias metrics='open http://localhost:9090'  # Prometheus
alias traces='open http://localhost:16686' # Jaeger

# Utility functions
function jwt-decode() {
    echo "$1" | cut -d. -f2 | base64 -d 2>/dev/null | jq .
}

function test-endpoint() {
    http --json "$@" Authorization:"Bearer $(cat ~/.hardcard/token 2>/dev/null)"
}

EOF

# Create initial test token for development
mkdir -p /home/vscode/.hardcard
echo "dev-token-for-testing" > /home/vscode/.hardcard/token

# Final message
echo "
✅ HardCard development environment setup complete!

🚀 Quick Start Commands:
  - Run AgentAuth API:     run-auth
  - Run tests:             test-all
  - Check code quality:    quality
  - View logs:             logs
  - Database shell:        db-shell
  - Redis CLI:             redis-cli

📚 Documentation:
  - API Docs:      http://localhost:8000/docs
  - Metrics:       http://localhost:9090
  - Traces:        http://localhost:16686
  - Mail:          http://localhost:8025

Happy coding! 🎉
"