#!/bin/bash
# Secure Git Initialization Script for HardCard
# Sets up git with security best practices

set -e
echo "🔐 Secure Git Setup for HardCard"
echo "================================"
echo ""

# Check if git is already initialized
if [ -d .git ]; then
    echo "⚠️  Git repository already exists!"
    read -p "Continue with security setup? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 0
    fi
else
    echo "📦 Initializing new Git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# Create comprehensive .gitignore
echo ""
echo "📝 Creating secure .gitignore..."
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
vendor/
package-lock.json
yarn.lock
pnpm-lock.yaml

# Environment variables and secrets
.env
.env.*
!.env.example
!.env.sample
secrets/
*.key
*.pem
*.p12
*.pfx
*.cer
*.crt

# API Keys and credentials
**/config/credentials.yml.enc
**/config/master.key
firebase-config.json
google-services.json
GoogleService-Info.plist

# Build outputs
dist/
build/
out/
.next/
.nuxt/
.output/
*.log
*.cache
.turbo/

# IDE and editors
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Sensitive business data
/data/customers/
/data/users/
/data/financials/
/data/analytics/
/backups/
*.sql
*.dump
*.sqlite
*.db

# Temporary files
tmp/
temp/
*.tmp
*.temp
*.bak
*.backup
*.old

# Test coverage and reports
coverage/
.nyc_output/
test-results/
reports/
*.lcov

# WordPress specific
wp-config.php
wp-content/uploads/
wp-content/cache/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Logs and debugging
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Desktop.ini

# Archives
*.zip
*.tar.gz
*.rar
*.7z

# Media files (usually)
*.mp4
*.mov
*.avi
*.mp3
*.wav

# But keep important docs
!docs/**/*
!README.md
!LICENSE
EOF
echo "✅ .gitignore created"

# Create .env.example
echo ""
echo "📝 Creating .env.example..."
cat > .env.example << 'EOF'
# Application
NODE_ENV=development
PORT=3000
APP_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hardcard

# Authentication
JWT_SECRET=generate-a-secure-random-string
SESSION_SECRET=generate-another-secure-random-string

# Payment Gateway
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASS=your-password

# Third Party APIs
GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X
SENTRY_DSN=https://...@sentry.io/...

# Feature Flags
ENABLE_FEATURE_X=false
ENABLE_BETA_FEATURES=false
EOF
echo "✅ .env.example created"

# Set up git user if not configured
if ! git config user.email > /dev/null 2>&1; then
    echo ""
    echo "📧 Git user configuration needed..."
    read -p "Enter your email for git commits: " GIT_EMAIL
    read -p "Enter your name for git commits: " GIT_NAME
    git config user.email "$GIT_EMAIL"
    git config user.name "$GIT_NAME"
    echo "✅ Git user configured"
fi

# Create initial commit structure
echo ""
echo "📁 Creating initial project structure..."
mkdir -p docs scripts tests backups/.gitkeep data/.gitkeep

# Create README if it doesn't exist
if [ ! -f README.md ]; then
    cat > README.md << 'EOF'
# HardCard Project

## Overview
HardCard is a comprehensive business management platform combining e-commerce, content management, and business automation.

## Security Notice
This repository follows security best practices. Never commit sensitive data.

## Setup
1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Install dependencies
4. Run the application

## Documentation
See `/docs` directory for detailed documentation.
EOF
fi

# Install git-secrets if available
echo ""
echo "🔒 Setting up git-secrets..."
if command -v git-secrets &> /dev/null; then
    git secrets --install
    git secrets --register-aws
    git secrets --register-gcp
    echo "✅ git-secrets configured"
else
    echo "⚠️  git-secrets not installed. Install with: brew install git-secrets"
fi

# Create pre-commit hook
echo ""
echo "🪝 Creating pre-commit hooks..."
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to check for secrets

echo "🔍 Running pre-commit security checks..."

# Check for common secret patterns
PATTERNS="password=|api_key=|secret=|private_key=|aws_access_key|PRIVATE KEY"
if git diff --cached --name-only | xargs grep -E "$PATTERNS" 2>/dev/null; then
    echo "❌ Potential secrets detected in commit!"
    echo "Please remove sensitive data before committing."
    exit 1
fi

# Check for large files
while read -r file; do
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    if [ "$size" -gt 10485760 ]; then  # 10MB
        echo "❌ Large file detected: $file ($(($size / 1048576))MB)"
        echo "Consider using Git LFS or excluding this file."
        exit 1
    fi
done < <(git diff --cached --name-only)

echo "✅ Pre-commit checks passed"
EOF
chmod +x .git/hooks/pre-commit
echo "✅ Pre-commit hooks created"

# Create backup script
echo ""
echo "💾 Creating backup script..."
cat > scripts/backup-encrypted.sh << 'EOF'
#!/bin/bash
# Encrypted backup script for HardCard

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/hardcard-backup-$DATE.tar.gz"

echo "🔐 Creating encrypted backup..."
mkdir -p "$BACKUP_DIR"

# Create tar archive excluding unnecessary files
tar --exclude='.git' \
    --exclude='node_modules' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='*.log' \
    --exclude='backups' \
    -czf "$BACKUP_FILE" .

# Encrypt the backup
echo "🔒 Encrypting backup..."
gpg -c "$BACKUP_FILE"
rm "$BACKUP_FILE"  # Remove unencrypted version

echo "✅ Encrypted backup created: $BACKUP_FILE.gpg"
echo "⚠️  Store the password securely!"
EOF
chmod +x scripts/backup-encrypted.sh
echo "✅ Backup script created"

# Initial commit
echo ""
echo "📝 Creating initial commit..."
git add .gitignore .env.example README.md
git add docs/.gitkeep scripts/.gitkeep tests/.gitkeep backups/.gitkeep data/.gitkeep
git add scripts/backup-encrypted.sh

git commit -m "Initial commit: Secure git setup for HardCard

- Comprehensive .gitignore for security
- Environment variable template
- Pre-commit hooks for secret detection
- Encrypted backup script
- Project structure initialization"

echo ""
echo "================================"
echo "✅ Secure Git Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Review .gitignore and adjust for your needs"
echo "2. Copy .env.example to .env and configure"
echo "3. Choose a remote repository:"
echo "   - GitHub: git remote add origin git@github.com:username/hardcard.git"
echo "   - GitLab: git remote add origin git@gitlab.com:username/hardcard.git"
echo "4. Run './scripts/backup-encrypted.sh' to create encrypted backups"
echo ""
echo "🔐 Security Reminders:"
echo "- Never commit .env files"
echo "- Use environment variables for secrets"
echo "- Review commits for sensitive data"
echo "- Keep backups encrypted"
echo "- Use private repositories for proprietary code"
echo ""
echo "💡 Tip: Install git-secrets for additional protection:"
echo "   brew install git-secrets"