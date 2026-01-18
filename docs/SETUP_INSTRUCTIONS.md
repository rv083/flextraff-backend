"""
Setup Instructions for User Management System

This file contains the steps needed to fully integrate the user management
system into your existing FlexTraff backend application.
"""

# ===========================================================================
# STEP 1: Update main.py to include user router
# ===========================================================================

"""
In your main.py, add the following imports and router registration:

```python
from app.routers.user_router import router as user_router

# Add this after initializing app and middleware:
app.include_router(user_router)
```

Complete example:

```python
#!/usr/bin/env python3
import asyncio
import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from mqtt_handler import mqtt
from fastapi import WebSocket, WebSocketDisconnect
from ws_broadcast import manager

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.services.database_service import DatabaseService
from app.services.traffic_calculator import TrafficCalculator
from app.routers.user_router import router as user_router  # ADD THIS

# ... rest of setup ...

# Initialize FastAPI app
app = FastAPI(...)
mqtt.init_app(app)
app.add_middleware(CORSMiddleware, ...)

# Include routers
app.include_router(user_router)  # ADD THIS

# ... rest of main.py ...
```
"""


# ===========================================================================
# STEP 2: Run database migrations
# ===========================================================================

"""
Run the migration in Supabase:

1. Go to Supabase Dashboard > SQL Editor
2. Click "New Query"
3. Copy and paste the contents of: migrations/001_add_user_management.sql
4. Click "Run"

This creates all necessary tables with indexes and triggers.
"""


# ===========================================================================
# STEP 3: Update .env file
# ===========================================================================

"""
Make sure your .env file includes:

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

JWT_SECRET_KEY=your-random-secret-key-at-least-32-characters-long

# Optional:
DEBUG=False
LOG_LEVEL=INFO
MQTT_BROKER=localhost
MQTT_PORT=1883
"""


# ===========================================================================
# STEP 4: Create initial admin user
# ===========================================================================

"""
Run this script to create the first admin user:

```python
import asyncio
from app.services.user_management_service import UserManagementService

async def create_admin():
    service = UserManagementService()
    user = await service.create_user(
        username="admin",
        password="change_this_password_immediately",
        full_name="System Administrator",
        role="ADMIN",
        email="admin@example.com"
    )
    print(f"Created admin user: {user}")

asyncio.run(create_admin())
```

Or use cURL:

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <existing-admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "change_this_password_immediately",
    "full_name": "System Administrator",
    "role": "ADMIN",
    "email": "admin@example.com"
  }'
```
"""


# ===========================================================================
# STEP 5: Add authentication to existing endpoints
# ===========================================================================

"""
Update your existing traffic management endpoints to enforce access control.

See INTEGRATION_GUIDE.md for detailed examples.

Quick example for a traffic endpoint:

FROM:
@app.get("/api/v1/traffic/junctions/{junction_id}")
async def get_junction(junction_id: int):
    return await db_service.get_junction(junction_id)

TO:
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
"""


# ===========================================================================
# STEP 6: Test the system
# ===========================================================================

"""
Test user creation and authentication:

1. Create a user:
   POST /api/v1/users
   Authorization: Bearer <admin_token>
   {
       "username": "test_operator",
       "password": "TestPassword123!",
       "full_name": "Test Operator",
       "email": "test@example.com",
       "role": "OPERATOR"
   }

2. Grant junction access:
   POST /api/v1/users/{user_id}/junctions/1/grant-access
   Authorization: Bearer <admin_token>
   {
       "user_id": 1,
       "junction_id": 1,
       "access_level": "OPERATOR"
   }

3. Login as the new user:
   POST /api/v1/users/login
   {
       "username": "test_operator",
       "password": "TestPassword123!"
   }

4. Access junction with new token:
   GET /api/v1/traffic/junctions/1
   Authorization: Bearer <user_token>
   
   Should return: 200 OK (access granted)

5. Try to access unauthorized junction:
   GET /api/v1/traffic/junctions/999
   Authorization: Bearer <user_token>
   
   Should return: 403 Forbidden (no access)
"""


# ===========================================================================
# STEP 7: Deploy and monitor
# ===========================================================================

"""
After deployment:

1. Monitor audit logs:
   SELECT * FROM user_audit_logs 
   ORDER BY timestamp DESC 
   LIMIT 100;

2. Check user sessions:
   SELECT * FROM user_sessions 
   WHERE is_active = true;

3. Review user access:
   SELECT u.username, uj.junction_id, uj.access_level
   FROM users u
   JOIN user_junctions uj ON u.id = uj.user_id
   ORDER BY u.username;
"""


# ===========================================================================
# SUMMARY OF NEW FILES AND CHANGES
# ===========================================================================

"""
NEW FILES CREATED:

Database & Schema:
- migrations/001_add_user_management.sql

Services:
- app/services/user_management_service.py

Models:
- app/models/user_models.py

API Routes:
- app/routers/user_router.py

Middleware:
- app/middleware/access_control.py

Utilities:
- app/utils/access_helpers.py
- app/config.py (if not already exists)

Documentation:
- docs/USER_MANAGEMENT.md
- docs/INTEGRATION_GUIDE.md

FILES TO MODIFY:

- main.py: Add user_router import and include_router()
- Existing router files: Add access control to endpoints (see INTEGRATION_GUIDE.md)
- .env: Add JWT_SECRET_KEY


FEATURES ADDED:

✅ User authentication with JWT tokens
✅ Role-based access control (ADMIN, OPERATOR, OBSERVER)
✅ Junction-level access control
✅ Admin-only user management
✅ Token refresh mechanism
✅ Session management
✅ Audit logging
✅ Bulk operations for junction access
✅ User deactivation
✅ Password management (admin-controlled)
✅ Multiple users per junction support
✅ Multiple junctions per user support
"""
