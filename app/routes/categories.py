"""Category routes.

This module contains all API endpoints for category management.
Business logic has been extracted to the CategoryService.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate, CategoryWithExerciseCount
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryWithExerciseCount])
async def get_categories(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> list[CategoryWithExerciseCount]:
    """Get all categories with exercise count.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of categories with their exercise counts
    """
    categories = await category_service.get_categories_with_exercise_count(db=db)

    # Apply pagination manually since the query already aggregates
    return categories[skip : skip + limit]  # type: ignore[return-value]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)) -> CategoryResponse:
    """Get a specific category by ID.

    Args:
        category_id: Category ID
        db: Database session

    Returns:
        Category object

    Raises:
        HTTPException: 404 if category not found
    """
    category = await category_service.get_category_by_id(db=db, category_id=category_id)
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate, db: AsyncSession = Depends(get_db)
) -> CategoryResponse:
    """Create a new category.

    Args:
        category_data: Category creation data
        db: Database session

    Returns:
        Created category

    Raises:
        HTTPException: 400 if category name already exists

    Note:
        TODO: Add authentication - Admin only
    """
    category = await category_service.create_category(db=db, category_data=category_data)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int, category_data: CategoryUpdate, db: AsyncSession = Depends(get_db)
) -> CategoryResponse:
    """Update a category.

    Args:
        category_id: Category ID to update
        category_data: Updated category data
        db: Database session

    Returns:
        Updated category

    Raises:
        HTTPException: 404 if category not found
        HTTPException: 400 if new name already exists

    Note:
        TODO: Add authentication - Admin only
    """
    category = await category_service.update_category(
        db=db, category_id=category_id, category_data=category_data
    )
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a category.

    This only removes the category, not the associated exercises (many-to-many).

    Args:
        category_id: Category ID to delete
        db: Database session

    Raises:
        HTTPException: 404 if category not found

    Note:
        TODO: Add authentication - Admin only
    """
    await category_service.delete_category(db=db, category_id=category_id)


@router.get("/{category_id}/stats", response_model=dict)
async def get_category_statistics(category_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    """Get statistics for a category.

    Args:
        category_id: Category ID
        db: Database session

    Returns:
        Dictionary with category statistics

    Raises:
        HTTPException: 404 if category not found
    """
    stats = await category_service.get_category_statistics(db=db, category_id=category_id)
    return stats
