import json
import subprocess
import tempfile
import time
from contextlib import suppress
from pathlib import Path
from typing import Any, ClassVar

from app.config.config import settings


class CodeExecutor:
    """Service for executing Python code in a sandboxed environment."""

    # Blacklisted imports and statements for security
    BLACKLIST: ClassVar[list[str]] = [
        "import os",
        "import sys",
        "import subprocess",
        "import shutil",
        "import socket",
        "import urllib",
        "import requests",
        "import http",
        "import ftplib",
        "import smtplib",
        "import pickle",
        "import shelve",
        "__import__",
        "eval(",
        "exec(",
        "compile(",
        "open(",
        "file(",
        "input(",
        "raw_input(",
    ]

    def __init__(self) -> None:
        self.timeout = settings.code_execution_timeout

    def _contains_blacklisted_code(self, code: str) -> tuple[bool, str]:
        """Check if code contains blacklisted imports or statements."""
        code_lower = code.lower()
        for blacklisted in self.BLACKLIST:
            if blacklisted.lower() in code_lower:
                return True, f"Prohibited statement found: {blacklisted}"
        return False, ""

    def _create_test_wrapper(
        self, user_code: str, function_name: str, test_cases: list[dict[str, Any]]
    ) -> str:
        """
        Create a wrapper script that:
        1. Defines the user's function
        2. Runs all test cases
        3. Returns results as JSON
        """
        wrapper = f"""
import json
import sys
from io import StringIO

# User's code
{user_code}

# Test execution
results = []

for i, test_case in enumerate({json.dumps(test_cases)}):
    try:
        input_data = test_case['input_data']
        expected_output = test_case['expected_output']

        # Call the user's function with unpacked arguments
        actual_output = {function_name}(**input_data)

        # Compare outputs
        passed = actual_output == expected_output

        results.append({{
            'test_id': test_case['id'],
            'passed': passed,
            'actual_output': actual_output,
            'error': None
        }})
    except Exception as e:
        results.append({{
            'test_id': test_case['id'],
            'passed': False,
            'actual_output': None,
            'error': str(e)
        }})

# Output results as JSON
print(json.dumps(results))
"""
        return wrapper

    def execute(
        self, user_code: str, function_name: str, test_cases: list[dict[str, Any]]
    ) -> tuple[bool, list[dict[str, Any]], str]:
        """
        Execute user code against test cases.

        Returns:
            Tuple of (success, results, error_message)
        """
        # Security check
        is_blacklisted, error_msg = self._contains_blacklisted_code(user_code)
        if is_blacklisted:
            return False, [], error_msg

        # Check if function is defined
        if f"def {function_name}" not in user_code:
            return False, [], f"Function '{function_name}' not found in code"

        # Create wrapper script
        wrapper_script = self._create_test_wrapper(user_code, function_name, test_cases)

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
            tmp_file.write(wrapper_script)
            tmp_file_path = tmp_file.name

        try:
            # Execute in subprocess with timeout and resource limits
            start_time = time.time()

            result = subprocess.run(
                ["python3", tmp_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                # Limit memory (Linux only)
                # preexec_fn=lambda: resource.setrlimit(
                #     resource.RLIMIT_AS,
                #     (settings.code_execution_memory_limit * 1024 * 1024,) * 2
                # )
            )

            time.time() - start_time

            # Check for execution errors
            if result.returncode != 0:
                error_msg = result.stderr.strip() or "Execution failed"
                # Clean up error message (remove temp file references)
                error_msg = error_msg.replace(tmp_file_path, "<user_code>")
                return False, [], error_msg

            # Parse results
            try:
                results = json.loads(result.stdout.strip())
                return True, results, ""
            except json.JSONDecodeError:
                return False, [], "Failed to parse execution results"

        except subprocess.TimeoutExpired:
            return False, [], f"Execution timed out (limit: {self.timeout}s)"

        except Exception as e:
            return False, [], f"Execution error: {e!s}"

        finally:
            # Clean up temporary file
            with suppress(OSError):
                Path(tmp_file_path).unlink()


# Singleton instance
code_executor = CodeExecutor()
