from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from controllers import ml_controller, chat_history_controller, upload_pdf_controller
from utils import create_db_tables

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_history_controller.chat_history_router)
app.include_router(upload_pdf_controller.upload_pdf_router)
app.include_router(ml_controller.ml_router)

# Startup event to initialize the database
@app.on_event("startup")
async def on_startup():
    await create_db_tables.main()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
