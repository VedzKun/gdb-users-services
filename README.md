# Users Service - Global Digital Bank (GDB)

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Requirements](#requirements)
4. [Features](#features)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [API Endpoints](#api-endpoints)
8. [Database Schema](#database-schema)
9. [Data Models](#data-models)
10. [Error Handling](#error-handling)
11. [Testing](#testing)
12. [Deployment](#deployment)

---

## 📌 Overview

The **Users Service** is a microservice within the Global Digital Bank (GDB) ecosystem, responsible for managing all user-related operations with role-based access control. It provides core user management functionalities including:

- **User Management**: Create, edit, view, and manage users
- **Role-Based Access Control (RBAC)**: Assign roles (CUSTOMER, TELLER, ADMIN)
- **User Activation/Deactivation**: Manage user account status
- **Credential Verification**: Verify user login credentials
- **Role Validation**: Validate user permissions and roles
- **Audit Trail**: Track all user management operations
- **Inter-service Communication**: Verify credentials for other services

**Service Port**: `8003`
**API Prefix**: `/api/v1`
**Internal Prefix**: `/internal/v1`

---

## 🏗️ Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT / API GATEWAY                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌────▼────┐  ┌───▼──────┐
   │ Accounts │  │  Trx    │  │  Users   │
   │ Service  │  │ Service │  │ Service  │
   │ (8001)   │  │ (8002)  │  │ (8003)   │
   └────┬────┘  └────┬────┘  └───┬──────┘
        │            │            │
   ┌────▼────────────▼────────────▼────┐
   │      PostgreSQL Database           │
   │  ┌─────────────────────────────┐   │
   │  │  accounts_db                │   │
   │  │  transactions_db            │   │
   │  │  users_db                   │   │
   │  └─────────────────────────────┘   │
   └────────────────────────────────────┘
```

### Microservice Architecture - Users Service

```
┌──────────────────────────────────────────────────────────────────┐
│                      USERS SERVICE (8003)                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 🌐 API Layer (FastAPI)                                      │  │
│  │  PUBLIC ENDPOINTS (User Management):                        │  │
│  │  ├─ POST   /api/v1/users                (Add User)         │  │
│  │  ├─ GET    /api/v1/users/{login_id}     (View User)        │  │
│  │  ├─ PUT    /api/v1/users/{login_id}     (Edit User)        │  │
│  │  ├─ POST   /api/v1/users/activate       (Activate)         │  │
│  │  ├─ POST   /api/v1/users/inactivate     (Inactivate)       │  │
│  │  └─ GET    /api/v1/health               (Health Check)    │  │
│  │                                                              │  │
│  │  INTERNAL ENDPOINTS (Service-to-Service):                  │  │
│  │  ├─ POST   /internal/v1/users/verify            (Verify)   │  │
│  │  ├─ GET    /internal/v1/users/{login_id}/status (Status)   │  │
│  │  ├─ GET    /internal/v1/users/{login_id}/role   (Role)     │  │
│  │  ├─ POST   /internal/v1/users/validate-role              │  │
│  │  └─ POST   /internal/v1/users/bulk-validate              │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────▼────────────────────────────────┐  │
│  │ 🔧 Service Layer (Business Logic)                           │  │
│  │  ├─ AddUserService                                          │  │
│  │  ├─ EditUserService                                         │  │
│  │  ├─ ViewUserService                                         │  │
│  │  ├─ ActivateUserService                                     │  │
│  │  ├─ InactivateUserService                                   │  │
│  │  ├─ InternalUserService (internal operations)              │  │
│  │  └─ AuditService (operation logging)                        │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 📦 Repository Layer (Data Access)                           │  │
│  │  └─ UserRepository                                          │  │
│  │     ├─ create_user()                                        │  │
│  │     ├─ get_user_by_login_id()                               │  │
│  │     ├─ get_user_by_id()                                     │  │
│  │     ├─ update_user()                                        │  │
│  │     ├─ activate_user()                                      │  │
│  │     ├─ inactivate_user()                                    │  │
│  │     └─ get_all_users()                                      │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 🔐 Utilities & Validators                                   │  │
│  │  ├─ role_validator.py           (Role validation)          │  │
│  │  ├─ user_input_validator.py     (Input validation)         │  │
│  │  ├─ user_existence_validator.py (Existence check)          │  │
│  │  └─ user_status_validator.py    (Status validation)        │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 💾 Database Layer (asyncpg)                                 │  │
│  │  ├─ Connection Management                                   │  │
│  │  ├─ Query Execution                                         │  │
│  │  └─ Async Transaction Support                               │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PostgreSQL DB    │
                    │  (users_db)        │
                    └────────────────────┘
```

### Layered Architecture Details

#### 1. **API Layer** (`app/api/`)
- **Public Routes** (User Management):
  - `add_user_routes.py`: Create new users
  - `edit_user_routes.py`: Update user information
  - `view_user_routes.py`: Retrieve user details
  - `activate_user_routes.py`: Activate user accounts
  - `inactivate_user_routes.py`: Deactivate user accounts
  
- **Internal Routes**:
  - `internal_user_routes.py`: Service-to-service endpoints for Auth Service
  
- Framework: FastAPI with dependency injection
- Middleware: CORS, error handling

#### 2. **Service Layer** (`app/services/`)
- **AddUserService**: User creation with validation
- **EditUserService**: User information updates
- **ViewUserService**: User retrieval and listing
- **ActivateUserService**: Activate user accounts
- **InactivateUserService**: Deactivate user accounts
- **InternalUserService**: Inter-service operations (verify, validate)
- **AuditService**: Audit trail logging

#### 3. **Repository Layer** (`app/repositories/`)
- **UserRepository**: Data access abstraction
- Raw SQL with asyncpg (no ORM)
- Implements CRUD operations
- Type-safe database interactions

#### 4. **Data Models** (`app/models/`)
- Pydantic v2 models for request/response validation
- Type safety with Field descriptors
- Custom validators for business rules
- Enums for role definitions

#### 5. **Exception Layer** (`app/exceptions/`)
- Custom exception hierarchy
- Error codes for external communication
- Detailed error messages

#### 6. **Utilities** (`app/utils/`)
- **role_validator.py**: Role validation (CUSTOMER, TELLER, ADMIN)
- **user_input_validator.py**: Input validation (username, password, login_id)
- **user_existence_validator.py**: Check user existence
- **user_status_validator.py**: Validate user status (active/inactive)

#### 7. **Configuration** (`app/config/`)
- **settings.py**: Environment-based configuration
- Support for development/staging/production
- Database connection parameters
- CORS settings

#### 8. **Database** (`app/database/`)
- **connection.py**: asyncpg connection management
- Lifecycle management (init/close)
- Connection pooling

---

## 📦 Requirements

### System Requirements
- **Python**: 3.9+
- **PostgreSQL**: 12.0+
- **asyncpg**: For async PostgreSQL driver
- **FastAPI**: 0.104.1+
- **uvicorn**: ASGI server

### Python Dependencies

```
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3

# Database
asyncpg==0.29.0
sqlalchemy==2.0.23

# Security & Encryption
bcrypt==4.1.1
python-jose[cryptography]==3.3.0
cryptography==41.0.7
jwt==1.3.1

# HTTP Client (Inter-service communication)
httpx==0.25.1
aiohttp==3.9.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3
uuid6==2025.0.1

# Logging
python-json-logger==2.0.7

# Development & Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.12.1
flake8==6.1.0
isort==5.13.2
mypy==1.7.1

# Environment Management
python-dotenv==1.0.0
```

### Database Requirements
- PostgreSQL database with the following tables:
  - `users`: Main user table
  - `user_audit_log`: Audit trail for user operations

---

## ✨ Features

### 1. User Management
- **Add Users**: Create new users with unique login_id
  - Assign roles: CUSTOMER, TELLER, ADMIN
  - Default role: CUSTOMER
  - Password hashing: bcrypt

- **Edit Users**: Modify user information
  - Update username, password, role
  - Only specific fields can be updated
  
- **View Users**: Retrieve user information
  - Get user details by login_id
  - Get all users (with filters)
  - User details include: user_id, username, login_id, role, status, created_at

- **Activate/Deactivate**: Manage user account status
  - Activate inactive users
  - Deactivate active users
  - Status validation

### 2. Role-Based Access Control (RBAC)
- **Three Role Types**:
  - **CUSTOMER**: End user for banking services
  - **TELLER**: Bank employee for teller operations
  - **ADMIN**: Administrator with full permissions

- **Role Management**:
  - Assign roles during user creation
  - Update roles for existing users
  - Validate user roles

### 3. Security
- **Password Security**:
  - Minimum 8 characters
  - Hashed using bcrypt
  - Never stored in plaintext
  - Validated during creation and update

- **Login Validation**:
  - login_id: 3-50 characters, alphanumeric + . - _
  - Unique constraint on login_id
  - Case-sensitive

- **Credential Verification**:
  - Verify login_id + password combination
  - Used by Auth Service for login

### 4. User Status Management
- **Status Tracking**:
  - Active/Inactive states
  - Active by default on creation
  - Can be toggled via API

- **Status Validation**:
  - Prevent operations on inactive users
  - Track status changes in audit log

### 5. Audit Trail
- **Audit Logging**:
  - Track all user creation events
  - Log all user updates
  - Record activation/deactivation
  - Timestamp all operations
  - Store audit data in database

### 6. Inter-service Communication
- **Internal APIs**:
  - Verify user credentials (Auth Service)
  - Get user status and role (Auth Service)
  - Validate user roles (Other services)
  - Bulk user validation (Other services)

---

## 🚀 Installation & Setup

### 1. Prerequisites
```bash
# Verify Python version
python --version  # Should be 3.9+

# Verify PostgreSQL
psql --version  # Should be 12+
```

### 2. Clone & Navigate
```bash
cd users_service
```

### 3. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup Database
```bash
# Initialize database
python setup_db.py

# Or manually:
# 1. Create PostgreSQL database: gdb_users_db
# 2. Run: migrations/001_add_role_column.sql (if needed)
```

### 6. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings:
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=gdb_users_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
LOG_LEVEL=INFO
```

### 7. Run Application
```bash
# Development
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Production
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8003 app.main:app
```

### 8. Verify Service
```bash
# Health check
curl http://localhost:8003/api/v1/health

# API docs
open http://localhost:8003/api/v1/docs
```

---

## ⚙️ Configuration

### Environment Variables

```env
# Application
SERVICE_NAME=GDB-User-Management-Service
TITLE=User Management Service
SERVICE_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8003

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=gdb_users_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/users_service.log

# Inter-service URLs
AUTH_SERVICE_URL=http://localhost:8004
TRANSACTIONS_SERVICE_URL=http://localhost:8002
ACCOUNTS_SERVICE_URL=http://localhost:8001

# API
API_PREFIX=/api/v1

# CORS
CORS_ORIGINS=["http://localhost", "http://localhost:3000"]
CORS_CREDENTIALS=True
CORS_METHODS=["*"]
CORS_HEADERS=["*"]
```

---

## 📡 API Endpoints

### Public API Endpoints

#### Add User
```http
POST /api/v1/users
Content-Type: application/json

{
  "username": "John Doe",
  "login_id": "john.doe",
  "password": "SecurePassword123!",
  "role": "CUSTOMER"
}
```

**Response (201 Created)**:
```json
{
  "user_id": 1,
  "username": "John Doe",
  "login_id": "john.doe",
  "role": "CUSTOMER",
  "is_active": true,
  "created_at": "2024-12-24T10:00:00",
  "message": "User created successfully"
}
```

#### View User
```http
GET /api/v1/users/john.doe
```

**Response (200 OK)**:
```json
{
  "user_id": 1,
  "username": "John Doe",
  "login_id": "john.doe",
  "role": "CUSTOMER",
  "is_active": true,
  "created_at": "2024-12-24T10:00:00",
  "updated_at": "2024-12-24T10:00:00"
}
```

#### Edit User
```http
PUT /api/v1/users/john.doe
Content-Type: application/json

{
  "username": "Jane Doe",
  "role": "TELLER"
}
```

#### Activate User
```http
POST /api/v1/users/activate
Content-Type: application/json

{
  "login_id": "john.doe"
}
```

#### Inactivate User
```http
POST /api/v1/users/inactivate
Content-Type: application/json

{
  "login_id": "john.doe"
}
```

### Internal API Endpoints (Service-to-Service)

#### Verify User Credentials
```http
POST /internal/v1/users/verify
Content-Type: application/json

{
  "login_id": "john.doe",
  "password": "SecurePassword123!"
}
```

**Response**:
```json
{
  "is_valid": true,
  "user_id": 1,
  "role": "CUSTOMER",
  "is_active": true
}
```

#### Get User Status
```http
GET /internal/v1/users/john.doe/status
```

**Response**:
```json
{
  "user_id": 1,
  "login_id": "john.doe",
  "role": "CUSTOMER",
  "is_active": true
}
```

#### Get User Role
```http
GET /internal/v1/users/john.doe/role
```

**Response**:
```json
{
  "user_id": 1,
  "login_id": "john.doe",
  "role": "CUSTOMER"
}
```

#### Validate User Role
```http
POST /internal/v1/users/validate-role
Content-Type: application/json

{
  "login_id": "john.doe",
  "required_role": "CUSTOMER"
}
```

#### Bulk Validate Users
```http
POST /internal/v1/users/bulk-validate
Content-Type: application/json

{
  "login_ids": ["john.doe", "jane.smith", "admin.user"]
}
```

---

## 💾 Database Schema

### Users Table
```sql
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(255) NOT NULL,
  login_id VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,  -- CUSTOMER, TELLER, ADMIN
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### User Audit Log Table
```sql
CREATE TABLE user_audit_log (
  audit_id SERIAL PRIMARY KEY,
  user_id INT,
  action VARCHAR(50) NOT NULL,  -- CREATE, UPDATE, ACTIVATE, INACTIVATE
  old_data JSONB,
  new_data JSONB,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## 🔍 Data Models

### Request Models

#### AddUserRequest
```python
{
  "username": str (1-255 chars),
  "login_id": str (3-50 chars, alphanumeric + . - _),
  "password": str (min 8 chars),
  "role": "CUSTOMER" | "TELLER" | "ADMIN" (optional, default: CUSTOMER)
}
```

#### EditUserRequest
```python
{
  "username": str (optional),
  "password": str (optional, min 8 chars),
  "role": "CUSTOMER" | "TELLER" | "ADMIN" (optional)
}
```

### Response Models

#### AddUserResponse
```python
{
  "user_id": int,
  "username": str,
  "login_id": str,
  "role": str,
  "is_active": bool,
  "created_at": datetime,
  "message": str
}
```

#### ViewUserResponse
```python
{
  "user_id": int,
  "username": str,
  "login_id": str,
  "role": str,
  "is_active": bool,
  "created_at": datetime,
  "updated_at": datetime
}
```

---

## ⚠️ Error Handling

### Error Response Format
```json
{
  "status_code": 400,
  "detail": "Error message"
}
```

### Common Error Codes

| Error Code | Status | Meaning |
|---|---|---|
| `USER_ALREADY_EXISTS` | 409 | User with login_id exists |
| `USER_NOT_FOUND` | 404 | User does not exist |
| `INVALID_INPUT` | 400 | Input validation failed |
| `INVALID_ROLE` | 400 | Invalid role provided |
| `INVALID_PASSWORD` | 400 | Password too weak |
| `INVALID_LOGIN_ID` | 400 | Invalid login_id format |
| `USER_INACTIVE` | 400 | User is not active |
| `USER_ALREADY_ACTIVE` | 400 | User already active |
| `USER_ALREADY_INACTIVE` | 400 | User already inactive |
| `INVALID_CREDENTIALS` | 401 | Login_id or password incorrect |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_user_management.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Test Files
- **test_user_management.py**: User CRUD operations
- **test_internal_apis.py**: Internal API testing
- **test_request_models.py**: Request validation
- **test_response_models.py**: Response formatting
- **test_role_validation.py**: Role-based testing
- **test_verify_endpoint_fix_new.py**: API endpoint verification

### Test Coverage
- ✅ 150+ automated tests
- ✅ Unit tests for all layers
- ✅ Integration tests
- ✅ Error scenario testing
- ✅ Role-based access control testing

---

## 📦 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: users-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: users-service
  template:
    metadata:
      labels:
        app: users-service
    spec:
      containers:
      - name: users-service
        image: gdb/users-service:latest
        ports:
        - containerPort: 8003
        env:
        - name: DATABASE_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8003
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Environment-specific Deployment

**Development**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

**Staging**:
```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8003 app.main:app
```

**Production**:
```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8003 \
  --access-logfile - --error-logfile - app.main:app
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8003/api/v1/docs
- **ReDoc**: http://localhost:8003/api/v1/redoc
- **Health Check**: http://localhost:8003/api/v1/health
- **Database Migrations**: `migrations/`
- **Configuration Template**: `.env.example`
- **Internal API Reference**: `INTERNAL_API_REFERENCE.md`

---

## 🤝 Contributing

### Code Style
- Use Black for formatting: `black app/`
- Use isort for imports: `isort app/`
- Run linting: `flake8 app/`

### Before Committing
```bash
black app/
isort app/
flake8 app/
pytest tests/
```

---

## 📝 License

Copyright © 2024 Global Digital Bank (GDB). All rights reserved.

---

## 📞 Support

For issues, questions, or support:
- Create an issue in the repository
- Contact: support@gdb.local
- Documentation: Check root directory for additional docs

---

**Last Updated**: December 24, 2024
**Version**: 1.0.0
**Maintainer**: GDB Architecture Team
