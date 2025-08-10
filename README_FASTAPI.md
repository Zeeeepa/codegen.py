# Codegen FastAPI Backend

A comprehensive FastAPI backend for managing Codegen agent runs with UI-optimized endpoints.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export CODEGEN_API_TOKEN="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
export CODEGEN_ORG_ID="323"
```

### 3. Run the Server

```bash
# Using the FastAPI backend directly
python fastapi_backend.py

# Or using uvicorn directly
uvicorn fastapi_backend:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Core Agent Run Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/create_agent_run/{mode}/{query}` | Create agent run with mode/query in path |
| `POST` | `/resume_agent_run/{agent_run_id}/{query}` | Resume agent run with additional query |
| `GET` | `/agent_runs/{agent_run_id}` | Get detailed agent run information |
| `GET` | `/agent_runs` | List agent runs with pagination |
| `DELETE` | `/agent_runs/{agent_run_id}` | Cancel/stop an agent run |

### Monitoring & Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/agent_runs/{agent_run_id}/logs` | Get paginated logs for an agent run |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/users/me` | Get current user information |

### Query Parameters

- **Pagination**: `page`, `limit`
- **Filtering**: `status`, `created_after`, `created_before`
- **Logs**: `skip`, `limit`

## 🎯 UI-Optimized Features

### Agent Run Cards
The API returns UI-optimized data structures perfect for frontend cards:

```json
{
  "id": 12345,
  "status": "running",
  "prompt": "Create a REST API endpoint",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "web_url": "https://app.codegen.com/agent/trace/12345",
  "result_preview": "Created FastAPI endpoint with proper validation...",
  "duration_seconds": 300.5,
  "metadata": {"mode": "api", "priority": "high"},
  "repo_name": "my-project",
  "branch_name": "feature/api-endpoint"
}
```

### Real-time Progress
- Detailed logs with tool execution tracking
- Status updates with timestamps
- Progress indicators for long-running tasks

## 🧪 Testing

### Run Validation Tests

```bash
python test_api_validation.py
```

This will:
- ✅ Validate SDK functionality against real API
- ✅ Test all FastAPI endpoints
- ✅ Verify integration between components
- ✅ Check error handling
- ✅ Generate comprehensive test report

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Create agent run
curl -X POST "http://localhost:8000/create_agent_run/test/hello-world" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a hello world function"}'

# List agent runs
curl "http://localhost:8000/agent_runs?limit=5"
```

## 🏗️ Architecture

### Components

1. **FastAPI Backend** (`fastapi_backend.py`)
   - RESTful API endpoints
   - Pydantic models for validation
   - CORS support for frontend integration
   - Comprehensive error handling

2. **Codegen SDK** (`codegen_api.py`)
   - Comprehensive Python client
   - Rate limiting and caching
   - Retry logic and error handling
   - Metrics and monitoring

3. **Test Suite** (`test_api_validation.py`)
   - Real API validation
   - Integration testing
   - Performance testing
   - Error scenario testing

### Data Flow

```
Frontend → FastAPI Backend → Codegen SDK → Codegen API
    ↑                                           ↓
    └─────── UI-Optimized Data ←──────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CODEGEN_API_TOKEN` | API authentication token | Required |
| `CODEGEN_ORG_ID` | Organization ID | Required |
| `CODEGEN_BASE_URL` | API base URL | `https://api.codegen.com/v1` |
| `CODEGEN_TIMEOUT` | Request timeout (seconds) | `30` |
| `CODEGEN_MAX_RETRIES` | Maximum retry attempts | `3` |

### FastAPI Configuration

The FastAPI app includes:
- CORS middleware for cross-origin requests
- Automatic OpenAPI documentation
- Request/response validation
- Error handling middleware

## 🚀 Deployment

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "fastapi_backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Security**: Configure CORS origins appropriately
2. **Authentication**: Add proper API key validation if needed
3. **Rate Limiting**: Implement rate limiting for public endpoints
4. **Monitoring**: Add logging and metrics collection
5. **Scaling**: Use multiple workers with Gunicorn

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600.5
}
```

### Metrics
The SDK includes comprehensive metrics:
- Request counts and error rates
- Response times and performance
- Cache hit rates
- Rate limiting status

## 🤝 Contributing

1. Install development dependencies
2. Run tests: `python test_api_validation.py`
3. Check API documentation: http://localhost:8000/docs
4. Submit pull requests with test coverage

## 📝 License

This project follows the same license as the main Codegen SDK.

---

**Ready to build amazing agent run management interfaces!** 🎉
