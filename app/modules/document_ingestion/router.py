from fastapi import (
    APIRouter,
    HTTPException,
    status,
    File,
    UploadFile,
    Depends,
    BackgroundTasks,
)
from .schema import UploadResponse
from .service import save_file, process_and_store_document
from typing import Annotated
from app.core.config import AppSettings, get_settings
from .dependencies import limit_docs_ingestion
from ..auth.dependencies import get_current_admin_user




router = APIRouter(
    prefix="/assets/documents",
    tags=["Document Ingestion"],
    dependencies=[Depends(limit_docs_ingestion), Depends(get_current_admin_user)],
)


@router.post("/upload_file", response_model=UploadResponse)
async def file_upload_controller(
    file: Annotated[UploadFile, File(description="Uploaded pdf document")],
    settings: Annotated[AppSettings, Depends(get_settings)],
    bg_text_processor: BackgroundTasks,
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            detail="Only uploading PDF files is supported",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        filepath = await save_file(file=file, settings=settings)
        bg_text_processor.add_task(process_and_store_document, filepath)

    except Exception as e:
        raise HTTPException(
            detail=f"An error occurred while saving file - Error: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return UploadResponse(filename=file.filename, message="file uploaded successfully")
