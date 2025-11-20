from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.exercise import DifficultyLevel
from app.schemas.category import CategoryResponse
from app.schemas.test_case import ExampleResponse, TestCaseResponse


class ExerciseBase(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLevel
    function_name: str


class ExerciseCreate(ExerciseBase):
    category_ids: list[int] = []
    test_cases: list[dict] = []
    examples: list[dict] = []


class ExerciseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty: DifficultyLevel | None = None
    function_name: str | None = None
    category_ids: list[int] | None = None


class ExerciseListItem(BaseModel):
    id: int
    title: str
    difficulty: DifficultyLevel
    categories: list[CategoryResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseDetail(ExerciseBase):
    id: int
    categories: list[CategoryResponse] = []
    test_cases: list[TestCaseResponse] = []
    examples: list[ExampleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseResponse(ExerciseDetail):
    pass
