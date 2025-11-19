from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.config.database import Base

class Example(Base):

	__tablename__ = 'examples'

	id = Column(Integer, primary_key=True, index=True)
	exercise_id = Column(Integer, ForeignKey('exercises.id', ondelete='CASCADE'), nullable=False)
	input = Column(Text, nullable=False)
	output = Column(Text, nullable=False)
	explanation = Column(Text, nullable=True)
	order = Column(Integer, default=0)

	exercise = relationship('Exercise', back_populates='examples')

	def __repr__(self) -> str:
		return f"<Example(id={self.id}, exercise_id={self.exercise_id}, input='{self.input}', output='{self.output}', explanation='{self.explanation}', order={self.order})>"
