"""Category service layer.

This module contains all business logic related to categories.
It separates business logic from the route handlers following the service pattern.
"""

from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Exercise
from app.schemas import CategoryCreate, CategoryUpdate

if TYPE_CHECKING:
    from app.models.exercise import DifficultyLevel


class CategoryService:
    """Service class for category-related business logic."""

    @staticmethod
    async def get_all_categories(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Category]:
        """Get all categories with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of categories

        Example:
            >>> categories = await CategoryService.get_all_categories(db)
        """
        query = (
            select(Category)
            .options(selectinload(Category.exercises))
            .offset(skip)
            .limit(limit)
            .order_by(Category.name)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> Category:
        """Get category by ID with exercises loaded.

        Args:
            db: Database session
            category_id: Category ID

        Returns:
            Category object

        Raises:
            HTTPException: 404 if category not found

        Example:
            >>> category = await CategoryService.get_category_by_id(db, 1)
        """
        query = (
            select(Category)
            .options(selectinload(Category.exercises))
            .where(Category.id == category_id)
        )

        result = await db.execute(query)
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found",
            )

        return category

    @staticmethod
    async def create_category(db: AsyncSession, category_data: CategoryCreate) -> Category:
        """Create a new category.

        Args:
            db: Database session
            category_data: Category creation data

        Returns:
            Created category object

        Raises:
            HTTPException: 400 if category name already exists

        Example:
            >>> category = await CategoryService.create_category(db, category_data)
        """
        # Check if category with same name already exists
        existing_category = await CategoryService.get_category_by_name(db, category_data.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_data.name}' already exists",
            )

        category = Category(
            name=category_data.name,
            description=category_data.description,
        )

        db.add(category)
        await db.commit()
        await db.refresh(category)

        return category

    @staticmethod
    async def update_category(
        db: AsyncSession, category_id: int, category_data: CategoryUpdate
    ) -> Category:
        """Update an existing category.

        Args:
            db: Database session
            category_id: Category ID to update
            category_data: Updated category data

        Returns:
            Updated category object

        Raises:
            HTTPException: 404 if category not found
            HTTPException: 400 if new name already exists

        Example:
            >>> updated = await CategoryService.update_category(db, 1, update_data)
        """
        category = await CategoryService.get_category_by_id(db, category_id)

        # Check if new name conflicts with existing category
        if category_data.name and category_data.name != category.name:
            existing_category = await CategoryService.get_category_by_name(db, category_data.name)
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with name '{category_data.name}' already exists",
                )

        # Update fields
        update_data = category_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(category, key):
                setattr(category, key, value)

        await db.commit()
        await db.refresh(category)

        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> None:
        """Delete a category.

        Note: This only removes the category, not the associated exercises
        (many-to-many relationship).

        Args:
            db: Database session
            category_id: Category ID to delete

        Raises:
            HTTPException: 404 if category not found

        Example:
            >>> await CategoryService.delete_category(db, 1)
        """
        category = await CategoryService.get_category_by_id(db, category_id)
        await db.delete(category)
        await db.commit()

    @staticmethod
    async def get_category_by_name(db: AsyncSession, name: str) -> Category | None:
        """Get category by name (for duplicate checking).

        Args:
            db: Database session
            name: Category name

        Returns:
            Category object or None if not found

        Example:
            >>> category = await CategoryService.get_category_by_name(db, "Algorithms")
        """
        query = select(Category).where(Category.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_category_statistics(db: AsyncSession, category_id: int) -> dict:
        """Get statistics for a category.

        Args:
            db: Database session
            category_id: Category ID

        Returns:
            Dictionary with statistics (exercise_count, difficulty_breakdown)

        Example:
            >>> stats = await CategoryService.get_category_statistics(db, 1)
            >>> print(stats["exercise_count"])
        """
        category = await CategoryService.get_category_by_id(db, category_id)

        # Count exercises by difficulty
        difficulty_query = (
            select(Exercise.difficulty, func.count(Exercise.id))
            .join(Exercise.categories)
            .where(Category.id == category_id)
            .group_by(Exercise.difficulty)
        )

        difficulty_result = await db.execute(difficulty_query)
        difficulty_breakdown: dict[DifficultyLevel, int] = {
            row[0]: row[1] for row in difficulty_result.all()
        }

        return {
            "category_id": category_id,
            "name": category.name,
            "exercise_count": len(category.exercises),
            "difficulty_breakdown": difficulty_breakdown,
        }

    @staticmethod
    async def get_categories_with_exercise_count(db: AsyncSession) -> list[dict]:
        """Get all categories with their exercise counts.

        Args:
            db: Database session

        Returns:
            List of dictionaries with category info and exercise counts

        Example:
            >>> categories = await CategoryService.get_categories_with_exercise_count(db)
        """
        query = (
            select(
                Category.id,
                Category.name,
                Category.description,
                Category.created_at,
                func.count(Exercise.id).label("exercise_count"),
            )
            .outerjoin(Category.exercises)
            .group_by(Category.id, Category.name, Category.description, Category.created_at)
            .order_by(Category.name)
        )

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "created_at": row.created_at,
                "exercise_count": row.exercise_count,
            }
            for row in rows
        ]


# Singleton instance for dependency injection
category_service = CategoryService()
