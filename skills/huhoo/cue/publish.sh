#!/bin/bash
# ClawHub Publish Script for Cue Skill

set -e

VERSION="${1:-1.0.0}"
echo "🚀 Publishing Cue Skill v${VERSION} to ClawHub..."

# Check if clawhub CLI is available
if ! command -v clawhub &> /dev/null; then
    echo "❌ Error: clawhub CLI not found"
    echo "Please install: npm install -g @openclaw/clawhub"
    exit 1
fi

# Package the skill
echo "📦 Packaging..."
./package.sh "$VERSION"

# Check if already logged in
if ! clawhub whoami &> /dev/null; then
    echo "🔑 Please login to ClawHub:"
    clawhub login
fi

# Publish
echo "📤 Publishing..."
clawhub publish "dist/cue-v${VERSION}.tar.gz" \
    --name cue \
    --version "$VERSION" \
    --description "AI-powered financial research assistant with monitoring generation" \
    --tags "finance,research,ai,monitoring,investment"

echo ""
echo "✅ Published successfully!"
echo ""
echo "View your skill:"
echo "  https://clawhub.com/skills/cue"
