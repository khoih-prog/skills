#!/bin/bash
# Dream Cycle - Memory Audit Script
# Run this nightly to audit and optimize memory files

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_DIR="$WORKSPACE/memory"
ARCHIVE_DIR="$WORKSPACE/memory/archive"
REPORT_FILE="/tmp/dream-audit-$(date +%Y%m%d).json"

# Ensure archive directory exists
mkdir -p "$ARCHIVE_DIR"

echo "=== Dream Cycle Audit ==="
echo "Date: $(date)"
echo ""

# File size thresholds (bytes)
AGENTS_MAX=2000
MEMORY_MAX=1500
USER_MAX=500

# Function to get file size
get_size() {
    wc -c < "$1" 2>/dev/null || echo 0
}

# Analyze AGENTS.md
AGENTS_SIZE=$(get_size "$WORKSPACE/AGENTS.md")
echo "AGENTS.md: $AGENTS_SIZE bytes"
if [ "$AGENTS_SIZE" -gt "$AGENTS_MAX" ]; then
    echo "  ⚠️  OVER LIMIT (max: $AGENTS_MAX)"
else
    echo "  ✅ OK"
fi

# Analyze MEMORY.md
MEMORY_SIZE=$(get_size "$WORKSPACE/MEMORY.md")
echo "MEMORY.md: $MEMORY_SIZE bytes"
if [ "$MEMORY_SIZE" -gt "$MEMORY_MAX" ]; then
    echo "  ⚠️  OVER LIMIT (max: $MEMORY_MAX)"
else
    echo "  ✅ OK"
fi

# Analyze USER.md
USER_SIZE=$(get_size "$WORKSPACE/USER.md")
echo "USER.md: $USER_SIZE bytes"
if [ "$USER_SIZE" -gt "$USER_MAX" ]; then
    echo "  ⚠️  OVER LIMIT (max: $USER_MAX)"
else
    echo "  ✅ OK"
fi

# Count memory files
MEMORY_FILES=$(find "$MEMORY_DIR" -name "*.md" 2>/dev/null | wc -l)
echo ""
echo "Memory files: $MEMORY_FILES"

# Count total memory size
TOTAL_MEMORY=$(du -ch "$MEMORY_DIR"/*.md 2>/dev/null | tail -1 | cut -f1)
echo "Total memory size: $TOTAL_MEMORY"

# Check QMD index if available
if command -v openclaw &> /dev/null; then
    echo ""
    echo "QMD Index Status:"
    openclaw memory status 2>/dev/null | grep -E "(Indexed|Vector|FTS)" || echo "  Status unavailable"
fi

echo ""
echo "=== Audit Complete ==="

# Output JSON report for automation
cat > "$REPORT_FILE" << EOF
{
  "date": "$(date -Iseconds)",
  "files": {
    "agents": {"path": "$WORKSPACE/AGENTS.md", "size": $AGENTS_SIZE, "max": $AGENTS_MAX, "over": $([ $AGENTS_SIZE -gt $AGENTS_MAX ] && echo "true" || echo "false")},
    "memory": {"path": "$WORKSPACE/MEMORY.md", "size": $MEMORY_SIZE, "max": $MEMORY_MAX, "over": $([ $MEMORY_SIZE -gt $MEMORY_MAX ] && echo "true" || echo "false")},
    "user": {"path": "$WORKSPACE/USER.md", "size": $USER_SIZE, "max": $USER_MAX, "over": $([ $USER_SIZE -gt $USER_MAX ] && echo "true" || echo "false")}
  },
  "memory_files": $MEMORY_FILES,
  "total_memory": "$TOTAL_MEMORY"
}
EOF
echo "Report saved to: $REPORT_FILE"
