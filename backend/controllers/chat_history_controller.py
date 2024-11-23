from fastapi import APIRouter
from services.history_service import get_history_by_username

chat_history_router = APIRouter()

@chat_history_router.get("/chat_history")
async def get_chat_history():
    return await get_history_by_username("test_user")