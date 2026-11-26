"""
Goals, Tasks, and Focus Sessions endpoints.
"""
from app.schemas.base import PaginationParams
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.core.dependencies import get_db_session, get_current_user, get_pagination_params
from app.models.goals import Goal, GoalProgress, Task, FocusSession
from app.models.user import User
from app.schemas.goals import (
    GoalBase,
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalWithProgress,
    GoalListParams,
    GoalProgressBase,
    GoalProgressCreate,
    GoalProgressUpdate,
    GoalProgressResponse,
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListParams,
    FocusSessionBase,
    FocusSessionCreate,
    FocusSessionUpdate,
    FocusSessionResponse,
    FocusSessionListParams,
)
from app.schemas.base import PaginatedResponse, paginate


router = APIRouter()


# Goals
@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED, summary="Create goal")
async def create_goal(
    request: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new goal."""
    goal = Goal(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


@router.get("", response_model=PaginatedResponse[GoalResponse], summary="List goals")
async def list_goals(
    params: GoalListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List user's goals with pagination."""
    query = select(Goal).where(Goal.user_id == current_user.id)

    if params.category:
        query = query.where(Goal.category == params.category)
    if params.status:
        query = query.where(Goal.status == params.status)
    if params.start_date_from:
        query = query.where(Goal.start_date >= params.start_date_from)
    if params.start_date_to:
        query = query.where(Goal.start_date <= params.start_date_to)

    query = query.order_by(Goal.priority, Goal.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/{goal_id}", response_model=GoalWithProgress, summary="Get goal with progress")
async def get_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get a goal with its progress records."""
    result = await db.execute(
        select(Goal)
        .options(selectinload(Goal.progress_records))
        .where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    return goal


@router.put("/{goal_id}", response_model=GoalResponse, summary="Update goal")
async def update_goal(
    goal_id: UUID,
    request: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a goal."""
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    await db.commit()
    await db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete goal")
async def delete_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a goal."""
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    await db.delete(goal)
    await db.commit()


# Goal Progress
@router.post("/{goal_id}/progress", response_model=GoalProgressResponse, status_code=status.HTTP_201_CREATED, summary="Add goal progress")
async def add_goal_progress(
    goal_id: UUID,
    request: GoalProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Add progress record for a goal."""
    # Verify goal exists and belongs to user
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    # Check if progress for this date already exists
    existing = await db.execute(
        select(GoalProgress).where(
            GoalProgress.goal_id == goal_id,
            GoalProgress.date == request.date,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Progress for this date already exists",
        )

    progress = GoalProgress(
        goal_id=goal_id,
        **request.model_dump(),
    )
    db.add(progress)

    # Update goal current value and streak
    goal.current_value = request.value
    goal.progress_percentage = min(100, (request.value / goal.target_value) * 100) if goal.target_value > 0 else 0

    if request.achieved:
        goal.last_completed_date = request.date
        # Calculate streak
        goal.streak_days = await calculate_streak(goal_id, request.date, db)

    await db.commit()
    await db.refresh(progress)
    return progress


async def calculate_streak(goal_id: UUID, current_date: date, db: AsyncSession) -> int:
    """Calculate current streak for a goal."""
    result = await db.execute(
        select(GoalProgress.date)
        .where(
            GoalProgress.goal_id == goal_id,
            GoalProgress.achieved == True,
            GoalProgress.date <= current_date,
        )
        .order_by(GoalProgress.date.desc())
    )
    dates = [row[0] for row in result.all()]

    if not dates:
        return 0

    streak = 1
    expected_date = dates[0]

    for d in dates[1:]:
        expected_date = date.fromordinal(expected_date.toordinal() - 1)
        if d == expected_date:
            streak += 1
        else:
            break

    return streak


@router.get("/{goal_id}/progress", response_model=PaginatedResponse[GoalProgressResponse], summary="List goal progress")
async def list_goal_progress(
    goal_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List progress records for a goal."""
    # Verify goal ownership
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    query = select(GoalProgress).where(GoalProgress.goal_id == goal_id).order_by(GoalProgress.date.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((pagination.page - 1) * pagination.page_size).limit(pagination.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, pagination)


@router.put("/progress/{progress_id}", response_model=GoalProgressResponse, summary="Update goal progress")
async def update_goal_progress(
    progress_id: UUID,
    request: GoalProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a progress record."""
    result = await db.execute(
        select(GoalProgress)
        .join(Goal)
        .where(GoalProgress.id == progress_id, Goal.user_id == current_user.id)
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress record not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(progress, field, value)

    await db.commit()
    await db.refresh(progress)
    return progress


# Tasks
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Create task")
async def create_task(
    request: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new task."""
    # Verify goal ownership if provided
    if request.goal_id:
        result = await db.execute(
            select(Goal).where(Goal.id == request.goal_id, Goal.user_id == current_user.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    task = Task(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/tasks", response_model=PaginatedResponse[TaskResponse], summary="List tasks")
async def list_tasks(
    params: TaskListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List user's tasks with pagination."""
    query = select(Task).where(Task.user_id == current_user.id)

    if params.status:
        query = query.where(Task.status == params.status)
    if params.category:
        query = query.where(Task.category == params.category)
    if params.priority:
        query = query.where(Task.priority == params.priority)
    if params.scheduled_date_from:
        query = query.where(Task.scheduled_date >= params.scheduled_date_from)
    if params.scheduled_date_to:
        query = query.where(Task.scheduled_date <= params.scheduled_date_to)
    if params.goal_id:
        query = query.where(Task.goal_id == params.goal_id)

    query = query.order_by(Task.priority.desc(), Task.scheduled_date.asc().nullslast())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.put("/tasks/{task_id}", response_model=TaskResponse, summary="Update task")
async def update_task(
    task_id: UUID,
    request: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a task."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = request.model_dump(exclude_unset=True)

    # Handle completion
    if "status" in update_data and update_data["status"] == "completed":
        task.completed_at = datetime.utcnow()
        if "actual_duration_minutes" not in update_data:
            update_data["actual_duration_minutes"] = task.estimated_duration_minutes

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete task")
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a task."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    await db.delete(task)
    await db.commit()


# Focus Sessions
@router.post("/focus-sessions", response_model=FocusSessionResponse, status_code=status.HTTP_201_CREATED, summary="Create focus session")
async def create_focus_session(
    request: FocusSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new focus session."""
    # Verify task/goal ownership if provided
    if request.task_id:
        result = await db.execute(
            select(Task).where(Task.id == request.task_id, Task.user_id == current_user.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if request.goal_id:
        result = await db.execute(
            select(Goal).where(Goal.id == request.goal_id, Goal.user_id == current_user.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    session = FocusSession(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/focus-sessions", response_model=PaginatedResponse[FocusSessionResponse], summary="List focus sessions")
async def list_focus_sessions(
    params: FocusSessionListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List user's focus sessions with pagination."""
    query = select(FocusSession).where(FocusSession.user_id == current_user.id)

    if params.status:
        query = query.where(FocusSession.status == params.status)
    if params.task_id:
        query = query.where(FocusSession.task_id == params.task_id)
    if params.goal_id:
        query = query.where(FocusSession.goal_id == params.goal_id)
    if params.date_from:
        query = query.where(FocusSession.actual_start >= params.date_from)
    if params.date_to:
        query = query.where(FocusSession.actual_start <= params.date_to)

    query = query.order_by(FocusSession.actual_start.desc().nullslast())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.put("/focus-sessions/{session_id}", response_model=FocusSessionResponse, summary="Update focus session")
async def update_focus_session(
    session_id: UUID,
    request: FocusSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a focus session."""
    result = await db.execute(
        select(FocusSession).where(FocusSession.id == session_id, FocusSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Focus session not found")

    update_data = request.model_dump(exclude_unset=True)

    # Handle status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "active" and session.status == "planned":
            session.actual_start = datetime.utcnow()
        elif new_status in ("completed", "interrupted", "cancelled") and session.status == "active":
            session.actual_end = datetime.utcnow()
            if session.actual_start:
                delta = session.actual_end - session.actual_start
                session.actual_duration_minutes = int(delta.total_seconds() / 60)

    for field, value in update_data.items():
        setattr(session, field, value)

    await db.commit()
    await db.refresh(session)
    return session


@router.post("/focus-sessions/{session_id}/start", response_model=FocusSessionResponse, summary="Start focus session")
async def start_focus_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Start a focus session."""
    result = await db.execute(
        select(FocusSession).where(FocusSession.id == session_id, FocusSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Focus session not found")

    if session.status != "planned":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already started")

    session.status = "active"
    session.actual_start = datetime.utcnow()
    await db.commit()
    await db.refresh(session)
    return session


@router.post("/focus-sessions/{session_id}/complete", response_model=FocusSessionResponse, summary="Complete focus session")
async def complete_focus_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Complete a focus session."""
    result = await db.execute(
        select(FocusSession).where(FocusSession.id == session_id, FocusSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Focus session not found")

    if session.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session not active")

    session.status = "completed"
    session.actual_end = datetime.utcnow()
    if session.actual_start:
        delta = session.actual_end - session.actual_start
        session.actual_duration_minutes = int(delta.total_seconds() / 60)

    await db.commit()
    await db.refresh(session)
    return session