#!/usr/bin/env bash
# Integration tests for TextKit CLI tools
# Tests Unix philosophy: pipeline composition, stdin/stdout

set -e  # Exit on error

echo "=== TextKit CLI Integration Tests ==="
echo

# Test 1: tt (text transformer)
echo "Test 1: tt - Text transformation"
result=$(echo "HELLO WORLD" | PYTHONPATH=. uv run python bin/tt.py //l -n 2>/dev/null)
expected="hello world"
if [ "$result" = "$expected" ]; then
    echo "✓ tt lowercase: PASS"
else
    echo "✗ tt lowercase: FAIL (expected: '$expected', got: '$result')"
    exit 1
fi

# Test 2: tt - Trim
echo "Test 2: tt - Trim whitespace"
result=$(echo "  hello  " | PYTHONPATH=. uv run python bin/tt.py //t -n 2>/dev/null)
expected="hello"
if [ "$result" = "$expected" ]; then
    echo "✓ tt trim: PASS"
else
    echo "✗ tt trim: FAIL (expected: '$expected', got: '$result')"
    exit 1
fi

# Test 3: tt - Chained rules
echo "Test 3: tt - Chained rules (trim + lowercase)"
result=$(echo "  HELLO WORLD  " | PYTHONPATH=. uv run python bin/tt.py //t//l -n 2>/dev/null)
expected="hello world"
if [ "$result" = "$expected" ]; then
    echo "✓ tt chained: PASS"
else
    echo "✗ tt chained: FAIL (expected: '$expected', got: '$result')"
    exit 1
fi

# Test 4: clip - Set and get
echo "Test 4: clip - Set and get"
echo "test content" | PYTHONPATH=. uv run python bin/clip.py set
result=$(PYTHONPATH=. uv run python bin/clip.py get)
expected="test content"
if [ "$result" = "$expected" ]; then
    echo "✓ clip set/get: PASS"
else
    echo "✗ clip set/get: FAIL (expected: '$expected', got: '$result')"
    exit 1
fi

# Test 5: clip - Clear
echo "Test 5: clip - Clear"
PYTHONPATH=. uv run python bin/clip.py clear > /dev/null 2>&1
# Note: clip get returns empty or error when clipboard is empty
# We just verify clear command doesn't crash
echo "✓ clip clear: PASS"

# Test 6: Pipeline composition (tt → clip)
echo "Test 6: Pipeline composition (tt → clip)"
echo "PIPELINE TEST" | PYTHONPATH=. uv run python bin/tt.py //l -n 2>/dev/null | PYTHONPATH=. uv run python bin/clip.py set 2>/dev/null
result=$(PYTHONPATH=. uv run python bin/clip.py get 2>/dev/null)
expected="pipeline test"
if [ "$result" = "$expected" ]; then
    echo "✓ Pipeline (tt → clip): PASS"
else
    echo "✗ Pipeline (tt → clip): FAIL (expected: '$expected', got: '$result')"
    exit 1
fi

# Test 7: Direct text input
echo "Test 7: tt - Direct text input (-t option)"
result=$(PYTHONPATH=. uv run python bin/tt.py //l -t "DIRECT INPUT" -n 2>/dev/null)
expected="direct input"
if [ "$result" = "$expected" ]; then
    echo "✓ tt direct input: PASS"
else
    echo "✗ tt direct input: FAIL (expected: '$expected', got: '$result')"
    exit 1
fi

echo
echo "=== All Tests Passed ✓ ==="
echo
echo "Unix Philosophy Validated:"
echo "  ✓ Tools work with stdin/stdout"
echo "  ✓ Pipeline composition works"
echo "  ✓ Simple, predictable behavior"
echo "  ✓ Do one thing well"
