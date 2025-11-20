import enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.config.database import Base


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


exercise_categories = Table(
    "exercise_categories",
    Base.metadata,
    Column(
        "exercise_id", Integer, ForeignKey("exercises.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        SQLEnum(DifficultyLevel), nullable=False, index=True
    )
    function_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    categories = relationship(
        "Category", secondary="exercise_categories", back_populates="exercises"
    )
    test_cases = relationship("TestCase", back_populates="exercise", cascade="all, delete-orphan")
    examples = relationship(
        "Example", back_populates="exercise", cascade="all, delete-orphan", order_by="Example.order"
    )

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, title='{self.title}')>"
