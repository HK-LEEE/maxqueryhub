# MAX Query Hub - Public API Documentation

## Overview

The MAX Query Hub Public API provides access to execute published queries without authentication. This allows external systems and applications to retrieve data through pre-defined, tested queries.

## Base URL

```
https://queryhub.yourdomain.com
```

## Authentication

**No authentication is required for public API endpoints.** Only queries with status `AVAILABLE` can be executed through the public API.

## Rate Limiting

- **Limit**: 100 requests per minute per IP address
- **Headers**: Rate limit information is included in response headers:
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Unix timestamp when the limit resets
  - `Retry-After`: Seconds to wait before retrying (only on 429 responses)

## Endpoints

### Execute Query

Execute a published query with optional parameters.

```
POST /execute/{query_id}
```

#### Parameters

- **query_id** (path, required): UUID of the query to execute

#### Request Body

```json
{
  "params": {
    "param_name": "param_value"
  }
}
```

- **params** (object, optional): Key-value pairs for query parameters

#### Response

##### Success Response (200 OK)

```json
{
  "query_id": "123e4567-e89b-12d3-a456-426614174000",
  "query_name": "Sales Report",
  "executed_at": "2024-06-25T10:30:00Z",
  "row_count": 150,
  "execution_time_ms": 245,
  "data": [
    {
      "column1": "value1",
      "column2": "value2"
    }
  ]
}
```

##### Error Responses

**404 Not Found** - Query not found or not available
```json
{
  "detail": "Query not found or not available for public access"
}
```

**400 Bad Request** - Missing required parameters
```json
{
  "detail": "Missing required parameter: start_date"
}
```

**422 Unprocessable Entity** - Invalid parameter format
```json
{
  "detail": "Invalid date format for parameter 'start_date'. Expected format: YYYY-MM-DD"
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

**500 Internal Server Error** - Query execution failed
```json
{
  "detail": "Query execution failed",
  "error": "Database connection timeout"
}
```

## Query Parameters

Queries may require parameters. The parameter requirements are defined when the query is created:

### Parameter Types

- **string**: Text values
- **integer**: Whole numbers
- **float**: Decimal numbers
- **date**: Date in YYYY-MM-DD format
- **datetime**: DateTime in ISO 8601 format
- **boolean**: true/false values

### Parameter Validation

- Required parameters must be provided
- Parameters are validated against their defined types
- Additional validation rules may apply (min/max values, patterns, etc.)

## Examples

### Example 1: Simple Query (No Parameters)

```bash
curl -X POST https://queryhub.yourdomain.com/execute/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Example 2: Query with Parameters

```bash
curl -X POST https://queryhub.yourdomain.com/execute/456e7890-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "department": "Sales"
    }
  }'
```

### Example 3: Python Client

```python
import requests
import json

# API endpoint
url = "https://queryhub.yourdomain.com/execute/123e4567-e89b-12d3-a456-426614174000"

# Parameters
payload = {
    "params": {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
}

# Execute query
response = requests.post(url, json=payload)

if response.status_code == 200:
    result = response.json()
    print(f"Query returned {result['row_count']} rows")
    for row in result['data']:
        print(row)
else:
    print(f"Error: {response.status_code} - {response.json()['detail']}")
```

### Example 4: JavaScript/Node.js Client

```javascript
const axios = require('axios');

async function executeQuery() {
    const queryId = '123e4567-e89b-12d3-a456-426614174000';
    const url = `https://queryhub.yourdomain.com/execute/${queryId}`;
    
    const payload = {
        params: {
            start_date: '2024-01-01',
            end_date: '2024-12-31'
        }
    };
    
    try {
        const response = await axios.post(url, payload);
        console.log(`Query returned ${response.data.row_count} rows`);
        console.log(response.data.data);
    } catch (error) {
        console.error(`Error: ${error.response.status} - ${error.response.data.detail}`);
    }
}

executeQuery();
```

## Best Practices

1. **Error Handling**: Always implement proper error handling for different HTTP status codes
2. **Rate Limiting**: Implement exponential backoff when receiving 429 responses
3. **Caching**: Cache query results when appropriate to reduce API calls
4. **Monitoring**: Monitor your API usage to stay within rate limits
5. **Parameters**: Validate parameters client-side before making API calls

## SDK Support

While no official SDK is provided, the API follows REST conventions and can be easily integrated with any HTTP client library.

## Support

For API support, query publishing requests, or to report issues:
- Email: support@yourdomain.com
- Documentation: https://queryhub.yourdomain.com/docs

## Changelog

### Version 1.0.0 (2024-06-25)
- Initial public API release
- UUID-based query identifiers
- Rate limiting implementation
- Parameter validation