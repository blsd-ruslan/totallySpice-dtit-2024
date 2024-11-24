import os

from fastapi import APIRouter
from services.ml_services.summarizator import PDFProcessor
from fastapi.responses import FileResponse

ml_router = APIRouter()


@ml_router.get("/get_processed_doc")
async def get_processed_doc(pdf_path="services/ml_services/docs/new.pdf", output_pdf_path="services/ml_services/docs/new_with_anomalies.pdf",
                            openai_api_key=os.getenv("OPENAI_API")):
    processor = PDFProcessor(pdf_path, output_pdf_path, openai_api_key)
    processor.process_pdf()
    file_path = "services/ml_services/docs/new_with_anomalies.pdf"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename="new_with_anomalies.pdf"
        )
    else:
        return {"error": "File not found"}