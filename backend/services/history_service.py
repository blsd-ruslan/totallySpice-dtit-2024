from models.history_model import History
from repositories.history_repository import get_user_history

async def get_history_by_username(username: str) -> list[History]:
    return await get_user_history(username)
