import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from models.history_model import History
from utils.db_utils import Base, async_session
from utils.environment_variables import DATABASE_URL


# Create an async engine
database_engine = create_async_engine(DATABASE_URL, echo=True)

# Function to create all tables asynchronously
async def create_tables():
    async with database_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully.")

# Function to fill history table with 10 random rows, all having the same username
async def fill_history_table():
    async with async_session() as session:
        async with session.begin():
            username = "test_user"
            chat_names = [
                "General Chat",
                "Support Chat",
                "Dev Team Chat",
                "Marketing Chat",
                "Sales Chat",
                "Product Chat",
                "HR Chat",
                "Finance Chat",
                "Random Chat",
                "Design Chat"
            ]
            rows = [
                History(username=username, chat_name=chat_name)
                for chat_name in chat_names
            ]
            session.add_all(rows)
        await session.commit()
    print("History table filled with 10 random rows.")

async def main():
    await create_tables()
    await fill_history_table()

if __name__ == "__main__":
    asyncio.run(main())