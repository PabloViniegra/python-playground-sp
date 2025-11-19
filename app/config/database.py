from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from app.config.config import settings

Base = declarative_base()

engine = create_engine(
	settings.database_url,
	pool_pre_ping=True,
	echo=settings.debug
)

async_engine = create_async_engine(
	settings.database_url_async,
	poolclass=NullPool,
	echo=settings.debug
)

AsyncSessionLocal = sessionmaker(
	bind=async_engine,
	class_=AsyncSession,
	expire_on_commit=False,
	autocommit=False,
	autoflush=False,
)

async def get_db():
	async with AsyncSessionLocal() as session:
		try:
			yield session
			await session.commit()
		except Exception:
			await session.rollback()
			raise
		finally:
			await session.close()
