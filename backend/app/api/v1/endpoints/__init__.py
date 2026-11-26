"""
API v1 endpoints package.
"""
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

__all__ = [
    "auth",
    "users",
    "goals",
    "digital",
    "physical",
    "ai",
    "knowledge",
    "notifications",
]