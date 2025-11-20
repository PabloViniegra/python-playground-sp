"""Exercise service layer.

This module contains all business logic related to exercises.
It separates business logic from the route handlers following the service pattern.
"""


from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Example, Exercise, TestCase
from app.schemas import ExerciseCreate, ExerciseUpdate


class ExerciseService:
    """Service class for exercise-related business logic."""

    @staticmethod
    async def get_all_exercises(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        difficulty: str | None = None,
        category_id: int | None = None,
    ) -> list[Exercise]:
        """Get all exercises with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            difficulty: Filter by difficulty level (beginner, intermediate, advanced)
            category_id: Filter by category ID

        Returns:
            List of exercises matching the filters

        Example:
            >>> exercises = await ExerciseService.get_all_exercises(db, difficulty="beginner")
        """
        query = select(Exercise).options(
            selectinload(Exercise.categories), selectinload(Exercise.test_cases)
        )

        # Apply filters
        if difficulty:
            query = query.where(Exercise.difficulty == difficulty)

        if category_id:
            query = query.join(Exercise.categories).where(Category.id == category_id)

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Exercise.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().unique().all())

    @staticmethod
    async def get_exercise_by_id(db: AsyncSession, exercise_id: int) -> Exercise:
        """Get exercise by ID with all relationships loaded.

        Args:
            db: Database session
            exercise_id: Exercise ID

        Returns:
            Exercise object

        Raises:
            HTTPException: 404 if exercise not found

        Example:
            >>> exercise = await ExerciseService.get_exercise_by_id(db, 1)
        """
        query = (
            select(Exercise)
            .options(
                selectinload(Exercise.categories),
                selectinload(Exercise.test_cases),
                selectinload(Exercise.examples),
            )
            .where(Exercise.id == exercise_id)
        )

        result = await db.execute(query)
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with ID {exercise_id} not found",
            )

        return exercise

    @staticmethod
    async def create_exercise(db: AsyncSession, exercise_data: ExerciseCreate) -> Exercise:
        """Create a new exercise with all related data.

        This method handles the creation of:
        - The exercise itself
        - Associated categories (many-to-many)
        - Test cases
        - Examples

        Args:
            db: Database session
            exercise_data: Exercise creation data

        Returns:
            Created exercise object

        Example:
            >>> exercise = await ExerciseService.create_exercise(db, exercise_data)
        """
        # Create exercise
        exercise = Exercise(
            title=exercise_data.title,
            description=exercise_data.description,
            difficulty=exercise_data.difficulty,
            function_name=exercise_data.function_name,
        )

        # Handle categories (many-to-many relationship)
        if exercise_data.category_ids:
            category_result = await db.execute(
                select(Category).where(Category.id.in_(exercise_data.category_ids))
            )
            categories = list(category_result.scalars().all())

            if len(categories) != len(exercise_data.category_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more category IDs are invalid",
                )

            exercise.categories = categories

        db.add(exercise)
        await db.flush()  # Get the exercise ID without committing

        # Create test cases
        if exercise_data.test_cases:
            for tc_data in exercise_data.test_cases:
                test_case = TestCase(
                    exercise_id=exercise.id,
                    input_data=tc_data["input_data"],
                    expected_output=tc_data["expected_output"],
                    description=tc_data["description"],
                    order=tc_data.get("order", 0),
                )
                db.add(test_case)

        # Create examples
        if exercise_data.examples:
            for ex_data in exercise_data.examples:
                example = Example(
                    exercise_id=exercise.id,
                    input=ex_data["input"],
                    output=ex_data["output"],
                    explanation=ex_data.get("explanation", ""),
                )
                db.add(example)

        await db.commit()
        await db.refresh(exercise)

        return exercise

    @staticmethod
    async def update_exercise(
        db: AsyncSession, exercise_id: int, exercise_data: ExerciseUpdate
    ) -> Exercise:
        """Update an existing exercise.

        Args:
            db: Database session
            exercise_id: Exercise ID to update
            exercise_data: Updated exercise data

        Returns:
            Updated exercise object

        Raises:
            HTTPException: 404 if exercise not found

        Example:
            >>> updated = await ExerciseService.update_exercise(db, 1, update_data)
        """
        exercise = await ExerciseService.get_exercise_by_id(db, exercise_id)

        # Update basic fields
        update_data = exercise_data.model_dump(exclude_unset=True)

        # Handle categories separately if provided
        if "category_ids" in update_data:
            category_ids = update_data.pop("category_ids")
            if category_ids is not None:
                category_result = await db.execute(
                    select(Category).where(Category.id.in_(category_ids))
                )
                categories = list(category_result.scalars().all())

                if len(categories) != len(category_ids):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="One or more category IDs are invalid",
                    )

                exercise.categories = categories

        # Update other fields
        for key, value in update_data.items():
            if hasattr(exercise, key):
                setattr(exercise, key, value)

        await db.commit()
        await db.refresh(exercise)

        return exercise

    @staticmethod
    async def delete_exercise(db: AsyncSession, exercise_id: int) -> None:
        """Delete an exercise.

        This will cascade delete all related test cases and examples.

        Args:
            db: Database session
            exercise_id: Exercise ID to delete

        Raises:
            HTTPException: 404 if exercise not found

        Example:
            >>> await ExerciseService.delete_exercise(db, 1)
        """
        exercise = await ExerciseService.get_exercise_by_id(db, exercise_id)
        await db.delete(exercise)
        await db.commit()

    @staticmethod
    async def get_next_exercise(
        db: AsyncSession, current_exercise_id: int, difficulty: str | None = None
    ) -> Exercise | None:
        """Get the next exercise based on current exercise.

        This method finds exercises with:
        - Same or higher difficulty
        - Created after the current exercise
        - Optionally filtered by difficulty

        Args:
            db: Database session
            current_exercise_id: Current exercise ID
            difficulty: Optional difficulty filter

        Returns:
            Next exercise or None if no more exercises

        Example:
            >>> next_ex = await ExerciseService.get_next_exercise(db, 1)
        """
        # Get current exercise to know its creation date
        current_exercise = await ExerciseService.get_exercise_by_id(db, current_exercise_id)

        # Build query for next exercise
        query = select(Exercise).options(selectinload(Exercise.categories))

        # Filter by difficulty if provided
        if difficulty:
            query = query.where(Exercise.difficulty == difficulty)
        else:
            # Get exercises of same or higher difficulty
            difficulty_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
            current_difficulty_value = current_exercise.difficulty.value
            current_level = difficulty_order.get(current_difficulty_value, 1)
            valid_difficulties = [k for k, v in difficulty_order.items() if v >= current_level]
            query = query.where(Exercise.difficulty.in_(valid_difficulties))

        # Get next exercise created after current one
        query = (
            query.where(Exercise.id != current_exercise_id)
            .where(Exercise.created_at > current_exercise.created_at)
            .order_by(Exercise.created_at.asc())
            .limit(1)
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_exercise_statistics(db: AsyncSession, exercise_id: int) -> dict:
        """Get statistics for an exercise.

        Args:
            db: Database session
            exercise_id: Exercise ID

        Returns:
            Dictionary with statistics (test_count, example_count, category_count)

        Example:
            >>> stats = await ExerciseService.get_exercise_statistics(db, 1)
            >>> print(stats["test_count"])
        """
        exercise = await ExerciseService.get_exercise_by_id(db, exercise_id)

        # Count test cases
        test_count_query = select(func.count(TestCase.id)).where(
            TestCase.exercise_id == exercise_id
        )
        test_count_result = await db.execute(test_count_query)
        test_count = test_count_result.scalar()

        # Count examples
        example_count_query = select(func.count(Example.id)).where(
            Example.exercise_id == exercise_id
        )
        example_count_result = await db.execute(example_count_query)
        example_count = example_count_result.scalar()

        return {
            "exercise_id": exercise_id,
            "title": exercise.title,
            "test_count": test_count,
            "example_count": example_count,
            "category_count": len(exercise.categories),
        }


# Singleton instance for dependency injection
exercise_service = ExerciseService()
