from fastapi import APIRouter, UploadFile, File, HTTPException
from services.minio_service import upload_file_to_minio

upload_pdf_router = APIRouter()

@upload_pdf_router.post("/upload_pdfs")
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

    return {"message": "Successfully uploaded both PDF files.", "files": [user_document.filename, instruction_document.filename]}
