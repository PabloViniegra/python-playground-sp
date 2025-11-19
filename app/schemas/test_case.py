from pydantic import BaseModel, ConfigDict
from typing import Any, Optional


class TestCaseBase(BaseModel):
    input_data: dict[str, Any]
    expected_output: Any
    description: str
    is_public: bool = True
    order: int = 0


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    input_data: Optional[dict[str, Any]] = None
    expected_output: Optional[Any] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    order: Optional[int] = None


class TestCaseResponse(TestCaseBase):
    id: int
    exercise_id: int

    model_config = ConfigDict(from_attributes=True)


class ExampleBase(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None
    order: int = 0


class ExampleCreate(ExampleBase):
    pass


class ExampleUpdate(BaseModel):
    input: Optional[str] = None
    output: Optional[str] = None
    explanation: Optional[str] = None
    order: Optional[int] = None


class ExampleResponse(ExampleBase):
    id: int
    exercise_id: int

    model_config = ConfigDict(from_attributes=True)
