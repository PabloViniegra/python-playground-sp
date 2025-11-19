from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
	name: str
	description: Optional[str] = None

class CategoryCreate(CategoryBase):
	pass

class CategoryUpdate(BaseModel):
	name: Optional[str] = None
	description: Optional[str] = None

class CategoryResponse(CategoryBase):
	id: int
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)

class CategoryWithExerciseCount(CategoryResponse):
	exercise_count: int = 0
