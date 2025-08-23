# Codegen API Endpoints Analysis

Based on the API documentation, here are the key endpoints available in the Codegen API:

## 1. User Endpoints
- `GET /v1/organizations/{org_id}/users` - Get users in an organization
- `GET /v1/organizations/{org_id}/users/{user_id}` - Get details for a specific user
- `GET /v1/current-user` - Get current user info

## 2. Agent Endpoints
- `POST /v1/organizations/{org_id}/agent/run` - Create agent run
- `GET /v1/organizations/{org_id}/agent/run/{agent_run_id}` - Get agent run status
- `GET /v1/organizations/{org_id}/agent/runs` - List agent runs
- `POST /v1/organizations/{org_id}/agent/run/{agent_run_id}/resume` - Resume agent run
- `POST /v1/organizations/{org_id}/agent/run/{agent_run_id}/ban-all-checks` - Ban all checks for agent run
- `POST /v1/organizations/{org_id}/agent/run/{agent_run_id}/unban-all-checks` - Unban all checks for agent run
- `POST /v1/organizations/{org_id}/agent/run/{agent_run_id}/remove-codegen-from-pr` - Remove Codegen from PR
- `GET /v1/organizations/{org_id}/agent/run/{agent_run_id}/logs` - Get agent run logs

## 3. Repository Endpoints
- `GET /v1/organizations/{org_id}/repos` - Get repositories

## 4. Organization Endpoints
- `GET /v1/organizations` - Get organizations

## 5. Integration Endpoints
- `GET /v1/organizations/{org_id}/integrations` - Get organization integrations

## 6. Sandbox Endpoints
- `POST /v1/sandbox/analyze-logs` - Analyze sandbox logs

## 7. Agent-Alpha Endpoints
- Various endpoints for experimental agent features

## Key Data Models

### Agent Run
```json
{
  "id": 123,
  "organization_id": 123,
  "status": "string",
  "created_at": "string",
  "web_url": "string",
  "result": "string",
  "summary": "string",
  "source_type": "LOCAL",
  "github_pull_requests": [
    {
      "id": 123,
      "title": "string",
      "url": "string",
      "created_at": "string",
      "head_branch_name": "string"
    }
  ],
  "metadata": {}
}
```

### Organization
```json
{
  "id": 123,
  "name": "string",
  "settings": {
    "enable_pr_creation": true,
    "enable_rules_detection": true
  }
}
```

### Repository
```json
{
  "id": 123,
  "name": "string",
  "full_name": "string",
  "description": "string",
  "github_id": "string",
  "organization_id": 123,
  "visibility": "string",
  "archived": true,
  "setup_status": "string",
  "language": "string"
}
```

### User
```json
{
  "id": 123,
  "email": "string",
  "github_user_id": "string",
  "github_username": "string",
  "avatar_url": "string",
  "full_name": "string",
  "role": "string",
  "is_admin": true
}
```

## Agent Run Logs
The agent run logs API provides detailed execution logs for agent runs, including:
- Tool executions
- Agent reasoning
- Error information
- Final answers

This is crucial for monitoring agent progress and debugging issues.

