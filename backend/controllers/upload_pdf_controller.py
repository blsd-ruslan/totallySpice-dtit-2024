import os
from fastapi.responses import FileResponse

from fastapi import APIRouter, UploadFile, File, HTTPException
from services.minio_service import upload_file_to_minio
from services.ml_services.summarizator import PDFProcessor

upload_pdf_router = APIRouter()

@upload_pdf_router.post("/process_pdf")
async def upload_pdfs(user_document: UploadFile = File(...), instruction_document: UploadFile = File(...)):
    # Validate the uploaded files are PDFs
    if user_document.content_type != 'application/pdf' or instruction_document.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Both files must be PDFs")

    try:
        await upload_file_to_minio(user_document)
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to upload {user_document.filename}: {str(err)}")

    try:
        await upload_file_to_minio(instruction_document)
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to upload {instruction_document.filename}: {str(err)}")

    output_file_path = "check.pdf"
    processor = PDFProcessor(user_document.filename, output_file_path)
    processor.process_pdf()
    if os.path.exists(output_file_path):
        return FileResponse(
            path=output_file_path,
            media_type="application/pdf",
            filename="new_with_anomalies.pdf"
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")


    # return {"message": "Successfully uploaded both PDF files.", "files": [user_document.filename, instruction_document.filename]}
