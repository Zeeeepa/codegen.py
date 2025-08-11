# API Reference

This document provides detailed API reference for the Codegen Python SDK.

## Agent Run Logs API

This endpoint is currently in ALPHA status and is subject to change. We welcome your feedback to help improve this API.

The Agent Run Logs API allows you to retrieve detailed execution logs for agent runs, providing insights into the agent's thought process, tool usage, and execution flow.

### Endpoint

```
GET /v1/organizations/{org_id}/agent/run/{agent_run_id}/logs
```

### Authentication

This endpoint requires API token authentication. Include your token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | integer | Yes | Your organization ID |
| agent_run_id | integer | Yes | The ID of the agent run to retrieve logs for |
| skip | integer | No | Number of logs to skip for pagination (default: 0) |
| limit | integer | No | Maximum number of logs to return (default: 100, max: 100) |

### Response Structure

The endpoint returns an `AgentRunWithLogsResponse` object containing the agent run details and paginated logs.

For complete API documentation, visit [https://api.codegen.com/docs](https://api.codegen.com/docs).

