"""Exercise routes.

This module contains all API endpoints for exercise management.
Business logic has been extracted to the ExerciseService.
"""


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models import DifficultyLevel
from app.schemas import ExerciseCreate, ExerciseDetail, ExerciseListItem, ExerciseUpdate
from app.services import exercise_service

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/", response_model=list[ExerciseListItem])
async def get_exercises(
    skip: int = 0,
    limit: int = 100,
    difficulty: DifficultyLevel | None = None,
    category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[ExerciseListItem]:
    """Get all exercises with optional filters.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        difficulty: Filter by difficulty level
        category_id: Filter by category ID
        db: Database session

    Returns:
        List of exercises matching the filters
    """
    exercises = await exercise_service.get_all_exercises(
        db=db, skip=skip, limit=limit, difficulty=difficulty, category_id=category_id
    )
    return exercises  # type: ignore[return-value]


@router.get("/{exercise_id}", response_model=ExerciseDetail)
async def get_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)) -> ExerciseDetail:
    """Get a specific exercise with all details.

    Args:
        exercise_id: Exercise ID
        db: Database session

    Returns:
        Exercise with all relationships loaded

    Raises:
        HTTPException: 404 if exercise not found
    """
    exercise = await exercise_service.get_exercise_by_id(db=db, exercise_id=exercise_id)
    return exercise


@router.post("/", response_model=ExerciseDetail, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise_data: ExerciseCreate, db: AsyncSession = Depends(get_db)
) -> ExerciseDetail:
    """Create a new exercise.

    This endpoint creates an exercise with:
    - Basic exercise data
    - Associated categories (many-to-many)
    - Test cases
    - Examples

    Args:
        exercise_data: Exercise creation data
        db: Database session

    Returns:
        Created exercise with all relationships

    Note:
        TODO: Add authentication - Admin only
    """
    exercise = await exercise_service.create_exercise(db=db, exercise_data=exercise_data)
    return exercise


@router.put("/{exercise_id}", response_model=ExerciseDetail)
async def update_exercise(
    exercise_id: int, exercise_data: ExerciseUpdate, db: AsyncSession = Depends(get_db)
) -> ExerciseDetail:
    """Update an exercise.

    Args:
        exercise_id: Exercise ID to update
        exercise_data: Updated exercise data
        db: Database session

    Returns:
        Updated exercise

    Raises:
        HTTPException: 404 if exercise not found

    Note:
        TODO: Add authentication - Admin only
    """
    exercise = await exercise_service.update_exercise(
        db=db, exercise_id=exercise_id, exercise_data=exercise_data
    )
    return exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete an exercise.

    This will cascade delete all related test cases and examples.

    Args:
        exercise_id: Exercise ID to delete
        db: Database session

    Raises:
        HTTPException: 404 if exercise not found

    Note:
        TODO: Add authentication - Admin only
    """
    await exercise_service.delete_exercise(db=db, exercise_id=exercise_id)


@router.get("/{exercise_id}/next", response_model=ExerciseListItem)
async def get_next_exercise(
    exercise_id: int,
    difficulty: DifficultyLevel | None = None,
    db: AsyncSession = Depends(get_db),
) -> ExerciseListItem:
    """Get the next suggested exercise after completing one.

    Args:
        exercise_id: Current exercise ID
        difficulty: Optional difficulty filter
        db: Database session

    Returns:
        Next recommended exercise

    Raises:
        HTTPException: 404 if no more exercises available
    """
    next_exercise = await exercise_service.get_next_exercise(
        db=db, current_exercise_id=exercise_id, difficulty=difficulty
    )

    if not next_exercise:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No more exercises available"
        )

    return next_exercise


@router.get("/{exercise_id}/stats", response_model=dict)
async def get_exercise_statistics(exercise_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    """Get statistics for an exercise.

    Args:
        exercise_id: Exercise ID
        db: Database session

    Returns:
        Dictionary with exercise statistics

    Raises:
        HTTPException: 404 if exercise not found
    """
    stats = await exercise_service.get_exercise_statistics(db=db, exercise_id=exercise_id)
    return stats
