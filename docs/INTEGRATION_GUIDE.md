"""
INTEGRATION GUIDE: Adding Access Control to Existing Endpoints

This file shows how to integrate junction access control into your existing
traffic management API endpoints.
"""

# ===========================================================================
# EXAMPLE 1: Simple GET endpoint with access control
# ===========================================================================

# BEFORE (without access control):
# 
# @app.get("/api/v1/traffic/junctions/{junction_id}")
# async def get_junction(junction_id: int):
#     return await db_service.get_junction(junction_id)


# AFTER (with access control):
from fastapi import Depends, HTTPException, status
from app.middleware.access_control import get_current_user
from app.utils.access_helpers import check_access

async def get_junction(
    junction_id: int,
    user: dict = Depends(get_current_user),
):
    """Get junction details with access control"""
    
    # Check if user has access to this junction
    if not check_access(user, junction_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have access to junction {junction_id}",
        )
    
    # If access granted, proceed with business logic
    return await db_service.get_junction(junction_id)


# ===========================================================================
# EXAMPLE 2: POST endpoint requiring OPERATOR role
# ===========================================================================

# BEFORE:
#
# @app.post("/api/v1/traffic/junctions/{junction_id}/control")
# async def control_junction(junction_id: int, control_data: dict):
#     return await db_service.update_junction(junction_id, control_data)


# AFTER:
from app.utils.access_helpers import assert_access

async def control_junction(
    junction_id: int,
    control_data: dict,
    user: dict = Depends(get_current_user),
):
    """Control junction (requires OPERATOR role)"""
    
    # Check if user is OPERATOR for this junction
    try:
        assert_access(user, junction_id, required_role="OPERATOR")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an OPERATOR to control junctions",
        )
    
    # Proceed with control logic
    return await db_service.update_junction(junction_id, control_data)


# ===========================================================================
# EXAMPLE 3: List endpoint filtering by user's junctions
# ===========================================================================

# BEFORE:
#
# @app.get("/api/v1/traffic/junctions")
# async def list_junctions():
#     return await db_service.list_all_junctions()


# AFTER:
from app.utils.access_helpers import filter_junctions

async def list_junctions(
    user: dict = Depends(get_current_user),
):
    """List junctions user has access to"""
    
    # Get all junctions (admin shortcut)
    all_junctions = await db_service.list_all_junctions()
    
    # Filter to only user's accessible junctions
    user_junction_ids = user.get("token_data", {}).get("junction_ids", [])
    
    if user.get("role") == "ADMIN":
        # Admins see all
        return all_junctions
    else:
        # Others see only assigned junctions
        filtered = [
            j for j in all_junctions 
            if j["id"] in user_junction_ids
        ]
        return filtered


# ===========================================================================
# EXAMPLE 4: Bulk operation with access control
# ===========================================================================

# BEFORE:
#
# @app.post("/api/v1/traffic/cycles/calculate")
# async def calculate_cycles(junction_ids: List[int]):
#     results = []
#     for jid in junction_ids:
#         results.append(await calculator.calculate(jid))
#     return results


# AFTER:
from typing import List

async def calculate_cycles(
    junction_ids: List[int],
    user: dict = Depends(get_current_user),
):
    """Calculate traffic cycles for multiple junctions"""
    
    # Filter to only user's accessible junctions
    user_junction_ids = user.get("token_data", {}).get("junction_ids", [])
    
    if user.get("role") != "ADMIN":
        # Filter junctions user can access
        accessible_ids = [
            jid for jid in junction_ids 
            if jid in user_junction_ids
        ]
        if not accessible_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to any of the requested junctions",
            )
        junction_ids = accessible_ids
    
    # Calculate for accessible junctions
    results = []
    for jid in junction_ids:
        results.append(await calculator.calculate(jid))
    
    return results


# ===========================================================================
# EXAMPLE 5: Using middleware with dependency injection
# ===========================================================================

from app.middleware.access_control import check_junction_access

# This approach uses a factory pattern
async def get_junction_with_access(
    junction_id: int,
    user: dict = Depends(get_current_user),
):
    """
    Custom dependency that validates junction access
    Use as: user = Depends(get_junction_with_access)
    """
    if not check_access(user, junction_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have access to junction {junction_id}",
        )
    return user


# Usage:
async def get_junction_details(
    junction_id: int,
    user: dict = Depends(get_junction_with_access),
):
    """Simplified - access already checked by dependency"""
    return await db_service.get_junction(junction_id)


# ===========================================================================
# EXAMPLE 6: Audit logging with access control
# ===========================================================================

from app.services.user_management_service import UserManagementService

user_service = UserManagementService()

async def update_signal_timing(
    junction_id: int,
    timing_data: dict,
    user: dict = Depends(get_current_user),
    request: Request,
):
    """Update signal timing with audit logging"""
    
    # Check access
    assert_access(user, junction_id, required_role="OPERATOR")
    
    # Update
    result = await db_service.update_signal_timing(junction_id, timing_data)
    
    # Log audit
    await user_service.log_audit(
        user_id=user["id"],
        junction_id=junction_id,
        action="UPDATE_SIGNAL_TIMING",
        resource=f"junction_{junction_id}",
        details={
            "lane_timings": timing_data,
        },
        ip_address=request.client.host if request.client else None,
    )
    
    return result


# ===========================================================================
# EXAMPLE 7: Quick reference - minimal changes needed
# ===========================================================================

# Minimal integration for existing endpoints:

"""
1. Add import at top of router file:
   from app.middleware.access_control import get_current_user
   from app.utils.access_helpers import check_access

2. Add user parameter to endpoint:
   async def your_endpoint(
       junction_id: int,
       user: dict = Depends(get_current_user),
   ):

3. Add access check at start of function:
   if not check_access(user, junction_id):
       raise HTTPException(status_code=403, detail="Access denied")

4. Continue with existing logic

That's it! Your endpoint now has access control.
"""


# ===========================================================================
# COMPLETE EXAMPLE: Traffic cycle calculation endpoint
# ===========================================================================

async def calculate_traffic_cycle(
    junction_id: int,
    user: dict = Depends(get_current_user),
):
    """
    Calculate optimal traffic cycle for a junction
    - OPERATOR: Can calculate for assigned junctions
    - OBSERVER: Cannot calculate, only view results
    - ADMIN: Can calculate for any junction
    """
    
    # Check access with OPERATOR role requirement
    if not check_access(user, junction_id, required_role="OPERATOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only operators can calculate traffic cycles",
        )
    
    # Check junction exists and has data
    junction = await db_service.get_junction(junction_id)
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction {junction_id} not found",
        )
    
    # Get recent vehicle detections
    detections = await db_service.get_recent_detections(
        junction_id,
        time_window_minutes=10,
    )
    
    # Calculate optimal timing
    lane_counts = [
        len([d for d in detections if d["lane_number"] == i])
        for i in range(1, 5)
    ]
    
    result = traffic_calculator.calculate(lane_counts, junction["algorithm_config"])
    
    # Log the calculation
    await user_service.log_audit(
        user_id=user["id"],
        junction_id=junction_id,
        action="CALCULATE_CYCLE",
        resource=f"cycle_calculation",
        details={
            "lane_counts": lane_counts,
            "result": result,
        },
    )
    
    # Save cycle
    await db_service.save_traffic_cycle(junction_id, result)
    
    return {
        "junction_id": junction_id,
        "cycle_time": result["total_cycle"],
        "green_times": result["green_times"],
        "lane_counts": lane_counts,
    }
