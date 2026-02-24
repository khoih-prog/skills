#!/bin/bash
# ClawHub Package Script for Cue Skill
# Usage: ./package.sh [version]

set -e

VERSION="${1:-1.0.0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="/usr/lib/node_modules/openclaw/skills/cue"
OUTPUT_DIR="$SCRIPT_DIR/dist"
PACKAGE_NAME="cue-v${VERSION}"

echo "📦 Packaging Cue Skill v${VERSION}..."

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Create package directory
PKG_DIR="$OUTPUT_DIR/$PACKAGE_NAME"
rm -rf "$PKG_DIR" 2>/dev/null || true
mkdir -p "$PKG_DIR"

# Copy skill files
echo "Copying skill files..."
# Exclude dist directory to avoid self-copying
rsync -av --exclude='dist' --exclude='*.tar.gz' "$SKILL_DIR/" "$PKG_DIR/" 2>/dev/null || \
    (find "$SKILL_DIR" -maxdepth 1 -type f -exec cp {} "$PKG_DIR/" \; && \
     find "$SKILL_DIR" -maxdepth 1 -type d ! -name 'dist' ! -name '.' -exec cp -r {} "$PKG_DIR/" \;)

# Create package manifest
cat > "$PKG_DIR/manifest.json" << EOF
{
  "name": "cue",
  "version": "${VERSION}",
  "description": "AI-powered financial research assistant with multi-user support and intelligent monitoring",
  "author": "cuecue",
  "license": "MIT",
  "homepage": "https://cuecue.cn",
  "repository": "https://github.com/cuecue/openclaw-skill-cue",
  "keywords": ["finance", "research", "ai", "monitoring", "investment"],
  "openclaw": {
    "minVersion": "0.5.0",
    "skills": ["cue"]
  }
}
EOF

# Create archive
cd "$OUTPUT_DIR"
tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

echo ""
echo "✅ Package created: $OUTPUT_DIR/${PACKAGE_NAME}.tar.gz"
echo ""
echo "To publish to ClawHub:"
echo "  clawhub publish $OUTPUT_DIR/${PACKAGE_NAME}.tar.gz"
