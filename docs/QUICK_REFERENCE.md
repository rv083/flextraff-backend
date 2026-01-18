"""
User Management System - Quick Reference
Complete API reference and usage guide
"""

# ===========================================================================
# QUICK START
# ===========================================================================

QUICK_START = """
1. Run migration: migrations/001_add_user_management.sql
2. Add to main.py: from app.routers.user_router import router as user_router
3. Include router: app.include_router(user_router)
4. Create admin user via API or script
5. Create other users and grant junction access
6. Users can now login and access assigned junctions
"""

# ===========================================================================
# DATABASE SCHEMA QUICK REFERENCE
# ===========================================================================

DATABASE_SCHEMA = """
TABLE: users
├── id (PK)
├── username (UNIQUE)
├── password_hash (bcrypt)
├── full_name
├── email (UNIQUE, nullable)
├── role (ADMIN, OPERATOR, OBSERVER)
├── is_active
├── last_login
├── created_at
└── updated_at

TABLE: user_junctions (many-to-many)
├── id (PK)
├── user_id (FK → users)
├── junction_id (FK → traffic_junctions)
├── access_level (OPERATOR, OBSERVER)
├── granted_at
├── granted_by (FK → users, nullable)
└── UNIQUE(user_id, junction_id)

TABLE: user_sessions
├── id (PK)
├── user_id (FK → users)
├── session_token (UNIQUE)
├── refresh_token (UNIQUE)
├── ip_address
├── user_agent
├── expires_at
├── last_used
├── is_active
└── created_at

TABLE: user_audit_logs
├── id (PK)
├── user_id (FK → users, nullable)
├── junction_id (FK → traffic_junctions, nullable)
├── action
├── resource
├── details (JSONB)
├── ip_address
└── timestamp
"""

# ===========================================================================
# ROLES & PERMISSIONS
# ===========================================================================

ROLES_TABLE = """
╔════════╦═══════════════════════╦════════════════╦════════════════╗
║ Role   ║ Can Create Users      ║ Can Control    ║ Can View       ║
║        ║ Manage Junctions      ║ Traffic        ║ Only           ║
╠════════╬═══════════════════════╬════════════════╬════════════════╣
║ ADMIN  ║ Yes / Yes             ║ All Junctions  ║ All            ║
║        ║ Change Passwords      ║                ║                ║
╠════════╬═══════════════════════╬════════════════╬════════════════╣
║ OPERAT-║ No / Only by Admin    ║ Assigned       ║ Assigned       ║
║ OR     ║                       ║ Junctions      ║ Junctions      ║
╠════════╬═══════════════════════╬════════════════╬════════════════╣
║ OBSERV-║ No / Only by Admin    ║ None           ║ Assigned       ║
║ ER     ║                       ║ (Read-only)    ║ Junctions      ║
╚════════╩═══════════════════════╩════════════════╩════════════════╝
"""

# ===========================================================================
# ENDPOINT REFERENCE
# ===========================================================================

ENDPOINTS_REFERENCE = """
AUTHENTICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /api/v1/users/login
├─ Body: {"username": "...", "password": "..."}
├─ Response: {access_token, refresh_token, user}
└─ Required: None (Public endpoint)

POST /api/v1/users/refresh-token
├─ Body: {"refresh_token": "..."}
├─ Response: {access_token, expires_in}
└─ Required: None (Public endpoint)

POST /api/v1/users/logout
├─ Body: None
├─ Response: {message: "Successfully logged out"}
└─ Required: Bearer token, Session-Token header


USER PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /api/v1/users/me
├─ Response: {id, username, full_name, role, junctions: [...]}
└─ Required: Bearer token


ADMIN: USER MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /api/v1/users
├─ Create new user
├─ Body: {username, password, full_name, email, role}
├─ Response: {id, username, full_name, role, is_active, ...}
└─ Required: ADMIN role

GET /api/v1/users
├─ List all users (paginated)
├─ Query params: limit (1-100), offset
├─ Response: {users: [...], total, page, page_size}
└─ Required: ADMIN role

GET /api/v1/users/{user_id}
├─ Get user details with junction access
├─ Response: {id, username, ..., junctions: [{id, junction_id, ...}]}
└─ Required: ADMIN role

PUT /api/v1/users/{user_id}
├─ Update user details
├─ Body: {full_name?, email?, is_active?, role?}
├─ Response: {id, username, full_name, ...}
└─ Required: ADMIN role

POST /api/v1/users/{user_id}/change-password
├─ Change user password
├─ Body: {user_id, new_password}
├─ Response: {message: "Password changed successfully"}
└─ Required: ADMIN role

POST /api/v1/users/{user_id}/deactivate
├─ Deactivate user account
├─ Body: None
├─ Response: {message: "User deactivated successfully"}
└─ Required: ADMIN role


ADMIN: JUNCTION ACCESS MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /api/v1/users/{user_id}/junctions
├─ Get all junctions user can access
├─ Response: {user_id, junction_ids: [...], count}
└─ Required: ADMIN role

POST /api/v1/users/{user_id}/junctions/{junction_id}/grant-access
├─ Grant access to single junction
├─ Body: {user_id, junction_id, access_level: "OPERATOR|OBSERVER"}
├─ Response: {message, access_level}
└─ Required: ADMIN role

POST /api/v1/users/{user_id}/junctions/{junction_id}/revoke-access
├─ Revoke access from single junction
├─ Body: None
├─ Response: {message}
└─ Required: ADMIN role

POST /api/v1/users/{user_id}/junctions/bulk-grant
├─ Grant access to multiple junctions
├─ Body: {user_id, junction_ids: [...], access_level}
├─ Response: {message, successful, failed, total}
└─ Required: ADMIN role

POST /api/v1/users/{user_id}/junctions/bulk-revoke
├─ Revoke access from multiple junctions
├─ Body: {user_id, junction_ids: [...]}
├─ Response: {message, successful, failed, total}
└─ Required: ADMIN role
"""

# ===========================================================================
# JWT TOKEN STRUCTURE
# ===========================================================================

JWT_STRUCTURE = """
ACCESS TOKEN:
{
    "sub": "1",                          // user_id
    "username": "john_operator",
    "role": "OPERATOR",
    "junction_ids": [1, 2, 3],          // Accessible junctions
    "exp": 1234567890,                   // Expiration timestamp
    "type": "access"
}

REFRESH TOKEN:
{
    "sub": "1",
    "exp": 1234567890,
    "type": "refresh"
}

USE IN REQUESTS:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
"""

# ===========================================================================
# ERROR CODES
# ===========================================================================

ERROR_CODES = """
400 Bad Request
├─ Invalid username format
├─ Password too short
├─ Role not valid (must be ADMIN, OPERATOR, OBSERVER)
└─ User already exists

401 Unauthorized
├─ Invalid credentials (wrong username/password)
├─ Token expired
├─ Token invalid or missing
└─ Session expired

403 Forbidden
├─ User doesn't have access to this junction
├─ User must be OPERATOR to control (not OBSERVER)
├─ Only admins can perform this action
└─ User account deactivated

404 Not Found
├─ User not found
├─ Junction not found
└─ Session not found

500 Internal Server Error
├─ Database error
├─ Authentication service error
└─ Unexpected server error
"""

# ===========================================================================
# COMMON TASKS
# ===========================================================================

COMMON_TASKS = """
TASK: Create User and Grant Access
═════════════════════════════════════════════════════════════════════

1. Create user:
   POST /api/v1/users
   {
       "username": "operator_1",
       "password": "SecurePass123!",
       "full_name": "Operator One",
       "email": "operator1@company.com",
       "role": "OPERATOR"
   }

2. Grant access to junctions:
   POST /api/v1/users/1/junctions/bulk-grant
   {
       "user_id": 1,
       "junction_ids": [1, 2, 3, 4, 5],
       "access_level": "OPERATOR"
   }

3. Operator logs in:
   POST /api/v1/users/login
   {
       "username": "operator_1",
       "password": "SecurePass123!"
   }

4. Operator uses access token to access junctions:
   GET /api/v1/traffic/junctions/1
   Authorization: Bearer <access_token>


TASK: Change User Permissions
═════════════════════════════════════════════════════════════════════

1. Downgrade from OPERATOR to OBSERVER:
   POST /api/v1/users/1/junctions/1/grant-access
   {
       "user_id": 1,
       "junction_id": 1,
       "access_level": "OBSERVER"
   }

2. Or revoke access entirely:
   POST /api/v1/users/1/junctions/1/revoke-access

3. Or revoke from multiple junctions:
   POST /api/v1/users/1/junctions/bulk-revoke
   {
       "user_id": 1,
       "junction_ids": [1, 2, 3]
   }


TASK: Reset User Password
═════════════════════════════════════════════════════════════════════

POST /api/v1/users/1/change-password
{
    "user_id": 1,
    "new_password": "NewSecurePass456!"
}


TASK: Deactivate User
═════════════════════════════════════════════════════════════════════

POST /api/v1/users/1/deactivate

User can no longer login. To reactivate:
PUT /api/v1/users/1
{
    "is_active": true
}


TASK: View User's Accessible Junctions
═════════════════════════════════════════════════════════════════════

GET /api/v1/users/1/junctions

Response:
{
    "user_id": 1,
    "junction_ids": [1, 2, 3, 4, 5],
    "count": 5
}


TASK: List All Users
═════════════════════════════════════════════════════════════════════

GET /api/v1/users?limit=10&offset=0

Response:
{
    "users": [...],
    "total": 25,
    "page": 1,
    "page_size": 10
}
"""

# ===========================================================================
# SECURITY CHECKLIST
# ===========================================================================

SECURITY_CHECKLIST = """
Before deploying to production:

□ Change JWT_SECRET_KEY to a strong random value (min 32 chars)
□ Update CORS origins to match your frontend domain
□ Set DEBUG=False in environment
□ Use HTTPS for all API calls (in production)
□ Implement rate limiting on login endpoint
□ Set up HTTPS on Supabase
□ Enable SSL for database connections
□ Rotate JWT_SECRET_KEY periodically
□ Monitor audit logs for suspicious activity
□ Implement password complexity requirements
□ Set up email notifications for admin actions
□ Use strong passwords for admin account
□ Regularly review user access permissions
□ Implement automatic session timeout (currently 7 days)
□ Enable multi-factor authentication (future enhancement)
□ Audit token expiration times (30 min access, 7 day refresh)
"""

# ===========================================================================
# TROUBLESHOOTING
# ===========================================================================

TROUBLESHOOTING = """
ISSUE: "Invalid or expired token"
─────────────────────────────────────────────────────────────────
SOLUTION:
1. Try refreshing token:
   POST /api/v1/users/refresh-token
   with your refresh_token
   
2. If refresh fails, login again:
   POST /api/v1/users/login

3. Check token expiration in JWT (exp claim)


ISSUE: "You do not have access to junction X"
─────────────────────────────────────────────────────────────────
SOLUTION:
1. Verify user has access:
   GET /api/v1/users/{user_id}/junctions
   
2. Grant access if needed:
   POST /api/v1/users/{user_id}/junctions/{junction_id}/grant-access


ISSUE: Cannot create user - "Invalid role"
─────────────────────────────────────────────────────────────────
SOLUTION:
Role must be exactly one of:
- ADMIN
- OPERATOR
- OBSERVER

Verify spelling and case sensitivity.


ISSUE: "Only admins can perform this action"
─────────────────────────────────────────────────────────────────
SOLUTION:
1. Use token from ADMIN account
2. Or promote user to ADMIN:
   PUT /api/v1/users/{user_id}
   {"role": "ADMIN"}


ISSUE: Junction IDs not in token
─────────────────────────────────────────────────────────────────
SOLUTION:
1. User needs to login again for token to refresh with new access
2. Or manually grant access:
   POST /api/v1/users/{user_id}/junctions/{junction_id}/grant-access
3. Then user logs out and back in


ISSUE: "User already exists"
─────────────────────────────────────────────────────────────────
SOLUTION:
Username must be unique. Either:
1. Use different username
2. Deactivate and reactivate existing user
3. Use different suffix (operator_1, operator_2, etc.)
"""

# ===========================================================================
# INTEGRATION CHECKLIST
# ===========================================================================

INTEGRATION_CHECKLIST = """
□ Created app/services/user_management_service.py
□ Created app/models/user_models.py
□ Created app/routers/user_router.py
□ Created app/middleware/access_control.py
□ Created app/utils/access_helpers.py
□ Created app/config.py
□ Created migrations/001_add_user_management.sql
□ Ran migration in Supabase
□ Added user_router to main.py
□ Created admin user
□ Updated existing endpoints with access control
□ Added JWT_SECRET_KEY to .env
□ Tested login endpoint
□ Tested user creation
□ Tested junction access control
□ Tested token refresh
□ Tested logout
□ Verified audit logs
□ Set up monitoring/alerting
□ Updated API documentation
□ Trained users on system
□ Deployed to production
"""
