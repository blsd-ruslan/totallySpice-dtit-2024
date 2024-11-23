from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers import chat_history_controller, upload_pdf_controller

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
