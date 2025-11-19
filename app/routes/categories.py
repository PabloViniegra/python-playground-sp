from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.config.database import get_db
from app.models import Category, Exercise
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithExerciseCount

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryWithExerciseCount])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all categories with exercise count."""
    # Query categories with exercise count
    query = (
        select(
            Category,
            func.count(Exercise.id).label('exercise_count')
        )
        .outerjoin(Category.exercises)
        .group_by(Category.id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    categories_with_count = result.all()

    return [
        CategoryWithExerciseCount(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            created_at=cat.created_at,
            exercise_count=count
        )
        for cat, count in categories_with_count
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific category by ID."""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new category (Admin only - add auth later)."""
    # Check if category with same name exists
    result = await db.execute(
        select(Category).where(Category.name == category_data.name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    category = Category(**category_data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a category (Admin only - add auth later)."""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a category (Admin only - add auth later)."""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    await db.delete(category)
    await db.commit()

    return None
