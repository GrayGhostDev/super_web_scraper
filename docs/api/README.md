```markdown
# Gray Ghost API Documentation

## Overview

The Gray Ghost API provides endpoints for profile data enrichment, search, and management. This documentation covers all available endpoints, authentication, and common usage patterns.

## Authentication

All API requests require authentication using JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your_token>
```

### Obtaining a Token

```http
POST /api/auth/token
Content-Type: application/json

{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

## Endpoints

### Profile Management

#### Search Profiles

```http
GET /api/profiles/search
```

Query Parameters:
- `q` (string): Search query
- `filters` (object): Search filters
- `page` (integer): Page number
- `limit` (integer): Results per page

#### Enrich Profile

```http
POST /api/profiles/{id}/enrich
```

Request Body:
```json
{
  "sources": ["linkedin", "hunter", "pdl"],
  "options": {
    "verify_email": true,
    "include_company": true
  }
}
```

### Data Export

#### Export Profiles

```http
POST /api/export
```

Request Body:
```json
{
  "format": "csv",
  "profiles": ["id1", "id2"],
  "fields": ["name", "email", "company"]
}
```

## Rate Limiting

- Default: 100 requests per hour
- Bulk operations: 10 requests per hour
- Export operations: 5 requests per hour

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Error description",
    "details": {}
  }
}
```

Common error codes:
- `auth_error`: Authentication failed
- `rate_limit`: Rate limit exceeded
- `validation_error`: Invalid request data
- `not_found`: Resource not found
```