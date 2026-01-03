#!/bin/bash
# Run all tests with coverage

# Temporarily rename listpick.py to avoid import conflicts
if [ -f "listpick.py" ]; then
    mv listpick.py listpick_entry.py.tmp
    RENAMED=1
fi

# Run tests
python3 -m pytest tests/ "$@"
EXIT_CODE=$?

# Restore listpick.py
if [ "$RENAMED" = "1" ]; then
    mv listpick_entry.py.tmp listpick.py
fi

exit $EXIT_CODE
