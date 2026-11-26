"""
Base Pydantic schemas.
"""
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        },
    )


class IDSchema(BaseSchema):
    """Schema with ID field."""
    id: UUID


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    created_at: datetime
    updated_at: datetime


class IDTimestampSchema(IDSchema, TimestampSchema):
    """Schema with ID and timestamps."""
    pass


# Pagination
T = TypeVar("T")


class PaginationParams(BaseSchema):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response wrapper."""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate(items: list[T], total: int, params: PaginationParams) -> PaginatedResponse[T]:
    """Create paginated response."""
    total_pages = (total + params.page_size - 1) // params.page_size
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
        has_next=params.page < total_pages,
        has_prev=params.page > 1,
    )


# Error responses
class ErrorDetail(BaseSchema):
    """Error detail."""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseSchema):
    """Error response."""
    error: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    request_id: Optional[str] = None


# Success responses
class SuccessResponse(BaseSchema):
    """Success response."""
    success: bool = True
    message: str
    data: Optional[Any] = None


class MessageResponse(BaseSchema):
    """Simple message response."""
    message: str


# Filtering and sorting
class SortParams(BaseSchema):
    """Sorting parameters."""
    sort_by: Optional[str] = None
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class DateRangeParams(BaseSchema):
    """Date range filter parameters."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Health check
class HealthCheckResponse(BaseSchema):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    database: str
    redis: str