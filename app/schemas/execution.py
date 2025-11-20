from typing import Any

from pydantic import BaseModel, Field


class CodeExecutionRequest(BaseModel):
    exercise_id: int
    code: str = Field(..., description="Python code to execute")


class TestResult(BaseModel):
    test_id: int
    passed: bool
    input_data: dict[str, Any]
    expected_output: Any
    actual_output: Any | None = None
    error: str | None = None
    description: str | None = None


class CodeExecutionResponse(BaseModel):
    success: bool
    total_tests: int
    passed_tests: int
    results: list[TestResult]
    execution_time: float
    error: str | None = None
