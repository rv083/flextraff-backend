# User Management & Access Control System

## Overview

The FlexTraff backend now includes a comprehensive user management system with role-based access control (RBAC). This system allows:

- **Admin-controlled user creation**: Users cannot self-register
- **Role-based permissions**: ADMIN, OPERATOR, OBSERVER roles
- **Junction-level access control**: Users can only access junctions they've been granted access to
- **Audit logging**: All actions are tracked for compliance
- **JWT-based authentication**: Secure token-based authentication with refresh tokens

## Database Schema

### Users Table
Stores user credentials and profile information.

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,      -- bcrypt hashed
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT CHECK (role IN ('ADMIN', 'OPERATOR', 'OBSERVER')),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### User Junctions Table
Maps users to traffic junctions (many-to-many relationship).

```sql
CREATE TABLE user_junctions (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    junction_id BIGINT NOT NULL REFERENCES traffic_junctions(id),
    access_level TEXT CHECK (access_level IN ('OPERATOR', 'OBSERVER')),
    granted_at TIMESTAMP,
    granted_by BIGINT REFERENCES users(id),
    UNIQUE(user_id, junction_id)
);
```

### User Sessions Table
Tracks active sessions for token management.

```sql
CREATE TABLE user_sessions (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    session_token TEXT UNIQUE,
    refresh_token TEXT UNIQUE,
    ip_address TEXT,
    user_agent TEXT,
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    is_active BOOLEAN,
    created_at TIMESTAMP
);
```

### User Audit Logs Table
Tracks all user actions for compliance and debugging.

```sql
CREATE TABLE user_audit_logs (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    junction_id BIGINT REFERENCES traffic_junctions(id),
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    details JSONB,
    ip_address TEXT,
    timestamp TIMESTAMP
);
```

## Roles and Permissions

### ADMIN Role
- Create, update, and deactivate users
- Manage user access to junctions
- View audit logs
- Change user passwords
- Access all junctions

### OPERATOR Role
- View assigned junctions
- Control traffic signal timing at assigned junctions
- Cannot access junctions not assigned
- Cannot manage other users

### OBSERVER Role
- View assigned junctions (read-only)
- Cannot control traffic signals
- Cannot access junctions not assigned

## Authentication Flow

### 1. User Login
```bash
POST /api/v1/users/login
Content-Type: application/json

{
    "username": "john_operator",
    "password": "secure_password"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
        "id": 1,
        "username": "john_operator",
        "full_name": "John Operator",
        "role": "OPERATOR"
    }
}
```

### 2. JWT Token Contents
The access token includes:
```json
{
    "sub": "1",                    // user_id
    "username": "john_operator",
    "role": "OPERATOR",
    "junction_ids": [1, 2, 3],    // Junctions user can access
    "exp": 1234567890,             // Expiration time
    "type": "access"
}
```

### 3. Using the Token
Include the access token in request headers:
```bash
GET /api/v1/traffic/junctions/1
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 4. Token Refresh
When access token expires, use refresh token:
```bash
POST /api/v1/users/refresh-token
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## API Endpoints

### Authentication Endpoints

#### Login
```bash
POST /api/v1/users/login
```
Authenticate user with username and password.

#### Refresh Token
```bash
POST /api/v1/users/refresh-token
```
Get new access token using refresh token.

#### Logout
```bash
POST /api/v1/users/logout
Authorization: Bearer <token>
Header: X-Session-Token: <session_token>
```

### User Profile Endpoints

#### Get Current User
```bash
GET /api/v1/users/me
Authorization: Bearer <token>
```
Get current user's profile and junction access information.

### Admin User Management

#### Create User (Admin Only)
```bash
POST /api/v1/users
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "username": "john_operator",
    "password": "secure_password",
    "full_name": "John Operator",
    "email": "john@example.com",
    "role": "OPERATOR"
}
```

#### List Users (Admin Only)
```bash
GET /api/v1/users?limit=10&offset=0
Authorization: Bearer <admin_token>
```

#### Get User Details (Admin Only)
```bash
GET /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
```

#### Update User (Admin Only)
```bash
PUT /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "full_name": "John Updated",
    "email": "john_new@example.com",
    "is_active": true,
    "role": "OPERATOR"
}
```

#### Change Password (Admin Only)
```bash
POST /api/v1/users/{user_id}/change-password
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "user_id": 1,
    "new_password": "new_secure_password"
}
```

#### Deactivate User (Admin Only)
```bash
POST /api/v1/users/{user_id}/deactivate
Authorization: Bearer <admin_token>
```

### Junction Access Management

#### Get User's Junctions (Admin Only)
```bash
GET /api/v1/users/{user_id}/junctions
Authorization: Bearer <admin_token>
```

#### Grant Junction Access (Admin Only)
```bash
POST /api/v1/users/{user_id}/junctions/{junction_id}/grant-access
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "user_id": 1,
    "junction_id": 1,
    "access_level": "OPERATOR"
}
```

#### Revoke Junction Access (Admin Only)
```bash
POST /api/v1/users/{user_id}/junctions/{junction_id}/revoke-access
Authorization: Bearer <admin_token>
```

#### Bulk Grant Access (Admin Only)
```bash
POST /api/v1/users/{user_id}/junctions/bulk-grant
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "user_id": 1,
    "junction_ids": [1, 2, 3, 4, 5],
    "access_level": "OPERATOR"
}
```

#### Bulk Revoke Access (Admin Only)
```bash
POST /api/v1/users/{user_id}/junctions/bulk-revoke
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "user_id": 1,
    "junction_ids": [1, 2, 3]
}
```

## Implementation Guide

### 1. Setup Database
Run the migration script to create user tables:

```bash
# In Supabase SQL Editor, run:
migrations/001_add_user_management.sql
```

### 2. Environment Variables
Add to `.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
JWT_SECRET_KEY=your-secret-key-min-32-characters
```

### 3. Import Router in main.py
```python
from app.routers.user_router import router as user_router

app.include_router(user_router)
```

### 4. Update Traffic Endpoint with Access Control

**Before:**
```python
@app.get("/api/v1/traffic/junctions/{junction_id}")
async def get_junction(junction_id: int):
    return db_service.get_junction(junction_id)
```

**After:**
```python
from app.middleware.access_control import check_junction_access

@app.get("/api/v1/traffic/junctions/{junction_id}")
async def get_junction(
    junction_id: int,
    user: dict = Depends(check_junction_access(junction_id=junction_id))
):
    return db_service.get_junction(junction_id)
```

**Or use helper function:**
```python
from app.middleware.access_control import get_current_user

@app.get("/api/v1/traffic/junctions/{junction_id}")
async def get_junction(
    junction_id: int,
    user: dict = Depends(get_current_user)
):
    # Check access
    if user.get("role") != "ADMIN":
        junction_ids = user.get("token_data", {}).get("junction_ids", [])
        if junction_id not in junction_ids:
            raise HTTPException(
                status_code=403,
                detail="You don't have access to this junction"
            )
    
    return db_service.get_junction(junction_id)
```

## Usage Examples

### Example 1: Create User and Grant Access

```python
# 1. Admin creates user
admin_token = "eyJ0eXAiOiJKV1QiLCJhbGc..."

response = requests.post(
    "http://localhost:8000/api/v1/users",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={
        "username": "operator_1",
        "password": "password123",
        "full_name": "Operator One",
        "email": "operator1@example.com",
        "role": "OPERATOR"
    }
)
user_id = response.json()["id"]

# 2. Admin grants access to junctions
response = requests.post(
    f"http://localhost:8000/api/v1/users/{user_id}/junctions/bulk-grant",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={
        "user_id": user_id,
        "junction_ids": [1, 2, 3],
        "access_level": "OPERATOR"
    }
)

# 3. Operator logs in
response = requests.post(
    "http://localhost:8000/api/v1/users/login",
    json={
        "username": "operator_1",
        "password": "password123"
    }
)
access_token = response.json()["access_token"]

# 4. Operator accesses assigned junctions
response = requests.get(
    "http://localhost:8000/api/v1/traffic/junctions/1",
    headers={"Authorization": f"Bearer {access_token}"}
)
# Success - user has access

# 5. Operator tries to access non-assigned junction
response = requests.get(
    "http://localhost:8000/api/v1/traffic/junctions/5",
    headers={"Authorization": f"Bearer {access_token}"}
)
# Error 403 - user doesn't have access
```

### Example 2: Update User Access

```python
# Admin changes operator's access level
requests.post(
    f"http://localhost:8000/api/v1/users/{user_id}/junctions/1/grant-access",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={
        "user_id": user_id,
        "junction_id": 1,
        "access_level": "OBSERVER"  # Downgrade to observer
    }
)

# Admin revokes access
requests.post(
    f"http://localhost:8000/api/v1/users/{user_id}/junctions/1/revoke-access",
    headers={"Authorization": f"Bearer {admin_token}"}
)
```

## Security Considerations

1. **Password Hashing**: All passwords are hashed with bcrypt
2. **JWT Tokens**: 
   - Access tokens expire in 30 minutes
   - Refresh tokens expire in 7 days
   - Tokens are signed with secret key
3. **Junction Access**: Enforced at middleware level
4. **Audit Logging**: All actions logged with user ID, IP, and timestamp
5. **Admin-Only Operations**: All user management operations require ADMIN role

## Troubleshooting

### Token Expired
Get new access token using refresh token:
```bash
POST /api/v1/users/refresh-token
```

### Access Denied
Check if user has access to the junction:
```bash
GET /api/v1/users/me
# Check the "junctions" field in response
```

### Invalid Credentials
Verify username and password are correct. Note: Usernames are case-sensitive.

### User Cannot Be Created
- Ensure username is unique
- Ensure password is at least 8 characters
- Ensure role is ADMIN, OPERATOR, or OBSERVER
