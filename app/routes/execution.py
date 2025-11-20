import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.database import get_db
from app.models import Exercise
from app.schemas import CodeExecutionRequest, CodeExecutionResponse, TestResult
from app.services.executor import code_executor

router = APIRouter(prefix="/execute", tags=["execution"])


@router.post("/", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest, db: AsyncSession = Depends(get_db)
) -> CodeExecutionResponse:
    """
    Execute user code against exercise test cases.
    """
    # Get exercise with test cases
    query = (
        select(Exercise)
        .options(selectinload(Exercise.test_cases))
        .where(Exercise.id == request.exercise_id)
    )

    result = await db.execute(query)
    exercise = result.scalar_one_or_none()

    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    if not exercise.test_cases:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Exercise has no test cases"
        )

    # Prepare test cases for executor
    test_cases_data = [
        {
            "id": tc.id,
            "input_data": tc.input_data,
            "expected_output": tc.expected_output,
            "description": tc.description,
        }
        for tc in exercise.test_cases
    ]

    # Execute code
    start_time = time.time()
    success, results, error = code_executor.execute(
        user_code=request.code,
        function_name=str(exercise.function_name),
        test_cases=test_cases_data,
    )
    execution_time = time.time() - start_time

    # If global error (syntax, timeout, etc.)
    if not success:
        return CodeExecutionResponse(
            success=False,
            total_tests=len(test_cases_data),
            passed_tests=0,
            results=[],
            execution_time=execution_time,
            error=error,
        )

    # Build test results
    test_results = []
    passed_count = 0

    for i, result_data in enumerate(results):
        tc = exercise.test_cases[i]

        test_result = TestResult(
            test_id=result_data["test_id"],
            passed=result_data["passed"],
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            actual_output=result_data.get("actual_output"),
            error=result_data.get("error"),
            description=tc.description,
        )

        test_results.append(test_result)

        if result_data["passed"]:
            passed_count += 1

    return CodeExecutionResponse(
        success=passed_count == len(test_cases_data),
        total_tests=len(test_cases_data),
        passed_tests=passed_count,
        results=test_results,
        execution_time=execution_time,
        error=None,
    )
