from sqlalchemy.future import select

from models.history_model import History
from utils.db_utils import async_session

async def get_user_history(username: str) -> list[History]:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(History).where(History.username == username)
            )
            user_history = result.scalars().all()
    return user_history