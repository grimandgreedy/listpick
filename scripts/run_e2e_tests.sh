#!/bin/bash
# Run E2E tests (requires kitty terminal)

# Check if kitty is installed
if ! command -v kitty &> /dev/null; then
    echo "Error: kitty terminal is not installed"
    echo "Install with: brew install kitty  # macOS"
    exit 1
fi

# Temporarily rename listpick.py to avoid import conflicts
if [ -f "listpick.py" ]; then
    mv listpick.py listpick_entry.py.tmp
    RENAMED=1
fi

# Run E2E tests
python3 -m pytest tests/e2e/ -m e2e "$@"
EXIT_CODE=$?

# Restore listpick.py
if [ "$RENAMED" = "1" ]; then
    mv listpick_entry.py.tmp listpick.py
fi

# Cleanup any lingering kitty processes
pkill -f "kitty --listen-on=unix:/tmp/listpick_test" 2>/dev/null || true

exit $EXIT_CODE
