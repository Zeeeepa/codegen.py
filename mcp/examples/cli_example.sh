#!/bin/bash
# Example CLI commands for the Codegen API MCP Server

# Set environment variables
export CODEGEN_API_TOKEN="your_api_token"  # Replace with your actual token
export CODEGEN_ORG_ID="your_org_id"        # Replace with your actual org ID

echo "Codegen API CLI Examples"
echo "========================"
echo

# Configuration examples
echo "1. Configuration Commands:"
echo "--------------------------"
echo "# Interactive setup"
echo "codegen config init"
echo
echo "# Manual configuration"
echo "codegen config set api-token YOUR_TOKEN"
echo "codegen config set org-id YOUR_ORG_ID"
echo "codegen config set api.base-url https://api.codegen.com"
echo
echo "# Verify setup"
echo "codegen config validate"
echo

# New agent run examples
echo "2. Create New Agent Run:"
echo "-----------------------"
echo "# Basic syntax"
echo "codegenapi new --repo Zeeeepa/codegen.py --task FEATURE_IMPLEMENTATION --query \"Implement JWT-based authentication\""
echo
echo "# With branch targeting"
echo "codegenapi new --repo Zeeeepa/codegen.py --branch feature/auth --task FEATURE_IMPLEMENTATION --query \"Implement JWT-based authentication\""
echo
echo "# With PR targeting"
echo "codegenapi new --repo Zeeeepa/codegen.py --pr 123 --task BUG_FIX --query \"Fix authentication issue in login form\""
echo
echo "# With wait for completion"
echo "codegenapi new --repo Zeeeepa/codegen.py --task CREATE_PLAN --query \"Create a plan for the project\" --wait-for-completion"
echo
echo "# With parent ID for orchestration"
echo "codegenapi new --repo Zeeeepa/codegen.py --task ANALYZE --query \"Analyze the codebase\" --parent-id 12345"
echo

# Resume agent run examples
echo "3. Resume Agent Run:"
echo "-------------------"
echo "# Basic syntax"
echo "codegenapi resume --task-id 12345 --message \"Please also include error handling\""
echo
echo "# With wait for completion"
echo "codegenapi resume --task-id 12345 --message \"Please also include error handling\" --wait-for-completion"
echo
echo "# With task type"
echo "codegenapi resume --task-id 12345 --message \"Please also include error handling\" --task BUG_FIX"
echo

# List agent runs examples
echo "4. List Agent Runs:"
echo "------------------"
echo "# List all recent tasks"
echo "codegenapi list"
echo
echo "# Filter by status"
echo "codegenapi list --status running --limit 20"
echo
echo "# Filter by repository"
echo "codegenapi list --repo Zeeeepa/codegen.py"
echo
echo "# Combined filters"
echo "codegenapi list --status completed --repo Zeeeepa/codegen.py --limit 50"
echo

echo "5. MCP Server Configuration:"
echo "--------------------------"
echo "{
  \"codegenapi\": {
    \"command\": \"uv\",
    \"args\": [
      \"--directory\",
      \"<Project'sRootDir>/mcp\",
      \"run\",
      \"server.py\"
    ]
  }
}"
echo
