# 🎯 SYSTEM ARCHITECTURE OVERVIEW

## User Management System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND PORTAL                              │
│  (Login page → Dashboard → Junction Control)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    JWT Token │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI BACKEND                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ API ROUTES (app/routers/user_router.py)                │   │
│  ├──────────────────────────────────────────────────────── │   │
│  │ • Authentication (login, refresh, logout)              │   │
│  │ • User Management (create, list, update)               │   │
│  │ • Junction Access Control (grant, revoke, bulk)        │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                              ↓                       │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │ MIDDLEWARE           │  │ ACCESS CONTROL       │             │
│  │ (access_control.py)  │  │ (access_helpers.py)  │             │
│  ├──────────────────────┤  ├──────────────────────┤             │
│  │ • JWT Verification   │  │ • Access Checking    │             │
│  │ • Token Parsing      │  │ • Junction Filtering │             │
│  │ • Role Extraction    │  │ • Helper Functions   │             │
│  └──────────────────────┘  └──────────────────────┘             │
│           ↓                              ↓                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ SERVICES (user_management_service.py)                 │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ • User Authentication                                 │    │
│  │ • Password Hashing (Bcrypt)                           │    │
│  │ • JWT Token Generation                                │    │
│  │ • Junction Access Management                          │    │
│  │ • Session Management                                  │    │
│  │ • Audit Logging                                       │    │
│  └────────────────────────────────────────────────────────┘    │
│           ↓                                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ DATABASE (Supabase)                                   │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### 1. Login Flow
```
User enters credentials
         ↓
POST /api/v1/users/login
         ↓
UserManagementService.authenticate_user()
         ↓
Check if user exists & active
         ↓
Verify password with bcrypt
         ↓
Create JWT tokens (access + refresh)
         ↓
Create session record in DB
         ↓
Return tokens to client
         ↓
Client stores tokens (localStorage/cookies)
```

### 2. Access Control Flow
```
User makes request to protected endpoint
         ↓
Include JWT token in Authorization header
         ↓
GET /api/v1/traffic/junctions/1
Authorization: Bearer <token>
         ↓
Middleware: get_current_user()
         ↓
Verify JWT signature & expiration
         ↓
Extract user_id, role, junction_ids
         ↓
Does user have ADMIN role?
    ├─ YES → Allow access ✅
    └─ NO → Check junction_ids list
             ├─ Junction in list? → Allow access ✅
             └─ Not in list? → 403 Forbidden ❌
```

### 3. Admin Grant Access Flow
```
Admin requests to grant access
         ↓
POST /api/v1/users/1/junctions/1/grant-access
Authorization: Bearer <admin_token>
         ↓
Middleware: require_admin()
         ↓
Is user ADMIN? 
    ├─ No → 403 Forbidden ❌
    └─ Yes → Continue
         ↓
UserManagementService.grant_junction_access()
         ↓
Check/Create user_junctions record
         ↓
Set access_level (OPERATOR or OBSERVER)
         ↓
Log audit entry
         ↓
Return success ✅
         ↓
Next login: User's JWT will include junction_id
```

---

## Database Schema Diagram

```
┌─────────────────────────────────┐
│          USERS                  │
├─────────────────────────────────┤
│ id (PK)                         │
│ username (UNIQUE)               │
│ password_hash                   │
│ full_name                       │
│ email                           │
│ role (ADMIN|OPERATOR|OBSERVER)  │
│ is_active                       │
│ last_login                      │
│ created_at                      │
│ updated_at                      │
└─────────────────────────────────┘
         ↑        │
         │        │
      1  │        │ n
         │        ↓
┌─────────────────────────────────┐
│      USER_JUNCTIONS             │
├─────────────────────────────────┤
│ id (PK)                         │
│ user_id (FK) ────┐              │
│ junction_id (FK) │              │
│ access_level     │              │
│ granted_at       │              │
│ granted_by       │              │
└─────────────────────────────────┘
         │        ↑
         │        │
      n  │        │ 1
         ↓        │
┌─────────────────────────────────┐
│    TRAFFIC_JUNCTIONS            │
├─────────────────────────────────┤
│ id (PK)                         │
│ junction_name                   │
│ location                        │
│ latitude                        │
│ longitude                       │
│ status                          │
│ created_at                      │
│ updated_at                      │
└─────────────────────────────────┘

┌──────────────────────────────────┐
│     USER_SESSIONS                │
├──────────────────────────────────┤
│ id (PK)                          │
│ user_id (FK)                     │
│ session_token                    │
│ refresh_token                    │
│ expires_at                       │
│ last_used                        │
│ is_active                        │
│ created_at                       │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     USER_AUDIT_LOGS              │
├──────────────────────────────────┤
│ id (PK)                          │
│ user_id (FK)                     │
│ junction_id (FK)                 │
│ action                           │
│ resource                         │
│ details (JSONB)                  │
│ ip_address                       │
│ timestamp                        │
└──────────────────────────────────┘
```

---

## Request Response Examples

### Login Request
```http
POST /api/v1/users/login HTTP/1.1
Content-Type: application/json

{
  "username": "operator_1",
  "password": "SecurePass123!"
}
```

### Login Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "operator_1",
    "full_name": "Operator One",
    "role": "OPERATOR"
  }
}
```

### Access Junction Request
```http
GET /api/v1/traffic/junctions/1 HTTP/1.1
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Access Junction Response (Success)
```json
{
  "id": 1,
  "junction_name": "Main Street & 5th Ave",
  "location": "Downtown",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "status": "active"
}
```

### Access Unauthorized Junction Response (Failure)
```json
{
  "detail": "You do not have access to junction 5"
}
```
HTTP Status: 403 Forbidden

---

## Token Structure

### Access Token (Expires in 30 minutes)
```json
{
  "sub": "1",                          // user_id
  "username": "operator_1",
  "role": "OPERATOR",
  "junction_ids": [1, 2, 3],          // Assigned junctions
  "exp": 1705502400,                   // Expiration time
  "type": "access"
}
```

### Refresh Token (Expires in 7 days)
```json
{
  "sub": "1",
  "exp": 1706107200,
  "type": "refresh"
}
```

---

## Role-Based Permissions Matrix

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Operation    │    ADMIN     │   OPERATOR   │   OBSERVER   │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Create User  │      ✅      │      ❌      │      ❌      │
│ Delete User  │      ✅      │      ❌      │      ❌      │
│ Grant Access │      ✅      │      ❌      │      ❌      │
│ View Logs    │      ✅      │      ❌      │      ❌      │
│ Control Ctrl │   All / ✅   │  Assigned ✅ │      ❌      │
│ View Data    │   All / ✅   │  Assigned ✅ │  Assigned ✅ │
│ Change Pwd   │      ✅      │      ❌      │      ❌      │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## Integration Pattern

### Simple 3-Line Integration
```python
# BEFORE (no auth)
@app.get("/api/v1/traffic/junctions/{junction_id}")
async def get_junction(junction_id: int):
    return await db_service.get_junction(junction_id)

# AFTER (with auth)
from app.middleware.access_control import get_current_user
from app.utils.access_helpers import check_access

@app.get("/api/v1/traffic/junctions/{junction_id}")
async def get_junction(
    junction_id: int,
    user: dict = Depends(get_current_user),
):
    if not check_access(user, junction_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return await db_service.get_junction(junction_id)
```

---

## Security Layers

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: HTTPS/TLS                                      │
│ Encrypt data in transit                                 │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: JWT VERIFICATION                               │
│ Verify token signature and expiration                   │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: ROLE CHECKING                                  │
│ Verify user has required role (ADMIN, OPERATOR, etc)   │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 4: JUNCTION ACCESS CONTROL                        │
│ Verify user has access to specific junction             │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 5: AUDIT LOGGING                                  │
│ Log all actions with user, IP, and timestamp            │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 6: DATABASE ENCRYPTION                            │
│ Supabase encrypts data at rest                          │
└─────────────────────────────────────────────────────────┘
```

---

## File Organization

```
flextraff-backend/
│
├── app/
│   ├── services/
│   │   ├── user_management_service.py  ← Business logic
│   │   └── database_service.py
│   │
│   ├── routers/
│   │   ├── user_router.py              ← API endpoints
│   │   └── (other routers)
│   │
│   ├── middleware/
│   │   └── access_control.py           ← Security layer
│   │
│   ├── utils/
│   │   └── access_helpers.py           ← Helper functions
│   │
│   ├── models/
│   │   └── user_models.py              ← Data models
│   │
│   └── config.py                       ← Configuration
│
├── migrations/
│   └── 001_add_user_management.sql     ← Database schema
│
├── tests/
│   └── test_user_management.py         ← Test suite
│
├── docs/
│   ├── USER_MANAGEMENT.md
│   ├── INTEGRATION_GUIDE.md
│   ├── SETUP_INSTRUCTIONS.md
│   ├── QUICK_REFERENCE.md
│   └── (other docs)
│
├── main.py                             ← FastAPI app
├── START_HERE.md                       ← Start here!
├── DELIVERABLES.md
├── IMPLEMENTATION_CHECKLIST.md
└── .env                                ← Environment variables
```

---

## Complete Workflow Example

```
    ADMIN
      │
      ├─ Creates Operator User
      │  POST /api/v1/users
      │  {"username":"op1","password":"...","role":"OPERATOR"}
      │
      ├─ Grants Access to Junctions
      │  POST /api/v1/users/1/junctions/bulk-grant
      │  {"junction_ids":[1,2,3],"access_level":"OPERATOR"}
      │
      └─ Notifies Operator of Credentials
         │
         └─ OPERATOR
            │
            ├─ Logs In
            │  POST /api/v1/users/login
            │  Receives: access_token, refresh_token
            │
            ├─ Views Assigned Junctions
            │  GET /api/v1/traffic/junctions
            │  Only sees: [1, 2, 3]
            │
            ├─ Controls Junction 1
            │  POST /api/v1/traffic/junctions/1/control
            │  ✅ Allowed (assigned)
            │
            ├─ Tries to Access Junction 5
            │  GET /api/v1/traffic/junctions/5
            │  ❌ 403 Forbidden (not assigned)
            │
            ├─ Refreshes Expired Token
            │  POST /api/v1/users/refresh-token
            │  Receives: new access_token
            │
            └─ Logs Out
               POST /api/v1/users/logout
               Session terminated ✅
```

---

## Performance Optimizations

```
✅ Indexed columns for fast lookups
   - users.username (login queries)
   - user_junctions.user_id (access checking)
   - user_junctions.junction_id (filtering)
   - user_sessions.refresh_token (token refresh)

✅ JWT token carries junction_ids
   - No database query needed to check access
   - Reduces load on database

✅ Middleware validates tokens
   - Prevents unnecessary database queries
   - Blocks unauthorized requests early

✅ Bulk operations
   - Single operation for multiple grants/revokes
   - Reduces API calls and database transactions

✅ Session tracking
   - Efficient logout mechanism
   - Token revocation support
```

---

## Scalability Features

```
✅ Horizontal scaling ready
   - Stateless JWT tokens
   - No server-side session storage
   - Works with multiple backend instances

✅ Database optimization
   - Proper indexes for fast queries
   - Foreign key constraints
   - Unique constraints prevent duplicates

✅ Audit trail
   - Helps identify bottlenecks
   - Supports compliance requirements
   - Historical data for analysis

✅ Bulk operations
   - Efficient for managing many users
   - Reduces number of API calls
   - Minimizes database transactions
```

---

*Architecture diagram created for comprehensive system understanding*
