# API Creation Template

## Task Context
- **Repository**: {repo_url}
- **Branch**: {target_branch}
- **Task Type**: API_CREATION
- **Priority**: {priority}
- **Assigned**: {assignee}
- **Created**: {created_at}

## API Specification
{query}

## API Design

### 1. Endpoint Overview
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | /api/v1/resource | List resources | Yes |
| GET | /api/v1/resource/{id} | Get specific resource | Yes |
| POST | /api/v1/resource | Create new resource | Yes |
| PUT | /api/v1/resource/{id} | Update resource | Yes |
| DELETE | /api/v1/resource/{id} | Delete resource | Yes |

### 2. Data Models
```json
{
  "Resource": {
    "id": "string (uuid)",
    "name": "string (required, max 100)",
    "description": "string (optional, max 500)",
    "status": "enum [active, inactive, pending]",
    "created_at": "datetime (ISO 8601)",
    "updated_at": "datetime (ISO 8601)",
    "created_by": "string (user_id)"
  }
}
```

### 3. Request/Response Examples

#### Create Resource
```http
POST /api/v1/resource
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "Example Resource",
  "description": "This is an example resource",
  "status": "active"
}
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Example Resource",
  "description": "This is an example resource",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "created_by": "user123"
}
```

## Implementation Checklist

### 1. Setup and Configuration
- [ ] Set up API routing
- [ ] Configure middleware (CORS, rate limiting, etc.)
- [ ] Set up request/response serialization
- [ ] Configure authentication/authorization
- [ ] Set up input validation
- [ ] Configure error handling

### 2. Data Layer
- [ ] Design database schema
- [ ] Create migration scripts
- [ ] Implement data models/entities
- [ ] Set up database connections
- [ ] Implement repository pattern
- [ ] Add database indexes

### 3. Business Logic Layer
- [ ] Implement service classes
- [ ] Add business rule validation
- [ ] Implement CRUD operations
- [ ] Add transaction management
- [ ] Implement caching strategy
- [ ] Add logging and monitoring

### 4. API Layer
- [ ] Implement controller/handler functions
- [ ] Add request validation
- [ ] Implement response formatting
- [ ] Add pagination support
- [ ] Implement filtering and sorting
- [ ] Add API versioning

### 5. Security Implementation
- [ ] Authentication middleware
- [ ] Authorization checks
- [ ] Input sanitization
- [ ] SQL injection prevention
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] API key management

### 6. Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for API endpoints
- [ ] Authentication/authorization tests
- [ ] Input validation tests
- [ ] Error handling tests
- [ ] Performance tests

### 7. Documentation
- [ ] OpenAPI/Swagger specification
- [ ] API documentation
- [ ] Usage examples
- [ ] Authentication guide
- [ ] Error code reference
- [ ] Rate limiting documentation

## API Endpoints Detail

### GET /api/v1/resource
**Description**: Retrieve a paginated list of resources

**Query Parameters**:
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20, max: 100)
- `sort` (string, optional): Sort field (default: created_at)
- `order` (string, optional): Sort order (asc/desc, default: desc)
- `status` (string, optional): Filter by status
- `search` (string, optional): Search in name and description

**Response**:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

### GET /api/v1/resource/{id}
**Description**: Retrieve a specific resource by ID

**Path Parameters**:
- `id` (string, required): Resource UUID

**Response**: Resource object or 404 if not found

### POST /api/v1/resource
**Description**: Create a new resource

**Request Body**: Resource object (without id, timestamps)
**Response**: Created resource object with 201 status

### PUT /api/v1/resource/{id}
**Description**: Update an existing resource

**Path Parameters**:
- `id` (string, required): Resource UUID

**Request Body**: Updated resource object
**Response**: Updated resource object

### DELETE /api/v1/resource/{id}
**Description**: Delete a resource

**Path Parameters**:
- `id` (string, required): Resource UUID

**Response**: 204 No Content on success

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "name",
        "message": "Name is required"
      }
    ],
    "request_id": "req_123456789"
  }
}
```

### Error Codes
- `400 BAD_REQUEST`: Invalid request format or parameters
- `401 UNAUTHORIZED`: Authentication required or invalid
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT_FOUND`: Resource not found
- `409 CONFLICT`: Resource already exists or conflict
- `422 VALIDATION_ERROR`: Input validation failed
- `429 RATE_LIMITED`: Too many requests
- `500 INTERNAL_ERROR`: Server error

## Authentication & Authorization

### Authentication
- **Method**: Bearer Token (JWT)
- **Header**: `Authorization: Bearer {token}`
- **Token Expiry**: 1 hour (configurable)
- **Refresh**: Refresh token mechanism

### Authorization
- **Role-based**: Admin, User, ReadOnly
- **Resource-based**: Owner can modify their resources
- **Scope-based**: API scopes for different operations

## Rate Limiting
- **Default**: 100 requests per minute per user
- **Burst**: 20 requests per 10 seconds
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Caching Strategy
- **GET requests**: Cache for 5 minutes
- **Cache headers**: ETag, Last-Modified
- **Cache invalidation**: On POST, PUT, DELETE
- **CDN**: Static content caching

## Monitoring and Logging
- **Request logging**: All API requests
- **Error logging**: All 4xx and 5xx responses
- **Performance metrics**: Response times, throughput
- **Health checks**: `/health` endpoint
- **Metrics endpoint**: `/metrics` for monitoring

## Database Schema
```sql
CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL,
    
    CONSTRAINT resources_status_check CHECK (status IN ('active', 'inactive', 'pending')),
    INDEX idx_resources_status (status),
    INDEX idx_resources_created_by (created_by),
    INDEX idx_resources_created_at (created_at)
);
```

## Testing Strategy

### Unit Tests
- [ ] Service layer business logic
- [ ] Validation functions
- [ ] Utility functions
- [ ] Error handling

### Integration Tests
- [ ] Database operations
- [ ] API endpoint responses
- [ ] Authentication flows
- [ ] Authorization checks

### End-to-End Tests
- [ ] Complete CRUD workflows
- [ ] Authentication scenarios
- [ ] Error scenarios
- [ ] Performance under load

## Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] API documentation deployed
- [ ] Monitoring and alerting set up
- [ ] Rate limiting configured
- [ ] SSL/TLS certificates installed
- [ ] Load balancer configured

## Performance Targets
- **Response Time**: < 200ms for GET requests
- **Throughput**: > 1000 requests/second
- **Availability**: 99.9% uptime
- **Error Rate**: < 0.1% for 5xx errors

## Files to Create/Modify
- `src/api/routes/resource.py` - API route definitions
- `src/api/controllers/resource.py` - Request handlers
- `src/services/resource.py` - Business logic
- `src/models/resource.py` - Data models
- `src/repositories/resource.py` - Data access layer
- `tests/api/test_resource.py` - API tests
- `docs/api/resource.md` - API documentation

---
**Implementation Status**: Planning | In Progress | Testing | Review | Complete
**Last Updated**: {updated_at}
**API Version**: v1.0

