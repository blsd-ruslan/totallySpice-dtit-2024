from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from fastapi.responses import FileResponse

from services.ml_services.summarizator import PDFProcessor, ChatProcessor

ml_router = APIRouter()

# Paths
pdf_path = "services/ml_services/docs/new.pdf"
output_pdf_path = "services/ml_services/docs/new_with_anomalies.pdf"
knowledge_base_path = "services/ml_services/docs/knowledge_base.json"
openai_api_key = os.getenv("OPENAI_API")

# Initialize processors
processor = PDFProcessor(pdf_path, output_pdf_path)


class ChatRequest(BaseModel):
    session_id: str
    user_query: str


# @ml_router.get("/get_processed_doc")
async def get_processed_doc():
    processor.process_pdf()
    file_path = output_pdf_path
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename="new_with_anomalies.pdf"
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")


@ml_router.post("/chat")
async def chat_with_pdf(request: ChatRequest):
    """
    Interact with the assistant using session memory.
    """
    chat_processor = ChatProcessor(knowledge_base_path)
    response = chat_processor.get_response(request.user_query, request.session_id)
    return {"response": response}
