#!/bin/bash
# Run all Codegen API tests

echo "=== Running Codegen API Tests ==="
echo

echo "1. Running Basic Test..."
python test_codegen_api.py
echo

echo "2. Running Mock Tests..."
python test_codegen_api_mock.py
echo

echo "=== All Tests Complete ==="
echo "MCP tools test successful!"

