"""
Seed script to populate the database with initial data.
Run with: python -m scripts.seed_data
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, AsyncSessionLocal
from app.models import Category, Exercise, TestCase, Example, DifficultyLevel


async def create_categories(db: AsyncSession):
    """Create initial categories."""
    categories_data = [
        {"name": "Strings", "description": "String manipulation and processing"},
        {"name": "Lists", "description": "List operations and algorithms"},
        {"name": "Mathematics", "description": "Mathematical problems and calculations"},
        {"name": "Algorithms", "description": "Algorithm design and implementation"},
        {"name": "Data Structures", "description": "Working with data structures"},
        {"name": "Recursion", "description": "Recursive solutions"},
        {"name": "Sorting", "description": "Sorting algorithms"},
        {"name": "Searching", "description": "Search algorithms"},
    ]

    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)
        categories.append(category)

    await db.flush()
    return categories


async def create_exercises(db: AsyncSession, categories: list):
    """Create sample exercises."""

    # Exercise 1: Sum Two Numbers (Beginner)
    exercise1 = Exercise(
        title="Sum Two Numbers",
        description="""# Sum Two Numbers

Write a function that takes two numbers as parameters and returns their sum.

## Requirements
- The function should accept two numeric parameters
- Return the sum of the two numbers

## Constraints
- Both inputs will be valid numbers
""",
        difficulty=DifficultyLevel.BEGINNER,
        function_name="sum_two_numbers"
    )
    exercise1.categories = [categories[2]]  # Mathematics
    db.add(exercise1)
    await db.flush()

    # Test cases for exercise 1
    test_cases_1 = [
        TestCase(
            exercise_id=exercise1.id,
            input_data={"a": 2, "b": 3},
            expected_output=5,
            description="Basic positive numbers",
            order=0
        ),
        TestCase(
            exercise_id=exercise1.id,
            input_data={"a": -1, "b": 1},
            expected_output=0,
            description="Positive and negative",
            order=1
        ),
        TestCase(
            exercise_id=exercise1.id,
            input_data={"a": 0, "b": 0},
            expected_output=0,
            description="Both zeros",
            order=2
        ),
    ]
    for tc in test_cases_1:
        db.add(tc)

    # Examples for exercise 1
    examples_1 = [
        Example(
            exercise_id=exercise1.id,
            input="sum_two_numbers(5, 7)",
            output="12",
            explanation="5 + 7 = 12",
            order=0
        ),
        Example(
            exercise_id=exercise1.id,
            input="sum_two_numbers(-3, 8)",
            output="5",
            explanation="-3 + 8 = 5",
            order=1
        ),
    ]
    for ex in examples_1:
        db.add(ex)

    # Exercise 2: Reverse String (Beginner)
    exercise2 = Exercise(
        title="Reverse a String",
        description="""# Reverse a String

Write a function that takes a string as input and returns the string reversed.

## Requirements
- Accept a string parameter
- Return the reversed string

## Example
If the input is "hello", the output should be "olleh"

## Constraints
- Input will be a valid string
- String may be empty
""",
        difficulty=DifficultyLevel.BEGINNER,
        function_name="reverse_string"
    )
    exercise2.categories = [categories[0]]  # Strings
    db.add(exercise2)
    await db.flush()

    # Test cases for exercise 2
    test_cases_2 = [
        TestCase(
            exercise_id=exercise2.id,
            input_data={"text": "hello"},
            expected_output="olleh",
            description="Simple word",
            order=0
        ),
        TestCase(
            exercise_id=exercise2.id,
            input_data={"text": "Python"},
            expected_output="nohtyP",
            description="Capitalized word",
            order=1
        ),
        TestCase(
            exercise_id=exercise2.id,
            input_data={"text": ""},
            expected_output="",
            description="Empty string",
            order=2
        ),
        TestCase(
            exercise_id=exercise2.id,
            input_data={"text": "a"},
            expected_output="a",
            description="Single character",
            order=3
        ),
    ]
    for tc in test_cases_2:
        db.add(tc)

    # Examples for exercise 2
    examples_2 = [
        Example(
            exercise_id=exercise2.id,
            input='reverse_string("world")',
            output='"dlrow"',
            explanation="The string is reversed character by character",
            order=0
        ),
    ]
    for ex in examples_2:
        db.add(ex)

    # Exercise 3: Find Maximum (Intermediate)
    exercise3 = Exercise(
        title="Find Maximum in List",
        description="""# Find Maximum in List

Write a function that takes a list of numbers and returns the maximum value.

## Requirements
- Accept a list of numbers as parameter
- Return the maximum value in the list
- Do NOT use the built-in `max()` function

## Constraints
- List will contain at least one number
- All elements will be valid numbers

## Challenge
Try to solve this without using any built-in functions!
""",
        difficulty=DifficultyLevel.INTERMEDIATE,
        function_name="find_maximum"
    )
    exercise3.categories = [categories[1], categories[3]]  # Lists, Algorithms
    db.add(exercise3)
    await db.flush()

    # Test cases for exercise 3
    test_cases_3 = [
        TestCase(
            exercise_id=exercise3.id,
            input_data={"numbers": [1, 5, 3, 9, 2]},
            expected_output=9,
            description="Unsorted list",
            order=0
        ),
        TestCase(
            exercise_id=exercise3.id,
            input_data={"numbers": [-5, -1, -10, -3]},
            expected_output=-1,
            description="All negative numbers",
            order=1
        ),
        TestCase(
            exercise_id=exercise3.id,
            input_data={"numbers": [42]},
            expected_output=42,
            description="Single element",
            order=2
        ),
        TestCase(
            exercise_id=exercise3.id,
            input_data={"numbers": [1, 2, 3, 4, 5]},
            expected_output=5,
            description="Sorted ascending",
            order=3
        ),
    ]
    for tc in test_cases_3:
        db.add(tc)

    # Examples for exercise 3
    examples_3 = [
        Example(
            exercise_id=exercise3.id,
            input="find_maximum([3, 7, 2, 8, 1])",
            output="8",
            explanation="8 is the largest number in the list",
            order=0
        ),
    ]
    for ex in examples_3:
        db.add(ex)

    # Exercise 4: Is Palindrome (Intermediate)
    exercise4 = Exercise(
        title="Check Palindrome",
        description="""# Check if String is Palindrome

Write a function that checks if a given string is a palindrome.

A palindrome is a word, phrase, or sequence that reads the same backward as forward.

## Requirements
- Accept a string parameter
- Return `True` if the string is a palindrome, `False` otherwise
- Ignore case (treat uppercase and lowercase as the same)
- Ignore spaces

## Examples
- "racecar" → True
- "hello" → False
- "A man a plan a canal Panama" → True (ignoring spaces and case)

## Constraints
- Input will be a valid string
""",
        difficulty=DifficultyLevel.INTERMEDIATE,
        function_name="is_palindrome"
    )
    exercise4.categories = [categories[0], categories[3]]  # Strings, Algorithms
    db.add(exercise4)
    await db.flush()

    # Test cases for exercise 4
    test_cases_4 = [
        TestCase(
            exercise_id=exercise4.id,
            input_data={"text": "racecar"},
            expected_output=True,
            description="Simple palindrome",
            order=0
        ),
        TestCase(
            exercise_id=exercise4.id,
            input_data={"text": "hello"},
            expected_output=False,
            description="Not a palindrome",
            order=1
        ),
        TestCase(
            exercise_id=exercise4.id,
            input_data={"text": "A man a plan a canal Panama"},
            expected_output=True,
            description="Palindrome with spaces and mixed case",
            order=2
        ),
        TestCase(
            exercise_id=exercise4.id,
            input_data={"text": ""},
            expected_output=True,
            description="Empty string is palindrome",
            order=3
        ),
    ]
    for tc in test_cases_4:
        db.add(tc)

    # Examples for exercise 4
    examples_4 = [
        Example(
            exercise_id=exercise4.id,
            input='is_palindrome("madam")',
            output="True",
            explanation="Reads the same forwards and backwards",
            order=0
        ),
        Example(
            exercise_id=exercise4.id,
            input='is_palindrome("python")',
            output="False",
            explanation="Does not read the same backwards",
            order=1
        ),
    ]
    for ex in examples_4:
        db.add(ex)

    print("✓ Created 4 exercises with test cases and examples")


async def seed_database():
    """Main seed function."""
    print("Starting database seed...")

    async with AsyncSessionLocal() as db:
        try:
            # Create categories
            print("Creating categories...")
            categories = await create_categories(db)
            print(f"✓ Created {len(categories)} categories")

            # Create exercises
            print("Creating exercises...")
            await create_exercises(db, categories)

            # Commit all changes
            await db.commit()
            print("\n✅ Database seeded successfully!")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
