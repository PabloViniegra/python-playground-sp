from pydantic import BaseModel, Field
from typing import Any, Optional, List

class CodeExecutionRequest(BaseModel):
	exercise_id: int
	code: str = Field(..., description='Python code to execute')

class TestResult(BaseModel):
	test_id: int
	passed: bool
	input_data: dict[str, Any]
	expected_output: Any
	actual_output: Optional[Any] = None
	error: Optional[str] = None
	description: Optional[str] = None

class CodeExecutionResponse(BaseModel):
	success: bool
	total_tests: int
	passed_tests: int
	results: List[TestResult]
	execution_time: float
	error: Optional[str] = None
