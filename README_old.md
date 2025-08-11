from codegen import Agent

# Initialize the Agent with your organization ID and API token
agent = Agent(org_id="...", token="...")

# Run an agent with a prompt
task = agent.run(prompt="Leave a review on PR #123")

# Check the initial status
print(task.status)

# Refresh the task to get updated status (tasks can take time)
task.refresh()

if task.status == "completed":
    print(task.result)  # Result often contains code, summaries, or links




Agent Run Logs API
This endpoint is currently in ALPHA status and is subject to change. We welcome your feedback to help improve this API.
The Agent Run Logs API allows you to retrieve detailed execution logs for agent runs, providing insights into the agent’s thought process, tool usage, and execution flow.
​
Endpoint

Copy

Ask AI
GET /v1/organizations/{org_id}/agent/run/{agent_run_id}/logs
​
Authentication
This endpoint requires API token authentication. Include your token in the Authorization header:

Copy

Ask AI
Authorization: Bearer YOUR_API_TOKEN
​
Parameters
Parameter	Type	Required	Description
org_id	integer	Yes	Your organization ID
agent_run_id	integer	Yes	The ID of the agent run to retrieve logs for
skip	integer	No	Number of logs to skip for pagination (default: 0)
limit	integer	No	Maximum number of logs to return (default: 100, max: 100)
​
Response Structure
The endpoint returns an AgentRunWithLogsResponse object containing the agent run details and paginated logs:

Copy

Ask AI
{
  "id": 12345,
  "organization_id": 67890,
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "web_url": "https://app.codegen.com/agent/trace/12345",
  "result": "Task completed successfully",
  "logs": [
    {
      "agent_run_id": 12345,
      "created_at": "2024-01-15T10:30:15Z",
      "tool_name": "ripgrep_search",
      "message_type": "ACTION",
      "thought": "I need to search for the user's function in the codebase",
      "observation": {
        "status": "success",
        "results": ["Found 3 matches..."]
      },
      "tool_input": {
        "query": "function getUserData",
        "file_extensions": [".js", ".ts"]
      },
      "tool_output": {
        "matches": 3,
        "files": ["src/user.js", "src/api.ts"]
      }
    }
  ],
  "total_logs": 25,
  "page": 1,
  "size": 100,
  "pages": 1
}
​
Agent Run Log Fields
Each log entry in the logs array contains the following fields:
​
Core Fields
Field	Type	Description
agent_run_id	integer	The ID of the agent run this log belongs to
created_at	string	ISO 8601 timestamp when the log entry was created
message_type	string	The type of log entry (see Log Types below)
​
Agent Reasoning Fields
Field	Type	Description
thought	string | null	The agent’s internal reasoning or thought process for this step
​
Tool Execution Fields
Field	Type	Description
tool_name	string | null	Name of the tool being executed (e.g., “ripgrep_search”, “file_write”)
tool_input	object | null	JSON object containing the parameters passed to the tool
tool_output	object | null	JSON object containing the tool’s execution results
observation	object | string | null	The agent’s observation of the tool execution results or other contextual data
​
Log Types
The message_type field indicates the type of log entry. Here are the possible values:
​
Plan Agent Types
Type	Description
ACTION	The agent is executing a tool or taking an action
PLAN_EVALUATION	The agent is evaluating or updating its plan
FINAL_ANSWER	The agent is providing its final response or conclusion
ERROR	An error occurred during execution
USER_MESSAGE	A message from the user (e.g., interruptions or additional context)
USER_GITHUB_ISSUE_COMMENT	A comment from a GitHub issue that the agent is processing
​
PR Agent Types
Type	Description
INITIAL_PR_GENERATION	The agent is generating the initial pull request
DETECT_PR_ERRORS	The agent is detecting errors in a pull request
FIX_PR_ERRORS	The agent is fixing errors found in a pull request
PR_CREATION_FAILED	Pull request creation failed
PR_EVALUATION	The agent is evaluating a pull request
​
Commit Agent Types
Type	Description
COMMIT_EVALUATION	The agent is evaluating commits
​
Link Types
Type	Description
AGENT_RUN_LINK	A link to another related agent run
​
Field Population Patterns
Different log types populate different fields:
​
ACTION Logs
Always have: tool_name, tool_input, tool_output
Often have: thought, observation
Example: Tool executions like searching code, editing files, creating PRs
​
PLAN_EVALUATION Logs
Always have: thought
May have: observation
Rarely have: Tool-related fields
Example: Agent reasoning about next steps
​
ERROR Logs
Always have: observation (containing error details)
May have: tool_name (if error occurred during tool execution)
Example: Failed tool executions or system errors
​
FINAL_ANSWER Logs
Always have: observation (containing the final response)
May have: thought
Example: Agent’s final response to the user
​
Usage Examples
​
Basic Log Retrieval

Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/organizations/67890/agent/run/12345/logs"
headers = {"Authorization": "Bearer YOUR_API_TOKEN"}

response = requests.get(url, headers=headers)
data = response.json()

print(f"Agent run status: {data['status']}")
print(f"Total logs: {data['total_logs']}")

for log in data['logs']:
    print(f"[{log['created_at']}] {log['message_type']}: {log['thought']}")
​
Filtering by Log Type

Copy

Ask AI
# Get only ACTION logs to see tool executions
action_logs = [log for log in data['logs'] if log['message_type'] == 'ACTION']

for log in action_logs:
    print(f"Tool: {log['tool_name']}")
    print(f"Input: {log['tool_input']}")
    print(f"Output: {log['tool_output']}")
    print("---")
​
Pagination Example

Copy

Ask AI
# Get logs in batches of 50
skip = 0
limit = 50
all_logs = []

while True:
    url = f"https://api.codegen.com/v1/organizations/67890/agent/run/12345/logs?skip={skip}&limit={limit}"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    all_logs.extend(data['logs'])
    
    if len(data['logs']) < limit:
        break  # No more logs
    
    skip += limit

print(f"Retrieved {len(all_logs)} total logs")
​
Debugging Failed Runs

Copy

Ask AI
# Find error logs to debug issues
error_logs = [log for log in data['logs'] if log['message_type'] == 'ERROR']

for error_log in error_logs:
    print(f"Error at {error_log['created_at']}: {error_log['observation']}")
    if error_log['tool_name']:
        print(f"Failed tool: {error_log['tool_name']}")
​
Common Use Cases
​
1. Building Monitoring Dashboards
Use the logs to create dashboards showing:
Agent execution progress
Tool usage patterns
Error rates and types
Execution timelines
​
2. Debugging Agent Behavior
Analyze logs to understand:
Why an agent made certain decisions
Where errors occurred in the execution flow
What tools were used and their results
​
3. Audit and Compliance
Track agent actions for:
Code change auditing
Compliance reporting
Security monitoring
​
4. Performance Analysis
Monitor:
Tool execution times
Common failure patterns
Agent reasoning efficiency
​
Rate Limits
60 requests per 60 seconds per API token
Rate limits are shared across all API endpoints
​
Error Responses
Status Code	Description
400	Bad Request - Invalid parameters
401	Unauthorized - Invalid or missing API token
403	Forbidden - Insufficient permissions
404	Not Found - Agent run not found
429	Too Many Requests - Rate limit exceeded
​
Feedback and Support
Since this endpoint is in ALPHA, we’d love your feedback! Please reach out through:




Get Agent Run Logs


Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/alpha/organizations/{org_id}/agent/run/{agent_run_id}/logs"

response = requests.get(url)

print(response.json())



{
  "id": 123,
  "organization_id": 123,
  "status": "<string>",
  "created_at": "<string>",
  "web_url": "<string>",
  "result": "<string>",
  "metadata": {},
  "logs": [
    {
      "agent_run_id": 123,
      "created_at": "<string>",
      "tool_name": "<string>",
      "message_type": "<string>",
      "thought": "<string>",
      "observation": {},
      "tool_input": {},
      "tool_output": {}
    }
  ],
  "total_logs": 123,
  "page": 123,
  "size": 123,
  "pages": 123
}

Get Agent Run Logs
Retrieve an agent run with its logs using pagination. This endpoint is currently in ALPHA and IS subject to change.

Returns the agent run details along with a paginated list of logs for the specified agent run. The agent run must belong to the specified organization. Logs are returned in chronological order. Uses standard pagination parameters (skip and limit) and includes pagination metadata in the response.

Rate limit: 60 requests per 60 seconds.

GET
/
v1
/
alpha
/
organizations
/
{org_id}
/
agent
/
run
/
{agent_run_id}
/
logs

Try it
Headers
​
authorization
any
Path Parameters
​
agent_run_id
integerrequired
​
org_id
integerrequired
Query Parameters
​
skip
integerdefault:0
Required range: x >= 0
​
limit
integerdefault:100
Required range: 1 <= x <= 100
Response
200

200
application/json
Successful Response

Represents an agent run in API responses

​
id
integerrequired
​
organization_id
integerrequired
​
logs
AgentRunLogResponse · object[]required
Show child attributes

​
status
string | null
​
created_at
string | null
​
web_url
string | null
​
result
string | null
​
metadata
object | null
​
total_logs
integer | null
​
page
integer | null
​
size
integer | null
​
pages
integer | null




Get Organizations


Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/organizations"

response = requests.get(url)

print(response.json())






Get Organizations
Get organizations for the authenticated user.

Returns a paginated list of all organizations that the authenticated user is a member of. Results include basic organization details such as name, ID, and membership information. Use pagination parameters to control the number of results returned.

Rate limit: 60 requests per 30 seconds.

GET
/
v1
/
organizations

Try it
Headers
​
authorization
any
Query Parameters
​
skip
integerdefault:0
Required range: x >= 0
​
limit
integerdefault:100
Required range: 1 <= x <= 100
Response
422

422
application/json
Validation Error

​
detail
ValidationError · object[]
Hide child attributes

​
loc
Location · arrayrequired
Hide child attributes

​

integer
​
msg
stringrequired
​
type
stringrequired

Get Organizations


Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/organizations"

response = requests.get(url)

print(response.json())


{
  "items": [
    {
      "id": 123,
      "name": "<string>",
      "settings": {
        "enable_pr_creation": true,
        "enable_rules_detection": true
      }
    }
  ],
  "total": 123,
  "page": 123,
  "size": 123,
  "pages": 123
}


import requests

url = "https://api.codegen.com/v1/organizations/{org_id}/agent/run/resume"

payload = {
    "agent_run_id": 123,
    "prompt": "<string>",
    "images": ["<string>"]
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print(response.json())

{
  "id": 123,
  "organization_id": 123,
  "status": "<string>",
  "created_at": "<string>",
  "web_url": "<string>",
  "result": "<string>",
  "source_type": "LOCAL",
  "github_pull_requests": [
    {
      "id": 123,
      "title": "<string>",
      "url": "<string>",
      "created_at": "<string>"
    }
  ],
  "metadata": {}
}


Resume Agent Run
Resume a paused agent run.

Resumes a paused agent run, allowing it to continue processing.

POST
/
v1
/
organizations
/
{org_id}
/
agent
/
run
/
resume

Try it
Headers
​
authorization
any
Path Parameters
​
org_id
integerrequired
Body
application/json
​
agent_run_id
integerrequired
​
prompt
stringrequired
​
images
string[] | null
List of base64 encoded data URIs representing images to be processed by the agent

Response
200

200
application/json
Successful Response

Represents an agent run in API responses

​
id
integerrequired
​
organization_id
integerrequired
​
status
string | null
​
created_at
string | null
​
web_url
string | null
​
result
string | null
​
source_type
enum<string> | null
Available options: LOCAL, SLACK, GITHUB, GITHUB_CHECK_SUITE, LINEAR, API, CHAT, JIRA 
​
github_pull_requests
GithubPullRequestResponse · object[] | null
Show child attributes

​
metadata
object | null

List Agent Runs


Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/organizations/{org_id}/agent/runs"

response = requests.get(url)

print(response.json())

{
  "items": [
    {
      "id": 123,
      "organization_id": 123,
      "status": "<string>",
      "created_at": "<string>",
      "web_url": "<string>",
      "result": "<string>",
      "source_type": "LOCAL",
      "github_pull_requests": [
        {
          "id": 123,
          "title": "<string>",
          "url": "<string>",
          "created_at": "<string>"
        }
      ],
      "metadata": {}
    }
  ],
  "total": 123,
  "page": 123,
  "size": 123,
  "pages": 123
}

List Agent Runs
List agent runs for an organization with optional user filtering.

Returns a paginated list of agent runs for the specified organization. Optionally filter by user_id to get only agent runs initiated by a specific user. Results are ordered by creation date (newest first).

Rate limit: 60 requests per 30 seconds.

GET
/
v1
/
organizations
/
{org_id}
/
agent
/
runs

Try it
Headers
​
authorization
any
Path Parameters
​
org_id
integerrequired
Query Parameters
​
user_id
integer | null
Filter by user ID who initiated the agent runs

​
source_type
enum<string> | null
Filter by source type of the agent runs

Available options: LOCAL, SLACK, GITHUB, GITHUB_CHECK_SUITE, LINEAR, API, CHAT, JIRA 
​
skip
integerdefault:0
Required range: x >= 0
​
limit
integerdefault:100
Required range: 1 <= x <= 100
Response
200

200
application/json
Successful Response

​
items
AgentRunResponse · object[]required
Show child attributes

​
total
integerrequired
​
page
integerrequired
​
size
integerrequired
​
pages
integerrequired



Get Agent Run


Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/organizations/{org_id}/agent/run/{agent_run_id}"

response = requests.get(url)

print(response.json())

200

403

404

422

429

Copy

Ask AI
{
  "id": 123,
  "organization_id": 123,
  "status": "<string>",
  "created_at": "<string>",
  "web_url": "<string>",
  "result": "<string>",
  "source_type": "LOCAL",
  "github_pull_requests": [
    {
      "id": 123,
      "title": "<string>",
      "url": "<string>",
      "created_at": "<string>"
    }
  ],
  "metadata": {}
}Get Agent Run
Retrieve the status and result of an agent run.

Returns the current status, progress, and any available results for the specified agent run. The agent run must belong to the specified organization. If the agent run is still in progress, this endpoint can be polled to check for completion.

Rate limit: 60 requests per 30 seconds.

GET
/
v1
/
organizations
/
{org_id}
/
agent
/
run
/
{agent_run_id}

Try it
Headers
​
authorization
any
Path Parameters
​
agent_run_id
integerrequired
​
org_id
integerrequired
Response
200

200
application/json
Successful Response

Represents an agent run in API responses

​
id
integerrequired
​
organization_id
integerrequired
​
status
string | null
​
created_at
string | null
​
web_url
string | null
​
result
string | null
​
source_type
enum<string> | null
Available options: LOCAL, SLACK, GITHUB, GITHUB_CHECK_SUITE, LINEAR, API, CHAT, JIRA 
​
github_pull_requests
GithubPullRequestResponse · object[] | null
Show child attributes

​
metadata
object | null

Create Agent Run


Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/organizations/{org_id}/agent/run"

payload = {
    "prompt": "<string>",
    "images": ["<string>"],
    "metadata": {}
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print(response.json())

200

402

403

404

422

429

Copy

Ask AI
{
  "id": 123,
  "organization_id": 123,
  "status": "<string>",
  "created_at": "<string>",
  "web_url": "<string>",
  "result": "<string>",
  "source_type": "LOCAL",
  "github_pull_requests": [
    {
      "id": 123,
      "title": "<string>",
      "url": "<string>",
      "created_at": "<string>"
    }
  ],
  "metadata": {}
}


Create Agent Run
Create a new agent run.

Creates and initiates a long-running agent process based on the provided prompt. The process will complete asynchronously, and the response contains the agent run ID which can be used to check the status later. The requesting user must be a member of the specified organization.

This endpoint accepts both a text prompt and an optional image file upload.

Rate limit: 10 requests per minute.

POST
/
v1
/
organizations
/
{org_id}
/
agent
/
run

Try it
Headers
​
authorization
any
Path Parameters
​
org_id
integerrequired
Body
application/json
​
prompt
stringrequired
​
images
string[] | null
List of base64 encoded data URIs representing images to be processed by the agent

​
metadata
object | null
Arbitrary JSON metadata to be stored with the agent run

Response
200

200
application/json
Successful Response

Represents an agent run in API responses

​
id
integerrequired
​
organization_id
integerrequired
​
status
string | null
​
created_at
string | null
​
web_url
string | null
​
result
string | null
​
source_type
enum<string> | null
Available options: LOCAL, SLACK, GITHUB, GITHUB_CHECK_SUITE, LINEAR, API, CHAT, JIRA 
​
github_pull_requests
GithubPullRequestResponse · object[] | null
Show child attributes

​
metadata
object | null



Get Current User Info


Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/users/me"

response = requests.get(url)

print(response.json())

200

403

422

429

Copy

Ask AI
{
  "id": 123,
  "email": "<string>",
  "github_user_id": "<string>",
  "github_username": "<string>",
  "avatar_url": "<string>",
  "full_name": "<string>"
}





Get Current User Info
Get current user information from API token.

Returns detailed information about the user associated with the provided API token. This is useful for applications that need to identify the current user from their API token.

Rate limit: 60 requests per 30 seconds.

GET
/
v1
/
users
/
me

Try it
Headers
​
authorization
any
Response
200

200
application/json
Successful Response

Represents a user in API responses

​
id
integerrequired
​
email
string | nullrequired
​
github_user_id
stringrequired
​
github_username
stringrequired
​
avatar_url
string | nullrequired
​
full_name
string | nullrequiredGet User


Copy

Ask AI
import requests

url = "https://api.codegen.com/v1/organizations/{org_id}/users/{user_id}"

response = requests.get(url)

print(response.json())

200

403

404

422

429

Copy

Ask AI
{
  "id": 123,
  "email": "<string>",
  "github_user_id": "<string>",
  "github_username": "<string>",
  "avatar_url": "<string>",
  "full_name": "<string>"
}Get User
Get details for a specific user in an organization.

Returns detailed information about a user within the specified organization. The requesting user must be a member of the organization to access this endpoint.

Rate limit: 60 requests per 30 seconds.

GET
/
v1
/
organizations
/
{org_id}
/
users
/
{user_id}

Try it
Headers
​
authorization
any
Path Parameters
​
org_id
stringrequired
​
user_id
stringrequired
Response
200

200
application/json
Successful Response

Represents a user in API responses

​
id
integerrequired
​
email
string | nullrequired
​
github_user_id
stringrequired
​
github_username
stringrequired
​
avatar_url
string | nullrequired
​
full_name
string | nullrequiredimport requests

url = "https://api.codegen.com/v1/organizations/{org_id}/users"

response = requests.get(url)

print(response.json())

200

403

422

429

Copy

Ask AI
{
  "items": [
    {
      "id": 123,
      "email": "<string>",
      "github_user_id": "<string>",
      "github_username": "<string>",
      "avatar_url": "<string>",
      "full_name": "<string>"
    }
  ],
  "total": 123,
  "page": 123,
  "size": 123,
  "pages": 123
}
Get Users
Get paginated list of users for a specific organization.

Returns a paginated list of all users associated with the specified organization. The requesting user must be a member of the organization to access this endpoint.

Rate limit: 60 requests per 30 seconds.

GET
/
v1
/
organizations
/
{org_id}
/
users

Try it
Headers
​
authorization
any
Path Parameters
​
org_id
stringrequired
Query Parameters
​
skip
integerdefault:0
Required range: x >= 0
​
limit
integerdefault:100
Required range: 1 <= x <= 100
Response
200

200
application/json
Successful Response

​
items
UserResponse · object[]required
Hide child attributes

​
id
integerrequired
​
email
string | nullrequired
​
github_user_id
stringrequired
​
github_username
stringrequired
​
avatar_url
string | nullrequired
​
full_name
string | nullrequired
​
total
integerrequired
​
page
integerrequired
​
size
integerrequired
​
pages
integerrequired



Can you create single - full comprehension codegen_sdk_api.py





UPGRADE below code for full comprehension implementation. Create full_api_test.py which tests all functions of codegen_sdk_api.py
use real 
CODEGEN_ORG_ID=323
CODEGEN_API_TOKEN=sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99



















"""


import os
import json
import time
import asyncio
import logging
import hashlib
import hmac
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Callable, AsyncGenerator, Iterator
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps, lru_cache
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

# HTTP clients
import requests
from requests import exceptions as requests_exceptions

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================


class SourceType(Enum):
    LOCAL = "LOCAL"
    SLACK = "SLACK"
    GITHUB = "GITHUB"
    GITHUB_CHECK_SUITE = "GITHUB_CHECK_SUITE"
    LINEAR = "LINEAR"
    API = "API"
    CHAT = "CHAT"
    JIRA = "JIRA"


class MessageType(Enum):
    ACTION = "ACTION"
    PLAN_EVALUATION = "PLAN_EVALUATION"
    FINAL_ANSWER = "FINAL_ANSWER"
    ERROR = "ERROR"
    USER_MESSAGE = "USER_MESSAGE"
    USER_GITHUB_ISSUE_COMMENT = "USER_GITHUB_ISSUE_COMMENT"
    INITIAL_PR_GENERATION = "INITIAL_PR_GENERATION"
    DETECT_PR_ERRORS = "DETECT_PR_ERRORS"
    FIX_PR_ERRORS = "FIX_PR_ERRORS"
    PR_CREATION_FAILED = "PR_CREATION_FAILED"
    PR_EVALUATION = "PR_EVALUATION"
    COMMIT_EVALUATION = "COMMIT_EVALUATION"
    AGENT_RUN_LINK = "AGENT_RUN_LINK"


class AgentRunStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ============================================================================
# EXCEPTIONS
# ============================================================================


class ValidationError(Exception):
    """Validation error for request parameters"""

    def __init__(
        self, message: str, field_errors: Optional[Dict[str, List[str]]] = None
    ):
        self.message = message
        self.field_errors = field_errors or {}
        super().__init__(message)


class CodegenAPIError(Exception):
    """Base exception for Codegen API errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        response_data: Optional[Dict] = None,
        request_id: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.request_id = request_id
        super().__init__(message)


class RateLimitError(CodegenAPIError):
    """Rate limiting error with retry information"""

    def __init__(self, retry_after: int = 60, request_id: Optional[str] = None):
        self.retry_after = retry_after
        super().__init__(
            f"Rate limited. Retry after {retry_after} seconds",
            429,
            request_id=request_id,
        )


class AuthenticationError(CodegenAPIError):
    """Authentication/authorization error"""

    def __init__(
        self, message: str = "Authentication failed", request_id: Optional[str] = None
    ):
        super().__init__(message, 401, request_id=request_id)


class NotFoundError(CodegenAPIError):
    """Resource not found error"""

    def __init__(
        self, message: str = "Resource not found", request_id: Optional[str] = None
    ):
        super().__init__(message, 404, request_id=request_id)


class ConflictError(CodegenAPIError):
    """Conflict error (409)"""

    def __init__(
        self, message: str = "Conflict occurred", request_id: Optional[str] = None
    ):
        super().__init__(message, 409, request_id=request_id)


class ServerError(CodegenAPIError):
    """Server-side error (5xx)"""

    def __init__(
        self,
        message: str = "Server error occurred",
        status_code: int = 500,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code, request_id=request_id)


class TimeoutError(CodegenAPIError):
    """Request timeout error"""

    def __init__(
        self, message: str = "Request timed out", request_id: Optional[str] = None
    ):
        super().__init__(message, 408, request_id=request_id)


class NetworkError(CodegenAPIError):
    """Network connectivity error"""

    def __init__(
        self, message: str = "Network error occurred", request_id: Optional[str] = None
    ):
        super().__init__(message, 0, request_id=request_id)


class WebhookError(Exception):
    """Webhook processing error"""

    pass


class BulkOperationError(Exception):
    """Bulk operation error"""

    def __init__(self, message: str, failed_items: Optional[List] = None):
        self.failed_items = failed_items or []
        super().__init__(message)


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class UserResponse:
    id: int
    email: Optional[str]
    github_user_id: str
    github_username: str
    avatar_url: Optional[str]
    full_name: Optional[str]


@dataclass
class GithubPullRequestResponse:
    id: int
    title: str
    url: str
    created_at: str


@dataclass
class AgentRunResponse:
    id: int
    organization_id: int
    status: Optional[str]
    created_at: Optional[str]
    web_url: Optional[str]
    result: Optional[str]
    source_type: Optional[SourceType]
    github_pull_requests: Optional[List[GithubPullRequestResponse]]
    metadata: Optional[Dict[str, Any]]


@dataclass
class AgentRunLogResponse:
    agent_run_id: int
    created_at: str
    message_type: str
    thought: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    observation: Optional[Union[Dict[str, Any], str]] = None


@dataclass
class OrganizationSettings:
    # Add specific settings fields as they become available
    pass


@dataclass
class OrganizationResponse:
    id: int
    name: str
    settings: OrganizationSettings


@dataclass
class PaginatedResponse:
    total: int
    page: int
    size: int
    pages: int


@dataclass
class UsersResponse(PaginatedResponse):
    items: List[UserResponse]


@dataclass
class AgentRunsResponse(PaginatedResponse):
    items: List[AgentRunResponse]


@dataclass
class OrganizationsResponse(PaginatedResponse):
    items: List[OrganizationResponse]


@dataclass
class AgentRunWithLogsResponse:
    id: int
    organization_id: int
    logs: List[AgentRunLogResponse]
    status: Optional[str]
    created_at: Optional[str]
    web_url: Optional[str]
    result: Optional[str]
    metadata: Optional[Dict[str, Any]]
    total_logs: Optional[int]
    page: Optional[int]
    size: Optional[int]
    pages: Optional[int]


@dataclass
class WebhookEvent:
    """Webhook event payload"""

    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    signature: Optional[str] = None


@dataclass
class BulkOperationResult:
    """Result of a bulk operation"""

    total_items: int
    successful_items: int
    failed_items: int
    success_rate: float
    duration_seconds: float
    errors: List[Dict[str, Any]]
    results: List[Any]


@dataclass
class RequestMetrics:
    """Metrics for a single request"""

    method: str
    endpoint: str
    status_code: int
    duration_seconds: float
    timestamp: datetime
    request_id: str
    cached: bool = False


@dataclass
class ClientStats:
    """Comprehensive client statistics"""

    uptime_seconds: float
    total_requests: int
    total_errors: int
    error_rate: float
    requests_per_minute: float
    average_response_time: float
    cache_hit_rate: float
    status_code_distribution: Dict[int, int]
    recent_requests: List[RequestMetrics]


# ============================================================================
# CONFIGURATION
# ============================================================================


@dataclass
class ClientConfig:
    """Configuration for the Codegen client"""

    # Core settings
    api_token: str = field(default_factory=lambda: os.getenv("CODEGEN_API_TOKEN", ""))
    org_id: str = field(default_factory=lambda: os.getenv("CODEGEN_ORG_ID", ""))
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "CODEGEN_BASE_URL", "https://api.codegen.com/v1"
        )
    )

    # Performance settings
    timeout: int = field(
        default_factory=lambda: int(os.getenv("CODEGEN_TIMEOUT", "30"))
    )
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("CODEGEN_MAX_RETRIES", "3"))
    )
    retry_delay: float = field(
        default_factory=lambda: float(os.getenv("CODEGEN_RETRY_DELAY", "1.0"))
    )
    retry_backoff_factor: float = field(
        default_factory=lambda: float(os.getenv("CODEGEN_RETRY_BACKOFF", "2.0"))
    )

    # Rate limiting
    rate_limit_requests_per_period: int = field(
        default_factory=lambda: int(os.getenv("CODEGEN_RATE_LIMIT_REQUESTS", "60"))
    )
    rate_limit_period_seconds: int = field(
        default_factory=lambda: int(os.getenv("CODEGEN_RATE_LIMIT_PERIOD", "60"))
    )
    rate_limit_buffer: float = 0.1

    # Caching
    enable_caching: bool = field(
        default_factory=lambda: os.getenv("CODEGEN_ENABLE_CACHING", "true").lower()
        == "true"
    )
    cache_ttl_seconds: int = field(
        default_factory=lambda: int(os.getenv("CODEGEN_CACHE_TTL", "300"))
    )
    cache_max_size: int = field(
        default_factory=lambda: int(os.getenv("CODEGEN_CACHE_MAX_SIZE", "128"))
    )

    # Features
    enable_webhooks: bool = field(
        default_factory=lambda: os.getenv("CODEGEN_ENABLE_WEBHOOKS", "true").lower()
        == "true"
    )
    enable_bulk_operations: bool = field(
        default_factory=lambda: os.getenv(
            "CODEGEN_ENABLE_BULK_OPERATIONS", "true"
        ).lower()
        == "true"
    )
    enable_streaming: bool = field(
        default_factory=lambda: os.getenv("CODEGEN_ENABLE_STREAMING", "true").lower()
        == "true"
    )
    enable_metrics: bool = field(
        default_factory=lambda: os.getenv("CODEGEN_ENABLE_METRICS", "true").lower()
        == "true"
    )

    # Bulk operations
    bulk_max_workers: int = field(
        default_factory=lambda: int(os.getenv("CODEGEN_BULK_MAX_WORKERS", "5"))
    )
    bulk_batch_size: int = field(
        default_factory=lambda: int(os.getenv("CODEGEN_BULK_BATCH_SIZE", "100"))
    )

    # Logging
    log_level: str = field(
        default_factory=lambda: os.getenv("CODEGEN_LOG_LEVEL", "INFO")
    )
    log_requests: bool = field(
        default_factory=lambda: os.getenv("CODEGEN_LOG_REQUESTS", "true").lower()
        == "true"
    )
    log_responses: bool = field(
        default_factory=lambda: os.getenv("CODEGEN_LOG_RESPONSES", "false").lower()
        == "true"
    )
    log_request_bodies: bool = field(
        default_factory=lambda: os.getenv("CODEGEN_LOG_REQUEST_BODIES", "false").lower()
        == "true"
    )

    # Webhook settings
    webhook_secret: Optional[str] = field(
        default_factory=lambda: os.getenv("CODEGEN_WEBHOOK_SECRET")
    )

    # User agent
    user_agent: str = field(default_factory=lambda: "codegen-python-client/2.0.0")

    def __post_init__(self):
        if not self.api_token:
            raise ValueError(
                "API token is required. Set CODEGEN_API_TOKEN environment variable or provide it directly."
            )

        # Set up logging
        logging.basicConfig(level=getattr(logging, self.log_level.upper()))


class ConfigPresets:
    """Predefined configuration presets"""

    @staticmethod
    def development() -> ClientConfig:
        """Development configuration with verbose logging and lower limits"""
        return ClientConfig(
            timeout=60,
            max_retries=1,
            rate_limit_requests_per_period=30,
            cache_ttl_seconds=60,
            log_level="DEBUG",
            log_requests=True,
            log_responses=True,
            log_request_bodies=True,
        )

    @staticmethod
    def production() -> ClientConfig:
        """Production configuration with optimized settings"""
        return ClientConfig(
            timeout=30,
            max_retries=3,
            rate_limit_requests_per_period=100,
            cache_ttl_seconds=300,
            log_level="INFO",
            log_requests=True,
            log_responses=False,
            log_request_bodies=False,
        )

    @staticmethod
    def high_performance() -> ClientConfig:
        """High performance configuration for heavy workloads"""
        return ClientConfig(
            timeout=45,
            max_retries=5,
            rate_limit_requests_per_period=200,
            cache_ttl_seconds=600,
            cache_max_size=256,
            bulk_max_workers=10,
            bulk_batch_size=200,
            log_level="WARNING",
        )

    @staticmethod
    def testing() -> ClientConfig:
        """Testing configuration with minimal caching and retries"""
        return ClientConfig(
            timeout=10,
            max_retries=1,
            enable_caching=False,
            rate_limit_requests_per_period=10,
            log_level="DEBUG",
        )


# ============================================================================
# UTILITY CLASSES
# ============================================================================


def retry_with_backoff(
    max_retries: int = 3, backoff_factor: float = 2.0, base_delay: float = 1.0
):
    """Decorator for retrying functions with exponential backoff"""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt == max_retries:
                        raise
                    logger.warning(f"Rate limited, waiting {e.retry_after} seconds")
                    time.sleep(e.retry_after)
                except (requests.RequestException, NetworkError) as e:
                    if attempt == max_retries:
                        raise CodegenAPIError(
                            f"Request failed after {max_retries} retries: {str(e)}", 0
                        )
                    sleep_time = base_delay * (backoff_factor**attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {sleep_time}s: {str(e)}"
                    )
                    time.sleep(sleep_time)
            return None

        return wrapper

    return decorator


class RateLimiter:
    """Thread-safe rate limiter with sliding window"""

    def __init__(self, requests_per_period: int, period_seconds: int):
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.requests = []
        self.lock = Lock()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()
            # Remove old requests
            self.requests = [
                req_time
                for req_time in self.requests
                if now - req_time < self.period_seconds
            ]

            if len(self.requests) >= self.requests_per_period:
                sleep_time = self.period_seconds - (now - self.requests[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)

            self.requests.append(now)

    def get_current_usage(self) -> Dict[str, Any]:
        """Get current rate limit usage"""
        with self.lock:
            now = time.time()
            recent_requests = [
                req_time
                for req_time in self.requests
                if now - req_time < self.period_seconds
            ]
            return {
                "current_requests": len(recent_requests),
                "max_requests": self.requests_per_period,
                "period_seconds": self.period_seconds,
                "usage_percentage": (len(recent_requests) / self.requests_per_period)
                * 100,
            }


class CacheManager:
    """Advanced in-memory cache with TTL support and statistics"""

    def __init__(self, max_size: int = 128, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            # Check if expired
            if time.time() - self._timestamps[key] > self.ttl_seconds:
                del self._cache[key]
                del self._timestamps[key]
                del self._access_counts[key]
                self._misses += 1
                return None

            self._hits += 1
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            return self._cache[key]

    def set(self, key: str, value: Any):
        """Set value in cache with TTL"""
        with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                if self._timestamps:  # Check if timestamps dict is not empty
                    oldest_key = min(self._timestamps, key=self._timestamps.get)
                    del self._cache[oldest_key]
                    del self._timestamps[oldest_key]
                    if oldest_key in self._access_counts:
                        del self._access_counts[oldest_key]

            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0)

    def clear(self):
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._access_counts.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) * 100 if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_percentage": hit_rate,
                "ttl_seconds": self.ttl_seconds,
            }


class WebhookHandler:
    """Advanced webhook event handler with signature verification and event filtering"""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key
        self.handlers: Dict[str, List[Callable]] = {}
        self.middleware: List[Callable] = []

    def register_handler(
        self, event_type: str, handler: Callable[[Dict[str, Any]], None]
    ):
        """Register a handler for specific webhook events"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Registered webhook handler for event type: {event_type}")

    def register_middleware(
        self, middleware: Callable[[Dict[str, Any]], Dict[str, Any]]
    ):
        """Register middleware to process all webhook events"""
        self.middleware.append(middleware)

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        if not self.secret_key:
            logger.warning(
                "No secret key configured for webhook signature verification"
            )
            return True

        expected_signature = hmac.new(
            self.secret_key.encode(), payload, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected_signature}", signature)

    def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None):
        """Process incoming webhook payload with middleware and handlers"""
        try:
            # Verify signature if provided
            if signature and not self.verify_signature(
                json.dumps(payload).encode(), signature
            ):
                raise WebhookError("Invalid webhook signature")

            # Apply middleware
            processed_payload = payload
            for middleware in self.middleware:
                processed_payload = middleware(processed_payload)

            event_type = processed_payload.get("event_type")
            if not event_type:
                raise WebhookError("Missing event_type in webhook payload")

            # Execute handlers
            if event_type in self.handlers:
                for handler in self.handlers[event_type]:
                    try:
                        handler(processed_payload)
                    except Exception as e:
                        logger.error(f"Handler error for {event_type}: {str(e)}")
                logger.info(f"Successfully processed webhook event: {event_type}")
            else:
                logger.warning(f"No handler registered for event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise WebhookError(f"Webhook processing failed: {str(e)}")


class BulkOperationManager:
    """Advanced manager for bulk operations with progress tracking"""

    def __init__(self, max_workers: int = 5, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size

    def execute_bulk_operation(
        self,
        operation_func: Callable,
        items: List[Any],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        *args,
        **kwargs,
    ) -> BulkOperationResult:
        """Execute a bulk operation with error handling, metrics, and progress tracking"""
        start_time = time.time()
        results = []
        errors = []
        successful_count = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(operation_func, item, *args, **kwargs): (i, item)
                for i, item in enumerate(items)
            }

            # Collect results with progress tracking
            completed = 0
            for future in as_completed(future_to_item):
                i, item = future_to_item[future]
                completed += 1

                try:
                    result = future.result()
                    results.append(result)
                    successful_count += 1
                except Exception as e:
                    error_info = {
                        "index": i,
                        "item": str(item),
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                    errors.append(error_info)
                    logger.error(f"Bulk operation failed for item {i}: {str(e)}")

                # Call progress callback
                if progress_callback:
                    progress_callback(completed, len(items))

        duration = time.time() - start_time
        success_rate = successful_count / len(items) if items else 0

        return BulkOperationResult(
            total_items=len(items),
            successful_items=successful_count,
            failed_items=len(errors),
            success_rate=success_rate,
            duration_seconds=duration,
            errors=errors,
            results=results,
        )


class MetricsCollector:
    """Advanced metrics collection and analysis"""

    def __init__(self):
        self.requests: List[RequestMetrics] = []
        self.start_time = datetime.now()
        self._lock = Lock()

    def record_request(
        self,
        method: str,
        endpoint: str,
        duration: float,
        status_code: int,
        request_id: str,
        cached: bool = False,
    ):
        """Record a request with comprehensive metrics"""
        with self._lock:
            metric = RequestMetrics(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                timestamp=datetime.now(),
                request_id=request_id,
                cached=cached,
            )
            self.requests.append(metric)

            # Keep only recent requests (last 1000)
            if len(self.requests) > 1000:
                self.requests = self.requests[-1000:]

    def get_stats(self) -> ClientStats:
        """Get comprehensive client statistics"""
        with self._lock:
            if not self.requests:
                return ClientStats(
                    uptime_seconds=0,
                    total_requests=0,
                    total_errors=0,
                    error_rate=0,
                    requests_per_minute=0,
                    average_response_time=0,
                    cache_hit_rate=0,
                    status_code_distribution={},
                    recent_requests=[],
                )

            uptime = (datetime.now() - self.start_time).total_seconds()
            total_requests = len(self.requests)
            error_requests = [r for r in self.requests if r.status_code >= 400]
            cached_requests = [r for r in self.requests if r.cached]

            avg_response_time = (
                sum(r.duration_seconds for r in self.requests) / total_requests
            )
            error_rate = (
                len(error_requests) / total_requests if total_requests > 0 else 0
            )
            cache_hit_rate = (
                len(cached_requests) / total_requests if total_requests > 0 else 0
            )
            requests_per_minute = total_requests / (uptime / 60) if uptime > 0 else 0

            # Status code distribution
            status_codes = {}
            for request in self.requests:
                status_codes[request.status_code] = (
                    status_codes.get(request.status_code, 0) + 1
                )

            return ClientStats(
                uptime_seconds=uptime,
                total_requests=total_requests,
                total_errors=len(error_requests),
                error_rate=error_rate,
                requests_per_minute=requests_per_minute,
                average_response_time=avg_response_time,
                cache_hit_rate=cache_hit_rate,
                status_code_distribution=status_codes,
                recent_requests=self.requests[-10:],
            )

    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self.requests.clear()
            self.start_time = datetime.now()


# ============================================================================
# MAIN CLIENT CLASSES
# ============================================================================


class CodegenClient:
    """Enhanced synchronous Codegen API client with comprehensive features"""

    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        self.headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "User-Agent": self.config.user_agent,
            "Content-Type": "application/json",
        }

        # Initialize components
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Rate limiting
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests_per_period,
            self.config.rate_limit_period_seconds,
        )

        # Caching
        self.cache = (
            CacheManager(
                max_size=self.config.cache_max_size,
                ttl_seconds=self.config.cache_ttl_seconds,
            )
            if self.config.enable_caching
            else None
        )

        # Webhooks
        self.webhook_handler = (
            WebhookHandler(secret_key=self.config.webhook_secret)
            if self.config.enable_webhooks
            else None
        )

        # Bulk operations
        self.bulk_manager = (
            BulkOperationManager(
                max_workers=self.config.bulk_max_workers,
                batch_size=self.config.bulk_batch_size,
            )
            if self.config.enable_bulk_operations
            else None
        )

        # Metrics
        self.metrics = MetricsCollector() if self.config.enable_metrics else None

        logger.info(f"Initialized CodegenClient with base URL: {self.config.base_url}")

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())

    def _validate_pagination(self, skip: int, limit: int):
        """Validate pagination parameters"""
        if skip < 0:
            raise ValidationError("skip must be >= 0")
        if not (1 <= limit <= 100):
            raise ValidationError("limit must be between 1 and 100")

    def _handle_response(
        self, response: requests.Response, request_id: str
    ) -> Dict[str, Any]:
        """Handle HTTP response with comprehensive error handling"""
        status_code: int = response.status_code

        if status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "60"))
            raise RateLimitError(retry_after, request_id)

        if status_code == 401:
            raise AuthenticationError(
                "Invalid API token or insufficient permissions", request_id
            )
        elif status_code == 404:
            raise NotFoundError("Requested resource not found", request_id)
        elif status_code == 409:
            raise ConflictError("Resource conflict occurred", request_id)
        elif status_code >= 500:
            raise ServerError(
                f"Server error: {status_code}",
                status_code,
                request_id,
            )
        elif not response.ok:
            try:
                error_data = response.json()
                message = error_data.get(
                    "message", f"API request failed: {status_code}"
                )
            except Exception:
                message = f"API request failed: {status_code}"
                error_data = None
            raise CodegenAPIError(
                message,
                status_code,
                error_data,
                request_id,
            )

        return response.json()

    def _make_request(
        self, method: str, endpoint: str, use_cache: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with rate limiting, caching, and metrics"""
        request_id = self._generate_request_id()

        # Rate limiting
        self.rate_limiter.wait_if_needed()

        # Check cache
        cache_key = None
        if use_cache and self.cache and method.upper() == "GET":
            cache_key = f"{method}:{endpoint}:{hash(str(kwargs))}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {endpoint} (request_id: {request_id})")
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, 0, 200, request_id, cached=True
                    )
                return cached_result

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.config.max_retries,
            backoff_factor=self.config.retry_backoff_factor,
            base_delay=self.config.retry_delay,
        )
        def _execute_request():
            start_time = time.time()
            url = f"{self.config.base_url}{endpoint}"

            if self.config.log_requests:
                logger.info(
                    f"Making {method} request to {endpoint} (request_id: {request_id})"
                )
                if self.config.log_request_bodies and "json" in kwargs:
                    logger.debug(
                        f"Request body: {json.dumps(kwargs['json'], indent=2)}"
                    )

            try:
                response = self.session.request(
                    method, url, timeout=self.config.timeout, **kwargs
                )
                duration = time.time() - start_time

                if self.config.log_requests:
                    logger.info(
                        f"Request completed in {duration:.2f}s - Status: {response.status_code} (request_id: {request_id})"
                    )

                if self.config.log_responses and response.ok:
                    logger.debug(f"Response: {response.text}")

                # Record metrics
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, response.status_code, request_id
                    )

                result = self._handle_response(response, request_id)

                # Cache successful GET requests
                if cache_key and response.ok:
                    self.cache.set(cache_key, result)

                return result

            except requests_exceptions.Timeout:
                duration = time.time() - start_time
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, 408, request_id
                    )
                raise TimeoutError(
                    f"Request timed out after {self.config.timeout}s", request_id
                )
            except requests_exceptions.ConnectionError as e:
                duration = time.time() - start_time
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, 0, request_id
                    )
                raise NetworkError(f"Network error: {str(e)}", request_id)
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Request failed after {duration:.2f}s: {str(e)} (request_id: {request_id})"
                )
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, 0, request_id
                    )
                raise

        return _execute_request()

    # ========================================================================
    # USER ENDPOINTS
    # ========================================================================

    def get_users(self, org_id: str, skip: int = 0, limit: int = 100) -> UsersResponse:
        """Get paginated list of users for a specific organization"""
        self._validate_pagination(skip, limit)

        response = self._make_request(
            "GET",
            f"/organizations/{org_id}/users",
            params={"skip": skip, "limit": limit},
            use_cache=True,
        )

        return UsersResponse(
            items=[
                UserResponse(
                    id=user.get("id", 0),
                    email=user.get("email"),
                    github_user_id=user.get("github_user_id", ""),
                    github_username=user.get("github_username", ""),
                    avatar_url=user.get("avatar_url"),
                    full_name=user.get("full_name"),
                )
                for user in response["items"]
                if user.get("id")
                and user.get("github_user_id")
                and user.get("github_username")
            ],
            total=response["total"],
            page=response["page"],
            size=response["size"],
            pages=response["pages"],
        )

    def get_user(self, org_id: str, user_id: str) -> UserResponse:
        """Get details for a specific user in an organization"""
        response = self._make_request(
            "GET", f"/organizations/{org_id}/users/{user_id}", use_cache=True
        )
        return UserResponse(
            id=response.get("id", 0),
            email=response.get("email"),
            github_user_id=response.get("github_user_id", ""),
            github_username=response.get("github_username", ""),
            avatar_url=response.get("avatar_url"),
            full_name=response.get("full_name"),
        )

    @lru_cache(maxsize=32)
    def get_user_cached(self, org_id: str, user_id: str) -> UserResponse:
        """Cached version of get_user for frequently accessed users"""
        return self.get_user(org_id, user_id)

    def get_current_user(self) -> UserResponse:
        """Get current user information from API token"""
        response = self._make_request("GET", "/users/me", use_cache=True)
        return UserResponse(
            id=response.get("id", 0),
            email=response.get("email"),
            github_user_id=response.get("github_user_id", ""),
            github_username=response.get("github_username", ""),
            avatar_url=response.get("avatar_url"),
            full_name=response.get("full_name"),
        )

    # ========================================================================
    # ORGANIZATION ENDPOINTS
    # ========================================================================

    def get_organizations(
        self, skip: int = 0, limit: int = 100
    ) -> OrganizationsResponse:
        """Get organizations for the authenticated user"""
        self._validate_pagination(skip, limit)

        response = self._make_request(
            "GET",
            "/organizations",
            params={"skip": skip, "limit": limit},
            use_cache=True,
        )

        return OrganizationsResponse(
            items=[
                OrganizationResponse(
                    id=org["id"],
                    name=org["name"],
                    settings=OrganizationSettings(),  # Populate as needed
                )
                for org in response["items"]
            ],
            total=response["total"],
            page=response["page"],
            size=response["size"],
            pages=response["pages"],
        )

    # ========================================================================
    # AGENT ENDPOINTS
    # ========================================================================

    def create_agent_run(
        self,
        org_id: int,
        prompt: str,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentRunResponse:
        """Create a new agent run"""
        # Validate inputs
        if not prompt or len(prompt.strip()) == 0:
            raise ValidationError("Prompt cannot be empty")
        if len(prompt) > 50000:  # Reasonable limit
            raise ValidationError("Prompt cannot exceed 50,000 characters")
        if images and len(images) > 10:
            raise ValidationError("Cannot include more than 10 images")

        data = {"prompt": prompt, "images": images, "metadata": metadata}

        response = self._make_request(
            "POST", f"/organizations/{org_id}/agent/run", json=data
        )

        return self._parse_agent_run_response(response)

    def get_agent_run(self, org_id: int, agent_run_id: int) -> AgentRunResponse:
        """Retrieve the status and result of an agent run"""
        response = self._make_request(
            "GET", f"/organizations/{org_id}/agent/run/{agent_run_id}", use_cache=True
        )
        return self._parse_agent_run_response(response)

    def list_agent_runs(
        self,
        org_id: int,
        user_id: Optional[int] = None,
        source_type: Optional[SourceType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> AgentRunsResponse:
        """List agent runs for an organization with optional filtering"""
        self._validate_pagination(skip, limit)

        params = {"skip": skip, "limit": limit}
        if user_id:
            params["user_id"] = user_id
        if source_type:
            params["source_type"] = source_type.value

        response = self._make_request(
            "GET", f"/organizations/{org_id}/agent/runs", params=params, use_cache=True
        )

        return AgentRunsResponse(
            items=[self._parse_agent_run_response(run) for run in response["items"]],
            total=response["total"],
            page=response["page"],
            size=response["size"],
            pages=response["pages"],
        )

    def resume_agent_run(
        self,
        org_id: int,
        agent_run_id: int,
        prompt: str,
        images: Optional[List[str]] = None,
    ) -> AgentRunResponse:
        """Resume a paused agent run"""
        if not prompt or len(prompt.strip()) == 0:
            raise ValidationError("Prompt cannot be empty")

        data = {"agent_run_id": agent_run_id, "prompt": prompt, "images": images}

        response = self._make_request(
            "POST", f"/organizations/{org_id}/agent/run/resume", json=data
        )

        return self._parse_agent_run_response(response)

    def _parse_agent_run_response(self, data: Dict[str, Any]) -> AgentRunResponse:
        """Parse agent run response data into AgentRunResponse object"""
        return AgentRunResponse(
            id=data["id"],
            organization_id=data["organization_id"],
            status=data.get("status"),
            created_at=data.get("created_at"),
            web_url=data.get("web_url"),
            result=data.get("result"),
            source_type=SourceType(data["source_type"])
            if data.get("source_type")
            else None,
            github_pull_requests=[
                GithubPullRequestResponse(
                    id=pr.get("id", 0),
                    title=pr.get("title", ""),
                    url=pr.get("url", ""),
                    created_at=pr.get("created_at", ""),
                )
                for pr in data.get("github_pull_requests", [])
                if all(key in pr for key in ["id", "title", "url", "created_at"])
            ],
            metadata=data.get("metadata"),
        )

    # ========================================================================
    # ALPHA ENDPOINTS
    # ========================================================================

    def get_agent_run_logs(
        self, org_id: int, agent_run_id: int, skip: int = 0, limit: int = 100
    ) -> AgentRunWithLogsResponse:
        """Retrieve an agent run with its logs using pagination (ALPHA)"""
        self._validate_pagination(skip, limit)

        response = self._make_request(
            "GET",
            f"/organizations/{org_id}/agent/run/{agent_run_id}/logs",
            params={"skip": skip, "limit": limit},
            use_cache=True,
        )

        return AgentRunWithLogsResponse(
            id=response["id"],
            organization_id=response["organization_id"],
            logs=[
                AgentRunLogResponse(
                    agent_run_id=log.get("agent_run_id", 0),
                    created_at=log.get("created_at", ""),
                    message_type=log.get("message_type", ""),
                    thought=log.get("thought"),
                    tool_name=log.get("tool_name"),
                    tool_input=log.get("tool_input"),
                    tool_output=log.get("tool_output"),
                    observation=log.get("observation"),
                )
                for log in response["logs"]
            ],
            status=response.get("status"),
            created_at=response.get("created_at"),
            web_url=response.get("web_url"),
            result=response.get("result"),
            metadata=response.get("metadata"),
            total_logs=response.get("total_logs"),
            page=response.get("page"),
            size=response.get("size"),
            pages=response.get("pages"),
        )

    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================

    def bulk_get_users(
        self,
        org_id: str,
        user_ids: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> BulkOperationResult:
        """Fetch multiple users concurrently"""
        if not self.bulk_manager:
            raise BulkOperationError("Bulk operations are disabled")

        return self.bulk_manager.execute_bulk_operation(
            self.get_user, user_ids, progress_callback, org_id
        )

    def bulk_create_agent_runs(
        self,
        org_id: int,
        run_configs: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> BulkOperationResult:
        """Create multiple agent runs concurrently"""
        if not self.bulk_manager:
            raise BulkOperationError("Bulk operations are disabled")

        def create_run(config):
            return self.create_agent_run(
                org_id=org_id,
                prompt=config["prompt"],
                images=config.get("images"),
                metadata=config.get("metadata"),
            )

        return self.bulk_manager.execute_bulk_operation(
            create_run, run_configs, progress_callback
        )

    def bulk_get_agent_runs(
        self,
        org_id: int,
        agent_run_ids: List[int],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> BulkOperationResult:
        """Fetch multiple agent runs concurrently"""
        if not self.bulk_manager:
            raise BulkOperationError("Bulk operations are disabled")

        return self.bulk_manager.execute_bulk_operation(
            self.get_agent_run, agent_run_ids, progress_callback, org_id
        )

    # ========================================================================
    # STREAMING METHODS
    # ========================================================================

    def stream_all_users(self, org_id: str) -> Iterator[UserResponse]:
        """Stream all users with automatic pagination"""
        if not self.config.enable_streaming:
            raise ValidationError("Streaming is disabled")

        skip = 0
        while True:
            response = self.get_users(org_id, skip=skip, limit=100)
            for user in response.items:
                yield user

            if len(response.items) < 100:
                break
            skip += 100

    def stream_all_agent_runs(
        self,
        org_id: int,
        user_id: Optional[int] = None,
        source_type: Optional[SourceType] = None,
    ) -> Iterator[AgentRunResponse]:
        """Stream all agent runs with automatic pagination"""
        if not self.config.enable_streaming:
            raise ValidationError("Streaming is disabled")

        skip = 0
        while True:
            response = self.list_agent_runs(
                org_id, user_id=user_id, source_type=source_type, skip=skip, limit=100
            )
            for run in response.items:
                yield run

            if len(response.items) < 100:
                break
            skip += 100

    def stream_all_logs(
        self, org_id: int, agent_run_id: int
    ) -> Iterator[AgentRunLogResponse]:
        """Stream all logs with automatic pagination"""
        if not self.config.enable_streaming:
            raise ValidationError("Streaming is disabled")

        skip = 0
        while True:
            response = self.get_agent_run_logs(
                org_id, agent_run_id, skip=skip, limit=100
            )
            for log in response.logs:
                yield log

            if len(response.logs) < 100:
                break
            skip += 100

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def wait_for_completion(
        self,
        org_id: int,
        agent_run_id: int,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None,
    ) -> AgentRunResponse:
        """Wait for an agent run to complete with polling"""
        start_time = time.time()

        while True:
            run = self.get_agent_run(org_id, agent_run_id)

            if run.status in [
                AgentRunStatus.COMPLETED.value,
                AgentRunStatus.FAILED.value,
                AgentRunStatus.CANCELLED.value,
            ]:
                return run

            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Agent run {agent_run_id} did not complete within {timeout} seconds"
                )

            time.sleep(poll_interval)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive client statistics"""
        stats = {
            "config": {
                "base_url": self.config.base_url,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "rate_limit_requests_per_period": self.config.rate_limit_requests_per_period,
                "caching_enabled": self.config.enable_caching,
                "webhooks_enabled": self.config.enable_webhooks,
                "bulk_operations_enabled": self.config.enable_bulk_operations,
                "streaming_enabled": self.config.enable_streaming,
                "metrics_enabled": self.config.enable_metrics,
            }
        }

        if self.metrics:
            client_stats = self.metrics.get_stats()
            stats["metrics"] = {
                "uptime_seconds": client_stats.uptime_seconds,
                "total_requests": client_stats.total_requests,
                "total_errors": client_stats.total_errors,
                "error_rate": client_stats.error_rate,
                "requests_per_minute": client_stats.requests_per_minute,
                "average_response_time": client_stats.average_response_time,
                "cache_hit_rate": client_stats.cache_hit_rate,
                "status_code_distribution": client_stats.status_code_distribution,
            }

        if self.cache:
            stats["cache"] = self.cache.get_stats()

        if hasattr(self, "rate_limiter"):
            stats["rate_limiter"] = self.rate_limiter.get_current_usage()

        return stats

    def clear_cache(self):
        """Clear all cached data"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache cleared")

    def reset_metrics(self):
        """Reset all metrics"""
        if self.metrics:
            self.metrics.reset()
            logger.info("Metrics reset")

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the API"""
        try:
            start_time = time.time()
            user = self.get_current_user()
            duration = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_seconds": duration,
                "user_id": user.id,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def close(self):
        """Clean up resources"""
        if self.session:
            self.session.close()
        logger.info("Client closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================================
# ASYNC CLIENT
# ============================================================================

if AIOHTTP_AVAILABLE:

    class AsyncCodegenClient:
        """Enhanced asynchronous Codegen API client with full feature parity"""

        def __init__(self, config: Optional[ClientConfig] = None):
            self.config = config or ClientConfig()
            self.session: Optional[aiohttp.ClientSession] = None

            # Initialize components (similar to sync client)
            self.rate_limiter = RateLimiter(
                self.config.rate_limit_requests_per_period,
                self.config.rate_limit_period_seconds,
            )

            self.cache = (
                CacheManager(
                    max_size=self.config.cache_max_size,
                    ttl_seconds=self.config.cache_ttl_seconds,
                )
                if self.config.enable_caching
                else None
            )

            self.webhook_handler = (
                WebhookHandler(secret_key=self.config.webhook_secret)
                if self.config.enable_webhooks
                else None
            )

            self.metrics = MetricsCollector() if self.config.enable_metrics else None

            logger.info(
                f"Initialized AsyncCodegenClient with base URL: {self.config.base_url}"
            )

        async def __aenter__(self):
            """Async context manager entry"""
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_token}",
                    "User-Agent": self.config.user_agent,
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            )
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            """Async context manager exit"""
            if self.session:
                await self.session.close()

        def _generate_request_id(self) -> str:
            """Generate unique request ID"""
            return str(uuid.uuid4())

        async def _make_request(
            self, method: str, endpoint: str, use_cache: bool = False, **kwargs
        ) -> Dict[str, Any]:
            """Make async HTTP request with rate limiting, caching, and metrics"""
            if not self.session:
                raise RuntimeError(
                    "Client not initialized. Use 'async with' context manager."
                )

            request_id = self._generate_request_id()

            # Rate limiting
            self.rate_limiter.wait_if_needed()

            # Check cache
            cache_key = None
            if use_cache and self.cache and method.upper() == "GET":
                cache_key = f"{method}:{endpoint}:{hash(str(kwargs))}"
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {endpoint} (request_id: {request_id})")
                    if self.metrics:
                        self.metrics.record_request(
                            method, endpoint, 0, 200, request_id, cached=True
                        )
                    return cached_result

            # Make request
            start_time = time.time()
            url = f"{self.config.base_url}{endpoint}"

            if self.config.log_requests:
                logger.info(
                    f"Making async {method} request to {endpoint} (request_id: {request_id})"
                )

            try:
                async with self.session.request(method, url, **kwargs) as response:
                    duration = time.time() - start_time

                    if self.config.log_requests:
                        logger.info(
                            f"Async request completed in {duration:.2f}s - Status: {response.status} (request_id: {request_id})"
                        )

                    # Record metrics
                    if self.metrics:
                        self.metrics.record_request(
                            method, endpoint, duration, response.status, request_id
                        )

                    # Handle response
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        raise RateLimitError(retry_after, request_id)
                    elif response.status == 401:
                        raise AuthenticationError(
                            "Invalid API token or insufficient permissions", request_id
                        )
                    elif response.status == 404:
                        raise NotFoundError("Requested resource not found", request_id)
                    elif response.status >= 500:
                        raise ServerError(
                            f"Server error: {response.status}",
                            response.status,
                            request_id,
                        )
                    elif not response.ok:
                        try:
                            error_data = await response.json()
                            message = error_data.get(
                                "message", f"API request failed: {response.status}"
                            )
                        except:
                            message = f"API request failed: {response.status}"
                        raise CodegenAPIError(
                            message,
                            response.status,
                            error_data if "error_data" in locals() else None,
                            request_id,
                        )

                    result = await response.json()

                    # Cache successful GET requests
                    if cache_key and response.ok:
                        self.cache.set(cache_key, result)

                    return result

            except asyncio.TimeoutError:
                duration = time.time() - start_time
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, 408, request_id
                    )
                raise TimeoutError(
                    f"Request timed out after {self.config.timeout}s", request_id
                )
            except aiohttp.ClientError as e:
                duration = time.time() - start_time
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, 0, request_id
                    )
                raise NetworkError(f"Network error: {str(e)}", request_id)

        # Async versions of main methods
        async def get_current_user(self) -> UserResponse:
            """Get current user information from API token"""
            response = await self._make_request("GET", "/users/me", use_cache=True)
            return UserResponse(**response)

        async def create_agent_run(
            self,
            org_id: int,
            prompt: str,
            images: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> AgentRunResponse:
            """Create a new agent run"""
            if not prompt or len(prompt.strip()) == 0:
                raise ValidationError("Prompt cannot be empty")

            data = {"prompt": prompt, "images": images, "metadata": metadata}

            response = await self._make_request(
                "POST", f"/organizations/{org_id}/agent/run", json=data
            )

            return AgentRunResponse(
                id=response["id"],
                organization_id=response["organization_id"],
                status=response.get("status"),
                created_at=response.get("created_at"),
                web_url=response.get("web_url"),
                result=response.get("result"),
                source_type=SourceType(response["source_type"])
                if response.get("source_type")
                else None,
                github_pull_requests=[
                    GithubPullRequestResponse(
                        id=pr.get("id", 0),
                        title=pr.get("title", ""),
                        url=pr.get("url", ""),
                        created_at=pr.get("created_at", ""),
                    )
                    for pr in data.get("github_pull_requests", [])
                    if all(key in pr for key in ["id", "title", "url", "created_at"])
                ],
                metadata=response.get("metadata"),
            )

        async def get_agent_run(
            self, org_id: int, agent_run_id: int
        ) -> AgentRunResponse:
            """Retrieve the status and result of an agent run"""
            response = await self._make_request(
                "GET",
                f"/organizations/{org_id}/agent/run/{agent_run_id}",
                use_cache=True,
            )

            return AgentRunResponse(
                id=response["id"],
                organization_id=response["organization_id"],
                status=response.get("status"),
                created_at=response.get("created_at"),
                web_url=response.get("web_url"),
                result=response.get("result"),
                source_type=SourceType(response["source_type"])
                if response.get("source_type")
                else None,
                github_pull_requests=[
                    GithubPullRequestResponse(
                        id=pr.get("id", 0),
                        title=pr.get("title", ""),
                        url=pr.get("url", ""),
                        created_at=pr.get("created_at", ""),
                    )
                    for pr in data.get("github_pull_requests", [])
                    if all(key in pr for key in ["id", "title", "url", "created_at"])
                ],
                metadata=response.get("metadata"),
            )

        async def stream_users(self, org_id: str) -> AsyncGenerator[UserResponse, None]:
            """Stream all users with automatic pagination"""
            skip = 0
            while True:
                response = await self._make_request(
                    "GET",
                    f"/organizations/{org_id}/users",
                    params={"skip": skip, "limit": 100},
                    use_cache=True,
                )

                users_response = UsersResponse(
                    items=[UserResponse(**user) for user in response["items"]],
                    total=response["total"],
                    page=response["page"],
                    size=response["size"],
                    pages=response["pages"],
                )

                for user in users_response.items:
                    yield user

                if len(users_response.items) < 100:
                    break
                skip += 100

        async def wait_for_completion(
            self,
            org_id: int,
            agent_run_id: int,
            poll_interval: float = 5.0,
            timeout: Optional[float] = None,
        ) -> AgentRunResponse:
            """Wait for an agent run to complete with polling"""
            start_time = time.time()

            while True:
                run = await self.get_agent_run(org_id, agent_run_id)

                if run.status in [
                    AgentRunStatus.COMPLETED.value,
                    AgentRunStatus.FAILED.value,
                    AgentRunStatus.CANCELLED.value,
                ]:
                    return run

                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError(
                        f"Agent run {agent_run_id} did not complete within {timeout} seconds"
                    )

                await asyncio.sleep(poll_interval)

        def get_stats(self) -> Dict[str, Any]:
            """Get comprehensive client statistics"""
            stats = {
                "config": {
                    "base_url": self.config.base_url,
                    "timeout": self.config.timeout,
                    "async_client": True,
                }
            }

            if self.metrics:
                client_stats = self.metrics.get_stats()
                stats["metrics"] = {
                    "uptime_seconds": client_stats.uptime_seconds,
                    "total_requests": client_stats.total_requests,
                    "total_errors": client_stats.total_errors,
                    "error_rate": client_stats.error_rate,
                    "requests_per_minute": client_stats.requests_per_minute,
                    "average_response_time": client_stats.average_response_time,
                    "cache_hit_rate": client_stats.cache_hit_rate,
                    "status_code_distribution": client_stats.status_code_distribution,
                }

            return stats

# ============================================================================
# USAGE EXAMPLES AND MAIN
# ============================================================================


def main():
    """Comprehensive example usage of the enhanced Codegen client"""

    # Example 1: Basic usage with default configuration
    print("=== Basic Usage ===")
    with CodegenClient() as client:
        try:
            # Health check
            health = client.health_check()
            print(f"Health check: {health['status']}")

            # Get current user
            user = client.get_current_user()
            print(f"Current user: {user.github_username}")

            # Get organizations
            orgs = client.get_organizations()
            if orgs.items:
                org_id = orgs.items[0].id
                print(f"Using organization: {orgs.items[0].name}")

                # Create agent run
                agent_run = client.create_agent_run(
                    org_id=org_id,
                    prompt="Help me refactor this code for better performance",
                    metadata={
                        "source": "enhanced_api_client",
                        "version": "2.0",
                        "priority": "high",
                    },
                )
                print(f"Created agent run: {agent_run.id}")

                # Wait for completion (with timeout)
                try:
                    completed_run = client.wait_for_completion(
                        org_id, agent_run.id, timeout=300
                    )
                    print(f"Agent run completed with status: {completed_run.status}")
                except TimeoutError:
                    print("Agent run did not complete within timeout")

                # Get agent run logs
                logs = client.get_agent_run_logs(org_id, agent_run.id)
                print(f"Agent run has {logs.total_logs} logs")

                # Stream all logs
                print("Streaming logs:")
                for i, log in enumerate(client.stream_all_logs(org_id, agent_run.id)):
                    print(f"  [{log.created_at}] {log.message_type}: {log.thought}")
                    if i >= 5:  # Limit output
                        print("  ... (truncated)")
                        break

        except Exception as e:
            print(f"Error: {e}")

    # Example 2: Using configuration presets
    print("\n=== Using Configuration Presets ===")
    dev_config = ConfigPresets.development()
    with CodegenClient(dev_config) as client:
        stats = client.get_stats()
        print(f"Client configuration: {stats['config']}")
        if "metrics" in stats:
            print(f"Request metrics: {stats['metrics']}")

    # Example 3: Bulk operations
    print("\n=== Bulk Operations ===")
    prod_config = ConfigPresets.production()
    with CodegenClient(prod_config) as client:
        try:
            orgs = client.get_organizations()
            if orgs.items:
                org_id = orgs.items[0].id

                # Bulk create agent runs
                run_configs = [
                    {
                        "prompt": f"Task {i}: Analyze code quality",
                        "metadata": {"task_id": i},
                    }
                    for i in range(3)
                ]

                def progress_callback(completed, total):
                    print(
                        f"Progress: {completed}/{total} ({(completed / total) * 100:.1f}%)"
                    )

                bulk_result = client.bulk_create_agent_runs(
                    org_id, run_configs, progress_callback
                )
                print(
                    f"Bulk operation: {bulk_result.successful_items}/{bulk_result.total_items} successful"
                )
                print(f"Success rate: {bulk_result.success_rate:.2%}")

        except Exception as e:
            print(f"Bulk operation error: {e}")

    # Example 4: Webhook handling
    print("\n=== Webhook Handling ===")
    client = CodegenClient()

    if client.webhook_handler:
        # Register event handlers
        @client.webhook_handler.register_handler("agent_run.completed")
        def on_agent_run_completed(payload: Dict[str, Any]):
            agent_run_id = payload["data"]["id"]
            print(f"✅ Agent run {agent_run_id} completed!")

        # Then register them
        client.webhook_handler.register_handler(
            "agent_run.completed", on_agent_run_completed
        )

        @client.webhook_handler.register_handler("agent_run.failed")
        def on_agent_run_failed(payload: Dict[str, Any]):
            agent_run_id = payload["data"]["id"]
            error = payload["data"].get("error", "Unknown error")
            print(f"❌ Agent run {agent_run_id} failed: {error}")

        # Register middleware
        def logging_middleware(payload: Dict[str, Any]) -> Dict[str, Any]:
            print(f"📨 Received webhook: {payload.get('event_type')}")
            return payload

        client.webhook_handler.register_middleware(logging_middleware)

        # Simulate webhook payloads
        webhook_payloads = [
            {
                "event_type": "agent_run.completed",
                "data": {"id": 12345, "status": "completed"},
                "timestamp": datetime.now().isoformat(),
            },
            {
                "event_type": "agent_run.failed",
                "data": {"id": 12346, "error": "Timeout occurred"},
                "timestamp": datetime.now().isoformat(),
            },
        ]

        for payload in webhook_payloads:
            try:
                client.webhook_handler.handle_webhook(payload)
            except Exception as e:
                print(f"Webhook error: {e}")

    client.close()

    # Example 5: Async usage
    if AIOHTTP_AVAILABLE:
        print("\n=== Async Usage ===")

        async def async_example():
            async with AsyncCodegenClient() as client:
                try:
                    user = await client.get_current_user()
                    print(f"Async - Current user: {user.github_username}")

                    # Stream users asynchronously
                    orgs = await client._make_request(
                        "GET", "/organizations", use_cache=True
                    )
                    if orgs.get("items"):
                        org_id = orgs["items"][0]["id"]
                        print("Async - Streaming users:")

                        count = 0
                        async for user in client.stream_users(str(org_id)):
                            print(f"  User: {user.github_username}")
                            count += 1
                            if count >= 3:  # Limit output
                                print("  ... (truncated)")
                                break

                except Exception as e:
                    print(f"Async error: {e}")

        asyncio.run(async_example())

    print("\n=== Complete! ===")


if __name__ == "__main__":
    main()
"""
