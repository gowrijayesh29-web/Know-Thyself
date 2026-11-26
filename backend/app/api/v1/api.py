"""
API v1 router - includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    goals,
    digital,
    physical,
    ai,
    knowledge,
    notifications,
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Users
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Goals
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])

# Digital Activity
api_router.include_router(digital.router, prefix="/digital", tags=["digital-activity"])

# Physical Health
api_router.include_router(physical.router, prefix="/physical", tags=["physical-health"])

# AI Intelligence
api_router.include_router(ai.router, prefix="/ai", tags=["ai-intelligence"])

# Knowledge Base
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

# Notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])