from fastapi import UploadFile
import os
import aiofiles
from aiofiles.os import makedirs
from app.core.config import AppSettings
from app.modules.text_generation.rag.extractor import pdf_text_extractor
from app.modules.text_generation.rag.service import vector_service
from loguru import logger
import asyncio


async def save_file(file: UploadFile, settings: AppSettings) -> str:
    await makedirs("uploads", exist_ok=True)
    filepath = os.path.join("uploads", file.filename)
    async with aiofiles.open(filepath, "wb") as f:
        while chunk := await file.read(settings.upload_chunk_size):
            await f.write(chunk)

    return filepath


async def process_and_store_document(filepath: str):
    txt_filepath = filepath.replace("pdf", "txt")

    try:
        logger.info(f"Starting extraction for {filepath}")

        await asyncio.to_thread(pdf_text_extractor, filepath)

        logger.info("Extraction successful. Starting vector storage.")

        await vector_service.store_file_content_in_db(
            filepath=txt_filepath, collection_name="KnowledgeBase"
        )

        logger.info(f"Successfully processed and stored {filepath}")

    except Exception as e:
        logger.error(f"Background processing failed for {filepath}: {e}")
