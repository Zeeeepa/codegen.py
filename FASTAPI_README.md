# Codegen FastAPI Server

A comprehensive FastAPI backend for Codegen agent run management with UI-friendly endpoints.

## 🚀 Features

- **Complete Agent Run Management**: Create, retrieve, list, and resume agent runs
- **Real-time Log Streaming**: Stream agent execution logs in real-time
- **Authentication & Security**: Bearer token authentication with proper error handling
- **Auto-generated Documentation**: Swagger UI and ReDoc documentation
- **CORS Support**: Ready for web UI integration
- **Comprehensive Error Handling**: Proper HTTP status codes and error messages
- **Pydantic Models**: Full request/response validation and serialization

## 📋 Prerequisites

```bash
pip install fastapi uvicorn requests httpx
```

## 🏃‍♂️ Quick Start

### Method 1: Using the Server Runner

```bash
python run_server.py
```

### Method 2: Direct Import

```python
from codegen_api import create_app
import uvicorn

app = create_app()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Method 3: Environment Variables

```bash
export CODEGEN_ORG_ID="323"
export CODEGEN_API_TOKEN="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
python run_server.py
```

## 📖 API Documentation

Once the server is running, access the documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔗 Available Endpoints

### System Endpoints
- `GET /health` - Health check endpoint
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

### User & Organization Endpoints
- `GET /users/me` - Get current user information
- `GET /organizations` - List organizations

### Agent Run Endpoints
- `POST /agent-runs` - Create a new agent run
- `GET /agent-runs` - List agent runs with pagination and filtering
- `GET /agent-runs/{id}` - Get specific agent run
- `POST /agent-runs/{id}/resume` - Resume a paused agent run

### Agent Log Endpoints
- `GET /agent-runs/{id}/logs` - Get agent run logs with pagination
- `GET /agent-runs/{id}/logs/stream` - Stream agent run logs in real-time

## 🧪 Testing

### Run Comprehensive Tests

```bash
python test_fastapi_server.py
```

### Run Live Server Validation

```bash
python validate_server.py
```

## 📝 Example Usage

### Create Agent Run

```bash
curl -X POST "http://localhost:8000/agent-runs" \
  -H "Authorization: Bearer sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Python function to calculate fibonacci numbers",
    "metadata": {"priority": "high", "source": "api"}
  }'
```

### Get Agent Run Logs

```bash
curl -X GET "http://localhost:8000/agent-runs/12345/logs?limit=10" \
  -H "Authorization: Bearer sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
```

### Stream Logs (Server-Sent Events)

```bash
curl -X GET "http://localhost:8000/agent-runs/12345/logs/stream" \
  -H "Authorization: Bearer sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99" \
  -H "Accept: text/event-stream"
```

## 🔧 Configuration

### Environment Variables

- `CODEGEN_ORG_ID`: Your organization ID (required)
- `CODEGEN_API_TOKEN`: Your API token (required)
- `CODEGEN_BASE_URL`: API base URL (default: https://api.codegen.com/v1)

### Server Configuration

```python
from codegen_api import create_app

app = create_app(
    title="My Codegen API",
    version="2.0.0"
)
```

## 🏗️ Architecture

The FastAPI server is built on top of the existing Codegen SDK:

```
┌─────────────────┐
│   FastAPI App   │  ← Web API Layer
├─────────────────┤
│  Codegen SDK    │  ← Business Logic Layer
├─────────────────┤
│  Codegen API    │  ← External API
└─────────────────┘
```

### Key Components

1. **Pydantic Models**: Request/response validation and serialization
2. **Dependency Injection**: Authentication and client management
3. **Error Handling**: Comprehensive exception handling
4. **CORS Middleware**: Cross-origin request support
5. **Real-time Streaming**: Server-sent events for log streaming

## 🔐 Authentication

All endpoints require Bearer token authentication:

```
Authorization: Bearer YOUR_API_TOKEN
```

The server validates tokens using the Codegen API and provides proper error responses for authentication failures.

## 📊 Response Formats

### Success Response
```json
{
  "id": 12345,
  "organization_id": 323,
  "status": "ACTIVE",
  "created_at": "2024-08-10T22:03:46.337400",
  "web_url": "https://codegen.com/agent/trace/12345",
  "result": null,
  "metadata": {"source": "api"}
}
```

### Error Response
```json
{
  "error": "Authentication failed",
  "status_code": 401,
  "request_id": "abc-123-def"
}
```

## 🚀 Deployment

### Development
```bash
python run_server.py
```

### Production
```bash
uvicorn codegen_api:create_app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install fastapi uvicorn requests httpx
EXPOSE 8000
CMD ["python", "run_server.py"]
```

## 🧩 Integration Examples

### JavaScript/TypeScript
```javascript
const response = await fetch('http://localhost:8000/agent-runs', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: 'Create a React component',
    metadata: { source: 'web_ui' }
  })
});
```

### Python Client
```python
import requests

headers = {'Authorization': 'Bearer YOUR_TOKEN'}
response = requests.post(
    'http://localhost:8000/agent-runs',
    json={'prompt': 'Create a Python function'},
    headers=headers
)
```

## 🔍 Monitoring & Debugging

### Health Check
```bash
curl http://localhost:8000/health
```

### Server Logs
The server provides detailed logging for all requests and operations.

### Error Tracking
All errors include request IDs for tracking and debugging.

## 🤝 Contributing

1. The FastAPI implementation is built on top of the existing SDK
2. All endpoints maintain backward compatibility
3. Follow the existing error handling patterns
4. Add comprehensive tests for new endpoints

## 📄 License

Same as the main Codegen SDK license.

---

**🎉 Your FastAPI server is ready! Visit http://localhost:8000/docs to explore the API.**
