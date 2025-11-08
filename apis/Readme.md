# Attendance Management System API Documentation

## RUN Code
```
npm i
node server.js
```
## Base URL
```
http://localhost:3000/api

or

https://attendance-nine-lemon.vercel.app/api

```

## Response Format

All API responses follow this standardized format:

```json
{
  "status": {
    "code": 200,
    "success": true,
    "timestamp": "2025-11-07T10:30:00.000Z"
  },
  "data": {},
  "error": {
    "display": false,
    "code": null,
    "text": ""
  },
  "message": {
    "display": true,
    "type": "success",
    "text": "Operation successful"
  },
  "meta": {
    "requestId": "req_1699356000000_abc123xyz",
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "totalPages": 5,
      "totalRecords": 100
    }
  }
}
```

---

## Authentication APIs

### 1. Register User

**Endpoint:** `POST /auth/register`

**Description:** Register a new user in the system.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "SecurePassword123",
  "role": "employee",
  "department": "Engineering"
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Full name of the user |
| email | string | Yes | Valid email address (must be unique) |
| password | string | Yes | User password (min 6 characters recommended) |
| role | string | No | User role: "admin" or "employee" (default: "employee") |
| department | string | No | Department name |

**Success Response (201):**
```json
{
  "status": {
    "code": 201,
    "success": true,
    "timestamp": "2025-11-07T10:30:00.000Z"
  },
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "employee",
    "department": "Engineering",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "error": {
    "display": false,
    "code": null,
    "text": ""
  },
  "message": {
    "display": true,
    "type": "success",
    "text": "User registered successfully"
  },
  "meta": {
    "requestId": "req_1699356000000_abc123xyz"
  }
}
```

**Error Responses:**

**400 - Missing Fields:**
```json
{
  "status": {
    "code": 400,
    "success": false,
    "timestamp": "2025-11-07T10:30:00.000Z"
  },
  "data": null,
  "error": {
    "display": true,
    "code": "MISSING_FIELDS",
    "text": "Name, email, and password are required"
  },
  "message": {
    "display": true,
    "type": "error",
    "text": "Name, email, and password are required"
  },
  "meta": {
    "requestId": "req_1699356000000_abc123xyz"
  }
}
```

**400 - Email Already Exists:**
```json
{
  "error": {
    "display": true,
    "code": "EMAIL_EXISTS",
    "text": "Email already registered"
  }
}
```

---

### 2. Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive JWT token.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123"
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| email | string | Yes | User's email address |
| password | string | Yes | User's password |

**Success Response (200):**
```json
{
  "status": {
    "code": 200,
    "success": true,
    "timestamp": "2025-11-07T10:30:00.000Z"
  },
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "employee",
    "department": "Engineering",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "error": {
    "display": false,
    "code": null,
    "text": ""
  },
  "message": {
    "display": true,
    "type": "success",
    "text": "Login successful"
  },
  "meta": {
    "requestId": "req_1699356000000_abc123xyz"
  }
}
```

**Error Responses:**

**400 - Missing Credentials:**
```json
{
  "error": {
    "display": true,
    "code": "MISSING_CREDENTIALS",
    "text": "Email and password are required"
  }
}
```

**401 - Invalid Credentials:**
```json
{
  "status": {
    "code": 401,
    "success": false
  },
  "error": {
    "display": true,
    "code": "INVALID_CREDENTIALS",
    "text": "Invalid email or password"
  }
}
```
