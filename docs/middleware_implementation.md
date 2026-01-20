# FastAPI Middleware Implementation

## Overview

This document describes the comprehensive middleware implementation for the Gousto Recipe Meal Planner API. The middleware stack provides error handling, request/response logging, and rate limiting functionality.

## Middleware Components

### 1. Error Handler Middleware (`src/api/middleware/error_handler.py`)

Provides centralized exception handling with consistent error response formatting.

**Features:**
- Custom `APIException` class with status code and detail
- Request validation error handling (Pydantic)
- SQLAlchemy database error handling (IntegrityError, OperationalError, DatabaseError)
- General exception handling with debug mode support
- Consistent JSON error response format

**Error Response Format:**
```json
{
  "detail": "Error message",
  "status": "error",
  "error_type": "validation_error|database_error|api_error|internal_error",
  "errors": [...],  // Optional: detailed field errors
  "debug": {...}    // Optional: debug info (only in debug mode)
}
```

**Usage Example:**
```python
from src.api.middleware import APIException

# Raise custom exception in route
raise APIException(
    status_code=404,
    detail="Recipe not found",
    headers={"X-Custom": "value"}
)
```

**HTTP Status Codes:**
- `400-499`: Client errors (validation, not found, etc.)
- `409`: Database integrity constraint violations
- `422`: Request validation errors
- `500`: Internal server errors
- `503`: Database unavailable (operational errors)

### 2. Logging Middleware (`src/api/middleware/logging.py`)

Logs all HTTP requests and responses with timing information.

**Features:**
- Request method, path, and query parameters logging
- Response status code and duration tracking
- Automatic request ID generation or extraction from header
- Client IP address tracking
- User agent logging
- Error logging with exception details
- Appropriate log levels based on status code (info/warning/error)

**Request ID:**
- Auto-generated UUID if not provided
- Can be provided via `X-Request-ID` header
- Included in response headers
- Available in route handlers via `request.state.request_id`

**Log Format:**
```
INFO - Request started: GET /api/v1/recipes - request_id: abc123 - client_ip: 192.168.1.1
INFO - Request completed: GET /api/v1/recipes - Status: 200 - Duration: 45.23ms - request_id: abc123
```

**Usage in Routes:**
```python
@app.get("/api/v1/recipes")
async def get_recipes(request: Request):
    request_id = request.state.request_id
    # Use request_id for tracking
    return {"data": [...]}
```

### 3. Rate Limit Middleware (`src/api/middleware/rate_limit.py`)

In-memory rate limiter using sliding window algorithm.

**Features:**
- Configurable requests per minute (default: 60)
- Per-client IP rate limiting
- Sliding window algorithm for accurate rate limiting
- Health check endpoint exemption
- Rate limit headers in responses
- Automatic cleanup of old entries
- X-Forwarded-For and X-Real-IP header support

**Rate Limit Response:**
```json
{
  "detail": "Rate limit exceeded",
  "status": "error",
  "error_type": "rate_limit_error",
  "limit": 60,
  "window": "1 minute",
  "retry_after": 42
}
```

**Response Headers:**
- `X-RateLimit-Limit`: Maximum requests per minute
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when window resets
- `Retry-After`: Seconds to wait before retry (on 429)

**Exempt Endpoints:**
- `/` - Root health check
- `/health` - Detailed health check
- `/docs` - API documentation
- `/redoc` - ReDoc documentation
- `/openapi.json` - OpenAPI schema

**Configuration:**
```bash
# .env file
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

## Middleware Registration Order

The middleware is registered in a specific order in `src/api/main.py`:

```python
# 1. CORS - Must be first to handle preflight requests
app.add_middleware(CORSMiddleware, ...)

# 2. Rate Limiting - Before logging to avoid logging rate-limited requests
app.add_middleware(RateLimitMiddleware)

# 3. Logging - Logs all allowed requests
app.add_middleware(LoggingMiddleware)

# 4. Exception Handlers - Registered separately
register_exception_handlers(app)
```

**Why this order?**
1. CORS handles preflight requests before any other middleware
2. Rate limiting rejects excessive requests early
3. Logging captures all requests that pass rate limiting
4. Exception handlers catch errors from all middleware and routes

## File Structure

```
src/api/middleware/
├── __init__.py              # Package exports
├── error_handler.py         # Exception handlers and APIException
├── logging.py              # Request/response logging
└── rate_limit.py           # Rate limiting

tests/unit/
├── test_error_handler.py            # 20 tests
├── test_logging_middleware.py       # 18 tests
└── test_rate_limit_middleware.py    # 15 tests

tests/integration/
└── test_middleware_integration.py   # 11 tests
```

## Test Coverage

**Overall: 64 tests, all passing**

- Error Handler: 20 tests, 95% coverage
- Logging Middleware: 18 tests, 95% coverage
- Rate Limit Middleware: 15 tests, 93% coverage
- Integration Tests: 11 tests

**Test Categories:**
- Unit tests for each middleware component
- Integration tests for middleware stack
- Error handling edge cases
- Rate limiting sliding window algorithm
- Request ID generation and propagation
- Log level appropriateness

## Usage Examples

### Basic Error Handling

```python
from fastapi import APIRouter
from src.api.middleware import APIException

router = APIRouter()

@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    recipe = get_recipe_from_db(recipe_id)
    if not recipe:
        raise APIException(
            status_code=404,
            detail=f"Recipe {recipe_id} not found"
        )
    return recipe
```

### Using Request ID for Tracking

```python
from fastapi import Request

@router.post("/recipes")
async def create_recipe(request: Request, recipe: RecipeCreate):
    request_id = request.state.request_id
    logger.info(f"Creating recipe - request_id: {request_id}")
    # ... create recipe
    return {"id": recipe.id, "request_id": request_id}
```

### Checking Rate Limit Headers

```bash
# Check rate limit status
curl -I https://api.example.com/api/v1/recipes

HTTP/1.1 200 OK
X-Request-ID: abc123-def456
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642435200
```

### Rate Limit Exceeded

```bash
curl https://api.example.com/api/v1/recipes

HTTP/1.1 429 Too Many Requests
Retry-After: 42
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0

{
  "detail": "Rate limit exceeded",
  "status": "error",
  "error_type": "rate_limit_error",
  "limit": 60,
  "window": "1 minute",
  "retry_after": 42
}
```

## Configuration

All middleware can be configured via environment variables in `.env`:

```bash
# Logging
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# API Debug Mode (affects error detail exposure)
API_DEBUG=false
```

## Production Considerations

### Error Handler
- Set `API_DEBUG=false` in production to hide sensitive error details
- Monitor error logs for unhandled exceptions
- Use structured logging for error aggregation

### Logging
- Configure log rotation in production
- Use centralized logging service (e.g., ELK, CloudWatch)
- Set appropriate log levels (INFO or WARNING in production)
- Include request IDs in all log messages for tracing

### Rate Limiting
- Adjust `RATE_LIMIT_PER_MINUTE` based on capacity
- Consider using Redis for distributed rate limiting
- Monitor rate limit metrics to detect abuse
- Whitelist trusted IPs if needed
- Use CDN/WAF for DDoS protection

### Performance
- Middleware executes on every request
- Current implementation uses in-memory storage (single server only)
- For multi-server deployments, use Redis-based rate limiting
- Monitor middleware overhead with profiling

## Troubleshooting

### Rate Limiting Issues

**Problem**: Getting 429 errors unexpectedly
```bash
# Check current rate limit headers
curl -I https://api.example.com/api/v1/recipes
```

**Solution**:
- Verify `RATE_LIMIT_PER_MINUTE` configuration
- Check if behind proxy (verify X-Forwarded-For handling)
- Consider IP whitelisting for trusted clients

### Request ID Not Appearing

**Problem**: Request ID missing from logs

**Solution**:
- Verify LoggingMiddleware is registered
- Check `request.state.request_id` is accessed correctly
- Ensure middleware order is correct

### Error Responses Not Formatted

**Problem**: Errors not using standard format

**Solution**:
- Verify `register_exception_handlers(app)` is called
- Check if custom exception handlers override defaults
- Ensure raising correct exception types

## Future Enhancements

Potential improvements for production deployments:

1. **Distributed Rate Limiting**
   - Use Redis for multi-server rate limiting
   - Add rate limiting by user/API key
   - Implement different tiers (free, premium)

2. **Enhanced Logging**
   - Add request/response body logging (optional)
   - Implement correlation IDs across services
   - Add custom log fields per route

3. **Advanced Error Handling**
   - Add error tracking integration (Sentry, Rollbar)
   - Implement circuit breaker pattern
   - Add retry logic for transient errors

4. **Performance Monitoring**
   - Add middleware execution time tracking
   - Implement request tracing (OpenTelemetry)
   - Add performance metrics (Prometheus)

## Testing

Run all middleware tests:

```bash
# Unit tests only
pytest tests/unit/test_error_handler.py tests/unit/test_logging_middleware.py tests/unit/test_rate_limit_middleware.py -v

# Integration tests
pytest tests/integration/test_middleware_integration.py -v

# All middleware tests
pytest tests/unit/test_error_handler.py tests/unit/test_logging_middleware.py tests/unit/test_rate_limit_middleware.py tests/integration/test_middleware_integration.py -v

# With coverage
pytest tests/unit/test_error_handler.py tests/unit/test_logging_middleware.py tests/unit/test_rate_limit_middleware.py --cov=src/api/middleware --cov-report=html
```

## References

- FastAPI Middleware: https://fastapi.tiangolo.com/advanced/middleware/
- Starlette Middleware: https://www.starlette.io/middleware/
- Exception Handlers: https://fastapi.tiangolo.com/tutorial/handling-errors/
- Rate Limiting: https://en.wikipedia.org/wiki/Rate_limiting
