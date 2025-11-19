from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.config.database import Base

class DifficultyLevel(str, enum.Enum):
	BEGINNER = "beginner"
	INTERMEDIATE = "intermediate"
	ADVANCED = "advanced"

exercise_categories = Table(
	'exercise_categories',
	Base.metadata,
	Column('exercise_id', Integer, ForeignKey('exercises.id', ondelete='CASCADE'), primary_key=True),
	Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)

class Exercise(Base):

	__tablename__ = 'exercises'

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(200), nullable=False, index=True)
	description = Column(Text, nullable=False)
	difficulty = Column(SQLEnum(DifficultyLevel), nullable=False, index=True)
	function_name = Column(String(100), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

	categories = relationship(
		'Category',
		secondary='exercise_categories',
		back_populates='exercises'
	)
	test_cases = relationship(
		'TestCase',
		back_populates='exercise',
		cascade='all, delete-orphan'
	)
	examples = relationship(
		'Example',
		back_populates='exercise',
		cascade='all, delete-orphan',
		order_by='Example.order'
	)

	def __repr__(self):
		return f"<Exercise(id={self.id}, title='{self.title}')>"
