import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base

from utils.environment_variables import DATABASE_URL

Base = declarative_base()

# Create an async engine
database_engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session maker for async sessions
async_session = sessionmaker(
    bind=database_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Function to get an async session
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Example usage of async connection
async def test_connection():
    async with async_session() as session:
        # Execute a simple SELECT query to test connection
        result = await session.execute(text("SELECT 1"))
        print("Database connection successful:", result.all())

# Run test connection when executing the script
if __name__ == "__main__":
    asyncio.run(test_connection())
