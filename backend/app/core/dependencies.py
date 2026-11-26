"""
FastAPI dependencies - Database, Authentication, Rate Limiting, etc.
"""
from typing import Optional, AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis

from app.db.session import get_db, async_session_maker
from app.core.config import settings
from app.core.security import verify_token, decode_token, get_rate_limit_key
from app.models.user import User, UserStatus


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
http_bearer = HTTPBearer(auto_error=False)


# Database dependency
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Redis dependency
_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """Get Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


# Authentication dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(token, "access")
    if not user_id:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (alias for clarity)."""
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """Get current user if token provided, otherwise None."""
    if not credentials:
        return None

    user_id = verify_token(credentials.credentials, "access")
    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or user.status != UserStatus.ACTIVE:
        return None

    return user


# Rate limiting dependency
async def rate_limit(
    request: Request,
    redis: Redis = Depends(get_redis),
    limit: int = None,
    window: int = None,
) -> None:
    """Rate limiting dependency."""
    if not settings.DEBUG:  # Skip in debug mode
        limit = limit or settings.RATE_LIMIT_REQUESTS
        window = window or settings.RATE_LIMIT_WINDOW

        # Use IP address as identifier
        client_ip = request.client.host if request.client else "unknown"
        endpoint = f"{request.method}:{request.url.path}"
        key = get_rate_limit_key(client_ip, endpoint)

        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, window)

        if current > limit:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds.",
                headers={"Retry-After": str(ttl)},
            )


# Pagination dependency
from app.schemas.base import PaginationParams


def get_pagination_params(
    page: int = 1,
    page_size: int = 20,
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(page=page, page_size=page_size)


# Request ID dependency
async def get_request_id(request: Request) -> str:
    """Get or generate request ID."""
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        import uuid
        request_id = str(uuid.uuid4())
    return request_id


# Permission checking
class PermissionChecker:
    """Check user permissions for resources."""

    def __init__(self, resource_type: str, action: str):
        self.resource_type = resource_type
        self.action = action

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session),
    ) -> User:
        # In a real implementation, check permissions from database
        # For now, allow users to access their own resources
        return current_user


def require_permission(resource_type: str, action: str) -> PermissionChecker:
    """Require specific permission."""
    return PermissionChecker(resource_type, action)