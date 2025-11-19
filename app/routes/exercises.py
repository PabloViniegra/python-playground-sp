from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.core.database import get_db
from app.models import Exercise, Category, TestCase, Example, DifficultyLevel
from app.schemas import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseListItem,
    ExerciseDetail,
    TestCaseCreate,
    ExampleCreate
)

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/", response_model=List[ExerciseListItem])
async def get_exercises(
    skip: int = 0,
    limit: int = 100,
    difficulty: Optional[DifficultyLevel] = None,
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all exercises with optional filters."""
    query = select(Exercise).options(
        selectinload(Exercise.categories)
    )

    # Apply filters
    if difficulty:
        query = query.where(Exercise.difficulty == difficulty)

    if category_id:
        query = query.join(Exercise.categories).where(Category.id == category_id)

    query = query.offset(skip).limit(limit).order_by(Exercise.created_at.desc())

    result = await db.execute(query)
    exercises = result.scalars().all()

    return exercises


@router.get("/{exercise_id}", response_model=ExerciseDetail)
async def get_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific exercise with all details."""
    query = select(Exercise).options(
        selectinload(Exercise.categories),
        selectinload(Exercise.test_cases),
        selectinload(Exercise.examples)
    ).where(Exercise.id == exercise_id)

    result = await db.execute(query)
    exercise = result.scalar_one_or_none()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    return exercise


@router.post("/", response_model=ExerciseDetail, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise_data: ExerciseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new exercise (Admin only - add auth later)."""
    # Create exercise
    exercise_dict = exercise_data.model_dump(exclude={'category_ids', 'test_cases', 'examples'})
    exercise = Exercise(**exercise_dict)

    # Add categories
    if exercise_data.category_ids:
        result = await db.execute(
            select(Category).where(Category.id.in_(exercise_data.category_ids))
        )
        categories = result.scalars().all()
        exercise.categories = list(categories)

    db.add(exercise)
    await db.flush()  # Get exercise ID

    # Add test cases
    for i, tc_data in enumerate(exercise_data.test_cases):
        test_case = TestCase(
            exercise_id=exercise.id,
            input_data=tc_data.get('input_data'),
            expected_output=tc_data.get('expected_output'),
            is_public=tc_data.get('is_public', True),
            description=tc_data.get('description'),
            order=tc_data.get('order', i)
        )
        db.add(test_case)

    # Add examples
    for i, ex_data in enumerate(exercise_data.examples):
        example = Example(
            exercise_id=exercise.id,
            input=ex_data.get('input'),
            output=ex_data.get('output'),
            explanation=ex_data.get('explanation'),
            order=ex_data.get('order', i)
        )
        db.add(example)

    await db.commit()

    # Reload with relationships
    await db.refresh(exercise)
    query = select(Exercise).options(
        selectinload(Exercise.categories),
        selectinload(Exercise.test_cases),
        selectinload(Exercise.examples)
    ).where(Exercise.id == exercise.id)

    result = await db.execute(query)
    exercise = result.scalar_one()

    return exercise


@router.put("/{exercise_id}", response_model=ExerciseDetail)
async def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an exercise (Admin only - add auth later)."""
    query = select(Exercise).options(
        selectinload(Exercise.categories),
        selectinload(Exercise.test_cases),
        selectinload(Exercise.examples)
    ).where(Exercise.id == exercise_id)

    result = await db.execute(query)
    exercise = result.scalar_one_or_none()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # Update basic fields
    update_data = exercise_data.model_dump(exclude={'category_ids'}, exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)

    # Update categories if provided
    if exercise_data.category_ids is not None:
        result = await db.execute(
            select(Category).where(Category.id.in_(exercise_data.category_ids))
        )
        categories = result.scalars().all()
        exercise.categories = list(categories)

    await db.commit()
    await db.refresh(exercise)

    return exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an exercise (Admin only - add auth later)."""
    result = await db.execute(
        select(Exercise).where(Exercise.id == exercise_id)
    )
    exercise = result.scalar_one_or_none()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    await db.delete(exercise)
    await db.commit()

    return None


@router.get("/{exercise_id}/next", response_model=ExerciseListItem)
async def get_next_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get the next suggested exercise after completing one."""
    # Get current exercise
    result = await db.execute(
        select(Exercise).where(Exercise.id == exercise_id)
    )
    current_exercise = result.scalar_one_or_none()

    if not current_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # Find next exercise with same difficulty
    query = (
        select(Exercise)
        .options(selectinload(Exercise.categories))
        .where(
            Exercise.difficulty == current_exercise.difficulty,
            Exercise.id != exercise_id
        )
        .order_by(Exercise.id)
        .limit(1)
    )

    result = await db.execute(query)
    next_exercise = result.scalar_one_or_none()

    if not next_exercise:
        # If no exercise with same difficulty, get any other exercise
        query = (
            select(Exercise)
            .options(selectinload(Exercise.categories))
            .where(Exercise.id != exercise_id)
            .order_by(Exercise.id)
            .limit(1)
        )
        result = await db.execute(query)
        next_exercise = result.scalar_one_or_none()

    if not next_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No more exercises available"
        )

    return next_exercise
