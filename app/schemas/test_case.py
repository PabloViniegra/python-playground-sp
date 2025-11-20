from typing import Any

from pydantic import BaseModel, ConfigDict


class TestCaseBase(BaseModel):
    input_data: dict[str, Any]
    expected_output: Any
    description: str
    is_public: bool = True
    order: int = 0


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    input_data: dict[str, Any] | None = None
    expected_output: Any | None = None
    description: str | None = None
    is_public: bool | None = None
    order: int | None = None


class TestCaseResponse(TestCaseBase):
    id: int
    exercise_id: int

    model_config = ConfigDict(from_attributes=True)


class ExampleBase(BaseModel):
    input: str
    output: str
    explanation: str | None = None
    order: int = 0


class ExampleCreate(ExampleBase):
    pass


class ExampleUpdate(BaseModel):
    input: str | None = None
    output: str | None = None
    explanation: str | None = None
    order: int | None = None


class ExampleResponse(ExampleBase):
    id: int
    exercise_id: int

    model_config = ConfigDict(from_attributes=True)
