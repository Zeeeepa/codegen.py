#!/bin/bash
# CLI Examples for CodegenAPI

echo "🚀 CodegenAPI CLI Examples"
echo "=========================="

# Check if environment variables are set
if [ -z "$CODEGEN_API_TOKEN" ]; then
    echo "❌ CODEGEN_API_TOKEN not set"
    echo "Please set it with: export CODEGEN_API_TOKEN='your_token'"
    exit 1
fi

echo "✅ Environment variables configured"

# Example 1: Create a feature implementation task
echo ""
echo "📝 Example 1: Feature Implementation Task"
echo "----------------------------------------"
codegenapi new \
  --repo https://github.com/Zeeeepa/codegen.py \
  --task FEATURE_IMPLEMENTATION \
  --query "Add input validation to all CLI commands"

# Example 2: Create a bug fix task with PR
echo ""
echo "🐛 Example 2: Bug Fix Task"
echo "-------------------------"
codegenapi new \
  --repo https://github.com/Zeeeepa/codegen.py \
  --task BUG_FIX \
  --query "Fix any import errors or missing dependencies"

# Example 3: Create a test generation task
echo ""
echo "🧪 Example 3: Test Generation Task"
echo "---------------------------------"
codegenapi new \
  --repo https://github.com/Zeeeepa/codegen.py \
  --task TEST_GENERATION \
  --query "Generate comprehensive unit tests for the TaskManager class"

# Example 4: List recent tasks
echo ""
echo "📋 Example 4: List Recent Tasks"
echo "------------------------------"
codegenapi list --limit 5

# Example 5: Check status of a specific task (you'll need to replace TASK_ID)
echo ""
echo "🔍 Example 5: Check Task Status"
echo "------------------------------"
echo "To check a specific task status, use:"
echo "codegenapi status <task_id>"

# Example 6: Resume a task (you'll need to replace TASK_ID)
echo ""
echo "🔄 Example 6: Resume Task"
echo "------------------------"
echo "To resume a task with additional instructions, use:"
echo "codegenapi resume --task-id <task_id> --message 'Additional instructions here'"

echo ""
echo "✅ CLI examples completed!"
echo "💡 Check task statuses with: codegenapi list"

