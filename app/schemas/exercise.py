from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

from app.models.exercise import DifficultyLevel
from app.schemas.category import CategoryResponse
from app.schemas.test_case import TestCaseResponse, ExampleResponse


class ExerciseBase(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLevel
    function_name: str


class ExerciseCreate(ExerciseBase):
    category_ids: List[int] = []
    test_cases: List[dict] = []
    examples: List[dict] = []


class ExerciseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    function_name: Optional[str] = None
    category_ids: Optional[List[int]] = None


class ExerciseListItem(BaseModel):
    id: int
    title: str
    difficulty: DifficultyLevel
    categories: List[CategoryResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseDetail(ExerciseBase):
    id: int
    categories: List[CategoryResponse] = []
    test_cases: List[TestCaseResponse] = []
    examples: List[ExampleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseResponse(ExerciseDetail):
    pass
