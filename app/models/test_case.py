from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.config.database import Base

class TestCase(Base):

	__tablename__ = 'test_cases'

	id = Column(Integer, primary_key=True, index=True)
	exercise_id = Column(Integer, ForeignKey('exercises.id', ondelete='CASCADE'), nullable=False)
	input_data = Column(JSON, nullable=False)
	expected_output = Column(JSON, nullable=False)
	is_public = Column(Boolean, default=True)
	description = Column(Text, nullable=False)
	order = Column(Integer, default=0)

	exercise = relationship('Exercise', back_populates='test_cases')

	def __repr__(self):
		return f"<TestCase(id={self.id}, exercise_id={self.exercise_id}, input_data={self.input_data}, expected_output={self.expected_output}, is_public={self.is_public}, description={self.description}, order={self.order})>"
