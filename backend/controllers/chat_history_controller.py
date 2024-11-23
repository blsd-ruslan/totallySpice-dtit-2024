from fastapi import APIRouter

chat_history_router = APIRouter()

@chat_history_router.get("/chat_history")
async def get_chat_history():
    return [
        "Chatter Chronicles",
        "Pixel Talk Archives",
        "Echo Threads",
        "Texted Tales",
        "Whispered Words",
        "Memory Bytes",
        "Dialogue Diary",
        "Message Maze",
        "Threaded Moments",
        "Chat Capsule"
    ]