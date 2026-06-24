# Users Service - Requirements Document

**Project**: Global Digital Bank (GDB) Microservices Architecture
**Service**: Users Service
**Version**: 1.0.0
**Last Updated**: December 24, 2024
**Status**: Active

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Functional Requirements](#functional-requirements)
3. [Non-Functional Requirements](#non-functional-requirements)
4. [API Requirements](#api-requirements)
5. [Database Requirements](#database-requirements)
6. [Security Requirements](#security-requirements)
7. [Performance Requirements](#performance-requirements)
8. [Availability & Reliability Requirements](#availability--reliability-requirements)
9. [Integration Requirements](#integration-requirements)
10. [Deployment Requirements](#deployment-requirements)

---

## 🎯 Executive Summary

The **Users Service** is a core microservice in the Global Digital Bank (GDB) ecosystem responsible for managing all user-related operations with role-based access control. It handles user creation, activation, credential verification, and inter-service communication with the Auth Service.

**Key Responsibility**: Maintain user data integrity, manage user lifecycle, provide role-based access control, and enable secure authentication via other services.

**Service Port**: 8003
**API Version**: v1
**Internal API Version**: v1
**Technology Stack**: FastAPI, PostgreSQL, asyncpg, bcrypt

---

## ✅ Functional Requirements

### FR1: User Creation

#### FR1.1: Add User
**ID**: FR1.1  
**Priority**: CRITICAL  
**Status**: ACTIVE  

**Requirement**:
The system SHALL allow creation of new users with the following validations:

**Input Parameters**:
- `username`: User name (1-255 characters)
- `login_id`: Unique login identifier (3-50 characters, alphanumeric + . - _)
- `password`: User password (minimum 8 characters)
- `role`: User role [CUSTOMER, TELLER, ADMIN] (default: CUSTOMER, optional)

**Validation Rules**:
1. Username length: 1-255 characters
2. login_id length: 3-50 characters
3. login_id format: Only alphanumeric, dots, hyphens, underscores
4. login_id must be unique (no duplicates)
5. Password minimum 8 characters
6. Role must be one of: CUSTOMER, TELLER, ADMIN
7. All fields are required except role

**Processing**:
1. Validate all input parameters
2. Check login_id uniqueness
3. Hash password using bcrypt with salt (min 10 rounds)
4. Set default role to CUSTOMER if not provided
5. Create user record with status ACTIVE
6. Record creation timestamp
7. Log audit action (CREATE)
8. Return user details with user_id

**Output**:
```json
{
  "user_id": <integer>,
  "username": "<string>",
  "login_id": "<string>",
  "role": "CUSTOMER|TELLER|ADMIN",
  "is_active": true,
  "created_at": "<ISO-8601 timestamp>",
  "message": "User created successfully"
}
```

**Error Handling**:
- User already exists → Return 409 with error code `USER_ALREADY_EXISTS`
- Invalid input → Return 400 with error code `INVALID_INPUT`
- Invalid role → Return 400 with error code `INVALID_ROLE`
- Invalid password → Return 400 with error code `INVALID_PASSWORD`
- Invalid login_id → Return 400 with error code `INVALID_LOGIN_ID`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint**:
```
POST /api/v1/users
Content-Type: application/json
```

---

### FR2: User Retrieval

#### FR2.1: View User by Login ID
**ID**: FR2.1  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL provide an endpoint to retrieve user details by login_id.

**Input Parameters**:
- `login_id`: String (path parameter)

**Processing**:
1. Validate login_id format
2. Query user from database
3. Return complete user details

**Output**:
```json
{
  "user_id": <integer>,
  "username": "<string>",
  "login_id": "<string>",
  "role": "CUSTOMER|TELLER|ADMIN",
  "is_active": <boolean>,
  "created_at": "<ISO-8601 timestamp>",
  "updated_at": "<ISO-8601 timestamp>"
}
```

**Error Handling**:
- User not found → Return 404 with error code `USER_NOT_FOUND`
- Invalid login_id → Return 422 with validation error
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint**:
```
GET /api/v1/users/{login_id}
```

---

### FR3: User Update

#### FR3.1: Edit User
**ID**: FR3.1  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL allow updating user information with specific constraints.

**Input Parameters**:
- `login_id`: String (path parameter)
- `username`: Optional new username (1-255 chars)
- `password`: Optional new password (min 8 chars)
- `role`: Optional new role (CUSTOMER, TELLER, ADMIN)

**Validation Rules**:
1. User must exist
2. If username provided: 1-255 characters
3. If password provided: minimum 8 characters
4. If role provided: must be valid role
5. At least one field must be provided for update

**Processing**:
1. Verify user exists
2. Validate provided fields
3. Update only provided fields
4. Hash password if provided
5. Update timestamp
6. Log audit action (UPDATE) with old and new data
7. Return updated user details

**Output**:
```json
{
  "user_id": <integer>,
  "username": "<string>",
  "login_id": "<string>",
  "role": "CUSTOMER|TELLER|ADMIN",
  "is_active": <boolean>,
  "created_at": "<ISO-8601 timestamp>",
  "updated_at": "<ISO-8601 timestamp>",
  "message": "User updated successfully"
}
```

**Error Handling**:
- User not found → Return 404 with error code `USER_NOT_FOUND`
- Invalid input → Return 400 with error code `INVALID_INPUT`
- Invalid role → Return 400 with error code `INVALID_ROLE`
- Invalid password → Return 400 with error code `INVALID_PASSWORD`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint**:
```
PUT /api/v1/users/{login_id}
Content-Type: application/json
```

---

### FR4: User Activation/Deactivation

#### FR4.1: Activate User
**ID**: FR4.1  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL allow activation of inactive user accounts.

**Input Parameters**:
- `login_id`: String (request body)

**Validation Rules**:
1. User must exist
2. User must be inactive
3. Cannot activate already active user

**Processing**:
1. Verify user exists
2. Check if user is already active
3. Update user status to ACTIVE
4. Update timestamp
5. Log audit action (ACTIVATE)
6. Return success response

**Output**:
```json
{
  "user_id": <integer>,
  "login_id": "<string>",
  "is_active": true,
  "message": "User activated successfully"
}
```

**Error Handling**:
- User not found → Return 404 with error code `USER_NOT_FOUND`
- User already active → Return 400 with error code `USER_ALREADY_ACTIVE`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint**:
```
POST /api/v1/users/activate
Content-Type: application/json
{
  "login_id": "<string>"
}
```

---

#### FR4.2: Inactivate User
**ID**: FR4.2  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL allow deactivation of active user accounts.

**Input Parameters**:
- `login_id`: String (request body)

**Validation Rules**:
1. User must exist
2. User must be active
3. Cannot inactivate already inactive user

**Processing**:
1. Verify user exists
2. Check if user is already inactive
3. Update user status to INACTIVE
4. Update timestamp
5. Log audit action (INACTIVATE)
6. Return success response

**Output**:
```json
{
  "user_id": <integer>,
  "login_id": "<string>",
  "is_active": false,
  "message": "User inactivated successfully"
}
```

**Error Handling**:
- User not found → Return 404 with error code `USER_NOT_FOUND`
- User already inactive → Return 400 with error code `USER_ALREADY_INACTIVE`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint**:
```
POST /api/v1/users/inactivate
Content-Type: application/json
{
  "login_id": "<string>"
}
```

---

### FR5: Credential Verification (Internal)

#### FR5.1: Verify User Credentials
**ID**: FR5.1  
**Priority**: CRITICAL  
**Status**: ACTIVE  

**Requirement**:
The system SHALL verify user credentials (login_id + password) for authentication purposes.

**Input Parameters**:
- `login_id`: String
- `password`: String (plaintext, will be hashed for comparison)

**Validation Rules**:
1. User must exist
2. User must be ACTIVE
3. Password must match stored hash
4. Both login_id and password are required

**Processing**:
1. Validate input parameters
2. Fetch user by login_id
3. Check if user exists and is active
4. Compare provided password with stored hash using bcrypt
5. Return verification result with user role and status

**Output (Success)**:
```json
{
  "is_valid": true,
  "user_id": <integer>,
  "login_id": "<string>",
  "role": "CUSTOMER|TELLER|ADMIN",
  "is_active": true
}
```

**Output (Failure)**:
```json
{
  "is_valid": false,
  "user_id": null,
  "role": null,
  "is_active": false
}
```

**Error Handling**:
- User not found → Return is_valid=false
- User inactive → Return is_valid=false
- Invalid credentials → Return is_valid=false
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint (Internal)**:
```
POST /internal/v1/users/verify
Content-Type: application/json
{
  "login_id": "<string>",
  "password": "<string>"
}
```

---

### FR6: User Status Retrieval (Internal)

#### FR6.1: Get User Status
**ID**: FR6.1  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL provide user status and role information for other services.

**Input Parameters**:
- `login_id`: String (path parameter)

**Processing**:
1. Fetch user by login_id
2. Return user status and role

**Output**:
```json
{
  "user_id": <integer>,
  "login_id": "<string>",
  "role": "CUSTOMER|TELLER|ADMIN",
  "is_active": <boolean>
}
```

**Error Handling**:
- User not found → Return 404 with error code `USER_NOT_FOUND`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint (Internal)**:
```
GET /internal/v1/users/{login_id}/status
```

---

#### FR6.2: Get User Role
**ID**: FR6.2  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL provide user role information only.

**Input Parameters**:
- `login_id`: String (path parameter)

**Processing**:
1. Fetch user by login_id
2. Return user role

**Output**:
```json
{
  "user_id": <integer>,
  "login_id": "<string>",
  "role": "CUSTOMER|TELLER|ADMIN"
}
```

**Error Handling**:
- User not found → Return 404 with error code `USER_NOT_FOUND`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint (Internal)**:
```
GET /internal/v1/users/{login_id}/role
```

---

### FR7: Role Validation (Internal)

#### FR7.1: Validate User Role
**ID**: FR7.1  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL validate if a user has a required role.

**Input Parameters**:
- `login_id`: String
- `required_role`: String (CUSTOMER, TELLER, ADMIN)

**Processing**:
1. Fetch user by login_id
2. Compare user role with required role
3. Check if user is active
4. Return validation result

**Output**:
```json
{
  "user_id": <integer>,
  "login_id": "<string>",
  "has_role": <boolean>,
  "user_role": "CUSTOMER|TELLER|ADMIN",
  "is_active": <boolean>
}
```

**Error Handling**:
- User not found → Return 404 with error code `USER_NOT_FOUND`
- Invalid role → Return 400 with error code `INVALID_ROLE`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint (Internal)**:
```
POST /internal/v1/users/validate-role
Content-Type: application/json
{
  "login_id": "<string>",
  "required_role": "CUSTOMER|TELLER|ADMIN"
}
```

---

### FR8: Bulk User Validation (Internal)

#### FR8.1: Bulk Validate Users
**ID**: FR8.1  
**Priority**: MEDIUM  
**Status**: ACTIVE  

**Requirement**:
The system SHALL validate multiple users in a single request.

**Input Parameters**:
- `login_ids`: List of login_id strings

**Processing**:
1. Validate input (non-empty list)
2. Fetch all users matching login_ids
3. Return list of user details

**Output**:
```json
{
  "valid_users": [
    {
      "user_id": <integer>,
      "login_id": "<string>",
      "role": "CUSTOMER|TELLER|ADMIN",
      "is_active": <boolean>
    }
  ],
  "invalid_login_ids": ["<string>"],
  "total_requested": <integer>,
  "total_found": <integer>
}
```

**Error Handling**:
- Empty login_ids list → Return 400 with validation error
- No users found → Return 200 with empty valid_users array
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint (Internal)**:
```
POST /internal/v1/users/bulk-validate
Content-Type: application/json
{
  "login_ids": ["<string>", "<string>", ...]
}
```

---

### FR9: Audit Trail

#### FR9.1: User Operation Audit Logging
**ID**: FR9.1  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL maintain an audit trail of all user management operations.

**Audit Events**:
1. **CREATE**: When new user is created
2. **UPDATE**: When user information is modified
3. **ACTIVATE**: When user account is activated
4. **INACTIVATE**: When user account is deactivated

**Audit Data Captured**:
- User ID
- Action type
- Old data (for updates)
- New data
- Timestamp

**Processing**:
1. Log every user creation event
2. Log every user update with old and new values
3. Log activation events
4. Log deactivation events
5. Store in database with timestamp
6. Retention: Keep audit logs indefinitely

**Output**: Audit records stored in `user_audit_log` table

**Error Handling**:
- Audit log failures should not block main operation
- Log failures to application logs
- Retry audit logging on transient failures

---

## 🔧 Non-Functional Requirements

### NFR1: Performance Requirements

**NFR1.1: Response Time**
- User creation: < 300ms (95th percentile)
- User retrieval: < 100ms (95th percentile)
- Credential verification: < 500ms (95th percentile) - includes bcrypt hashing
- Role validation: < 100ms (95th percentile)

**NFR1.2: Throughput**
- Minimum 500 requests per second (RPS)
- Minimum 250 concurrent users
- Support for 100 simultaneous credential verifications

**NFR1.3: Database Performance**
- Database queries must complete in < 50ms (except bcrypt hashing)
- bcrypt verification: < 400ms at 10 salt rounds
- Connection pool: Support 15 concurrent connections

---

### NFR2: Scalability Requirements

**NFR2.1: Horizontal Scalability**
- Service must support running multiple instances (min 2, max 5)
- Stateless design for instance independence
- Load balancing support

**NFR2.2: Data Scalability**
- Support for 100,000+ users
- Efficient indexing on login_id (unique), user_id (primary)
- Support for growth to 1 million users

---

### NFR3: Reliability Requirements

**NFR3.1: Availability**
- Service availability: 99.9% (four nines)
- Maximum planned downtime: 43 minutes/month
- Zero-downtime deployments support

**NFR3.2: Data Consistency**
- ACID compliance for all user operations
- Transaction support for multi-step operations
- Unique constraint enforcement on login_id

**NFR3.3: Error Recovery**
- Automatic retry logic for transient failures
- Exponential backoff for retries
- Graceful error handling with user-friendly messages

---

### NFR4: Maintainability Requirements

**NFR4.1: Code Quality**
- Code coverage: minimum 80%
- All public methods documented with docstrings
- Type hints for all function parameters and returns

**NFR4.2: Logging**
- Structured logging for all operations
- Log levels: DEBUG, INFO, WARNING, ERROR
- Separate log files for different log levels

**NFR4.3: Monitoring**
- Health check endpoint: `/api/v1/health`
- Metrics for request count and duration
- Error rate monitoring

---

### NFR5: Security Requirements

**NFR5.1: Authentication & Authorization**
- Service-to-service authentication via API tokens
- Password hashing using bcrypt (min 10 rounds)
- No password stored in plaintext
- No password in logs or error messages

**NFR5.2: Data Protection**
- Encryption in transit (HTTPS/TLS 1.2+)
- Password hashing: bcrypt with salt
- PII (Personally Identifiable Information) protection

**NFR5.3: Access Control**
- Role-based access control (RBAC)
- Three roles: CUSTOMER, TELLER, ADMIN
- User status validation (active/inactive)

---

## 📡 API Requirements

### API Specification

**Base URL**: `http://<host>:8003/api/v1` (Public)
**Internal URL**: `http://<host>:8003/internal/v1` (Internal)

**Content Type**: `application/json`

**Authentication**: Service token (internal APIs)

**API Version**: v1

**Versioning Strategy**: URL-based versioning

### HTTP Status Codes

| Code | Usage |
|---|---|
| 200 | Successful GET/PUT operations |
| 201 | Successful POST (user creation) |
| 400 | Bad request / validation error |
| 401 | Unauthorized / invalid credentials |
| 404 | Resource not found |
| 409 | Conflict (user already exists) |
| 500 | Internal server error |

---

## 💾 Database Requirements

### Database Platform
- **DBMS**: PostgreSQL 12+
- **Driver**: asyncpg
- **Connection Pooling**: Min 5, Max 15 connections

### Schema Requirements

**users table**:
- Primary key: user_id (SERIAL)
- Unique constraint: login_id (VARCHAR, 50)
- Role column: VARCHAR(50) - CUSTOMER, TELLER, ADMIN
- Status column: is_active (BOOLEAN)
- Timestamps: created_at, updated_at
- Password: password_hash (VARCHAR, bcrypt hashed)

**user_audit_log table**:
- Primary key: audit_id (SERIAL)
- Foreign key: user_id
- Action column: VARCHAR(50) - CREATE, UPDATE, ACTIVATE, INACTIVATE
- Data columns: old_data (JSONB), new_data (JSONB)
- Timestamp: timestamp

---

## 🔐 Security Requirements

### SEC1: Password Management
- Password hashing: bcrypt with minimum 10 salt rounds
- Minimum password length: 8 characters
- Password never stored in plaintext
- Password never logged or returned in responses
- Password comparison: constant-time to prevent timing attacks

### SEC2: User Credentials
- login_id format: 3-50 characters, alphanumeric + . - _
- login_id case-sensitive
- login_id must be unique
- Credential verification: login_id + password

### SEC3: Data Protection
- User passwords: bcrypt hashing
- User status: encrypted or protected
- Audit logs: immutable records
- GDPR/PII compliance

### SEC4: API Security
- CORS: Allow only known origins
- Rate limiting: 1000 requests/minute per IP
- API authentication: Service token validation (internal APIs)
- No sensitive data in URLs

### SEC5: Transport Security
- HTTPS/TLS 1.2+ mandatory
- Certificate pinning optional
- Secure headers: X-Content-Type-Options, X-Frame-Options

---

## ⚡ Performance SLAs

| Operation | Target (p95) | Limit (p99) |
|---|---|---|
| User Creation | 300ms | 600ms |
| User Retrieval | 100ms | 200ms |
| Credential Verification | 500ms | 1000ms |
| Role Validation | 100ms | 200ms |

### Throughput SLAs
| Metric | Requirement |
|---|---|
| Minimum RPS | 500 |
| Concurrent Users | 250+ |
| Credential Verifications | 100 simultaneous |

---

## 📈 Availability & Reliability Requirements

### Uptime Requirements
- Target Availability: 99.9%
- Acceptable Downtime: 43 minutes/month
- RTO (Recovery Time Objective): < 5 minutes
- RPO (Recovery Point Objective): < 1 minute

### Failover Requirements
- Multi-instance deployment support
- Database replication: PostgreSQL streaming replication
- Load balancer: Active-active configuration
- Health checks: Every 10 seconds

---

## 🔗 Integration Requirements

### INT1: Service-to-Service Communication

**Auth Service (Port 8004)**:
- Call `/internal/v1/users/verify` for login verification
- Call `/internal/v1/users/{login_id}/role` for role info
- Call `/internal/v1/users/validate-role` for permission checks
- Implement retry logic with exponential backoff

**Transactions Service (Port 8002)**:
- Optional: Verify user role before transaction operations
- Call role validation endpoints as needed

**Accounts Service (Port 8001)**:
- Optional: Link user_id to account operations
- May call user service for user validation

### INT2: Message Format

**Request Headers**:
```
Content-Type: application/json
Authorization: Bearer <service-token>
X-Request-ID: <uuid>
```

**Response Headers**:
```
Content-Type: application/json
X-Request-ID: <uuid>
X-RateLimit-Limit: <integer>
X-RateLimit-Remaining: <integer>
```

---

## 🚀 Deployment Requirements

### DEP1: Containerization
- Docker image: `gdb/users-service:latest`
- Base image: `python:3.9-slim`
- Multi-stage build: Separate build and runtime stages
- Health check: Built-in health endpoint

### DEP2: Orchestration
- Kubernetes: Deployment with 2+ replicas
- Auto-scaling: HPA with min 2, max 5 replicas
- Rolling updates: Zero-downtime deployment
- Service discovery: Kubernetes DNS

### DEP3: Infrastructure
- Persistent storage: PostgreSQL database
- Logging: ELK stack or CloudWatch
- Monitoring: Prometheus + Grafana
- CI/CD: GitHub Actions or Jenkins

### DEP4: Configuration Management
- Environment variables for configuration
- .env file support for local development
- Secrets management: Kubernetes Secrets or Vault
- Feature flags: Optional for gradual rollout

---

## 📋 Testing Requirements

### TEST1: Unit Tests
- Minimum coverage: 80%
- Test framework: pytest
- Async support: pytest-asyncio
- Mock external dependencies

### TEST2: Integration Tests
- Database integration tests
- Service-to-service API tests
- End-to-end scenarios
- Error path testing
- Role validation testing

### TEST3: Performance Tests
- Load testing: k6 or JMeter
- Stress testing: 2x peak load
- Endurance testing: 24-hour run
- Password hashing performance: < 500ms

---

## 🔍 Monitoring & Observability Requirements

### MON1: Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging with request IDs
- Error stack traces in DEBUG level
- No passwords or sensitive data in logs

### MON2: Metrics
- Prometheus metrics:
  - Request count by endpoint
  - Request duration histogram
  - Error count by type
  - Database connection pool stats
  - Password hashing time metrics
- Grafana dashboards for visualization

### MON3: Tracing
- Distributed tracing: OpenTelemetry (optional)
- Trace IDs: X-Trace-ID header
- Trace sampling: Configurable (10% default)

### MON4: Alerting
- Alert on service down
- Alert on high error rate (> 1%)
- Alert on slow responses (p95 > 300ms)
- Alert on database connection pool exhaustion

---

## 📝 Documentation Requirements

### DOC1: API Documentation
- OpenAPI/Swagger specification
- Interactive API explorer: Swagger UI
- Auto-generated from code comments
- Updated with each release
- Internal API reference: INTERNAL_API_REFERENCE.md

### DOC2: Developer Documentation
- Setup guide
- Architecture diagrams
- Code examples
- Troubleshooting guide
- Role-based access control explanation

### DOC3: Operational Documentation
- Deployment guide
- Configuration reference
- Monitoring setup
- Incident response procedures

---

## ✨ Additional Requirements

### REQ1: Audit Trail
- Log all user creation events
- Log all user update events
- Log all activation/deactivation events
- Retain audit logs for 7 years
- JSONB storage for flexible audit data

### REQ2: Role Management
- Three predefined roles: CUSTOMER, TELLER, ADMIN
- Role assignment during user creation
- Role updates for existing users
- Role validation on every permission check

### REQ3: Compliance
- GDPR compliance for EU users
- PII data protection
- User audit trail
- Data retention policies

### REQ4: Backward Compatibility
- Maintain API v1 compatibility
- Database schema versioning
- Migration scripts for updates

---

## 📅 Acceptance Criteria

### Definition of Done
- ✅ All unit tests passing (coverage >= 80%)
- ✅ All integration tests passing
- ✅ API documentation complete
- ✅ Code review approved
- ✅ Performance benchmarks met
- ✅ Security audit passed
- ✅ Deployed to staging environment
- ✅ Load testing passed
- ✅ Monitoring configured
- ✅ No passwords in logs

---

## 🎯 Success Metrics

| Metric | Target | Status |
|---|---|---|
| Service Availability | 99.9% | Active |
| API Response Time (p95) | < 300ms | Active |
| Error Rate | < 0.1% | Active |
| Code Coverage | >= 80% | Active |
| Deployment Frequency | Daily | Active |
| Mean Time to Recovery | < 5 min | Active |
| Password Hash Time | < 500ms | Active |

---

## 📌 Service-Specific Notes

### User Service Characteristics

1. **No Idempotency Requirement**: Unlike Accounts/Transactions services, Users Service doesn't implement idempotency keys. Each operation is processed once.

2. **Password Security**: All password operations use bcrypt with minimum 10 salt rounds. Passwords are never logged, returned, or stored in plaintext.

3. **Role-Based Design**: Built around three core roles (CUSTOMER, TELLER, ADMIN) used for permission and access control across the GDB platform.

4. **Audit Everything**: Every user operation is logged to the audit trail for compliance and debugging purposes.

5. **Minimal Internal Surface**: Only 5 internal API endpoints provided for Auth Service integration - minimal, secure, audit-ready.

---

**Document Version**: 1.0.0  
**Last Updated**: December 24, 2024  
**Next Review**: June 24, 2025  
**Owner**: GDB Architecture Team  
**Status**: APPROVED
