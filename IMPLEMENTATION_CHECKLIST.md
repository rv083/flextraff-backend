"""
IMPLEMENTATION CHECKLIST
Step-by-step guide to integrate the user management system
"""

# ===========================================================================
# PRE-IMPLEMENTATION
# ===========================================================================

PRE_IMPLEMENTATION = """
BEFORE YOU START:
  ☐ Back up your database
  ☐ Back up your existing code
  ☐ Have Supabase access ready
  ☐ Have your JWT_SECRET_KEY ready
  ☐ Have admin credentials planned
"""

# ===========================================================================
# DATABASE SETUP (STEP 1)
# ===========================================================================

STEP_1_DATABASE = """
STEP 1: Set Up Database Schema (5 minutes)
═════════════════════════════════════════════════════════════════════

1. Open Supabase Dashboard > SQL Editor
2. Click "New Query"
3. Copy entire contents of:
   migrations/001_add_user_management.sql
4. Paste into SQL Editor
5. Click "Run" button
6. Verify tables created:
   - users ✅
   - user_junctions ✅
   - user_sessions ✅
   - user_audit_logs ✅

Expected output:
  "Executed successfully"

✅ Database schema ready
"""

# ===========================================================================
# ENVIRONMENT SETUP (STEP 2)
# ===========================================================================

STEP_2_ENVIRONMENT = """
STEP 2: Configure Environment Variables (2 minutes)
═════════════════════════════════════════════════════════════════════

1. Open .env file in your project root

2. Add JWT configuration:
   JWT_SECRET_KEY=your-random-secret-key-minimum-32-characters

   IMPORTANT: Make it random and secure!
   
   Option A: Generate using Python:
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   Option B: Use online generator (don't use for production)
   https://randomkeygen.com/

3. Verify Supabase variables are set:
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_SERVICE_KEY=xxx
   SUPABASE_ANON_KEY=xxx

4. Save .env file

✅ Environment variables configured
"""

# ===========================================================================
# FILE CREATION (STEP 3)
# ===========================================================================

STEP_3_FILES = """
STEP 3: Verify All Files Exist (2 minutes)
═════════════════════════════════════════════════════════════════════

Check these files are in your project:

Backend Services:
  ☐ app/services/user_management_service.py
  ☐ app/config.py

API Routes:
  ☐ app/routers/user_router.py

Security:
  ☐ app/middleware/access_control.py
  ☐ app/utils/access_helpers.py

Models:
  ☐ app/models/user_models.py

Database:
  ☐ migrations/001_add_user_management.sql

Tests:
  ☐ tests/test_user_management.py

Documentation:
  ☐ docs/USER_MANAGEMENT.md
  ☐ docs/INTEGRATION_GUIDE.md
  ☐ docs/SETUP_INSTRUCTIONS.md
  ☐ docs/QUICK_REFERENCE.md

✅ All files present
"""

# ===========================================================================
# CODE INTEGRATION (STEP 4)
# ===========================================================================

STEP_4_INTEGRATION = """
STEP 4: Integrate User Router into Main Application (5 minutes)
═════════════════════════════════════════════════════════════════════

1. Open main.py

2. Add import at the top (after other imports):
   
   from app.routers.user_router import router as user_router

3. Find the section where app middleware is configured:
   
   app.add_middleware(CORSMiddleware, ...)

4. After middleware setup, add:
   
   # Include user management router
   app.include_router(user_router)

5. Save file

6. Test that application starts:
   python main.py
   
   Should see:
   "INFO: Uvicorn running on..."
   WITHOUT any import errors

✅ Router integrated successfully
"""

# ===========================================================================
# INITIAL ADMIN USER (STEP 5)
# ===========================================================================

STEP_5_ADMIN = """
STEP 5: Create First Admin User (5 minutes)
═════════════════════════════════════════════════════════════════════

OPTION A: Using Python Script
─────────────────────────────────────────────────────────────

1. Create file: create_admin.py in project root

2. Add code:
   
   import asyncio
   from app.services.user_management_service import UserManagementService
   
   async def create_admin():
       service = UserManagementService()
       user = await service.create_user(
           username="admin",
           password="ChangeMe123!",  # CHANGE THIS!
           full_name="System Administrator",
           role="ADMIN",
           email="admin@yourcompany.com"
       )
       if user:
           print(f"✅ Admin user created:")
           print(f"   ID: {user['id']}")
           print(f"   Username: {user['username']}")
       else:
           print("❌ Failed to create admin user")
   
   asyncio.run(create_admin())

3. Run:
   python create_admin.py

4. Should output:
   ✅ Admin user created:
      ID: 1
      Username: admin

5. Delete create_admin.py after use:
   rm create_admin.py


OPTION B: Using Supabase Direct Insert
─────────────────────────────────────────────────────────────

1. From your project, generate password hash:
   python -c "from app.services.user_management_service import UserManagementService; s = UserManagementService(); print(s.hash_password('YourPassword123!'))"

2. Copy the hash output

3. In Supabase SQL Editor:
   INSERT INTO users (username, password_hash, full_name, role, is_active)
   VALUES ('admin', '[PASTE_HASH_HERE]', 'System Administrator', 'ADMIN', true);

4. Verify:
   SELECT * FROM users WHERE username = 'admin';


✅ Admin user created and ready to use
"""

# ===========================================================================
# API TESTING (STEP 6)
# ===========================================================================

STEP_6_TESTING = """
STEP 6: Test the API (10 minutes)
═════════════════════════════════════════════════════════════════════

1. Start your application:
   python main.py

2. Test Login Endpoint:
   
   curl -X POST http://localhost:8000/api/v1/users/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"ChangeMe123!"}'
   
   Expected Response:
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "bearer",
     "expires_in": 1800,
     "user": {
       "id": 1,
       "username": "admin",
       "full_name": "System Administrator",
       "role": "ADMIN"
     }
   }

3. Save the access_token for next tests:
   ADMIN_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

4. Test Getting User Profile:
   
   curl -X GET http://localhost:8000/api/v1/users/me \
     -H "Authorization: Bearer $ADMIN_TOKEN"
   
   Expected: Returns admin user details

5. Test Creating New User:
   
   curl -X POST http://localhost:8000/api/v1/users \
     -H "Authorization: Bearer $ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "operator_1",
       "password": "OpPass123!",
       "full_name": "Operator One",
       "email": "operator@company.com",
       "role": "OPERATOR"
     }'
   
   Expected: Returns new user with id

6. Test List Users:
   
   curl -X GET "http://localhost:8000/api/v1/users?limit=10&offset=0" \
     -H "Authorization: Bearer $ADMIN_TOKEN"
   
   Expected: Returns list with admin and new operator

7. Test Granting Junction Access:
   
   curl -X POST http://localhost:8000/api/v1/users/2/junctions/1/grant-access \
     -H "Authorization: Bearer $ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 2,
       "junction_id": 1,
       "access_level": "OPERATOR"
     }'
   
   Expected: {"message": "Access granted..."}

✅ All API endpoints working
"""

# ===========================================================================
# EXISTING ENDPOINT INTEGRATION (STEP 7)
# ===========================================================================

STEP_7_ENDPOINTS = """
STEP 7: Add Access Control to Existing Endpoints (variable)
═════════════════════════════════════════════════════════════════════

For EACH traffic management endpoint you want to protect:

1. Open the router file containing the endpoint

2. Add imports at top:
   
   from app.middleware.access_control import get_current_user
   from app.utils.access_helpers import check_access

3. Find endpoint function, for example:
   
   @app.get("/api/v1/traffic/junctions/{junction_id}")
   async def get_junction(junction_id: int):
       return await db_service.get_junction(junction_id)

4. Add user parameter and access check:
   
   @app.get("/api/v1/traffic/junctions/{junction_id}")
   async def get_junction(
       junction_id: int,
       user: dict = Depends(get_current_user),
   ):
       if not check_access(user, junction_id):
           raise HTTPException(status_code=403, detail="Access denied")
       return await db_service.get_junction(junction_id)

5. Save and test:
   - With admin token (should work for any junction)
   - With operator token for assigned junction (should work)
   - With operator token for unassigned junction (should fail with 403)

6. Repeat for all endpoints that need protection:
   - GET /api/v1/traffic/junctions
   - POST /api/v1/traffic/junctions/{id}/control
   - GET /api/v1/traffic/cycles
   - Any other sensitive endpoints

See docs/INTEGRATION_GUIDE.md for detailed examples.

✅ All critical endpoints protected
"""

# ===========================================================================
# SECURITY REVIEW (STEP 8)
# ===========================================================================

STEP_8_SECURITY = """
STEP 8: Security Review (10 minutes)
═════════════════════════════════════════════════════════════════════

Before going to production, verify:

Authentication:
  ☐ JWT_SECRET_KEY is strong (32+ random characters)
  ☐ Access token expiry is 30 minutes
  ☐ Refresh token expiry is 7 days
  ☐ Passwords are hashed with bcrypt

Authorization:
  ☐ All sensitive endpoints have get_current_user dependency
  ☐ Junction access is validated with check_access()
  ☐ Admin-only endpoints use require_admin middleware
  ☐ Users cannot access non-assigned junctions (tested)

Database:
  ☐ All passwords stored as hashes (never plain text)
  ☐ All password_hash fields are excluded from responses
  ☐ Audit logs are being created for all actions
  ☐ Sessions are tracked and can be revoked

Environment:
  ☐ DEBUG = False in production
  ☐ CORS origins updated to your domain
  ☐ HTTPS enabled (in production)
  ☐ All secrets are in environment, not in code

Testing:
  ☐ Invalid tokens are rejected
  ☐ Expired tokens return 401
  ☐ Unauthorized access returns 403
  ☐ All endpoints have proper error handling

✅ Security review complete
"""

# ===========================================================================
# DEPLOYMENT (STEP 9)
# ===========================================================================

STEP_9_DEPLOYMENT = """
STEP 9: Deploy to Production (variable)
═════════════════════════════════════════════════════════════════════

Before deployment:

1. Review SECURITY CHECKLIST in docs/QUICK_REFERENCE.md

2. Update your deployment configuration:
   - Set DEBUG=False
   - Update CORS origins to your domain
   - Ensure HTTPS is enabled
   - Update JWT_SECRET_KEY to production secret
   - Verify Supabase production credentials

3. Run tests locally:
   pytest tests/test_user_management.py -v

4. Build and deploy according to your process:
   - Docker: Update Dockerfile if needed
   - Vercel/Render: Push to repository
   - VM: Manual deployment

5. Monitor initial usage:
   - Check application logs for errors
   - Verify audit logs in Supabase
   - Test with real users
   - Monitor performance

6. Post-deployment:
   - Change admin password to something secure
   - Create operator accounts for team members
   - Grant appropriate junction access
   - Document access levels for your team
   - Set up alerts/monitoring

✅ Deployed successfully
"""

# ===========================================================================
# ONGOING MAINTENANCE (STEP 10)
# ===========================================================================

STEP_10_MAINTENANCE = """
STEP 10: Ongoing Maintenance
═════════════════════════════════════════════════════════════════════

Regular Tasks:

Daily:
  ☐ Monitor audit logs for suspicious activity
  ☐ Check error logs in application

Weekly:
  ☐ Review user access permissions
  ☐ Verify all users are still active
  ☐ Check for unauthorized access attempts

Monthly:
  ☐ Review and archive audit logs
  ☐ Deactivate unused accounts
  ☐ Update access for team changes
  ☐ Review security practices

Quarterly:
  ☐ Audit all user permissions
  ☐ Update documentation as needed
  ☐ Test disaster recovery procedures
  ☐ Review and update security policies

As Needed:
  ☐ Add new users
  ☐ Change user permissions
  ☐ Reset passwords (admin controlled)
  ☐ Deactivate employees
  ☐ Export audit logs for compliance

Documentation:
  ☐ Keep docs/USER_MANAGEMENT.md updated
  ☐ Update QUICK_REFERENCE.md with new procedures
  ☐ Maintain internal runbook for your team

✅ System maintained and secure
"""

# ===========================================================================
# TROUBLESHOOTING
# ===========================================================================

TROUBLESHOOTING = """
COMMON ISSUES & SOLUTIONS
═════════════════════════════════════════════════════════════════════

Issue: "Module not found: app.routers.user_router"
└─ Solution: Verify file exists at app/routers/user_router.py
           Check import statement in main.py

Issue: "403 Forbidden: You do not have access to junction"
└─ Solution: Admin grant access:
           POST /api/v1/users/{user_id}/junctions/1/grant-access

Issue: "Invalid or expired token"
└─ Solution: Token expired, refresh it:
           POST /api/v1/users/refresh-token

Issue: "Database connection failed"
└─ Solution: Verify Supabase credentials in .env
           Check Supabase service is online
           Verify migration was run successfully

Issue: "Can't create user - Username already exists"
└─ Solution: Use different username
           Or deactivate existing user first

Issue: "JWT_SECRET_KEY is too short"
└─ Solution: Generate new key with:
           python -c "import secrets; print(secrets.token_urlsafe(32))"

For more help, see docs/QUICK_REFERENCE.md - TROUBLESHOOTING section
"""

# ===========================================================================
# SUMMARY
# ===========================================================================

COMPLETE_SUMMARY = """
✅ IMPLEMENTATION COMPLETE
═════════════════════════════════════════════════════════════════════

You have successfully implemented a complete user management system!

What You Have:
  ✅ User authentication with JWT
  ✅ Role-based access control (3 roles)
  ✅ Junction-level access management
  ✅ Admin user management interface
  ✅ Audit logging for compliance
  ✅ Complete API documentation
  ✅ Test suite for validation
  ✅ Integration guide for existing code

Total Files Created/Modified: 15+
Total Lines of Code: 3000+
Documentation Pages: 5+

Next Steps:
  1. Complete the 10-step implementation checklist above
  2. Test thoroughly with your team
  3. Deploy to staging environment first
  4. Get team feedback
  5. Deploy to production
  6. Monitor and maintain

For Questions:
  - See docs/USER_MANAGEMENT.md for detailed reference
  - Check docs/INTEGRATION_GUIDE.md for integration examples
  - Refer to docs/QUICK_REFERENCE.md for quick lookups
  - Review tests/test_user_management.py for usage examples

Estimated Time to Full Integration: 1-2 hours

Current Status: ✅ READY TO DEPLOY
"""

print(COMPLETE_SUMMARY)
